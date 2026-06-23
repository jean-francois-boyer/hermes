# Export .mcworld — Test Packaging Agent Minecraft

Export généré le : 2026-06-20 17:46

## Fichier à importer

- `.mcworld` : `/opt/data/workspace/agent-minecraft-bedrock/exports/worlds/test-packaging-agent-minecraft.mcworld`

## Statut

⚠️ Ce fichier a été généré avec un template de test. Il vérifie le packaging, mais il ne remplace pas un vrai monde exporté depuis Minecraft Bedrock.

## Packs injectés

- Behavior Pack : `Les Îles du Port d’Émeraude - Behavior Pack` / `a8d100cc-51b1-4de0-9b6e-a01662c1d60b`
- Resource Pack : `Les Îles du Port d’Émeraude - Resource Pack` / `bd23c5ef-de34-476c-9d9f-eecfb4cb1994`

## Procédure fiable

1. Sur Minecraft Bedrock PC/mobile, crée un monde vierge.
2. Exporte-le en `.mcworld`.
3. Lance :

```bash
python3 mcworld_export_agent.py --template /chemin/ton_monde.mcworld --world-name "Test Packaging Agent Minecraft"
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
