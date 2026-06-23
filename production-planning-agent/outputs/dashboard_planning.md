# Dashboard planning horloger + Supply Chain/S&OP

Scenario: Données d'exemple — planification manufacture horlogère de luxe
Horizon: Semaine 2026-W27

## Synthèse
- OF total: 4
- OF GO: 1
- OF GO partiel: 1
- OF bloqués composant: 1
- OF bloqués qualité: 1
- Promesses à risque ATP/CTP: 3
- Charge/capacité globale: 76.3%

## KPI Supply Chain
| KPI | Valeur | Unité | Interprétation |
|---|---:|---|---|
| Taux OF GO | 25.0 | % | part des OF lançables complets |
| Taux OF bloqués | 50.0 | % | composants/qualité bloquants |
| Charge/capacité | 76.3 | % | pression capacité atelier |
| Promesses à risque | 3 | OF | ATP/CTP non promettables ou risqués |
| Fiabilité fournisseur moyenne | 83.3 | % | moyenne registre fournisseurs |

## Statut ATP/CTP par OF
| OF | Référence | ATP | CTP | Promesse | Statut | Décision |
|---|---|---|---|---|---|---|
| OF-2607-001 | MH-CLASSIQUE-38-ARGENT | OUI | OUI | PROMETTABLE | GO | GO assemblage final possible selon capacité atelier |
| OF-2607-002 | MH-SQUELETTE-40-OR | NON | OUI | NON_PROMETTABLE | NO_GO_COMPOSANT | NO-GO assemblage final |
| OF-2607-003 | MH-SPORT-41-NOIR | PARTIEL | OUI | PROMESSE_RISQUEE | GO_PARTIEL | GO préparation/étapes amont uniquement; finalisation après réception confirmée et libération qualité |
| OF-2607-004 | MH-HERITAGE-36-ACIER | NON | OUI | NON_PROMETTABLE | NO_GO_QUALITE | NO-GO avant libération qualité |

## Exceptions composants / qualité
| OF | Référence | Composant | Statut | Qté manquante | Réception | Raison |
|---|---|---|---|---:|---|---|
| OF-2607-002 | MH-SQUELETTE-40-OR | spiral | NO_GO_COMPOSANT | 2 | 2026-07-09 | composant obligatoire manquant |
| OF-2607-003 | MH-SPORT-41-NOIR | bracelet | GO_PARTIEL | 5 | 2026-07-11 | réception attendue: finalisation à confirmer après réception/libération qualité |
| OF-2607-004 | MH-HERITAGE-36-ACIER | cadran | NO_GO_QUALITE | 10 | 2026-07-07 | stock disponible physiquement mais bloqué qualité |

## What-if / scénarios
| Scénario | OF à risque | Impact | Action recommandée |
|---|---|---|---|
| retard spiral +10 jours | OF-2607-002;OF-2607-003;OF-2607-004 | OF avec réception attendue ou composant manquant glissent; promesses à revalider | avancer OF complets, relancer fournisseur, alerter commercial |
| réception bracelet 50% | OF-2607-002;OF-2607-003;OF-2607-004 | allocation nécessaire; finalisation partielle possible | prioriser VIP/date promise, repousser OF faible priorité |
| capacité atelier -20% | OF-2607-002;OF-2607-003;OF-2607-004 | CTP dégradé; charge atelier à réduire | réduire lancements, sous-traiter si validé, lisser charge |
| commande VIP urgente | OF-2607-002;OF-2607-003;OF-2607-004 | réallocation composants rares possible | arbitrage direction S&OP et communication clients impactés |
| lot cadrans rejeté qualité | OF-2607-002;OF-2607-003;OF-2607-004 | NO-GO qualité; WIP bloqué | prioriser contrôle entrée, ouvrir plan correction fournisseur |
