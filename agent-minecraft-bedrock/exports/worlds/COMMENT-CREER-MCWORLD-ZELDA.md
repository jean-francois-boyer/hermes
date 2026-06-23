# Créer le vrai fichier .mcworld pour le monde aventure fantasy

## Pourquoi il me faut un template

Un vrai fichier `.mcworld` Bedrock contient une base de données interne `db/` + `level.dat`.
Ces fichiers sont générés par Minecraft Bedrock lui-même. Sans eux, un `.mcworld` fabriqué depuis zéro risque de ne pas s'ouvrir.

Le pack actuel existe déjà :

- `mission-aventure-fantasy.mcaddon` — pack principal
- `heros-aventure-fantasy.mcpack` — skin du héros

Mais pour générer un **vrai monde importable `.mcworld`**, il faut partir d'un monde vierge exporté par Minecraft Bedrock.

## Étapes côté utilisateur

1. Ouvre Minecraft Bedrock sur Windows, Android, iPhone ou iPad.
2. Crée un nouveau monde :
   - Nom : `Monde Aventure Fantasy Template`
   - Mode : Créatif
   - Triche : Activée
   - Type : Plat de préférence
3. Entre dans le monde une fois, puis quitte pour qu'il soit bien sauvegardé.
4. Dans la liste des mondes, clique sur le crayon / paramètres.
5. Choisis **Exporter le monde**.
6. Tu obtiens un fichier `.mcworld`.
7. Envoie-moi ce fichier ici, ou place-le dans :

```text
/opt/data/workspace/agent-minecraft-bedrock/templates/monde-vierge-aventure-fantasy.mcworld
```

## Ce que je ferai ensuite automatiquement

Quand le template sera disponible, je générerai :

```text
/opt/data/workspace/agent-minecraft-bedrock/exports/worlds/monde-aventure-fantasy.mcworld
```

Ce fichier contiendra :

- le monde Bedrock réel (`db/`, `level.dat`),
- le behavior pack aventure fantasy,
- le resource pack,
- les fonctions `/function start` et `/function quests`,
- les fonctions des zones : village, temple, volcan, sanctuaire.

## Pour Switch

Ensuite :

1. Importe le `.mcworld` final sur PC/mobile Bedrock.
2. Ouvre le monde et lance `/function start`.
3. Envoie le monde sur Realms.
4. Ouvre le Realm depuis ta Nintendo Switch.
