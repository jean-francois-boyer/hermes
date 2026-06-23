# Agent Minecraft Bedrock pour Switch

Ce dossier contient la première version de ton agent de création de monde Minecraft Bedrock.

Objectif : générer des concepts de mondes, zones, quêtes, PNJ, règles de gameplay et commandes compatibles Minecraft Bedrock, puis préparer le contenu pour l’importer dans un monde Bedrock et l’utiliser sur Nintendo Switch via Minecraft Realms.

## Important pour la Switch

La Switch ne peut pas facilement rejoindre un serveur Bedrock personnalisé par IP. Le workflow recommandé est :

1. Créer ou modifier le monde sur PC/mobile avec Minecraft Bedrock.
2. Utiliser l’agent pour générer le design du monde, les commandes, les quêtes et les add-ons.
3. Importer ou reproduire le contenu dans Minecraft Bedrock.
4. Mettre le monde sur un Realm.
5. Rejoindre le Realm depuis la Switch avec le même compte Microsoft/Xbox.

## Contenu du projet

- `agent_prompt.md` : prompt système de l’agent.
- `world_brief_template.md` : formulaire pour demander un monde à l’agent.
- `output_format.md` : format que l’agent doit respecter.
- `examples/village_medieval.md` : exemple de demande.
- `scripts/create_world_blueprint.py` : générateur local de blueprint de base sans API.
- `bedrock-addon-template/` : squelette d’add-on Bedrock avec behavior pack et resource pack.

## Utilisation simple

Copie le contenu de `agent_prompt.md` dans ton outil IA préféré comme prompt système.

Puis donne-lui une demande basée sur `world_brief_template.md`, par exemple :

"Crée un monde aventure médiéval-fantasy Bedrock compatible Switch, avec une ville de départ, 5 quêtes, 3 donjons, des PNJ, une économie simple et une zone secrète."

L’agent doit répondre avec :

- un plan global du monde
- une carte textuelle
- une liste de zones
- les PNJ
- les quêtes
- les règles
- les commandes Bedrock utiles
- les étapes d’import dans Minecraft Bedrock / Realm

## Utilisation locale sans API

### Générateur simple historique

Depuis ce dossier :

```bash
python3 scripts/create_world_blueprint.py "Village médiéval avec quêtes, donjon et économie"
```

Cela génère un fichier `generated/world_blueprint.md`.

### Nouvel agent complet

Le fichier `minecraft_agent.py` reprend les fichiers déjà créés dans ce workspace :

- `agent_prompt.md`
- `world_brief_template.md`
- `output_format.md`
- `examples/village_medieval.md`
- `bedrock-addon-template/`

Il génère :

- un blueprint complet : `generated/world_blueprint.md`
- une version nommée du blueprint : `generated/<nom>-blueprint.md`
- des fichiers `.mcfunction` : `generated/addon/behavior_pack/functions/`
- un add-on importable : `generated/<nom>.mcaddon`

#### Exemple rapide

```bash
python3 minecraft_agent.py "Crée un monde médiéval fantasy compatible Switch avec 5 quêtes, 5 PNJ, un château, une mine et un port marchand"
```

#### Exemple avec le fichier de brief

```bash
python3 minecraft_agent.py --brief-file examples/village_medieval.md
```

#### Export importable dans Minecraft Bedrock

Le nouvel agent `mcaddon_export_agent.py` prépare un export propre pour Bedrock :

- il vérifie/corrige les `manifest.json`
- il crée un `.mcpack` pour le behavior pack
- il crée un `.mcpack` pour le resource pack si présent
- il crée un `.mcaddon` contenant les `.mcpack`
- il génère un guide d’import `*-IMPORT.md`

```bash
python3 mcaddon_export_agent.py
```

Sortie principale :

```text
exports/import-ready/<nom-du-pack>.mcaddon
```

Si tu veux forcer le nom du pack :

```bash
python3 mcaddon_export_agent.py --name "Mon Monde Bedrock"
```

Si Minecraft refuse un import à cause d’un conflit d’UUID, relance :

```bash
python3 mcaddon_export_agent.py --regenerate-uuids
```

#### Export d’un vrai monde `.mcworld`

Le fichier `mcworld_export_agent.py` est le troisième agent. Il sert à générer un `.mcworld` en partant d’un **vrai monde modèle exporté depuis Minecraft Bedrock**.

Pourquoi un template est nécessaire : un monde Bedrock complet contient une base LevelDB dans `db/`. La créer proprement depuis zéro est beaucoup moins fiable que partir d’un monde vierge exporté par Minecraft.

Workflow recommandé :

1. Ouvre Minecraft Bedrock sur PC/mobile.
2. Crée un monde vierge.
3. Exporte ce monde en `.mcworld`.
4. Copie ce fichier dans le workspace.
5. Lance :

```bash
python3 mcworld_export_agent.py --template /chemin/ton_monde.mcworld --world-name "Mon Monde Agent Minecraft"
```

Sortie principale :

```text
exports/worlds/mon-monde-agent-minecraft.mcworld
```

Pour tester uniquement le packaging sans vrai monde jouable :

```bash
python3 mcworld_export_agent.py --create-test-template --world-name "Test Packaging"
```

#### Agent de création de skins Minecraft

Le fichier `skin_agent.py` génère des skins Minecraft sans dépendance externe :

- skin PNG 64x64 compatible Bedrock/Java
- prévisualisation agrandie
- skin pack Bedrock `.mcpack`
- guide d’import

Exemple :

```bash
python3 skin_agent.py "chevalier futuriste bleu et or" --name "Chevalier IA" --model classic
```

Sorties :

```text
generated/skins/chevalier-ia.png
generated/skins/chevalier-ia-preview.png
exports/skin-packs/chevalier-ia.mcpack
```

Autres thèmes utiles :

```bash
python3 skin_agent.py "youtubeur IA rouge et noir" --name "YouTubeur IA"
python3 skin_agent.py "ninja cyber violet" --name "Ninja Cyber" --model slim
python3 skin_agent.py "pirate aventure avec veste rouge" --name "Pirate Aventure"
python3 skin_agent.py "mage bleu avec symbole doré" --name "Mage Bleu"
```

#### Agent de structures Minecraft

Le fichier `structure_agent.py` génère des constructions Bedrock sous forme de fichiers `.mcfunction` :

- spawn / hub
- maisons
- marché
- donjon avec mobs, piège et coffre
- tour simple
- guide d’import
- archive `.zip` des fonctions

Exemple village :

```bash
python3 structure_agent.py "village médiéval avec spawn, maisons, marché et donjon" --name "Village Demo" --origin "0 70 0"
```

Exemple donjon :

```bash
python3 structure_agent.py "donjon sombre avec boss, pièges et coffre récompense" --name "Donjon Demo" --origin "0 70 0"
```

Sorties :

```text
generated/structures/<nom>/<nom>.mcfunction
generated/structures/<nom>/<nom>_spawn.mcfunction
generated/structures/<nom>/<nom>_market.mcfunction
generated/structures/<nom>/<nom>_houses.mcfunction
generated/structures/<nom>/<nom>_dungeon.mcfunction
exports/structures/<nom>-structures.zip
```

Par défaut, l’agent copie aussi les fonctions dans :

```text
generated/addon/behavior_pack/functions/
```

Puis tu peux réexporter le `.mcaddon` :

```bash
python3 mcaddon_export_agent.py --regenerate-uuids
```

Dans Minecraft Bedrock :

```mcfunction
/function village-demo
```

#### Dans Minecraft Bedrock

Après import du `.mcaddon`, active le Behavior Pack dans les paramètres du monde, puis lance :

```mcfunction
/function start
/function quests
```

Pour importer un skin :

1. Ouvre Minecraft Bedrock.
2. Va dans le vestiaire.
3. Importe le PNG 64x64 généré, ou ouvre le `.mcpack` avec Minecraft.
4. Sélectionne le modèle `classic` ou `slim` selon la génération.

## Prochaine étape

L’agent génère maintenant un vrai squelette d’add-on Bedrock, des `.mcpack`, et un `.mcaddon` importable. Les limites restantes sont :

- génération de structures `.mcstructure` non incluse
- monde `.mcworld` complet non généré automatiquement
- test final à faire dans Minecraft Bedrock PC/mobile avant l’envoi sur Realm/Switch
