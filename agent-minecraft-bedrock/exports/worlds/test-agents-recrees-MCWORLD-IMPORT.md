# Export .mcworld — Test Agents Recréés

Export généré le : 2026-06-21 20:37

## Fichier à importer

- `.mcworld` : `/opt/data/workspace/agent-minecraft-bedrock/exports/worlds/test-agents-recrees.mcworld`

## Statut

⚠️ Ce fichier a été généré avec un template de test. Il vérifie le packaging, mais il ne remplace pas un vrai monde exporté depuis Minecraft Bedrock.

## Packs injectés

- Behavior Pack : `Le Royaume des Blocs Oubliés - Behavior Pack` / `f599363b-927a-429f-aa2f-e78d06f4c6e2`
- Resource Pack : `Le Royaume des Blocs Oubliés - Resource Pack` / `8f4d9056-72ca-4ab2-8432-0239db0b3b4f`

## Procédure fiable

1. Sur Minecraft Bedrock PC/mobile, crée un monde vierge.
2. Exporte-le en `.mcworld`.
3. Lance :

```bash
python3 mcworld_export_agent.py --template /chemin/ton_monde.mcworld --world-name "Test Agents Recréés"
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
