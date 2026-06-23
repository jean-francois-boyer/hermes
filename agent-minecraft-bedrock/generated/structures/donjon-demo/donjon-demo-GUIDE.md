# Guide Structure — Donjon Demo

Généré le : 2026-06-20 18:46

## Brief

donjon sombre avec boss, pièges et coffre récompense

## Origine

`100 60 100`

## Fichiers `.mcfunction`

- `donjon-demo.mcfunction`
- `donjon-demo_spawn.mcfunction`
- `donjon-demo_market.mcfunction`
- `donjon-demo_dungeon.mcfunction`
- `donjon-demo_houses.mcfunction`

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
/function donjon-demo
```

Tu peux aussi lancer les modules séparés :

```mcfunction
/function donjon-demo_spawn
/function donjon-demo_market
/function donjon-demo_houses
/function donjon-demo_dungeon
```

## Attention

Les commandes utilisent `/fill` et `/setblock`. Teste d'abord dans une copie du monde.
