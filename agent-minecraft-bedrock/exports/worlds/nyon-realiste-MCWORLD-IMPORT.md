# Export .mcworld — Nyon Realiste

Export généré le : 2026-06-22 17:46

## Fichier à importer

- `.mcworld` : `/opt/data/workspace/agent-minecraft-bedrock/exports/worlds/nyon-realiste.mcworld`

## Statut

Ce fichier a été généré depuis un template .mcworld fourni. Il doit être importable dans Minecraft Bedrock si le template d'origine était valide.

## Packs injectés

- Behavior Pack : `Nyon Réaliste (OSM)` / `4ab4889b-cbff-41b6-88b0-2fdb0be5244a`
- Resource Pack : non inclus

## Procédure fiable

1. Sur Minecraft Bedrock PC/mobile, crée un monde vierge.
2. Exporte-le en `.mcworld`.
3. Lance :

```bash
python3 mcworld_export_agent.py --template /chemin/ton_monde.mcworld --world-name "Nyon Realiste"
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
