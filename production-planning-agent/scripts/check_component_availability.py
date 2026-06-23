#!/usr/bin/env python3
"""Contrôle composants + bonnes pratiques Supply Chain/S&OP pour OF horlogers.

Entrée par défaut: examples/donnees_exemple_planification_horlogere.json
Sorties par défaut dans outputs/:
- component_availability_report.json
- component_availability_by_of.csv
- missing_components_report.csv
- of_status_report.csv
- dashboard_planning.md
- sop_kpi_dashboard.csv
- atp_ctp_report.csv
- inventory_policy_report.csv
- supplier_risk_report.csv
- exception_report.csv
- what_if_report.csv
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = BASE_DIR / "examples" / "donnees_exemple_planification_horlogere.json"
DEFAULT_OUTPUT_DIR = BASE_DIR / "outputs"

STATUS_OK = "GO"
STATUS_PARTIAL = "GO_PARTIEL"
STATUS_MISSING = "NO_GO_COMPOSANT"
STATUS_QUALITY = "NO_GO_QUALITE"
STATUS_INSUFFICIENT = "DONNEES_INSUFFISANTES"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        keys: list[str] = []
        for row in rows:
            for key in row:
                if key not in keys:
                    keys.append(key)
        fieldnames = keys
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def component_status(stock: dict[str, Any]) -> tuple[str, int, str]:
    besoin = int(stock.get("besoin_total") or 0)
    dispo = int(stock.get("stock_dispo") or 0)
    bloque_qualite = int(stock.get("stock_qualite_bloque") or 0)
    statut_source = str(stock.get("statut") or "").upper()
    manque = max(besoin - dispo, 0)

    if bloque_qualite >= besoin and besoin > 0:
        return STATUS_QUALITY, besoin, "stock disponible physiquement mais bloqué qualité"
    if "BLOQUE_QUALITE" in statut_source:
        return STATUS_QUALITY, manque or besoin, "composant bloqué qualité"
    if manque > 0:
        if "RECEPTION_ATTENDUE" in statut_source:
            return STATUS_PARTIAL, manque, "réception attendue: finalisation à confirmer après réception/libération qualité"
        return STATUS_MISSING, manque, "composant obligatoire manquant"
    return STATUS_OK, 0, "disponible et libéré selon données fournies"


def next_action(status: str) -> str:
    if status == STATUS_OK:
        return "Réserver les composants et planifier selon capacité atelier."
    if status == STATUS_PARTIAL:
        return "Confirmer réception, réserver les composants présents, ne pas finaliser avant libération."
    if status == STATUS_MISSING:
        return "Relancer fournisseur/approvisionnement, confirmer date, arbitrer réservation composants rares."
    if status == STATUS_QUALITY:
        return "Accélérer contrôle entrée / décision qualité, prévoir scénario de replanification."
    return "Compléter BOM et données de stock."


def priority_score(priority: str) -> int:
    p = (priority or "").lower()
    if "crit" in p:
        return 100
    if "haut" in p:
        return 75
    if "moy" in p:
        return 50
    return 25


def build_report(data: dict[str, Any]) -> dict[str, Any]:
    ofs = data.get("of", [])
    stocks = data.get("stocks_composants", [])
    receptions = data.get("receptions_attendues", [])
    capacities = data.get("capacite_atelier", [])
    inventory_policy = data.get("inventory_policy", [])
    supplier_risks = data.get("supplier_risks", [])

    receptions_by_ref_comp: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for rec in receptions:
        receptions_by_ref_comp[(rec.get("reference", ""), rec.get("composant", ""))].append(rec)

    stocks_by_ref: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for stock in stocks:
        stocks_by_ref[stock.get("reference", "")].append(stock)

    policy_by_component = {p.get("composant", ""): p for p in inventory_policy}
    supplier_by_component: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for s in supplier_risks:
        supplier_by_component[s.get("composant", "")].append(s)

    of_rows: list[dict[str, Any]] = []
    missing_rows: list[dict[str, Any]] = []
    summary_by_of: list[dict[str, Any]] = []
    atp_ctp_rows: list[dict[str, Any]] = []
    exception_rows: list[dict[str, Any]] = []
    allocation_candidates: list[dict[str, Any]] = []

    total_capacity_h = sum(float(c.get("capacite_h_semaine") or 0) for c in capacities)
    total_required_h_est = 0.0

    for of in ofs:
        of_id = of.get("of", "")
        ref = of.get("reference", "")
        qty = int(of.get("quantite") or 0)
        component_rows = stocks_by_ref.get(ref, [])
        statuses: list[str] = []
        blockers: list[str] = []
        required_h_est = qty * 6.9  # exemple: somme temps standard grossière sur postes fournis
        total_required_h_est += required_h_est

        for stock in component_rows:
            comp = stock.get("composant", "")
            status, missing_qty, reason = component_status(stock)
            statuses.append(status)
            recs = receptions_by_ref_comp.get((ref, comp), [])
            rec = recs[0] if recs else {}
            policy = policy_by_component.get(comp, {})
            suppliers = supplier_by_component.get(comp, [])
            supplier = suppliers[0] if suppliers else {}
            stock_dispo = int(stock.get("stock_dispo") or 0)
            monthly = float(policy.get("conso_mensuelle_moy") or 0)
            coverage_days = round((stock_dispo / monthly * 30), 1) if monthly else ""
            safety = int(policy.get("stock_securite") or 0)
            reorder_point = int(policy.get("point_commande") or 0)

            row = {
                "of": of_id,
                "reference": ref,
                "calibre": of.get("calibre", ""),
                "quantite_of": qty,
                "date_promise": of.get("date_promise", ""),
                "priorite": of.get("priorite", ""),
                "client_canal": of.get("client_canal", ""),
                "composant": comp,
                "abc": policy.get("abc", ""),
                "xyz": policy.get("xyz", ""),
                "criticite": policy.get("criticite", ""),
                "besoin_total": stock.get("besoin_total", ""),
                "stock_dispo": stock.get("stock_dispo", ""),
                "stock_reserve": stock.get("stock_reserve", ""),
                "stock_qualite_bloque": stock.get("stock_qualite_bloque", ""),
                "stock_securite": safety,
                "point_commande": reorder_point,
                "couverture_jours": coverage_days,
                "reception_attendue": rec.get("quantite", ""),
                "date_reception": rec.get("date_reception", ""),
                "date_confirmee": rec.get("date_confirmee", ""),
                "fiabilite": rec.get("fiabilite", ""),
                "fournisseur": supplier.get("fournisseur", rec.get("fournisseur", "")),
                "risque_fournisseur": supplier.get("risque", ""),
                "quantite_manquante": missing_qty,
                "statut": status,
                "raison": reason,
            }
            of_rows.append(row)
            if status in {STATUS_MISSING, STATUS_QUALITY, STATUS_PARTIAL}:
                missing_rows.append(row)
                blockers.append(f"{comp}: {status} ({reason})")
                exception_rows.append({
                    "exception": status,
                    "of": of_id,
                    "reference": ref,
                    "composant": comp,
                    "priorite": of.get("priorite", ""),
                    "impact": "date promise à risque" if priority_score(of.get("priorite", "")) >= 75 else "replanification atelier",
                    "action": next_action(status),
                    "owner": "Approvisionnement" if status != STATUS_QUALITY else "Qualité",
                })
            if policy.get("abc") == "A" and policy.get("xyz") in {"Y", "Z"}:
                allocation_candidates.append({
                    "composant": comp,
                    "of": of_id,
                    "reference": ref,
                    "priorite": of.get("priorite", ""),
                    "client_canal": of.get("client_canal", ""),
                    "score_priorite": priority_score(of.get("priorite", "")),
                    "stock_dispo": stock_dispo,
                    "besoin_total": stock.get("besoin_total", ""),
                    "recommandation": "réserver si OF prioritaire; arbitrage S&OP si stock insuffisant",
                })

        if not component_rows:
            final_status = STATUS_INSUFFICIENT
            decision = "NO-GO tant que la BOM/stock par référence n'est pas fournie"
        elif STATUS_MISSING in statuses:
            final_status = STATUS_MISSING
            decision = "NO-GO assemblage final"
        elif STATUS_QUALITY in statuses:
            final_status = STATUS_QUALITY
            decision = "NO-GO avant libération qualité"
        elif STATUS_PARTIAL in statuses:
            final_status = STATUS_PARTIAL
            decision = "GO préparation/étapes amont uniquement; finalisation après réception confirmée et libération qualité"
        else:
            final_status = STATUS_OK
            decision = "GO assemblage final possible selon capacité atelier"

        atp = "OUI" if final_status == STATUS_OK else ("PARTIEL" if final_status == STATUS_PARTIAL else "NON")
        ctp = "OUI" if required_h_est <= max(total_capacity_h, 1) else "NON"
        promise = "PROMETTABLE" if atp == "OUI" and ctp == "OUI" else ("PROMESSE_RISQUEE" if atp == "PARTIEL" and ctp == "OUI" else "NON_PROMETTABLE")
        atp_ctp_rows.append({
            "of": of_id,
            "reference": ref,
            "date_promise": of.get("date_promise", ""),
            "atp_composants": atp,
            "atp_raison": "; ".join(blockers) if blockers else "composants disponibles selon données fournies",
            "ctp_capacite": ctp,
            "ctp_raison": f"charge estimée {required_h_est:.1f}h vs capacité globale {total_capacity_h:.1f}h",
            "statut_promesse": promise,
            "date_promesse_realiste": of.get("date_promise", "") if promise == "PROMETTABLE" else "à revalider après résolution exceptions",
            "risque": "faible" if promise == "PROMETTABLE" else ("moyen" if promise == "PROMESSE_RISQUEE" else "élevé"),
        })
        summary_by_of.append({
            "of": of_id,
            "reference": ref,
            "calibre": of.get("calibre", ""),
            "quantite": qty,
            "date_promise": of.get("date_promise", ""),
            "priorite": of.get("priorite", ""),
            "client_canal": of.get("client_canal", ""),
            "statut_final": final_status,
            "atp": atp,
            "ctp": ctp,
            "statut_promesse": promise,
            "decision": decision,
            "bloquants": "; ".join(blockers),
            "prochaine_action": next_action(final_status),
        })

    summary = {
        "of_total": len(summary_by_of),
        "of_go": sum(1 for x in summary_by_of if x["statut_final"] == STATUS_OK),
        "of_go_partiel": sum(1 for x in summary_by_of if x["statut_final"] == STATUS_PARTIAL),
        "of_bloque_composant": sum(1 for x in summary_by_of if x["statut_final"] == STATUS_MISSING),
        "of_bloque_qualite": sum(1 for x in summary_by_of if x["statut_final"] == STATUS_QUALITY),
        "lignes_composants_a_traiter": len(missing_rows),
        "charge_estimee_h": round(total_required_h_est, 1),
        "capacite_globale_h": round(total_capacity_h, 1),
        "charge_capacite_pct": round((total_required_h_est / total_capacity_h * 100), 1) if total_capacity_h else 0,
        "otif_risque_count": sum(1 for x in atp_ctp_rows if x["statut_promesse"] != "PROMETTABLE"),
    }
    kpis = build_kpis(summary, supplier_risks)
    inventory_rows = build_inventory_report(of_rows, inventory_policy)
    supplier_rows = build_supplier_report(supplier_risks, missing_rows)
    what_if_rows = build_what_if(data, summary_by_of)
    allocation_rows = sorted(allocation_candidates, key=lambda x: (-x["score_priorite"], x["composant"]))

    return {
        "scenario": data.get("scenario", ""),
        "horizon": data.get("horizon", ""),
        "regle_metier": data.get("regle_metier", ""),
        "summary": summary,
        "kpis": kpis,
        "of_status": summary_by_of,
        "component_rows": of_rows,
        "missing_components": missing_rows,
        "atp_ctp": atp_ctp_rows,
        "inventory_policy_report": inventory_rows,
        "supplier_risk_report": supplier_rows,
        "exception_report": exception_rows,
        "allocation_report": allocation_rows,
        "what_if_report": what_if_rows,
    }


def build_kpis(summary: dict[str, Any], supplier_risks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    total = summary["of_total"] or 1
    go_rate = round(summary["of_go"] / total * 100, 1)
    blocked_rate = round((summary["of_bloque_composant"] + summary["of_bloque_qualite"]) / total * 100, 1)
    avg_supplier_reliability = round(sum(float(s.get("fiabilite_livraison_pct") or 0) for s in supplier_risks) / len(supplier_risks), 1) if supplier_risks else ""
    return [
        {"kpi": "Taux OF GO", "valeur": go_rate, "unite": "%", "interpretation": "part des OF lançables complets"},
        {"kpi": "Taux OF bloqués", "valeur": blocked_rate, "unite": "%", "interpretation": "composants/qualité bloquants"},
        {"kpi": "Charge/capacité", "valeur": summary["charge_capacite_pct"], "unite": "%", "interpretation": "pression capacité atelier"},
        {"kpi": "Promesses à risque", "valeur": summary["otif_risque_count"], "unite": "OF", "interpretation": "ATP/CTP non promettables ou risqués"},
        {"kpi": "Fiabilité fournisseur moyenne", "valeur": avg_supplier_reliability, "unite": "%", "interpretation": "moyenne registre fournisseurs"},
    ]


def build_inventory_report(component_rows: list[dict[str, Any]], policies: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: dict[str, dict[str, Any]] = {}
    for row in component_rows:
        comp = row["composant"]
        if comp not in seen:
            seen[comp] = {
                "composant": comp,
                "abc": row.get("abc", ""),
                "xyz": row.get("xyz", ""),
                "stock_dispo": row.get("stock_dispo", ""),
                "stock_securite": row.get("stock_securite", ""),
                "point_commande": row.get("point_commande", ""),
                "couverture_jours": row.get("couverture_jours", ""),
                "statut_politique": "SOUS_POINT_COMMANDE" if str(row.get("point_commande", "0")).isdigit() and int(row.get("stock_dispo") or 0) < int(row.get("point_commande") or 0) else "OK/NA",
            }
    for p in policies:
        comp = p.get("composant", "")
        if comp and comp not in seen:
            seen[comp] = {"composant": comp, **p, "statut_politique": "POLITIQUE_SANS_STOCK_EXEMPLE"}
    return list(seen.values())


def build_supplier_report(supplier_risks: list[dict[str, Any]], missing_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    impacted = defaultdict(list)
    for row in missing_rows:
        impacted[row.get("composant", "")].append(row.get("of", ""))
    rows=[]
    for s in supplier_risks:
        comp=s.get("composant", "")
        rows.append({**s, "of_impactes": ";".join(sorted(set(impacted.get(comp, [])))), "action_recommandee": "revue fournisseur prioritaire" if s.get("risque") == "élevé" or impacted.get(comp) else "surveillance standard"})
    return rows


def build_what_if(data: dict[str, Any], of_status: list[dict[str, Any]]) -> list[dict[str, Any]]:
    scenarios = data.get("sop", {}).get("what_if", [])
    if not scenarios:
        scenarios = ["retard fournisseur", "capacité réduite", "commande VIP urgente"]
    risky = [x["of"] for x in of_status if x["statut_promesse"] != "PROMETTABLE"]
    rows=[]
    for sc in scenarios:
        s=sc.lower()
        if "retard" in s:
            impact="OF avec réception attendue ou composant manquant glissent; promesses à revalider"
            action="avancer OF complets, relancer fournisseur, alerter commercial"
        elif "50%" in s or "partielle" in s:
            impact="allocation nécessaire; finalisation partielle possible"
            action="prioriser VIP/date promise, repousser OF faible priorité"
        elif "capacité" in s:
            impact="CTP dégradé; charge atelier à réduire"
            action="réduire lancements, sous-traiter si validé, lisser charge"
        elif "vip" in s:
            impact="réallocation composants rares possible"
            action="arbitrage direction S&OP et communication clients impactés"
        elif "qualité" in s or "rejet" in s:
            impact="NO-GO qualité; WIP bloqué"
            action="prioriser contrôle entrée, ouvrir plan correction fournisseur"
        else:
            impact="impact à analyser"
            action="préparer scénario nominal/pessimiste/optimisé"
        rows.append({"scenario": sc, "of_a_risque": ";".join(risky), "impact": impact, "action_recommandee": action})
    return rows


def write_dashboard(path: Path, report: dict[str, Any]) -> None:
    s = report["summary"]
    lines = [
        "# Dashboard planning horloger + Supply Chain/S&OP",
        "",
        f"Scenario: {report.get('scenario', '')}",
        f"Horizon: {report.get('horizon', '')}",
        "",
        "## Synthèse",
        f"- OF total: {s['of_total']}",
        f"- OF GO: {s['of_go']}",
        f"- OF GO partiel: {s['of_go_partiel']}",
        f"- OF bloqués composant: {s['of_bloque_composant']}",
        f"- OF bloqués qualité: {s['of_bloque_qualite']}",
        f"- Promesses à risque ATP/CTP: {s['otif_risque_count']}",
        f"- Charge/capacité globale: {s['charge_capacite_pct']}%",
        "",
        "## KPI Supply Chain",
        "| KPI | Valeur | Unité | Interprétation |",
        "|---|---:|---|---|",
    ]
    for k in report["kpis"]:
        lines.append(f"| {k['kpi']} | {k['valeur']} | {k['unite']} | {k['interpretation']} |")
    lines.extend(["", "## Statut ATP/CTP par OF", "| OF | Référence | ATP | CTP | Promesse | Statut | Décision |", "|---|---|---|---|---|---|---|"])
    for row in report["of_status"]:
        lines.append(f"| {row['of']} | {row['reference']} | {row['atp']} | {row['ctp']} | {row['statut_promesse']} | {row['statut_final']} | {row['decision']} |")
    lines.extend(["", "## Exceptions composants / qualité", "| OF | Référence | Composant | Statut | Qté manquante | Réception | Raison |", "|---|---|---|---|---:|---|---|"])
    for row in report["missing_components"]:
        lines.append(f"| {row['of']} | {row['reference']} | {row['composant']} | {row['statut']} | {row['quantite_manquante']} | {row['date_reception']} | {row['raison']} |")
    lines.extend(["", "## What-if / scénarios", "| Scénario | OF à risque | Impact | Action recommandée |", "|---|---|---|---|"])
    for row in report["what_if_report"]:
        lines.append(f"| {row['scenario']} | {row['of_a_risque']} | {row['impact']} | {row['action_recommandee']} |")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Contrôle composants + ATP/CTP + KPI S&OP pour planification horlogère")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="JSON de données planning")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Dossier de sortie")
    args = parser.parse_args()

    data = load_json(args.input)
    report = build_report(data)
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)

    (out / "component_availability_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_csv(out / "component_availability_by_of.csv", report["component_rows"])
    write_csv(out / "missing_components_report.csv", report["missing_components"])
    write_csv(out / "of_status_report.csv", report["of_status"])
    write_csv(out / "atp_ctp_report.csv", report["atp_ctp"])
    write_csv(out / "sop_kpi_dashboard.csv", report["kpis"])
    write_csv(out / "inventory_policy_report.csv", report["inventory_policy_report"])
    write_csv(out / "supplier_risk_report.csv", report["supplier_risk_report"])
    write_csv(out / "exception_report.csv", report["exception_report"])
    write_csv(out / "allocation_report.csv", report["allocation_report"])
    write_csv(out / "what_if_report.csv", report["what_if_report"])
    write_dashboard(out / "dashboard_planning.md", report)

    print(json.dumps(report["summary"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
