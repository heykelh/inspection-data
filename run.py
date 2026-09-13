import json, os, csv, sys, math
import pandas as pd
import generate_noveo, controls, evaluate

RECOS = {
 "QUAL-001":"Rendre le montant et la notation obligatoires a la saisie et rejeter les enregistrements incomplets a l'integration.",
 "QUAL-002":"Ajouter des controles de bornes en amont du chargement : montant strictement positif, taux dans une plage definie.",
 "QUAL-003":"Introduire une regle bloquante de coherence entre date de naissance et date d'octroi lors de la creation du pret.",
 "QUAL-004":"Deployer une deduplication sur cle metier (nom, naissance, email) et un controle d'unicite a l'entree du referentiel client.",
 "QUAL-005":"Definir un seuil de fraicheur par donnee et declencher une alerte automatique au-dela de la duree attendue.",
 "GOUV-001":"Attribuer un Data Owner a chaque donnee critique et formaliser la responsabilite dans le catalogue de donnees.",
 "GOUV-002":"Documenter le systeme source de chaque donnee et retablir le lineage de bout en bout (source vers reporting).",
 "GOUV-003":"Contraindre la notation aux valeurs du referentiel officiel et rejeter toute valeur hors liste a la saisie.",
 "QUAL-006":"Contraindre le statut aux valeurs du referentiel a la saisie.",
 "QUAL-007":"Imposer une contrainte d'integrite referentielle entre prets et clients.",
 "GOUV-004":"Renseigner un niveau de sensibilite pour chaque donnee du catalogue.",
 "PROT-004":"Documenter le systeme source de chaque donnee personnelle.",
 "PROT-001":"Bloquer tout traitement sans base legale : recueillir ou regulariser le consentement avant exploitation des donnees.",
 "PROT-002":"Mettre en place une purge automatique des donnees dont la duree de conservation legale est depassee.",
 "PROT-003":"Definir et documenter une duree de retention pour chaque donnee personnelle du catalogue.",
}
POURQUOI = {
 "QUAL-001":"Un pret sans montant ou sans notation ne peut etre ni suivi ni provisionne : c'est un angle mort dans le calcul du risque de credit de la banque.",
 "QUAL-002":"Un montant negatif ou un taux aberrant fausse les agregats de risque et peut passer inapercu dans un reporting reglementaire (exigence d'exactitude BCBS 239).",
 "QUAL-003":"Un pret accorde avant la majorite du client trahit une donnee fausse ou une faille de controle a l'octroi : risque juridique et risque de fraude.",
 "QUAL-004":"Un meme client compte deux fois gonfle le portefeuille et fausse l'exposition au risque comme les obligations de connaissance client (KYC).",
 "QUAL-005":"Une donnee client trop ancienne peut ne plus refleter la realite (adresse, situation) : des decisions sont alors prises sur une base perimee.",
 "GOUV-001":"Sans Data Owner identifie, personne n'est responsable de la qualite ni des acces a la donnee : c'est une exigence de base de la gouvernance (DAMA-DMBOK).",
 "GOUV-002":"Sans systeme source documente, impossible de tracer d'ou vient un chiffre : le lineage est indispensable pour fiabiliser un reporting reglementaire.",
 "GOUV-003":"Une notation hors referentiel casse la comparabilite et l'agregation du risque : les indicateurs de risque deviennent non fiables.",
 "QUAL-006":"Un statut hors referentiel empeche tout suivi et fausse les etats de gestion : la nomenclature doit etre maitrisee.",
 "QUAL-007":"Un pret rattache a un client inexistant est une donnee orpheline : elle echappe au suivi et fausse l'exposition par client.",
 "GOUV-004":"Sans niveau de sensibilite, impossible d'appliquer les bonnes regles de protection et d'acces : la classification est le socle de la securite des donnees.",
 "PROT-004":"Une donnee personnelle sans systeme source identifie ne peut etre ni tracee ni securisee correctement : exigence de tracabilite du RGPD.",
 "PROT-001":"Traiter des donnees personnelles sans base legale est une violation directe du RGPD, exposant la banque a un risque de sanction.",
 "PROT-002":"Conserver des donnees au-dela de la duree legale viole le principe de limitation de conservation du RGPD.",
 "PROT-003":"Une donnee personnelle sans duree de retention definie ne peut etre purgee dans les temps : non-conformite au RGPD par defaut.",
}
CADRAGE = ("Mission d'inspection portant sur la chaine de donnees du risque de credit de NOVEO Banque. "
 "L'inspection evalue la qualite, la gouvernance et la protection des donnees clients et prets au regard "
 "des exigences BCBS 239, du referentiel DAMA-DMBOK et du RGPD. Les controles sont automatises et "
 "reproductibles ; chaque constat est chiffre et note par niveau de criticite.")

def main():
    clients_df, prets_df, cat_df, gt_df = generate_noveo.build()
    pop = {"prets":len(prets_df), "clients":len(clients_df), "catalogue":len(cat_df)}
    results = controls.run_all(clients_df, prets_df, cat_df)
    ev = evaluate.evaluate(results, gt_df)
    controles = []; synthese = {"Critique":0,"Élevé":0,"Modéré":0,"conformes":0}
    for c in results:
        exc = len(c["ids"]); population = pop[c["entite"]]
        taux = round(exc/population*100,2) if population else 0.0
        conforme = exc == 0; criticite = "Conforme" if conforme else c["severite"]
        if conforme: synthese["conformes"]+=1
        else: synthese[c["severite"]] = synthese.get(c["severite"],0)+1
        controles.append({"id":c["id"],"pilier":c["pilier"],"entite":c["entite"],
            "libelle":c["libelle"],"description":c["description"],"regle":c["sql"],
            "pourquoi":POURQUOI.get(c["id"],""),
            "severite":c["severite"],"statut":"CONFORME" if conforme else "NON CONFORME",
            "criticite":criticite,"exceptions":exc,"population":population,"taux":taux,
            "constat":(f"{exc} enregistrement(s) sur {population} ({taux} %) en anomalie." if not conforme else "Aucune anomalie detectee sur ce controle."),
            "recommandation":RECOS.get(c["id"],"") if not conforme else "",
            "exemples":c["ids"][:5],"fiabilite":ev["par_controle"][c["id"]]})
    findings = {"mission":{"titre":"Mission d'inspection Data","entite":"NOVEO Banque",
        "perimetre":"Chaine de donnees du risque de credit","date_mission":controls.REF,
        "referentiels":["BCBS 239","DAMA-DMBOK","RGPD"],"cadrage":CADRAGE},
        "dataset":pop,"controles":controles,"eval":ev["global"],"synthese":synthese}
    os.makedirs("web", exist_ok=True)
    with open("web/findings.js","w",encoding="utf-8") as f:
        f.write("window.INSPECTION_DATA = "+json.dumps(findings,ensure_ascii=False,indent=2)+";")
    with open("data/registre.csv","w",newline="",encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["id","pilier","libelle","severite","statut","exceptions","population","taux","criticite","recommandation"])
        for c in controles: w.writerow([c["id"],c["pilier"],c["libelle"],c["severite"],c["statut"],c["exceptions"],c["population"],c["taux"],c["criticite"],c["recommandation"]])

    # --- export des donnees pour l'explorateur du site ---
    flags = {"prets": {}, "clients": {}, "catalogue": {}}
    for c in results:
        for _id in c["ids"]:
            flags[c["entite"]].setdefault(_id, []).append(c["id"])
    def _rows(df, entite, key):
        out = []
        for r in df.to_dict("records"):
            row = {}
            for k, v in r.items():
                if k == "adresse": continue
                if isinstance(v, pd.Timestamp): v = v.date().isoformat()
                elif isinstance(v, float) and math.isnan(v): v = None
                elif hasattr(v, "item"): v = v.item()
                row[k] = v
            row["_flags"] = flags[entite].get(r[key], [])
            out.append(row)
        return out
    rows = {"prets": _rows(prets_df,"prets","pret_id"),
            "clients": _rows(clients_df,"clients","client_id"),
            "catalogue": _rows(cat_df,"catalogue","champ"),
            "controls": [{"id":c["id"],"libelle":c["libelle"],"entite":c["entite"]} for c in results]}
    with open("web/data.js","w",encoding="utf-8") as f:
        f.write("window.INSPECTION_ROWS = "+json.dumps(rows, ensure_ascii=False)+";")

    nc = sum(1 for c in controles if c["statut"]=="NON CONFORME")
    print(f"Controles : {len(controles)} | non conformes : {nc} | F1 global : {ev['global']['f1']}")
    print("eval global:", ev["global"])

    if "--pdf" in sys.argv:
        try:
            import report_pdf
            report_pdf.build_pdf()
        except Exception as e:
            print(f"PDF non genere ({e}).")
            print("Installe Playwright : pip install playwright ; python -m playwright install chromium")

if __name__ == "__main__":
    main()
