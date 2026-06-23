# Agent Planification de Production — Manufacture horlogère de luxe

Profil Hermes principal: productionplanner

Rôle: aider à planifier l'assemblage de montres de luxe en tenant compte des nomenclatures, composants critiques, stocks, délais fournisseurs, capacités atelier, priorités commerciales et contraintes qualité.

Point clé métier: si un seul composant obligatoire manque, l'assemblage de la montre ne peut pas être finalisé. L'agent doit donc raisonner en disponibilité complète par référence / ordre de fabrication, pas seulement en charge atelier.

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

## Commandes de lancement

Agent principal:

HERMES_HOME=/opt/data hermes --profile productionplanner chat -q "Planifie les assemblages horlogers de la semaine avec ces OF, stocks composants, réceptions attendues et capacités atelier: ..."

Sous-agents:

HERMES_HOME=/opt/data hermes --profile prodstrategy chat -q "Priorise ces OF horlogers selon clients, dates promises, valeur et disponibilité composants: ..."
HERMES_HOME=/opt/data hermes --profile prodcapacity chat -q "Vérifie la capacité atelier et les goulots pour ce planning d'assemblage: ..."
HERMES_HOME=/opt/data hermes --profile prodcalendar chat -q "Ordonnance ces OF selon disponibilité composants et capacité: ..."
HERMES_HOME=/opt/data hermes --profile prodpostprod chat -q "Planifie QC, emboîtage, habillage, packaging et expédition: ..."
HERMES_HOME=/opt/data hermes --profile prodverifier chat -q "Audite ce planning: composants manquants, OF bloqués, risques qualité/délai: ..."

## Fichiers utiles

- agent_prompt.md: prompt complet de l'agent principal
- subagents/*.md: prompts spécialisés
- templates/brief_production.md: formulaire de brief manufacture horlogère
- templates/planning_board.csv: modèle de planning OF / composants
- templates/weekly_plan.csv: modèle hebdomadaire atelier
- templates/missing_components.csv: modèle de suivi des composants manquants
- workflow.md: méthode opérationnelle de planification horlogère
