#!/usr/bin/env python3
"""Agent d'export .mcworld pour Minecraft Bedrock.

Important : créer un monde Bedrock complet depuis zéro est complexe, car Bedrock
stocke les chunks et entités dans une base LevelDB (`db/`). Le workflow fiable est
plutôt :

1. Créer un monde vierge/modèle dans Minecraft Bedrock PC/mobile.
2. Exporter ce monde en `.mcworld`.
3. Lancer cet agent avec `--template ton_monde.mcworld`.
4. L'agent injecte le Behavior Pack / Resource Pack générés et produit un
   nouveau `.mcworld` importable.

Cet agent ne falsifie pas de monde : sans vrai template `.mcworld`, il peut créer
un template de test pour vérifier le packaging, mais le résultat de test n'est pas
un vrai monde jouable.
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
EXPORT_DIR = ROOT / "exports" / "worlds"
IMPORT_READY_DIR = ROOT / "exports" / "import-ready"


@dataclass
class PackInfo:
    uuid: str
    version: list[int]
    name: str


@dataclass
class WorldExportResult:
    world_name: str
    mcworld: Path
    report: Path
    behavior_pack: PackInfo
    resource_pack: PackInfo | None


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9àâäéèêëîïôöùûüçñ -]", "", text)
    text = text.translate(str.maketrans("àâäéèêëîïôöùûüçñ", "aaaeeeeiioouuucn"))
    text = re.sub(r"\s+", "-", text)
    return text[:70].strip("-") or "monde-bedrock"


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"JSON invalide dans {path}: {exc}") from exc


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def ensure_addon_exists() -> Path:
    if (DEFAULT_ADDON_DIR / "behavior_pack" / "manifest.json").exists():
        return DEFAULT_ADDON_DIR
    minecraft_agent = ROOT / "minecraft_agent.py"
    example = ROOT / "examples" / "village_medieval.md"
    if minecraft_agent.exists():
        cmd = [sys.executable, str(minecraft_agent)]
        if example.exists():
            cmd += ["--brief-file", str(example)]
        subprocess.run(cmd, cwd=ROOT, check=True)
    if not (DEFAULT_ADDON_DIR / "behavior_pack" / "manifest.json").exists():
        raise SystemExit("Aucun add-on généré trouvé. Lance d'abord minecraft_agent.py.")
    return DEFAULT_ADDON_DIR


def read_pack_info(pack_dir: Path) -> PackInfo:
    manifest_path = pack_dir / "manifest.json"
    if not manifest_path.exists():
        raise SystemExit(f"Manifest introuvable : {manifest_path}")
    manifest = load_json(manifest_path)
    header = manifest.get("header", {})
    pack_uuid = header.get("uuid")
    if not isinstance(pack_uuid, str):
        raise SystemExit(f"UUID manquant dans {manifest_path}")
    try:
        uuid.UUID(pack_uuid)
    except ValueError as exc:
        raise SystemExit(f"UUID invalide dans {manifest_path}: {pack_uuid}") from exc
    version = header.get("version", [1, 0, 0])
    if not isinstance(version, list) or len(version) != 3:
        version = [1, 0, 0]
    name = str(header.get("name", pack_dir.name))
    return PackInfo(uuid=pack_uuid, version=[int(x) for x in version], name=name)


def extract_mcworld(template: Path, destination: Path) -> None:
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True)
    if not template.exists():
        raise SystemExit(f"Template .mcworld introuvable : {template}")
    with zipfile.ZipFile(template) as zf:
        zf.extractall(destination)


def detect_world_name(world_dir: Path, fallback: str | None) -> str:
    if fallback:
        return fallback
    levelname = world_dir / "levelname.txt"
    if levelname.exists():
        name = levelname.read_text(encoding="utf-8", errors="ignore").strip()
        if name:
            return name
    return "Mon Monde Agent Minecraft"


def inject_packs(world_dir: Path, addon_dir: Path) -> tuple[PackInfo, PackInfo | None]:
    behavior_src = addon_dir / "behavior_pack"
    resource_src = addon_dir / "resource_pack"
    behavior_info = read_pack_info(behavior_src)
    resource_info = read_pack_info(resource_src) if (resource_src / "manifest.json").exists() else None

    behavior_dest_root = world_dir / "behavior_packs"
    resource_dest_root = world_dir / "resource_packs"
    behavior_dest_root.mkdir(exist_ok=True)
    resource_dest_root.mkdir(exist_ok=True)

    behavior_dest = behavior_dest_root / slugify(behavior_info.name)
    if behavior_dest.exists():
        shutil.rmtree(behavior_dest)
    shutil.copytree(behavior_src, behavior_dest)

    if resource_info is not None:
        resource_dest = resource_dest_root / slugify(resource_info.name)
        if resource_dest.exists():
            shutil.rmtree(resource_dest)
        shutil.copytree(resource_src, resource_dest)

    write_json(world_dir / "world_behavior_packs.json", [
        {"pack_id": behavior_info.uuid, "version": behavior_info.version}
    ])
    if resource_info is not None:
        write_json(world_dir / "world_resource_packs.json", [
            {"pack_id": resource_info.uuid, "version": resource_info.version}
        ])

    return behavior_info, resource_info


def write_world_metadata(world_dir: Path, world_name: str) -> None:
    (world_dir / "levelname.txt").write_text(world_name + "\n", encoding="utf-8")
    (world_dir / "README_AGENT_IMPORT.txt").write_text(
        "Monde préparé par mcworld_export_agent.py\n"
        "Après import dans Minecraft Bedrock, vérifier que les packs sont actifs.\n"
        "Commandes de test : /function start puis /function quests\n",
        encoding="utf-8",
    )


def zip_mcworld(world_dir: Path, output: Path) -> None:
    if output.exists():
        output.unlink()
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(world_dir.rglob("*")):
            if path.is_file():
                zf.write(path, path.relative_to(world_dir))


def validate_mcworld_structure(mcworld: Path, expect_real_world: bool) -> None:
    with zipfile.ZipFile(mcworld) as zf:
        names = set(zf.namelist())
    required = {
        "levelname.txt",
        "world_behavior_packs.json",
    }
    missing = sorted(required - names)
    if missing:
        raise SystemExit(f".mcworld incomplet : fichiers manquants {missing}")
    if not any(name.startswith("behavior_packs/") and name.endswith("manifest.json") for name in names):
        raise SystemExit(".mcworld incomplet : behavior pack non injecté")
    if expect_real_world and not any(name.startswith("db/") for name in names):
        raise SystemExit(
            ".mcworld non valide comme vrai monde Bedrock : dossier db/ absent. "
            "Fournis un .mcworld exporté depuis Minecraft Bedrock comme template."
        )


def export_world(template: Path, addon_dir: Path, world_name: str | None, allow_no_db: bool = False) -> WorldExportResult:
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="mcworld-export-") as tmp:
        work = Path(tmp) / "world"
        extract_mcworld(template, work)
        detected_name = detect_world_name(work, world_name)
        write_world_metadata(work, detected_name)
        behavior_info, resource_info = inject_packs(work, addon_dir)
        output = EXPORT_DIR / f"{slugify(detected_name)}.mcworld"
        zip_mcworld(work, output)

    validate_mcworld_structure(output, expect_real_world=not allow_no_db)
    report = EXPORT_DIR / f"{slugify(detected_name)}-MCWORLD-IMPORT.md"
    write_report(report, detected_name, output, behavior_info, resource_info, allow_no_db)
    return WorldExportResult(detected_name, output, report, behavior_info, resource_info)


def create_test_template(output: Path) -> Path:
    """Crée un faux template pour tester le packaging. Non jouable dans Bedrock."""
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="mcworld-test-template-") as tmp:
        world = Path(tmp) / "world"
        (world / "db").mkdir(parents=True)
        (world / "levelname.txt").write_text("Template Test Agent Minecraft\n", encoding="utf-8")
        (world / "db" / "PLACEHOLDER_NOT_A_REAL_LEVELDB.txt").write_text(
            "Ce fichier sert uniquement au test du packaging. Crée un vrai monde dans Minecraft Bedrock pour l'import réel.\n",
            encoding="utf-8",
        )
        with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zf:
            for path in sorted(world.rglob("*")):
                if path.is_file():
                    zf.write(path, path.relative_to(world))
    return output


def write_report(report: Path, world_name: str, mcworld: Path, behavior: PackInfo, resource: PackInfo | None, test_mode: bool) -> None:
    warning = (
        "⚠️ Ce fichier a été généré avec un template de test. Il vérifie le packaging, "
        "mais il ne remplace pas un vrai monde exporté depuis Minecraft Bedrock."
        if test_mode else
        "Ce fichier a été généré depuis un template .mcworld fourni. Il doit être importable dans Minecraft Bedrock si le template d'origine était valide."
    )
    resource_line = f"- Resource Pack : `{resource.name}` / `{resource.uuid}`" if resource else "- Resource Pack : non inclus"
    report.write_text(
        f"""# Export .mcworld — {world_name}

Export généré le : {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Fichier à importer

- `.mcworld` : `{mcworld}`

## Statut

{warning}

## Packs injectés

- Behavior Pack : `{behavior.name}` / `{behavior.uuid}`
{resource_line}

## Procédure fiable

1. Sur Minecraft Bedrock PC/mobile, crée un monde vierge.
2. Exporte-le en `.mcworld`.
3. Lance :

```bash
python3 mcworld_export_agent.py --template /chemin/ton_monde.mcworld --world-name "{world_name}"
```

4. Importe le `.mcworld` généré dans Minecraft Bedrock.
5. Ouvre les paramètres du monde et vérifie que les packs sont actifs.
6. Active les cheats si besoin.
7. Teste :

```mcfunction
/function start
/function quests
```

## Switch

Une fois le monde testé sur PC/mobile, upload-le sur Minecraft Realms puis rejoins-le depuis la Switch avec le même compte Microsoft/Xbox.
""",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Agent d’export .mcworld pour Minecraft Bedrock")
    parser.add_argument("--template", type=Path, help="Vrai fichier .mcworld exporté depuis Minecraft Bedrock")
    parser.add_argument("--addon-dir", type=Path, default=None, help="Dossier addon contenant behavior_pack/resource_pack")
    parser.add_argument("--world-name", default=None, help="Nom du monde exporté")
    parser.add_argument("--create-test-template", action="store_true", help="Crée un template de test non jouable pour valider le packaging")
    args = parser.parse_args()

    addon_dir = args.addon_dir or ensure_addon_exists()

    allow_no_db = False
    if args.create_test_template:
        template = create_test_template(EXPORT_DIR / "_template-test-non-jouable.mcworld")
        allow_no_db = True
    elif args.template:
        template = args.template
    else:
        raise SystemExit(
            "Il faut fournir un vrai template .mcworld :\n"
            "  python3 mcworld_export_agent.py --template /chemin/monde.mcworld\n\n"
            "Pour tester seulement le packaging :\n"
            "  python3 mcworld_export_agent.py --create-test-template"
        )

    result = export_world(template, addon_dir, args.world_name, allow_no_db=allow_no_db)
    print("Export .mcworld terminé ✅")
    print(f"- monde: {result.world_name}")
    print(f"- mcworld: {result.mcworld}")
    print(f"- guide_import: {result.report}")
    print(f"- behavior_pack: {result.behavior_pack.name}")
    if result.resource_pack:
        print(f"- resource_pack: {result.resource_pack.name}")


if __name__ == "__main__":
    main()
