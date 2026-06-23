# Guide Structure — Village Kokiri Original

Généré le : 2026-06-20 22:46

## Brief

village forestier héroïque type aventure fantasy avec spawn, maisons en bois, marché aux émeraudes, sanctuaire central et mini donjon

## Origine

`0 70 0`

## Fichiers `.mcfunction`

- `village-kokiri-original.mcfunction`
- `village-kokiri-original_spawn.mcfunction`
- `village-kokiri-original_market.mcfunction`
- `village-kokiri-original_dungeon.mcfunction`
- `village-kokiri-original_houses.mcfunction`

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
/function village-kokiri-original
```

Tu peux aussi lancer les modules séparés :

```mcfunction
/function village-kokiri-original_spawn
/function village-kokiri-original_market
/function village-kokiri-original_houses
/function village-kokiri-original_dungeon
```

## Attention

Les commandes utilisent `/fill` et `/setblock`. Teste d'abord dans une copie du monde.
