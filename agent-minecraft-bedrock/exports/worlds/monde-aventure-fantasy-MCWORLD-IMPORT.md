# Export .mcworld — Monde Aventure Fantasy

Export généré le : 2026-06-22 17:36

## Fichier à importer

- `.mcworld` : `/opt/data/workspace/agent-minecraft-bedrock/exports/worlds/monde-aventure-fantasy.mcworld`

## Statut

Ce fichier a été généré depuis un template .mcworld fourni. Il doit être importable dans Minecraft Bedrock si le template d'origine était valide.

## Packs injectés

- Behavior Pack : `Mission Aventure Fantasy - Behavior Pack` / `84b3e3f8-3ee8-4d6a-b0d4-3ae4ec5d0cb2`
- Resource Pack : `Mission Aventure Fantasy - Resource Pack` / `79fb8989-87b9-4623-b3cd-3e008eb65450`

## Procédure fiable

1. Sur Minecraft Bedrock PC/mobile, crée un monde vierge.
2. Exporte-le en `.mcworld`.
3. Lance :

```bash
python3 mcworld_export_agent.py --template /chemin/ton_monde.mcworld --world-name "Monde Aventure Fantasy"
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
