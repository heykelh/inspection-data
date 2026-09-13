import duckdb
REF = "2026-09-01"
RETENTION_CLIENT_JOURS = 3650  # politique : donnees client conservees 10 ans max

CONTROLS = [
    # ---------- QUALITE ----------
    {"id":"QUAL-001","pilier":"Qualité","entite":"prets","severite":"Élevé",
     "libelle":"Complétude des champs critiques",
     "description":"Chaque prêt doit renseigner un montant et une notation de risque.",
     "sql":"SELECT pret_id FROM prets WHERE montant IS NULL OR isnan(montant) OR notation_risque IS NULL"},
    {"id":"QUAL-002","pilier":"Qualité","entite":"prets","severite":"Critique",
     "libelle":"Validité des bornes",
     "description":"Le montant doit être strictement positif et le taux compris entre 0 et 25 %.",
     "sql":"SELECT pret_id FROM prets WHERE (montant IS NOT NULL AND NOT isnan(montant) AND montant <= 0) OR (taux < 0 OR taux > 25)"},
    {"id":"QUAL-003","pilier":"Qualité","entite":"prets","severite":"Modéré",
     "libelle":"Cohérence temporelle",
     "description":"La date d'octroi doit être postérieure à la majorité du client.",
     "sql":"SELECT p.pret_id FROM prets p JOIN clients c ON p.client_id=c.client_id WHERE p.date_octroi < c.date_naissance + INTERVAL 18 YEAR"},
    {"id":"QUAL-004","pilier":"Qualité","entite":"clients","severite":"Élevé",
     "libelle":"Unicité des clients",
     "description":"Aucun client ne doit exister en double sur une clé métier (nom, naissance, email).",
     "sql":"SELECT client_id FROM (SELECT client_id, ROW_NUMBER() OVER (PARTITION BY nom,prenom,date_naissance,email ORDER BY client_id) AS rn FROM clients) WHERE rn > 1"},
    {"id":"QUAL-005","pilier":"Qualité","entite":"clients","severite":"Modéré",
     "libelle":"Fraîcheur des données",
     "description":"Les données client doivent avoir été mises à jour depuis moins d'un an.",
     "sql":f"SELECT client_id FROM clients WHERE date_maj < DATE '{REF}' - INTERVAL 365 DAY"},
    {"id":"QUAL-006","pilier":"Qualité","entite":"prets","severite":"Modéré",
     "libelle":"Validité du statut",
     "description":"Le statut du prêt doit appartenir au référentiel (EN_COURS, SOLDE, DEFAUT).",
     "sql":"SELECT pret_id FROM prets WHERE statut NOT IN ('EN_COURS','SOLDE','DEFAUT')"},
    {"id":"QUAL-007","pilier":"Qualité","entite":"prets","severite":"Élevé",
     "libelle":"Intégrité référentielle client",
     "description":"Chaque prêt doit être rattaché à un client existant dans le référentiel.",
     "sql":"SELECT pret_id FROM prets WHERE client_id NOT IN (SELECT client_id FROM clients)"},
    # ---------- GOUVERNANCE ----------
    {"id":"GOUV-001","pilier":"Gouvernance","entite":"catalogue","severite":"Élevé",
     "libelle":"Propriété des données (Data Owner)",
     "description":"Chaque donnée du périmètre doit avoir un Data Owner identifié.",
     "sql":"SELECT champ FROM catalogue WHERE data_owner IS NULL"},
    {"id":"GOUV-002","pilier":"Gouvernance","entite":"catalogue","severite":"Élevé",
     "libelle":"Traçabilité (lineage)",
     "description":"Chaque donnée doit avoir un système source documenté (pas de rupture de lineage).",
     "sql":"SELECT champ FROM catalogue WHERE source_systeme IS NULL"},
    {"id":"GOUV-003","pilier":"Gouvernance","entite":"prets","severite":"Modéré",
     "libelle":"Conformité au référentiel",
     "description":"La notation de risque doit appartenir au référentiel officiel (A à E).",
     "sql":"SELECT pret_id FROM prets WHERE notation_risque IS NOT NULL AND notation_risque NOT IN ('A','B','C','D','E')"},
    {"id":"GOUV-004","pilier":"Gouvernance","entite":"catalogue","severite":"Modéré",
     "libelle":"Classification de sensibilité",
     "description":"Chaque donnée du catalogue doit avoir un niveau de sensibilité renseigné.",
     "sql":"SELECT champ FROM catalogue WHERE sensibilite IS NULL"},
    # ---------- PROTECTION DES DONNEES ----------
    {"id":"PROT-001","pilier":"Protection","entite":"clients","severite":"Critique",
     "libelle":"Base légale (consentement RGPD)",
     "description":"Chaque client doit disposer d'un consentement RGPD valide.",
     "sql":"SELECT client_id FROM clients WHERE consentement_rgpd = FALSE"},
    {"id":"PROT-002","pilier":"Protection","entite":"clients","severite":"Élevé",
     "libelle":"Respect de la durée de rétention",
     "description":"Aucune donnée client ne doit être conservée au-delà de la durée légale (10 ans).",
     "sql":f"SELECT client_id FROM clients WHERE date_collecte < DATE '{REF}' - INTERVAL {RETENTION_CLIENT_JOURS} DAY"},
    {"id":"PROT-003","pilier":"Protection","entite":"catalogue","severite":"Modéré",
     "libelle":"Rétention des données personnelles définie",
     "description":"Chaque donnée personnelle (PII) doit avoir une durée de rétention définie.",
     "sql":"SELECT champ FROM catalogue WHERE is_pii = TRUE AND duree_retention_jours = -1"},
    {"id":"PROT-004","pilier":"Protection","entite":"catalogue","severite":"Élevé",
     "libelle":"Traçabilité des données personnelles",
     "description":"Chaque donnée personnelle (PII) doit avoir un système source identifié.",
     "sql":"SELECT champ FROM catalogue WHERE is_pii = TRUE AND source_systeme IS NULL"},
]

def run_all(clients_df, prets_df, catalogue_df):
    con = duckdb.connect()
    con.register("clients", clients_df); con.register("prets", prets_df); con.register("catalogue", catalogue_df)
    results = []
    for c in CONTROLS:
        ids = [r[0] for r in con.execute(c["sql"]).fetchall()]
        results.append({**c, "sql":" ".join(c["sql"].split()), "ids":ids})
    con.close(); return results
