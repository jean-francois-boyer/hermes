# Workflow — Planification de production horlogère

## Entrées à demander ou importer

- OF / ordres de fabrication: référence, calibre, quantité, priorité, client, date promise
- BOM / nomenclature par référence
- BOM générique de référence déjà fournie: /opt/data/workspace/production-planning-agent/references/bom_montre_mecanique.json
- Stock disponible, stock réservé, stock en quarantaine, stock qualité bloqué
- Réceptions attendues: composant, fournisseur, quantité, date confirmée, fiabilité
- Capacité atelier: horlogers, postes, compétences, temps standard, absences
- Étapes nécessaires: kit, mouvement, emboîtage, cadran/aiguilles, réglage, QC, étanchéité, habillage, packaging
- Contraintes: séries limitées, VIP, lancement, SAV, sous-traitance, validation qualité

## Étapes

1. Collecter OF + BOM + stocks + réceptions + capacité.
2. Faire le contrôle de complétude composants par OF en comparant chaque OF à la BOM de référence ou à sa BOM spécifique. Pour automatiser ce contrôle, lancer `python3 scripts/check_component_availability.py --input examples/donnees_exemple_planification_horlogere.json`.
3. Classer les OF:
   - complet: tous composants disponibles et libérés qualité
   - partiel: démarrage possible mais finalisation impossible
   - bloqué composant: pièce obligatoire manquante
   - bloqué capacité: composants OK mais atelier saturé
   - bloqué qualité/décision: validation ou non-conformité en attente
4. Prioriser les OF complets ou stratégiques.
5. Construire un planning qui évite de lancer des montres immobilisées inutilement en WIP.
6. Réserver les composants rares pour les OF prioritaires.
7. Créer le plan d'action des manquants: relance fournisseur, réception, contrôle entrée, alternative validée, replanification.
8. Vérifier les goulots: horlogers spécialisés, réglage, QC, étanchéité, composants critiques.
9. Publier le planning atelier + la liste des décisions à prendre.

## Règles de planification

- Pas d'assemblage final planifié si la BOM obligatoire n'est pas complète.
- Pour une montre mécanique à remontage manuel, contrôler au minimum: habillage, cadran/affichage, mouvement complet, organes de remontage/mise à l'heure, minuterie, bâti/ponts/pierres et composants d'étanchéité.
- Une date de réception non confirmée doit être traitée comme risque, pas comme disponibilité ferme.
- Ne pas consommer un composant rare sur un OF non prioritaire si cela bloque une livraison critique.
- Prévoir un buffer pour contrôle qualité et reprises.
- Réduire le WIP: préférer finir des OF complets plutôt qu'ouvrir trop de lots incomplets.
- Distinguer disponibilité physique, disponibilité réservée et disponibilité libérée qualité.

## Contrôle automatique

Le script `scripts/check_component_availability.py` génère dans `outputs/`:

- component_availability_report.json
- component_availability_by_of.csv
- missing_components_report.csv
- of_status_report.csv
- dashboard_planning.md


## Cycle S&OP / S&OE

1. Demand Review: commandes fermes, prévisions, lancements, VIP, wholesale.
2. Supply Review: composants, fournisseurs, qualité, capacité atelier, contraintes.
3. Pre-S&OP: scénarios, gaps demande/supply, arbitrages possibles.
4. Executive S&OP: décisions direction, promesses client, allocations composants rares.
5. S&OE: exécution hebdomadaire/quotidienne, exceptions et replanification.

## ATP / CTP

- ATP = disponibilité composants + qualité + réceptions confirmées.
- CTP = capacité atelier + compétences + postes + qualité + délai réaliste.
- Une promesse client n'est fiable que si ATP = OUI et CTP = OUI.

## Exception management

Remonter en priorité:
- OF bloqué composant
- OF bloqué qualité
- réception fournisseur non confirmée
- capacité insuffisante
- composant rare à allouer
- date promise irréaliste

## KPI Supply Chain

- taux OF GO
- taux OF bloqués composant/qualité
- OTIF / promesses à risque
- charge/capacité
- couverture de stock
- fiabilité fournisseur
- backlog jours
