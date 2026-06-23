# Nyon réaliste — Bedrock

## Fichier principal recommandé

Importer dans Minecraft Bedrock :

```text
../export/nyon-realiste.mcworld
```

## Fichiers Bedrock disponibles

- `nyon-realiste.mcworld` — monde avec pack Nyon attaché.
- `nyon-realiste-mcworld.zip` — copie ZIP si l'extension `.mcworld` est refusée.
- `nyon-realiste.mcaddon` — add-on de construction Nyon.
- `nyon-preview.png` — aperçu visuel.

## Commandes en jeu

Pour construire Nyon :

```mcfunction
/function build_nyon
```

Méthode plus sûre par morceaux :

```mcfunction
/function nyon/nyon_part000
...
/function nyon/nyon_part110
/function fix_lake_geneva
```

