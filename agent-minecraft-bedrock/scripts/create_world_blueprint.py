#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime
import sys
import textwrap


def main():
    idea = " ".join(sys.argv[1:]).strip()
    if not idea:
        idea = "Village médiéval fantasy avec quêtes, donjon, PNJ et économie"

    root = Path(__file__).resolve().parents[1]
    out_dir = root / "generated"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "world_blueprint.md"

    content = f"""# Blueprint de monde Minecraft Bedrock

Généré le : {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Idée de départ

{idea}

## Nom proposé

Le Royaume des Blocs Oubliés

## Objectif

Créer un monde aventure Minecraft Bedrock jouable sur Nintendo Switch via Realm. Le joueur commence dans une zone sûre, rencontre des PNJ, accomplit des quêtes, explore des zones dangereuses et débloque des récompenses.

## Paramètres recommandés

- Édition : Minecraft Bedrock
- Accès Switch : Minecraft Realms
- Mode : Survie avec commandes de préparation
- Difficulté : Normale
- Command blocks : Activés
- Coordonnées du spawn : 0 70 0
- Keep inventory : true pour une expérience plus accessible

## Carte textuelle

- Centre : village de départ, spawn, marché, panneau de quêtes
- Nord : château en ruine avec mini-boss
- Sud : mine abandonnée avec ressources rares
- Est : port marchand avec boutiques
- Ouest : forêt magique avec énigmes
- Sous-sol : salle secrète finale

## Coordonnées proposées

- Spawn : 0 70 0
- Village : -40 65 -40 à 40 80 40
- Château : 0 80 -220
- Mine : 0 55 220
- Port : 220 64 0
- Forêt : -220 70 0
- Salle finale : 0 30 0

## PNJ

1. Maire Aldric : accueille le joueur et donne la quête principale.
2. Forgeronne Mira : vend armes et outils.
3. Cartographe Noé : donne les coordonnées des zones.
4. Marchande Lila : échange des ressources contre émeraudes.
5. Gardien Ordan : débloque l’accès au château.

## Quêtes

### Quête 1 — Bienvenue au village

Objectif : parler au maire et lire le panneau de règles.
Récompense : pain, torches, carte.

### Quête 2 — La mine oubliée

Objectif : récupérer 10 minerais de fer dans la mine.
Récompense : épée en fer.

### Quête 3 — Les bois magiques

Objectif : trouver une fleur rare dans la forêt.
Récompense : potion de soin.

### Quête 4 — Le port marchand

Objectif : échanger 5 émeraudes avec un marchand.
Récompense : arc et flèches.

### Quête 5 — Le château en ruine

Objectif : vaincre le mini-boss et récupérer la relique.
Récompense : accès à la salle finale.

## Commandes Bedrock de base

```mcfunction
/setworldspawn 0 70 0
/gamerule keepinventory true
/gamerule mobgriefing false
/title @a title Bienvenue dans le Royaume des Blocs Oubliés
/give @a bread 16
/give @a torch 32
```

## Exemple de scoreboard pour quêtes

```mcfunction
/scoreboard objectives add quete dummy Quêtes
/scoreboard players set @a quete 0
```

Progression suggérée :

- 0 : arrivée
- 1 : quête village terminée
- 2 : mine terminée
- 3 : forêt terminée
- 4 : port terminé
- 5 : château terminé

## Checklist de construction

1. Créer le monde Bedrock.
2. Activer les cheats et command blocks.
3. Définir le spawn.
4. Construire le village central.
5. Placer les panneaux de règles et de quêtes.
6. Construire les 4 zones principales.
7. Ajouter coffres, récompenses et mobs.
8. Tester chaque quête.
9. Importer le monde dans un Realm.
10. Rejoindre le Realm depuis la Switch.

## Procédure Switch

1. Ouvre Minecraft Bedrock sur PC ou mobile.
2. Crée ou importe le monde.
3. Teste le monde localement.
4. Ouvre ton Realm.
5. Remplace le monde du Realm par ce monde.
6. Sur Switch, connecte-toi au même compte Microsoft.
7. Va dans Amis / Realms et rejoins le monde.
"""

    out_file.write_text(content, encoding="utf-8")
    print(f"Blueprint généré : {out_file}")


if __name__ == "__main__":
    main()
