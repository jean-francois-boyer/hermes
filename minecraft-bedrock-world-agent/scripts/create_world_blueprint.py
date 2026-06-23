#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime

root = Path(__file__).resolve().parents[1]
out = root / "generated" / "custom_world_brief.md"
out.parent.mkdir(parents=True, exist_ok=True)

content = f"""# Nouveau brief de monde Minecraft Bedrock

Créé le : {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Demande à copier dans l'agent

Crée un monde Minecraft Bedrock compatible Switch via Realms.

Style : médiéval fantasy
Type : aventure/survie
Joueurs : solo ou amis
Contraintes : sans mods obligatoires, commandes Bedrock simples, facile à construire.

Je veux :
- une zone de spawn
- un village
- 5 PNJ
- 5 quêtes
- 2 donjons
- une économie avec émeraudes
- une checklist pour importer sur Realms et jouer sur Switch
"""

out.write_text(content, encoding="utf-8")
print(out)
