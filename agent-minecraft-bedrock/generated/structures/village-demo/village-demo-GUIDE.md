# Guide Structure — Village Demo

Généré le : 2026-06-20 18:46

## Brief

village médiéval avec spawn, maisons, marché et donjon

## Origine

`0 70 0`

## Fichiers `.mcfunction`

- `village-demo.mcfunction`
- `village-demo_spawn.mcfunction`
- `village-demo_market.mcfunction`
- `village-demo_dungeon.mcfunction`
- `village-demo_houses.mcfunction`

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
/function village-demo
```

Tu peux aussi lancer les modules séparés :

```mcfunction
/function village-demo_spawn
/function village-demo_market
/function village-demo_houses
/function village-demo_dungeon
```

## Attention

Les commandes utilisent `/fill` et `/setblock`. Teste d'abord dans une copie du monde.
