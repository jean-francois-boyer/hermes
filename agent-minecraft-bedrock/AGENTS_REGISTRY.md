# Registre des agents Minecraft Bedrock recréés

Dernière recréation demandée : 2026-06-21

Ce workspace contient les agents Minecraft Bedrock/Switch-via-Realms suivants.

| Agent | Fichier | Rôle | Sorties principales |
|---|---|---|---|
| Monde | `minecraft_agent.py` | Génère blueprint, zones, PNJ, quêtes, commandes Bedrock et add-on de base | `generated/world_blueprint.md`, `generated/addon/`, `generated/*.mcaddon` |
| Export add-on | `mcaddon_export_agent.py` | Produit un `.mcaddon` importable, avec `.mcpack` behavior/resource | `exports/import-ready/*.mcaddon` |
| Monde complet | `mcworld_export_agent.py` | Injecte les packs dans un template `.mcworld` Bedrock réel | `exports/worlds/*.mcworld` |
| Skins | `skin_agent.py` | Génère skin PNG 64x64, preview et skin pack | `generated/skins/*.png`, `exports/skin-packs/*.mcpack` |
| Structures | `structure_agent.py` | Génère villages, donjons, tours, marchés en `.mcfunction` | `generated/structures/*`, `exports/structures/*.zip` |

## Point d’entrée unique

Pour recréer/vérifier tous les artefacts principaux :

```bash
cd /opt/data/workspace/agent-minecraft-bedrock
python3 recreate_all_minecraft_agents.py
```

Le rapport est écrit ici :

```text
generated/recreate_all_agents_report.json
```

## Commandes individuelles

### Monde

```bash
python3 minecraft_agent.py "Crée un monde aventure fantasy compatible Switch avec village, quêtes, donjon, PNJ et économie."
```

### Structures

```bash
python3 structure_agent.py "village médiéval avec spawn, maisons, marché et donjon" --name "Village Recree" --origin "0 70 0"
```

### Skin

```bash
python3 skin_agent.py "héros aventure fantasy vert bleu et or" --name "Heros Recree" --model slim
```

### Add-on importable

```bash
python3 mcaddon_export_agent.py --regenerate-uuids --name "Agents Minecraft Recréés"
```

### Monde `.mcworld`

Avec un vrai template Bedrock :

```bash
python3 mcworld_export_agent.py --template /chemin/monde-vierge.mcworld --world-name "Mon Monde Recréé"
```

Test packaging uniquement :

```bash
python3 mcworld_export_agent.py --create-test-template --world-name "Test Agents Recréés"
```

## Important Switch / Realms

La Switch doit généralement passer par Minecraft Realms : créer/tester le monde sur Bedrock PC/mobile, importer les packs, puis envoyer le monde sur Realm et rejoindre depuis la Switch avec le même compte Microsoft/Xbox.
