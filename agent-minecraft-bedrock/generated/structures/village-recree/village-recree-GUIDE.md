# Guide Structure — Village Recree

Généré le : 2026-06-21 20:37

## Brief

village médiéval avec spawn, maisons, marché et donjon

## Origine

`0 70 0`

## Fichiers `.mcfunction`

- `village-recree.mcfunction`
- `village-recree_spawn.mcfunction`
- `village-recree_market.mcfunction`
- `village-recree_dungeon.mcfunction`
- `village-recree_houses.mcfunction`

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
/function village-recree
```

Tu peux aussi lancer les modules séparés :

```mcfunction
/function village-recree_spawn
/function village-recree_market
/function village-recree_houses
/function village-recree_dungeon
```

## Attention

Les commandes utilisent `/fill` et `/setblock`. Teste d'abord dans une copie du monde.
