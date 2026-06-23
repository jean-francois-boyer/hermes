# Agents Minecraft Bedrock visibles

J’ai retrouvé les 5 agents Minecraft créés dans le workspace et je les ai déclarés comme profils Hermes séparés.

## Les 5 agents

1. Agent Monde Minecraft Bedrock
- Profil: minecraft-world-generator-agent
- Script: /workspace/agent-minecraft-bedrock/minecraft_agent.py
- Commande: HERMES_HOME=/opt/data hermes --profile minecraft-world-generator-agent

2. Agent Export .mcaddon / .mcpack
- Profil: minecraft-mcaddon-export-agent
- Script: /workspace/agent-minecraft-bedrock/mcaddon_export_agent.py
- Commande: HERMES_HOME=/opt/data hermes --profile minecraft-mcaddon-export-agent

3. Agent Export Monde .mcworld
- Profil: minecraft-mcworld-export-agent
- Script: /workspace/agent-minecraft-bedrock/mcworld_export_agent.py
- Commande: HERMES_HOME=/opt/data hermes --profile minecraft-mcworld-export-agent

4. Agent Skins Minecraft
- Profil: minecraft-skin-agent
- Script: /workspace/agent-minecraft-bedrock/skin_agent.py
- Commande: HERMES_HOME=/opt/data hermes --profile minecraft-skin-agent

5. Agent Structures Minecraft
- Profil: minecraft-structure-agent
- Script: /workspace/agent-minecraft-bedrock/structure_agent.py
- Commande: HERMES_HOME=/opt/data hermes --profile minecraft-structure-agent

## Registres que l’interface peut lire

- /workspace/00_agents_visuels.json
- /workspace/operations/agents.json
- /workspace/.conductor/agents.json

Chemins réels côté outils:

- /opt/data/workspace/00_agents_visuels.json
- /opt/data/workspace/operations/agents.json
- /opt/data/workspace/.conductor/agents.json

## Profils Hermes créés

- /opt/data/profiles/minecraft-world-generator-agent/config.yaml
- /opt/data/profiles/minecraft-mcaddon-export-agent/config.yaml
- /opt/data/profiles/minecraft-mcworld-export-agent/config.yaml
- /opt/data/profiles/minecraft-skin-agent/config.yaml
- /opt/data/profiles/minecraft-structure-agent/config.yaml

Anciens profils conservés:

- minecraft-bedrock-world-agent
- agent-minecraft-bedrock

---

# Agent Planification Production Horlogère

Profil Hermes principal: productionplanner

Usage: planification d'assemblage pour manufacture horlogère de luxe.
Règle clé: si un composant obligatoire manque, l'assemblage final de la montre est bloqué.

Chemins:
- Workspace UI: /workspace/production-planning-agent
- Chemin réel: /opt/data/workspace/production-planning-agent
- Carte opérations: /workspace/operations/agents/production-planner-agent/README.md

Commande:
HERMES_HOME=/opt/data hermes --profile productionplanner chat -q "Planifie mes OF horlogers selon BOM, stocks composants et capacité atelier"

Sous-agents:
- prodstrategy: priorisation OF / clients / valeur / dates promises
- prodcapacity: capacité atelier horloger / postes / goulots
- prodcalendar: ordonnancement et replanification
- prodpostprod: QC final / habillage / packaging / expédition
- prodverifier: audit BOM / composants manquants / faisabilité
- prodprocurement: approvisionnement / fournisseurs / relances / composants rares
- prodsop: S&OP/S&OE / ATP-CTP / KPI / scénarios / arbitrages direction

Registres mis à jour:
- /workspace/00_agents_visuels.json
- /workspace/operations/agents.json
- /workspace/.conductor/agents.json


Améliorations opérationnelles ajoutées:
- Script contrôle composants: /workspace/production-planning-agent/scripts/check_component_availability.py
- Matrice BOM x OF x stock: /workspace/production-planning-agent/templates/bom_requirements_by_of.csv
- Rapports générés: /workspace/production-planning-agent/outputs/

Templates Supply Chain/S&OP ajoutés dans /workspace/production-planning-agent/templates/: sop_monthly_review, supplier_risk_register, inventory_policy_abc_xyz, atp_ctp_template, what_if_scenarios, exception_management, allocation_components, quality_traceability, demand_supply_balance, sop_decision_log.
