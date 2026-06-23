# Conductor - Agents Minecraft

Ce dossier déclare les agents Minecraft pour que Conductor/Operations puisse les repérer comme agents prêts à lancer, et pas seulement comme dossiers de projet.

Registres créés :

- /workspace/agents.json
- /workspace/.conductor/agents.json
- /workspace/.conductor/conductor.yaml
- /workspace/operations/agents.json

Agents déclarés :

1. minecraft-bedrock-world-agent
   - Type : prompt-agent
   - Entrée : /workspace/minecraft-bedrock-world-agent/agent_prompt.md
   - Rôle : conception de mondes Bedrock compatibles Switch via Realms.

2. agent-minecraft-bedrock
   - Type : python-agent-suite
   - Entrée : /workspace/agent-minecraft-bedrock/minecraft_agent.py
   - Rôle : génération de blueprints, structures .mcfunction, skins, .mcaddon/.mcpack et .mcworld.

Si l'interface ne rafraîchit pas automatiquement, recharge Operations/Conductor ou ouvre directement /workspace/agents.json.
