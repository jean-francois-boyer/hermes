# Agent Planification de Production — Manufacture horlogère de luxe

Profil Hermes principal: productionplanner

Rôle: aider à planifier l'assemblage de montres de luxe en tenant compte des nomenclatures, composants critiques, stocks, délais fournisseurs, capacités atelier, priorités commerciales et contraintes qualité.

Point clé métier: si un seul composant obligatoire manque, l'assemblage de la montre ne peut pas être finalisé. L'agent doit donc raisonner en disponibilité complète par référence / ordre de fabrication, pas seulement en charge atelier.

BOM de référence intégrée: montre mécanique à remontage manuel, enregistrée dans `references/bom_montre_mecanique.json` et en version tableur dans `references/bom_montre_mecanique_flat.csv`.

## Ce que l'agent produit

- planning d'assemblage réaliste par OF / référence / calibre / client
- contrôle de complétude BOM avant lancement atelier
- liste des composants manquants et bloquants
- analyse des dates possibles selon stock, réception attendue et capacité
- arbitrages de priorité entre séries, commandes VIP, SAV, lancements et contraintes commerciales
- détection des goulots: composants, horlogers, postes, contrôle qualité, emboîtage, bracelets, certification
- plan d'action approvisionnement / relance fournisseur / substitution validée / replanification

## Sous-agents créés

1. prodstrategy: priorisation des OF et arbitrages business/atelier
2. prodcapacity: capacité atelier, horlogers, postes, charge et goulots
3. prodcalendar: ordonnancement, jalons, dates de début/fin et replanification
4. prodpostprod: contrôle qualité final, emboîtage, habillage, packaging, expédition
5. prodverifier: vérification des composants, BOM, risques et faisabilité avant lancement
6. prodprocurement: approvisionnement, composants manquants, fournisseurs, relances et réservations
7. prodsop: S&OP/S&OE, ATP/CTP, KPI, scénarios, allocations et arbitrages direction

## Commandes de lancement

Agent principal:

HERMES_HOME=/opt/data hermes --profile productionplanner chat -q "Planifie les assemblages horlogers de la semaine avec ces OF, stocks composants, réceptions attendues et capacités atelier: ..."

Sous-agents:

HERMES_HOME=/opt/data hermes --profile prodstrategy chat -q "Priorise ces OF horlogers selon clients, dates promises, valeur et disponibilité composants: ..."
HERMES_HOME=/opt/data hermes --profile prodcapacity chat -q "Vérifie la capacité atelier et les goulots pour ce planning d'assemblage: ..."
HERMES_HOME=/opt/data hermes --profile prodcalendar chat -q "Ordonnance ces OF selon disponibilité composants et capacité: ..."
HERMES_HOME=/opt/data hermes --profile prodpostprod chat -q "Planifie QC, emboîtage, habillage, packaging et expédition: ..."
HERMES_HOME=/opt/data hermes --profile prodverifier chat -q "Audite ce planning: composants manquants, OF bloqués, risques qualité/délai: ..."
HERMES_HOME=/opt/data hermes --profile prodprocurement chat -q "Analyse les composants manquants et propose les relances fournisseurs prioritaires: ..."

## Fichiers utiles

- agent_prompt.md: prompt complet de l'agent principal
- subagents/*.md: prompts spécialisés
- templates/brief_production.md: formulaire de brief manufacture horlogère
- templates/planning_board.csv: modèle de planning OF / composants
- templates/weekly_plan.csv: modèle hebdomadaire atelier
- templates/missing_components.csv: modèle de suivi des composants manquants
- templates/bom_requirements_by_of.csv: matrice BOM x OF x stock
- scripts/check_component_availability.py: contrôle automatique des composants et génération de rapports
- references/bom_montre_mecanique.json: nomenclature structurée de référence
- references/bom_montre_mecanique_flat.csv: nomenclature aplatie pour tableur / contrôle de stock
- workflow.md: méthode opérationnelle de planification horlogère


## Bonnes pratiques Supply Chain / S&OP ajoutées

L’agent couvre maintenant:

- S&OP mensuel: Demand Review, Supply Review, Pre-S&OP, Executive S&OP
- S&OE hebdomadaire: OF à lancer, exceptions, replanification court terme
- ATP: Available To Promise côté composants, stock, qualité et réceptions confirmées
- CTP: Capable To Promise côté capacité atelier, compétences, postes et qualité
- stocks de sécurité, point de commande, couverture de stock
- segmentation ABC/XYZ des composants
- fournisseur critique: délai, fiabilité, qualité, MOQ, alternatives, risque
- scénarios what-if: retard fournisseur, réception partielle, capacité réduite, VIP urgent, rejet qualité
- exception management: ne remonter que les décisions nécessaires
- allocation de composants rares
- traçabilité qualité par lot, certificat et libération qualité

## Templates Supply Chain / S&OP

- templates/sop_monthly_review.csv
- templates/supplier_risk_register.csv
- templates/inventory_policy_abc_xyz.csv
- templates/atp_ctp_template.csv
- templates/what_if_scenarios.csv
- templates/exception_management.csv
- templates/allocation_components.csv
- templates/quality_traceability.csv
- templates/demand_supply_balance.csv
- templates/sop_decision_log.csv

## Rapports générés par le script

- outputs/atp_ctp_report.csv
- outputs/sop_kpi_dashboard.csv
- outputs/inventory_policy_report.csv
- outputs/supplier_risk_report.csv
- outputs/exception_report.csv
- outputs/allocation_report.csv
- outputs/what_if_report.csv
