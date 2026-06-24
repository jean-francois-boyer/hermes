# Europa‑Park réaliste — Minecraft Bedrock

Reconstruction **géographiquement fidèle et stylisée** du parc d’attractions **Europa‑Park** à Rust, Allemagne, générée à partir des données réelles **OpenStreetMap**.

> Données © contributeurs OpenStreetMap — licence ODbL.

## Dossiers

```text
Minecraft/EuropaPark/
├── export/   # fichiers à importer dans Minecraft Bedrock
├── source/   # générateur + données OSM + fonctions source
└── docs/     # guides et statistiques
```

## Fichier recommandé

Importer dans Minecraft Bedrock :

```text
../export/europa-park-realiste.mcworld
```

## Fichiers exportés

| Fichier | Usage |
|---|---|
| `europa-park-realiste.mcworld` | Monde Bedrock avec le pack attaché |
| `europa-park-realiste-mcworld.zip` | Copie ZIP si `.mcworld` est refusé par une plateforme |
| `europa-park-realiste.mcaddon` | Add-on seul, à activer dans un monde Bedrock |
| `europa-park-preview.png` | Aperçu carte du parc généré |

## Commandes en jeu

Après import du monde, active les triches si nécessaire, lance le monde, appuie sur `T`, puis :

```mcfunction
/function start_europa_park
```

Pour construire tout le parc :

```mcfunction
/function build_europa_park
```

Méthode plus sûre par morceaux :

```mcfunction
/function europa_park/europa_park_part000
/function europa_park/europa_park_part001
...
/function europa_park/europa_park_part147
```

## Limites honnêtes

- C’est une reconstruction **OSM en blocs** : positions, chemins, bâtiments, eau, rails et montagnes russes sont stylisés à partir des données réelles.
- Version réaliste v2 : matériaux différenciés, toits, fenêtres, rails de montagnes russes avec hauteurs variables, supports, lampadaires, arbres, fleurs et marqueurs d’attractions.
- Ce n’est pas une copie texturée/photographique : pas d’intérieurs, pas de détails de décors officiels, pas de personnages ou logos protégés.
- Le fichier contient le pack de construction ; comme pour Nyon, les blocs apparaissent après exécution des fonctions `/function`.
- Pour Nintendo Switch : construire/tester sur Windows Bedrock ou mobile, sauvegarder, puis envoyer sur Realms.
