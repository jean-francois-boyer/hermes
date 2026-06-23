# Minecraft Swarm Hermes/Kanban

Ce fichier documente le swarm créé pour rendre les agents Minecraft visibles/organisés côté Hermes/Kanban.

## Board

- Slug : `minecraft-swarm`
- Nom : `Minecraft Swarm`
- Workspace par défaut : `/opt/data/workspace/agent-minecraft-bedrock`

Commandes utiles :

```bash
hermes kanban boards switch minecraft-swarm
hermes kanban --board minecraft-swarm list
hermes kanban --board minecraft-swarm stats
hermes kanban --board minecraft-swarm assignees
```

## Profils Hermes créés

| Profil | Rôle |
|---|---|
| `minecraftorchestrator` | Orchestration / décomposition du swarm |
| `minecraftworld` | Blueprint monde, quêtes, zones, PNJ |
| `minecraftstructures` | Structures `.mcfunction` |
| `minecraftskins` | Skins PNG + `.mcpack` |
| `minecraftaddon` | Packaging `.mcaddon` |
| `minecraftmcworld` | Workflow `.mcworld` avec template Bedrock |
| `minecraftverifier` | QA / vérification des artefacts |
| `minecraftsynthesizer` | Synthèse finale utilisateur |

## Swarm initial créé

Root : `t_57cc6e42`

Workers parallèles :

- `t_4fde38e9` → `minecraftworld` → Créer le blueprint monde Bedrock complet
- `t_e35dde75` → `minecraftstructures` → Générer structures Bedrock mcfunction
- `t_a9291ea9` → `minecraftskins` → Générer skin héros et skin pack
- `t_35c9e17e` → `minecraftaddon` → Exporter mcaddon importable Bedrock
- `t_a3b979e7` → `minecraftmcworld` → Préparer workflow mcworld avec template

Fan-in :

- `t_7a7a697f` → `minecraftverifier` → Verify swarm outputs
- `t_2e125eba` → `minecraftsynthesizer` → Synthesize swarm outputs

## Créer un nouveau swarm Minecraft

```bash
hermes kanban --board minecraft-swarm swarm \
  "Mission complète Minecraft Bedrock: produire un monde aventure original compatible Switch via Realms, avec blueprint, structures, skin, add-on importable et préparation mcworld." \
  --worker "minecraftworld:Créer le blueprint monde Bedrock complet" \
  --worker "minecraftstructures:Générer structures Bedrock mcfunction" \
  --worker "minecraftskins:Générer skin héros et skin pack" \
  --worker "minecraftaddon:Exporter mcaddon importable Bedrock" \
  --worker "minecraftmcworld:Préparer workflow mcworld avec template" \
  --verifier minecraftverifier \
  --synthesizer minecraftsynthesizer \
  --tenant minecraft \
  --priority 10 \
  --created-by minecraftorchestrator \
  --json
```

## Notes

Le gateway Hermes doit rester actif pour que le dispatcher Kanban lance les workers. Le profil `default` a actuellement le gateway en route.
