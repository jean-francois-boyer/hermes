#!/usr/bin/env python3
"""Agent d'export .mcaddon importable dans Minecraft Bedrock.

Objectif : prendre le dossier généré par `minecraft_agent.py` ou le template Bedrock,
valider les manifests, créer des `.mcpack`, puis créer un `.mcaddon` propre pour
l'import dans Minecraft Bedrock PC/mobile avant l'envoi sur Realm/Switch.

Workflow recommandé :
1. `python3 minecraft_agent.py --brief-file examples/village_medieval.md`
2. `python3 mcaddon_export_agent.py`
3. Double-cliquer / importer le fichier dans `exports/import-ready/*.mcaddon`
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
import uuid
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
GENERATED_DIR = ROOT / "generated"
DEFAULT_ADDON_DIR = GENERATED_DIR / "addon"
TEMPLATE_DIR = ROOT / "bedrock-addon-template"
EXPORT_DIR = ROOT / "exports" / "import-ready"


@dataclass
class ExportResult:
    name: str
    behavior_mcpack: Path
    resource_mcpack: Path | None
    mcaddon: Path
    report: Path


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9àâäéèêëîïôöùûüçñ -]", "", text)
    text = text.translate(str.maketrans("àâäéèêëîïôöùûüçñ", "aaaeeeeiioouuucn"))
    text = re.sub(r"\s+", "-", text)
    return text[:70].strip("-") or "addon-bedrock"


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"JSON invalide dans {path}: {exc}") from exc


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def ensure_generated_addon() -> Path:
    """S'assure qu'un addon existe. Sinon lance minecraft_agent.py avec l'exemple."""
    if (DEFAULT_ADDON_DIR / "behavior_pack" / "manifest.json").exists():
        return DEFAULT_ADDON_DIR

    minecraft_agent = ROOT / "minecraft_agent.py"
    example = ROOT / "examples" / "village_medieval.md"
    if minecraft_agent.exists():
        cmd = [sys.executable, str(minecraft_agent)]
        if example.exists():
            cmd += ["--brief-file", str(example)]
        subprocess.run(cmd, cwd=ROOT, check=True)
        if (DEFAULT_ADDON_DIR / "behavior_pack" / "manifest.json").exists():
            return DEFAULT_ADDON_DIR

    if TEMPLATE_DIR.exists():
        DEFAULT_ADDON_DIR.parent.mkdir(parents=True, exist_ok=True)
        if DEFAULT_ADDON_DIR.exists():
            shutil.rmtree(DEFAULT_ADDON_DIR)
        shutil.copytree(TEMPLATE_DIR, DEFAULT_ADDON_DIR)
        return DEFAULT_ADDON_DIR

    raise SystemExit("Impossible de trouver ou générer un dossier add-on Bedrock.")


def detect_pack_name(addon_dir: Path, fallback: str | None = None) -> str:
    manifest = addon_dir / "behavior_pack" / "manifest.json"
    if manifest.exists():
        data = load_json(manifest)
        header_name = data.get("header", {}).get("name")
        if isinstance(header_name, str) and header_name.strip():
            cleaned = header_name.replace("- Behavior Pack", "").strip()
            return cleaned or header_name.strip()
    if fallback:
        return fallback
    return "Agent Minecraft Bedrock"


def validate_and_fix_manifest(path: Path, pack_kind: str, pack_name: str, regenerate_uuids: bool) -> list[str]:
    """Valide et corrige un manifest Bedrock minimal."""
    warnings: list[str] = []
    if not path.exists():
        raise SystemExit(f"Manifest manquant : {path}")

    data = load_json(path)
    data.setdefault("format_version", 2)
    header = data.setdefault("header", {})
    modules = data.setdefault("modules", [{}])
    if not modules:
        modules.append({})

    header.setdefault("description", f"{pack_name} généré par l’agent d’export .mcaddon")
    header["name"] = f"{pack_name} - {pack_kind}"
    header.setdefault("version", [1, 0, 0])
    header.setdefault("min_engine_version", [1, 20, 0])

    expected_module_type = "data" if pack_kind == "Behavior Pack" else "resources"
    modules[0].setdefault("description", f"Module {pack_kind}")
    modules[0]["type"] = expected_module_type
    modules[0].setdefault("version", [1, 0, 0])

    for key_path, container in [("header.uuid", header), ("modules[0].uuid", modules[0])]:
        current = container.get("uuid")
        if regenerate_uuids or not is_uuid(current):
            if current and not is_uuid(current):
                warnings.append(f"UUID invalide remplacé dans {path.name}: {key_path}")
            container["uuid"] = str(uuid.uuid4())

    write_json(path, data)
    return warnings


def is_uuid(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        uuid.UUID(value)
        return True
    except ValueError:
        return False


def zip_directory(source_dir: Path, output_file: Path) -> None:
    if output_file.exists():
        output_file.unlink()
    with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(source_dir.rglob("*")):
            if path.is_file():
                # Pour un .mcpack, manifest.json doit être à la racine du zip.
                zf.write(path, path.relative_to(source_dir))


def validate_zip_contains(zip_path: Path, required: list[str]) -> None:
    with zipfile.ZipFile(zip_path) as zf:
        names = set(zf.namelist())
    missing = [item for item in required if item not in names]
    if missing:
        raise SystemExit(f"Export incomplet dans {zip_path}: fichiers manquants {missing}")


def export_mcaddon(addon_dir: Path, name: str | None = None, regenerate_uuids: bool = False) -> ExportResult:
    pack_name = name or detect_pack_name(addon_dir)
    slug = slugify(pack_name)
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    # Travail dans une copie pour ne pas casser les sources générées.
    with tempfile.TemporaryDirectory(prefix="mcaddon-export-") as tmp:
        work = Path(tmp) / "addon"
        shutil.copytree(addon_dir, work)

        behavior_dir = work / "behavior_pack"
        resource_dir = work / "resource_pack"
        if not behavior_dir.exists():
            raise SystemExit(f"behavior_pack manquant dans {addon_dir}")

        warnings = []
        warnings += validate_and_fix_manifest(
            behavior_dir / "manifest.json", "Behavior Pack", pack_name, regenerate_uuids
        )

        has_resource = resource_dir.exists() and (resource_dir / "manifest.json").exists()
        if has_resource:
            warnings += validate_and_fix_manifest(
                resource_dir / "manifest.json", "Resource Pack", pack_name, regenerate_uuids
            )

        behavior_mcpack = EXPORT_DIR / f"{slug}-behavior.mcpack"
        resource_mcpack = EXPORT_DIR / f"{slug}-resources.mcpack" if has_resource else None
        mcaddon = EXPORT_DIR / f"{slug}.mcaddon"
        report = EXPORT_DIR / f"{slug}-IMPORT.md"

        zip_directory(behavior_dir, behavior_mcpack)
        validate_zip_contains(behavior_mcpack, ["manifest.json"])

        if has_resource and resource_mcpack is not None:
            zip_directory(resource_dir, resource_mcpack)
            validate_zip_contains(resource_mcpack, ["manifest.json"])

        if mcaddon.exists():
            mcaddon.unlink()
        with zipfile.ZipFile(mcaddon, "w", zipfile.ZIP_DEFLATED) as zf:
            # Format robuste : le .mcaddon contient les .mcpack.
            zf.write(behavior_mcpack, behavior_mcpack.name)
            if resource_mcpack is not None:
                zf.write(resource_mcpack, resource_mcpack.name)

        required = [behavior_mcpack.name]
        if resource_mcpack is not None:
            required.append(resource_mcpack.name)
        validate_zip_contains(mcaddon, required)

    write_import_report(report, pack_name, behavior_mcpack, resource_mcpack, mcaddon, warnings)
    return ExportResult(pack_name, behavior_mcpack, resource_mcpack, mcaddon, report)


def write_import_report(
    report: Path,
    pack_name: str,
    behavior_mcpack: Path,
    resource_mcpack: Path | None,
    mcaddon: Path,
    warnings: list[str],
) -> None:
    warning_block = "\n".join(f"- {w}" for w in warnings) if warnings else "- Aucun avertissement."
    resource_line = f"- Resource pack : `{resource_mcpack}`" if resource_mcpack else "- Resource pack : non inclus"
    report.write_text(
        f"""# Import Bedrock — {pack_name}

Export généré le : {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Fichier principal à importer

- `.mcaddon` : `{mcaddon}`
- Behavior pack : `{behavior_mcpack}`
{resource_line}

## Procédure d’import Minecraft Bedrock

1. Télécharge ou copie le fichier `.mcaddon` sur l’appareil où Minecraft Bedrock est installé.
2. Double-clique sur le fichier `.mcaddon`, ou ouvre-le avec Minecraft.
3. Minecraft doit afficher un message du type « Import started » puis « Successfully imported ».
4. Crée ou modifie un monde.
5. Dans les paramètres du monde, active le Behavior Pack et le Resource Pack générés.
6. Active les cheats / commandes si tu veux lancer les fonctions.
7. Dans le monde, teste :

```mcfunction
/function start
/function quests
```

## Pour jouer sur Switch

1. Fais d’abord l’import et le test sur Minecraft Bedrock PC/mobile.
2. Upload ensuite le monde sur Minecraft Realms.
3. Sur Switch, connecte-toi au même compte Microsoft/Xbox.
4. Rejoins le Realm depuis l’onglet Amis / Realms.

## Avertissements / corrections

{warning_block}
""",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Agent d’export .mcaddon pour Minecraft Bedrock")
    parser.add_argument("--addon-dir", type=Path, default=None, help="Dossier contenant behavior_pack/resource_pack")
    parser.add_argument("--name", default=None, help="Nom public du pack exporté")
    parser.add_argument("--regenerate-uuids", action="store_true", help="Regénère les UUID des manifests")
    args = parser.parse_args()

    addon_dir = args.addon_dir or ensure_generated_addon()
    result = export_mcaddon(addon_dir, name=args.name, regenerate_uuids=args.regenerate_uuids)

    print("Export .mcaddon terminé ✅")
    print(f"- nom: {result.name}")
    print(f"- mcaddon: {result.mcaddon}")
    print(f"- behavior_mcpack: {result.behavior_mcpack}")
    if result.resource_mcpack:
        print(f"- resource_mcpack: {result.resource_mcpack}")
    print(f"- guide_import: {result.report}")


if __name__ == "__main__":
    main()
