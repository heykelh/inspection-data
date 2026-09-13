"""
INSPECTION DATA - Moteur de controles.
Chaque controle est une regle SQL exécutée sur les données NOVEO.
Le code detecte, compte et note. Aucune interpretation par un modele.
"""
import duckdb

# Date de la mission (identique au generateur)
REF = "2026-09-01"

CONTROLS = [
    {
        "id": "QUAL-001", "pilier": "Qualité", "entite": "prets", "severite": "Élevé",
        "libelle": "Complétude des champs critiques",
        "description": "Chaque prêt doit renseigner un montant et une notation de risque.",
        "sql": """
            SELECT pret_id FROM prets
            WHERE montant IS NULL OR isnan(montant) OR notation_risque IS NULL
        """,
    },
    {
        "id": "QUAL-002", "pilier": "Qualité", "entite": "prets", "severite": "Critique",
        "libelle": "Validité des bornes",
        "description": "Le montant doit être strictement positif et le taux compris entre 0 et 25 %.",
        "sql": """
            SELECT pret_id FROM prets
            WHERE (montant IS NOT NULL AND NOT isnan(montant) AND montant <= 0)
               OR (taux < 0 OR taux > 25)
        """,
    },
    {
        "id": "QUAL-003", "pilier": "Qualité", "entite": "prets", "severite": "Modéré",
        "libelle": "Cohérence temporelle",
        "description": "La date d'octroi doit être postérieure à la majorité du client.",
        "sql": """
            SELECT p.pret_id
            FROM prets p JOIN clients c ON p.client_id = c.client_id
            WHERE p.date_octroi < c.date_naissance + INTERVAL 18 YEAR
        """,
    },
    {
        "id": "QUAL-004", "pilier": "Qualité", "entite": "clients", "severite": "Élevé",
        "libelle": "Unicité des clients",
        "description": "Aucun client ne doit exister en double sur une clé métier (nom, naissance, email).",
        "sql": """
            SELECT client_id FROM (
                SELECT client_id, ROW_NUMBER() OVER (
                    PARTITION BY nom, prenom, date_naissance, email ORDER BY client_id
                ) AS rn FROM clients
            ) WHERE rn > 1
        """,
    },
    {
        "id": "QUAL-005", "pilier": "Qualité", "entite": "clients", "severite": "Modéré",
        "libelle": "Fraîcheur des données",
        "description": "Les données client doivent avoir été mises à jour depuis moins d'un an.",
        "sql": f"""
            SELECT client_id FROM clients
            WHERE date_maj < DATE '{REF}' - INTERVAL 365 DAY
        """,
    },
]


def run_all(clients_df, prets_df):
    con = duckdb.connect()
    con.register("clients", clients_df)
    con.register("prets", prets_df)
    results = []
    for c in CONTROLS:
        ids = [row[0] for row in con.execute(c["sql"]).fetchall()]
        results.append({**c, "sql": " ".join(c["sql"].split()), "ids": ids})
    con.close()
    return results
