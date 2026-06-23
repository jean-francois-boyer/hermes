# Agent Minecraft Bedrock World Builder

Agent IA francophone pour concevoir des mondes Minecraft Bedrock compatibles avec Nintendo Switch via Minecraft Realms.

## Objectif

Cet agent ne contrôle pas directement la Switch. Il crée le contenu nécessaire pour construire un monde Bedrock : concept, zones, bâtiments, PNJ, quêtes, économie, commandes Bedrock, fonctions .mcfunction, add-ons optionnels et checklist Realms/Switch.

## Utilisation rapide

1. Ouvre agent_prompt.md.
2. Copie son contenu dans ton outil IA : Hermes, ChatGPT, Claude, etc.
3. Donne une demande comme :

Crée un monde Minecraft Bedrock compatible Switch via Realms. Style médiéval fantasy. Je veux une zone de spawn, un village, 5 PNJ, 5 quêtes, 2 donjons, une économie avec émeraudes, et des commandes simples Bedrock.

4. L'agent répond avec le format défini dans output_format.md.
5. Tu construis/testes le monde dans Minecraft Bedrock sur PC/mobile.
6. Tu l'envoies sur Minecraft Realms.
7. Tu rejoins le Realm depuis ta Switch avec le même compte Microsoft/Xbox.

## Fichiers

- agent_prompt.md : prompt système de l'agent.
- world_brief_template.md : formulaire pour décrire le monde voulu.
- output_format.md : format de sortie obligatoire.
- examples/village_medieval.md : exemple de demande.
- generated/first_world_blueprint.md : premier monde généré.
- bedrock-addon-template/ : base de pack Bedrock.

## Important Switch

Sur Nintendo Switch, le chemin recommandé est Minecraft Realms. Les serveurs Bedrock personnalisés par IP sont compliqués sur Switch. Pour un projet stable : PC/mobile pour créer le monde, Realms pour y accéder depuis Switch.
