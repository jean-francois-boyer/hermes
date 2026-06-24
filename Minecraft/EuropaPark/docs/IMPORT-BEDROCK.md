# Importer Europa‑Park réaliste dans Minecraft Bedrock Windows

## Option la plus simple : `.mcworld`

1. Télécharge :

```text
europa-park-realiste.mcworld
```

2. Double-clique dessus dans Windows.
3. Minecraft Bedrock s’ouvre et affiche normalement :

```text
Importation commencée
Importation réussie
```

4. Clique `Jouer` → `Mondes`.
5. Ouvre le monde `Europa Park Realiste`.
6. Appuie sur `T` et tape :

```mcfunction
/function start_europa_park
```

7. Pour générer le parc :

```mcfunction
/function build_europa_park
```

⚠️ Le parc contient plus d’un million de commandes. Si Minecraft rame, lance plutôt les fonctions par lots :

```mcfunction
/function europa_park/europa_park_part000
/function europa_park/europa_park_part001
/function europa_park/europa_park_part002
```

Continue progressivement jusqu’à :

```mcfunction
/function europa_park/europa_park_part147
```

## Option add-on : `.mcaddon`

Utilise :

```text
europa-park-realiste.mcaddon
```

1. Double-clique le `.mcaddon`.
2. Minecraft importe le pack.
3. Crée ou modifie un monde.
4. Active : `Packs de comportement` → `Europa‑Park Réaliste (OSM)`.
5. Active `Jeu` → `Activer la triche`.
6. Lance les fonctions ci-dessus.

## Pour Nintendo Switch

La Switch importe mal les fichiers directement. Méthode conseillée :

1. Importer et construire le monde sur Windows Bedrock.
2. Sauvegarder le monde construit.
3. Uploader le monde sur Minecraft Realms.
4. Ouvrir le Realm depuis la Switch avec le même compte Microsoft.
