# Guide Structure — Temple Foret

Généré le : 2026-06-20 22:46

## Brief

donjon temple de la forêt avec boss, pièges, couloirs, coffre récompense et ambiance héroïque

## Origine

`220 70 0`

## Fichiers `.mcfunction`

- `temple-foret.mcfunction`
- `temple-foret_spawn.mcfunction`
- `temple-foret_market.mcfunction`
- `temple-foret_dungeon.mcfunction`
- `temple-foret_houses.mcfunction`

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
/function temple-foret
```

Tu peux aussi lancer les modules séparés :

```mcfunction
/function temple-foret_spawn
/function temple-foret_market
/function temple-foret_houses
/function temple-foret_dungeon
```

## Attention

Les commandes utilisent `/fill` et `/setblock`. Teste d'abord dans une copie du monde.
