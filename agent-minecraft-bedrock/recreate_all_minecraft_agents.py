#!/usr/bin/env python3
"""Recrée/vérifie tous les agents Minecraft Bedrock du workspace.

Ce script sert de point d'entrée unique pour restaurer les artefacts générés par
les agents déjà créés : monde, structures, skins, .mcaddon et .mcworld de test.
Il ne remplace pas un vrai template .mcworld Bedrock : pour un monde jouable, il
faut fournir un export .mcworld venant de Minecraft Bedrock.
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent

AGENTS = {
    "minecraft_agent.py": "Agent monde : blueprint, quêtes, PNJ, commandes Bedrock, add-on template.",
    "mcaddon_export_agent.py": "Agent export : prépare un .mcaddon importable Bedrock.",
    "mcworld_export_agent.py": "Agent monde complet : injecte les packs dans un template .mcworld.",
    "skin_agent.py": "Agent skins : génère PNG 64x64, prévisualisation et .mcpack.",
    "structure_agent.py": "Agent structures : génère villages/donjons/sanctuaires en .mcfunction.",
}


def run(cmd: list[str]) -> dict[str, object]:
    proc = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    return {
        "cmd": cmd,
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }


def require_agents() -> None:
    missing = [name for name in AGENTS if not (ROOT / name).exists()]
    if missing:
        raise SystemExit(f"Agents manquants: {', '.join(missing)}")


def main() -> None:
    require_agents()
    python = sys.executable
    results: list[dict[str, object]] = []

    # Compilation syntaxique de tous les agents.
    results.append(run([python, "-m", "py_compile", *AGENTS.keys()]))

    # Recréation des artefacts principaux.
    results.append(run([
        python,
        "minecraft_agent.py",
        "Crée un monde aventure fantasy compatible Switch avec village, quêtes, donjon, PNJ et économie.",
    ]))
    results.append(run([
        python,
        "structure_agent.py",
        "village médiéval avec spawn, maisons, marché et donjon",
        "--name",
        "Village Recree",
        "--origin",
        "0 70 0",
    ]))
    results.append(run([
        python,
        "skin_agent.py",
        "héros aventure fantasy vert bleu et or",
        "--name",
        "Heros Recree",
        "--model",
        "slim",
    ]))
    results.append(run([python, "mcaddon_export_agent.py", "--regenerate-uuids", "--name", "Agents Minecraft Recréés"]))
    results.append(run([python, "mcworld_export_agent.py", "--create-test-template", "--world-name", "Test Agents Recréés"]))

    ok = all(item["returncode"] == 0 for item in results)
    report = {
        "status": "ok" if ok else "error",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "root": str(ROOT),
        "agents": AGENTS,
        "results": results,
        "important_note": "Le .mcworld de test valide le packaging mais n'est pas un vrai monde jouable sans template Bedrock réel.",
    }
    out = ROOT / "generated" / "recreate_all_agents_report.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"status": report["status"], "report": str(out)}, indent=2, ensure_ascii=False))
    if not ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
