window.INSPECTION_DATA = {
  "mission": {
    "titre": "Mission d'inspection Data",
    "entite": "NOVEO Banque",
    "perimetre": "Chaine de donnees du risque de credit",
    "date_mission": "2026-09-01",
    "referentiels": [
      "BCBS 239",
      "DAMA-DMBOK",
      "RGPD"
    ],
    "cadrage": "Mission d'inspection portant sur la chaine de donnees du risque de credit de NOVEO Banque. L'inspection evalue la qualite des donnees clients et prets au regard des exigences BCBS 239, du referentiel DAMA-DMBOK et des principes de protection des donnees. Les controles sont automatises et reproductibles ; chaque constat est chiffre et note par niveau de criticite."
  },
  "dataset": {
    "prets": 1510,
    "clients": 1025
  },
  "controles": [
    {
      "id": "QUAL-001",
      "pilier": "Qualité",
      "entite": "prets",
      "libelle": "Complétude des champs critiques",
      "description": "Chaque prêt doit renseigner un montant et une notation de risque.",
      "regle": "SELECT pret_id FROM prets WHERE montant IS NULL OR isnan(montant) OR notation_risque IS NULL",
      "severite": "Élevé",
      "statut": "NON CONFORME",
      "criticite": "Élevé",
      "exceptions": 40,
      "population": 1510,
      "taux": 2.65,
      "constat": "40 enregistrement(s) sur 1510 (2.65 %) en anomalie.",
      "recommandation": "Rendre le montant et la notation obligatoires a la saisie et rejeter les enregistrements incomplets a l'integration.",
      "exemples": [
        "PRT000005",
        "PRT000075",
        "PRT000078",
        "PRT000095",
        "PRT000115"
      ],
      "fiabilite": {
        "precision": 1.0,
        "rappel": 1.0,
        "f1": 1.0,
        "tp": 40,
        "fp": 0,
        "fn": 0
      }
    },
    {
      "id": "QUAL-002",
      "pilier": "Qualité",
      "entite": "prets",
      "libelle": "Validité des bornes",
      "description": "Le montant doit être strictement positif et le taux compris entre 0 et 25 %.",
      "regle": "SELECT pret_id FROM prets WHERE (montant IS NOT NULL AND NOT isnan(montant) AND montant <= 0) OR (taux < 0 OR taux > 25)",
      "severite": "Critique",
      "statut": "NON CONFORME",
      "criticite": "Critique",
      "exceptions": 30,
      "population": 1510,
      "taux": 1.99,
      "constat": "30 enregistrement(s) sur 1510 (1.99 %) en anomalie.",
      "recommandation": "Ajouter des controles de bornes en amont du chargement : montant strictement positif, taux dans une plage definie.",
      "exemples": [
        "PRT000028",
        "PRT000139",
        "PRT000205",
        "PRT000211",
        "PRT000253"
      ],
      "fiabilite": {
        "precision": 1.0,
        "rappel": 1.0,
        "f1": 1.0,
        "tp": 30,
        "fp": 0,
        "fn": 0
      }
    },
    {
      "id": "QUAL-003",
      "pilier": "Qualité",
      "entite": "prets",
      "libelle": "Cohérence temporelle",
      "description": "La date d'octroi doit être postérieure à la majorité du client.",
      "regle": "SELECT p.pret_id FROM prets p JOIN clients c ON p.client_id = c.client_id WHERE p.date_octroi < c.date_naissance + INTERVAL 18 YEAR",
      "severite": "Modéré",
      "statut": "NON CONFORME",
      "criticite": "Modéré",
      "exceptions": 20,
      "population": 1510,
      "taux": 1.32,
      "constat": "20 enregistrement(s) sur 1510 (1.32 %) en anomalie.",
      "recommandation": "Introduire une regle bloquante de coherence entre date de naissance et date d'octroi lors de la creation du pret.",
      "exemples": [
        "PRT000012",
        "PRT000059",
        "PRT000153",
        "PRT000172",
        "PRT000314"
      ],
      "fiabilite": {
        "precision": 1.0,
        "rappel": 1.0,
        "f1": 1.0,
        "tp": 20,
        "fp": 0,
        "fn": 0
      }
    },
    {
      "id": "QUAL-004",
      "pilier": "Qualité",
      "entite": "clients",
      "libelle": "Unicité des clients",
      "description": "Aucun client ne doit exister en double sur une clé métier (nom, naissance, email).",
      "regle": "SELECT client_id FROM ( SELECT client_id, ROW_NUMBER() OVER ( PARTITION BY nom, prenom, date_naissance, email ORDER BY client_id ) AS rn FROM clients ) WHERE rn > 1",
      "severite": "Élevé",
      "statut": "NON CONFORME",
      "criticite": "Élevé",
      "exceptions": 25,
      "population": 1025,
      "taux": 2.44,
      "constat": "25 enregistrement(s) sur 1025 (2.44 %) en anomalie.",
      "recommandation": "Deployer une deduplication sur cle metier (nom, naissance, email) et un controle d'unicite a l'entree du referentiel client.",
      "exemples": [
        "CLI001005",
        "CLI001016",
        "CLI001023",
        "CLI001014",
        "CLI001013"
      ],
      "fiabilite": {
        "precision": 1.0,
        "rappel": 1.0,
        "f1": 1.0,
        "tp": 25,
        "fp": 0,
        "fn": 0
      }
    },
    {
      "id": "QUAL-005",
      "pilier": "Qualité",
      "entite": "clients",
      "libelle": "Fraîcheur des données",
      "description": "Les données client doivent avoir été mises à jour depuis moins d'un an.",
      "regle": "SELECT client_id FROM clients WHERE date_maj < DATE '2026-09-01' - INTERVAL 365 DAY",
      "severite": "Modéré",
      "statut": "NON CONFORME",
      "criticite": "Modéré",
      "exceptions": 30,
      "population": 1025,
      "taux": 2.93,
      "constat": "30 enregistrement(s) sur 1025 (2.93 %) en anomalie.",
      "recommandation": "Definir un seuil de fraicheur par donnee et declencher une alerte automatique au-dela de la duree attendue.",
      "exemples": [
        "CLI000017",
        "CLI000022",
        "CLI000028",
        "CLI000048",
        "CLI000181"
      ],
      "fiabilite": {
        "precision": 1.0,
        "rappel": 1.0,
        "f1": 1.0,
        "tp": 30,
        "fp": 0,
        "fn": 0
      }
    }
  ],
  "eval": {
    "precision": 1.0,
    "rappel": 1.0,
    "f1": 1.0,
    "tp": 145,
    "fp": 0,
    "fn": 0
  },
  "synthese": {
    "Critique": 1,
    "Élevé": 2,
    "Modéré": 2,
    "conformes": 0
  }
};