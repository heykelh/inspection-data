"""
INSPECTION DATA - Orchestrateur P0.
Genere NOVEO, execute les controles, evalue, et ecrit le rapport (web/findings.js).
"""
import json
import os

import generate_noveo
import controls
import evaluate

RECOS = {
    "QUAL-001": "Rendre le montant et la notation obligatoires a la saisie et rejeter les enregistrements incomplets a l'integration.",
    "QUAL-002": "Ajouter des controles de bornes en amont du chargement : montant strictement positif, taux dans une plage definie.",
    "QUAL-003": "Introduire une regle bloquante de coherence entre date de naissance et date d'octroi lors de la creation du pret.",
    "QUAL-004": "Deployer une deduplication sur cle metier (nom, naissance, email) et un controle d'unicite a l'entree du referentiel client.",
    "QUAL-005": "Definir un seuil de fraicheur par donnee et declencher une alerte automatique au-dela de la duree attendue.",
}

CADRAGE = (
    "Mission d'inspection portant sur la chaine de donnees du risque de credit de NOVEO Banque. "
    "L'inspection evalue la qualite des donnees clients et prets au regard des exigences BCBS 239, "
    "du referentiel DAMA-DMBOK et des principes de protection des donnees. Les controles sont "
    "automatises et reproductibles ; chaque constat est chiffre et note par niveau de criticite."
)


def main():
    clients_df, prets_df, gt_df = generate_noveo.build()
    pop = {"prets": len(prets_df), "clients": len(clients_df)}

    results = controls.run_all(clients_df, prets_df)
    ev = evaluate.evaluate(results, gt_df)

    controles, synthese = [], {"Critique": 0, "Élevé": 0, "Modéré": 0, "conformes": 0}
    for c in results:
        exceptions = len(c["ids"])
        population = pop[c["entite"]]
        taux = round(exceptions / population * 100, 2) if population else 0.0
        conforme = exceptions == 0
        criticite = "Conforme" if conforme else c["severite"]
        if conforme:
            synthese["conformes"] += 1
        else:
            synthese[c["severite"]] = synthese.get(c["severite"], 0) + 1

        controles.append({
            "id": c["id"], "pilier": c["pilier"], "entite": c["entite"],
            "libelle": c["libelle"], "description": c["description"], "regle": c["sql"],
            "severite": c["severite"], "statut": "CONFORME" if conforme else "NON CONFORME",
            "criticite": criticite, "exceptions": exceptions, "population": population, "taux": taux,
            "constat": (f"{exceptions} enregistrement(s) sur {population} ({taux} %) en anomalie."
                        if not conforme else "Aucune anomalie detectee sur ce controle."),
            "recommandation": RECOS[c["id"]] if not conforme else "",
            "exemples": c["ids"][:5],
            "fiabilite": ev["par_controle"][c["id"]],
        })

    findings = {
        "mission": {
            "titre": "Mission d'inspection Data",
            "entite": "NOVEO Banque",
            "perimetre": "Chaine de donnees du risque de credit",
            "date_mission": controls.REF,
            "referentiels": ["BCBS 239", "DAMA-DMBOK", "RGPD"],
            "cadrage": CADRAGE,
        },
        "dataset": pop,
        "controles": controles,
        "eval": ev["global"],
        "synthese": synthese,
    }

    os.makedirs("web", exist_ok=True)
    with open("web/findings.js", "w", encoding="utf-8") as f:
        f.write("window.INSPECTION_DATA = " + json.dumps(findings, ensure_ascii=False, indent=2) + ";")

    # registre exporte (livrable)
    import csv
    with open("data/registre.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "pilier", "libelle", "severite", "statut", "exceptions", "population", "taux", "criticite", "recommandation"])
        for c in controles:
            w.writerow([c["id"], c["pilier"], c["libelle"], c["severite"], c["statut"],
                        c["exceptions"], c["population"], c["taux"], c["criticite"], c["recommandation"]])

    nc = sum(1 for c in controles if c["statut"] == "NON CONFORME")
    print(f"Controles : {len(controles)} | non conformes : {nc} | F1 global : {ev['global']['f1']}")
    print("Rapport ecrit dans web/findings.js. Ouvre web/index.html.")


if __name__ == "__main__":
    main()
