# 🏘️ Nyon Réaliste — Monde Minecraft Bedrock (données OSM réelles)

Reconstitution **réaliste** du centre-ville de **Nyon (Vaud, Suisse)** générée à
partir des **vraies données OpenStreetMap** (licence ODbL), à l'échelle
**1 bloc = 1 mètre**.

## 📦 Contenu généré

| Élément | Valeur |
|---|---|
| Bâtiments réels | **1018** (empreintes + hauteurs OSM extrudées) |
| Routes / rues | **820** |
| 🌊 Eau (lac + cours d'eau) | 14 zones + **surface complète du Lac Léman** |
| Taille du monde | **2837 × 2786 blocs** (≈ 2,8 km × 2,8 km) |
| Commandes générées | **1 013 039** |
| Fichiers `.mcfunction` | 111 parties + 1 maître + 1 correctif Lac Léman |
| `.mcaddon` | `exports/nyon-realiste.mcaddon` (~3,27 Mo) |

Zone couverte (bbox) : `46.3673, 6.2276` → `46.3923, 6.2646`
(château de Nyon, vieille ville, port, bord du lac Léman).

## ✅ Import sur Minecraft Bedrock (PC/mobile)

1. Double-clique sur `nyon-realiste.mcaddon` → Minecraft l'importe (behavior pack).
2. Crée **un nouveau monde plat (Superflat)** :
   - Type de monde : **Plat**
   - Active **« Activer la triche »** (obligatoire pour `/function`)
   - Active le **behavior pack « Nyon Réaliste (OSM) »** dans les réglages du monde.
3. Place-toi en `0 64 0`, oriente-toi, puis lance la construction :

```mcfunction
/function build_nyon
```

> ⚠️ Le monde fait ~1 million de commandes. Lance plutôt les parties **par lots**
> pour éviter de saturer le moteur :
>
> ```mcfunction
> /function nyon/nyon_part000
> /function nyon/nyon_part001
> ...
> /function nyon/nyon_part110
> /function fix_lake_geneva
> ```

## 🎮 Jouer sur Nintendo Switch (via Realms)

1. Construis et teste le monde sur **PC/mobile Bedrock** (les `/function` ne
   peuvent pas être importées directement sur Switch).
2. Une fois construit, **téléverse le monde sur Minecraft Realms**.
3. Rejoins le Realm depuis ta **Switch** avec le **même compte Microsoft/Xbox**.

## 🧱 Légende des matériaux (réalisme par type OSM)

| Type réel (OSM) | Murs | Toit |
|---|---|---|
| Château / patrimoine | `cobblestone` | dalle de pierre |
| Église / lieu de culte | `quartz_block` (blanc) | dalle deepslate |
| Commerce / boutique | `bricks` | dalle de brique |
| Industriel / entrepôt | `smooth_stone` | `iron_block` |
| Public (école, hôpital, gare) | `stone_bricks` | dalle andésite polie |
| Résidentiel (maisons, immeubles) | `bricks` | `dark_oak_planks` |
| Sol / terrain | `grass_block` | — |
| Lac Léman, eau | `water` | — |
| Routes | `stone` | — |

✨ **Améliorations v2** : chaque bâtiment a désormais un **toit plein** posé à son
sommet, et les **matériaux varient selon le type réel** du bâtiment (déduit des
tags OpenStreetMap).

## ⚠️ Limites (honnêteté technique)

- C'est une **reconstitution géographiquement fidèle** (positions, formes,
  hauteurs des bâtiments réels + **relief topographique réel**), **pas une copie
  texturée** : pas de fenêtres ni intérieurs — ce sont des volumes extrudés.
- Les **hauteurs de bâtiments** viennent des tags OSM `height` /
  `building:levels` quand ils existent, sinon 3 étages par défaut.
- Le **relief** provient des données d'altitude réelles **SRTM 30 m**
  (OpenTopoData) : dénivelé réel de **60 m** (lac Léman ~370 m → collines ~430 m),
  interpolé par tuiles de 16×16 blocs.
- Données © contributeurs **OpenStreetMap** (ODbL) + **SRTM/NASA** (élévation).

## 🔁 Régénérer / agrandir

```bash
cd nyon-realistic
# re-télécharger les données OSM (modifier la bbox dans la commande curl)
python3 osm_to_minecraft.py --input nyon_osm_raw.json --out generated --name nyon
python3 package_mcaddon.py
```
