#!/usr/bin/env python3
"""Agent incrémental Google Drive -> workspace.

- Synchronise Google Drive vers /opt/data/workspace/drive.
- Conserve un état par file_id pour éviter les doublons.
- Écrase le fichier local si le fichier Drive a changé.
- Exporte les fichiers Google natifs vers des formats locaux utiles.
- En mode watchdog/cron, reste silencieux s'il n'y a aucun changement.
"""
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

def default_token() -> str:
    """Token path: env override, else container path if present, else macOS home."""
    env = os.environ.get("HERMES_GOOGLE_TOKEN")
    if env:
        return env
    container = Path("/opt/data/google_token.json")
    if container.exists():
        return str(container)
    return str(Path.home() / ".hermes" / "google_token.json")


def default_output() -> Path:
    """Output dir: env override, else container path if present, else macOS home."""
    env = os.environ.get("HERMES_DRIVE_OUTPUT")
    if env:
        return Path(env)
    container = Path("/opt/data/workspace/drive")
    if container.parent.exists():
        return container
    return Path.home() / "HermesDrive"


STATE_NAME = "_drive_sync_state.json"
REPORT_NAME = "_drive_sync_last_report.json"
FOLDER_MIME = "application/vnd.google-apps.folder"
SHORTCUT_MIME = "application/vnd.google-apps.shortcut"
GOOGLE_EXPORTS = {
    "application/vnd.google-apps.document": ("application/pdf", ".pdf"),
    "application/vnd.google-apps.spreadsheet": (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".xlsx",
    ),
    "application/vnd.google-apps.presentation": ("application/pdf", ".pdf"),
    "application/vnd.google-apps.drawing": ("image/png", ".png"),
    "application/vnd.google-apps.script": ("application/vnd.google-apps.script+json", ".json"),
}


def safe_name(name: str) -> str:
    name = re.sub(r"[\\/:*?\"<>|\x00-\x1f]", "_", name).strip()
    return name or "unnamed"


def load_state(output: Path) -> dict[str, Any]:
    path = output / STATE_NAME
    if not path.exists():
        return {"files": {}, "folders": {}}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"files": {}, "folders": {}}


def save_state(output: Path, state: dict[str, Any]) -> None:
    (output / STATE_NAME).write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def load_service(token: str):
    if not Path(token).exists():
        raise SystemExit(f"Google token introuvable: {token} (utilise --token ou HERMES_GOOGLE_TOKEN)")
    creds = Credentials.from_authorized_user_file(token)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        Path(token).write_text(json.dumps(json.loads(creds.to_json()), indent=2), encoding="utf-8")
    if not creds.valid:
        raise SystemExit("Google credentials are not valid")
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def list_children(service, parent_id: str):
    page_token = None
    while True:
        resp = service.files().list(
            q=f"'{parent_id}' in parents and trashed = false",
            spaces="drive",
            fields=(
                "nextPageToken, files("
                "id,name,mimeType,modifiedTime,size,md5Checksum,shortcutDetails,webViewLink)"
            ),
            pageSize=1000,
            pageToken=page_token,
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
        ).execute()
        yield from resp.get("files", [])
        page_token = resp.get("nextPageToken")
        if not page_token:
            break


def download_request(request, output: Path) -> int:
    output.parent.mkdir(parents=True, exist_ok=True)
    tmp = output.with_name(output.name + ".download")
    with tmp.open("wb") as fh:
        downloader = MediaIoBaseDownload(fh, request, chunksize=1024 * 1024)
        done = False
        while not done:
            _, done = downloader.next_chunk()
    tmp.replace(output)
    return output.stat().st_size


def local_path_for_file(local_dir: Path, item: dict[str, Any]) -> Path:
    name = safe_name(item.get("name", "unnamed"))
    mime = item.get("mimeType", "")
    if mime in GOOGLE_EXPORTS:
        _, suffix = GOOGLE_EXPORTS[mime]
        if not name.lower().endswith(suffix.lower()):
            name += suffix
    return local_dir / name


def should_download(item: dict[str, Any], path: Path, state: dict[str, Any]) -> bool:
    file_id = item["id"]
    previous = state.get("files", {}).get(file_id)
    if not previous:
        return True
    if previous.get("modifiedTime") != item.get("modifiedTime"):
        return True
    if previous.get("local_path") != str(path):
        return True
    if not path.exists():
        return True
    return False


def download_file(service, item: dict[str, Any], local_dir: Path, state: dict[str, Any], stats: dict[str, Any]) -> None:
    path = local_path_for_file(local_dir, item)
    file_id = item["id"]
    mime = item.get("mimeType", "")

    if not should_download(item, path, state):
        stats["unchanged"] += 1
        return

    try:
        if mime in GOOGLE_EXPORTS:
            export_mime, _ = GOOGLE_EXPORTS[mime]
            request = service.files().export_media(fileId=file_id, mimeType=export_mime)
            size = download_request(request, path)
            stats["native_exported"] += 1
        else:
            request = service.files().get_media(fileId=file_id, supportsAllDrives=True)
            size = download_request(request, path)
            stats["binary_downloaded"] += 1

        old = state.setdefault("files", {}).get(file_id)
        if old:
            stats["updated"] += 1
        else:
            stats["new"] += 1

        state.setdefault("files", {})[file_id] = {
            "name": item.get("name"),
            "mimeType": mime,
            "modifiedTime": item.get("modifiedTime"),
            "md5Checksum": item.get("md5Checksum"),
            "size": item.get("size"),
            "local_path": str(path),
            "webViewLink": item.get("webViewLink"),
        }
        stats["bytes_downloaded"] += size
        stats["changed_paths"].append(str(path))
    except HttpError as exc:
        err = path.with_name(path.name + ".download-error.txt")
        err.write_text(f"Could not download/export {item.get('name')} ({file_id}): {exc}\n", encoding="utf-8")
        stats["errors"] += 1
        stats["changed_paths"].append(str(err))


def sync_folder(service, parent_id: str, local_dir: Path, state: dict[str, Any], stats: dict[str, Any], seen: set[str]) -> None:
    if parent_id in seen:
        stats["folders_skipped_cycle"] += 1
        return
    seen.add(parent_id)
    local_dir.mkdir(parents=True, exist_ok=True)
    state.setdefault("folders", {})[parent_id] = str(local_dir)

    for item in list_children(service, parent_id):
        mime = item.get("mimeType", "")
        name = safe_name(item.get("name", "unnamed"))
        if mime == FOLDER_MIME:
            stats["folders_seen"] += 1
            sync_folder(service, item["id"], local_dir / name, state, stats, seen)
        elif mime == SHORTCUT_MIME:
            target = item.get("shortcutDetails", {}).get("targetId")
            target_mime = item.get("shortcutDetails", {}).get("targetMimeType")
            if not target:
                stats["shortcuts_skipped"] += 1
                continue
            stats["shortcuts_followed"] += 1
            if target_mime == FOLDER_MIME:
                sync_folder(service, target, local_dir / f"{name} - shortcut", state, stats, seen)
            else:
                meta = service.files().get(
                    fileId=target,
                    fields="id,name,mimeType,modifiedTime,size,md5Checksum,webViewLink",
                    supportsAllDrives=True,
                ).execute()
                download_file(service, meta, local_dir, state, stats)
        else:
            download_file(service, item, local_dir, state, stats)


def run_sync(output: Path, token: str) -> dict[str, Any]:
    output.mkdir(parents=True, exist_ok=True)
    state = load_state(output)
    stats: dict[str, Any] = {
        "output": str(output),
        "folders_seen": 0,
        "folders_skipped_cycle": 0,
        "new": 0,
        "updated": 0,
        "unchanged": 0,
        "binary_downloaded": 0,
        "native_exported": 0,
        "shortcuts_followed": 0,
        "shortcuts_skipped": 0,
        "errors": 0,
        "bytes_downloaded": 0,
        "changed_paths": [],
    }
    service = load_service(token)
    sync_folder(service, "root", output, state, stats, set())
    save_state(output, state)
    (output / REPORT_NAME).write_text(json.dumps(stats, indent=2, ensure_ascii=False), encoding="utf-8")
    return stats


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=default_output())
    parser.add_argument("--token", default=default_token(), help="Chemin du google_token.json")
    parser.add_argument("--verbose", action="store_true", help="Affiche un rapport même sans changement")
    args = parser.parse_args()

    stats = run_sync(args.output.resolve(), args.token)
    changed = stats["new"] + stats["updated"] + stats["errors"]
    if args.verbose or changed:
        print(json.dumps(stats, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
