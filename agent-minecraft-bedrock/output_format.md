# Format de sortie attendu de l’agent

L’agent doit utiliser cette structure pour chaque monde.

## 1. Concept du monde

Nom du monde :
Genre :
Résumé :
Objectif principal :
Durée estimée :
Nombre de joueurs :

## 2. Paramètres Minecraft Bedrock

Mode recommandé :
Difficulté :
Coordonnée du spawn :
Command blocks : activés/désactivés
Keep inventory : oui/non
Mob griefing : oui/non

## 3. Carte textuelle

Exemple :

Nord : Montagnes gelées
Sud : Marais hanté
Est : Village marchand
Ouest : Forêt ancienne
Centre : Ville de départ

## 4. Zones

Pour chaque zone :

- Nom
- Coordonnées approximatives
- Taille
- Biome conseillé
- Matériaux
- Fonction gameplay
- Secrets

## 5. Spawn

- Description
- Construction
- Commandes de base
- Message de bienvenue

## 6. PNJ

Pour chaque PNJ :

- Nom
- Rôle
- Apparence suggérée
- Position
- Dialogue
- Quête associée

## 7. Quêtes

Pour chaque quête :

- Nom
- Donneur de quête
- Objectif
- Étapes
- Récompense
- Commandes utiles

## 8. Donjons et défis

Pour chaque donjon :

- Nom
- Thème
- Entrée
- Salles
- Ennemis
- Boss
- Récompense

## 9. Économie

- Monnaie
- Boutiques
- Prix
- Récompenses

## 10. Commandes Bedrock

Inclure les commandes utiles, par exemple :

```mcfunction
/setworldspawn 0 70 0
/gamerule keepinventory true
/title @a title Bienvenue dans le royaume
```

## 11. Add-on Bedrock optionnel

Indiquer seulement si nécessaire :

- Behavior pack
- Resource pack
- Entités custom
- Items custom
- Loot tables

## 12. Checklist de construction

- Étape 1
- Étape 2
- Étape 3

## 13. Test Bedrock

- Tester sur PC/mobile Bedrock
- Vérifier les commandes
- Vérifier les chunks
- Vérifier les permissions

## 14. Mise sur Realm pour Switch

1. Ouvrir Minecraft Bedrock sur PC/mobile.
2. Importer ou ouvrir le monde.
3. Aller dans Realms.
4. Remplacer le monde du Realm par ce monde.
5. Ouvrir Minecraft sur Switch.
6. Se connecter au même compte Microsoft.
7. Rejoindre le Realm.