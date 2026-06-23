# Guide Structure — Mont Volcan

Généré le : 2026-06-20 22:46

## Brief

donjon volcanique sombre avec boss, lave, pièges et coffre récompense

## Origine

`0 80 -240`

## Fichiers `.mcfunction`

- `mont-volcan.mcfunction`
- `mont-volcan_spawn.mcfunction`
- `mont-volcan_market.mcfunction`
- `mont-volcan_dungeon.mcfunction`
- `mont-volcan_houses.mcfunction`

## Import dans Bedrock

1. Copie les fichiers `.mcfunction` dans le behavior pack :
   `behavior_pack/functions/`
2. Réexporte le `.mcaddon` avec :

```bash
python3 mcaddon_export_agent.py --regenerate-uuids
```

3. Dans Minecraft Bedrock, active le behavior pack.
4. Lance :

```mcfunction
/function mont-volcan
```

Tu peux aussi lancer les modules séparés :

```mcfunction
/function mont-volcan_spawn
/function mont-volcan_market
/function mont-volcan_houses
/function mont-volcan_dungeon
```

## Attention

Les commandes utilisent `/fill` et `/setblock`. Teste d'abord dans une copie du monde.
