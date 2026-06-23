#!/usr/bin/env python3
from __future__ import annotations

import argparse
import io
import json
import os
import re
from pathlib import Path

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError

TOKEN = "/opt/data/google_token.json"
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


def unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    stem, suffix = path.stem, path.suffix
    parent = path.parent
    i = 2
    while True:
        candidate = parent / f"{stem} ({i}){suffix}"
        if not candidate.exists():
            return candidate
        i += 1


def load_service():
    creds = Credentials.from_authorized_user_file(TOKEN)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        Path(TOKEN).write_text(json.dumps(json.loads(creds.to_json()), indent=2), encoding="utf-8")
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


def download_request(request, output: Path):
    output.parent.mkdir(parents=True, exist_ok=True)
    tmp = output.with_suffix(output.suffix + ".download")
    with tmp.open("wb") as fh:
        downloader = MediaIoBaseDownload(fh, request, chunksize=1024 * 1024)
        done = False
        while not done:
            _, done = downloader.next_chunk()
    tmp.replace(output)


def download_file(service, file, local_dir: Path, stats: dict):
    name = safe_name(file["name"])
    mime = file.get("mimeType", "")
    file_id = file["id"]

    if mime in GOOGLE_EXPORTS:
        export_mime, suffix = GOOGLE_EXPORTS[mime]
        if not Path(name).suffix:
            name += suffix
        else:
            name += suffix
        output = unique_path(local_dir / name)
        try:
            request = service.files().export_media(fileId=file_id, mimeType=export_mime)
            download_request(request, output)
            stats["google_native_exported"] += 1
            stats["bytes_downloaded"] += output.stat().st_size
            return output
        except HttpError as exc:
            err = local_dir / f"{safe_name(file['name'])}.download-error.txt"
            err.write_text(f"Could not export {file['name']} ({file_id}) as {export_mime}: {exc}\n", encoding="utf-8")
            stats["errors"] += 1
            return err

    output = unique_path(local_dir / name)
    try:
        request = service.files().get_media(fileId=file_id, supportsAllDrives=True)
        download_request(request, output)
        stats["binary_downloaded"] += 1
        stats["bytes_downloaded"] += output.stat().st_size
        return output
    except HttpError as exc:
        err = local_dir / f"{name}.download-error.txt"
        err.write_text(f"Could not download {file['name']} ({file_id}): {exc}\n", encoding="utf-8")
        stats["errors"] += 1
        return err


def sync_folder(service, parent_id: str, local_dir: Path, stats: dict, seen_folders: set[str]):
    if parent_id in seen_folders:
        stats["folders_skipped_cycle"] += 1
        return
    seen_folders.add(parent_id)
    local_dir.mkdir(parents=True, exist_ok=True)

    for item in list_children(service, parent_id):
        mime = item.get("mimeType", "")
        name = safe_name(item.get("name", "unnamed"))
        if mime == FOLDER_MIME:
            child_dir = unique_path(local_dir / name)
            stats["folders_created"] += 1
            sync_folder(service, item["id"], child_dir, stats, seen_folders)
        elif mime == SHORTCUT_MIME:
            target = item.get("shortcutDetails", {}).get("targetId")
            target_mime = item.get("shortcutDetails", {}).get("targetMimeType")
            if target and target_mime == FOLDER_MIME:
                child_dir = unique_path(local_dir / f"{name} - shortcut")
                stats["shortcuts_followed"] += 1
                sync_folder(service, target, child_dir, stats, seen_folders)
            elif target:
                meta = service.files().get(
                    fileId=target,
                    fields="id,name,mimeType,modifiedTime,size,md5Checksum,webViewLink",
                    supportsAllDrives=True,
                ).execute()
                stats["shortcuts_followed"] += 1
                download_file(service, meta, local_dir, stats)
            else:
                stats["shortcuts_skipped"] += 1
        else:
            download_file(service, item, local_dir, stats)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default="/opt/data/workspace/drive")
    args = ap.parse_args()

    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)

    service = load_service()
    about = service.about().get(fields="user(displayName,emailAddress),storageQuota").execute()
    stats = {
        "folders_created": 0,
        "folders_skipped_cycle": 0,
        "binary_downloaded": 0,
        "google_native_exported": 0,
        "shortcuts_followed": 0,
        "shortcuts_skipped": 0,
        "errors": 0,
        "bytes_downloaded": 0,
        "output": str(output),
        "user": about.get("user", {}),
    }

    sync_folder(service, "root", output, stats, set())
    report = output / "_sync_report.json"
    report.write_text(json.dumps(stats, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(stats, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
