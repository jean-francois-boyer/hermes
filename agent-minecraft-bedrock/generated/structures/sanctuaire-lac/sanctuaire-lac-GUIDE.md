# Guide Structure — Sanctuaire Lac

Généré le : 2026-06-20 22:46

## Brief

tour sanctuaire du lac bleu avec lumière, énigme et coffre récompense

## Origine

`-220 68 0`

## Fichiers `.mcfunction`

- `sanctuaire-lac.mcfunction`
- `sanctuaire-lac_spawn.mcfunction`
- `sanctuaire-lac_market.mcfunction`
- `sanctuaire-lac_dungeon.mcfunction`
- `sanctuaire-lac_tower.mcfunction`

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
/function sanctuaire-lac
```

Tu peux aussi lancer les modules séparés :

```mcfunction
/function sanctuaire-lac_spawn
/function sanctuaire-lac_market
/function sanctuaire-lac_houses
/function sanctuaire-lac_dungeon
```

## Attention

Les commandes utilisent `/fill` et `/setblock`. Teste d'abord dans une copie du monde.
