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
    "cadrage": "Mission d'inspection portant sur la chaine de donnees du risque de credit de NOVEO Banque. L'inspection evalue la qualite, la gouvernance et la protection des donnees clients et prets au regard des exigences BCBS 239, du referentiel DAMA-DMBOK et du RGPD. Les controles sont automatises et reproductibles ; chaque constat est chiffre et note par niveau de criticite."
  },
  "dataset": {
    "prets": 1510,
    "clients": 1025,
    "catalogue": 16
  },
  "controles": [
    {
      "id": "QUAL-001",
      "pilier": "Qualité",
      "entite": "prets",
      "libelle": "Complétude des champs critiques",
      "description": "Chaque prêt doit renseigner un montant et une notation de risque.",
      "regle": "SELECT pret_id FROM prets WHERE montant IS NULL OR isnan(montant) OR notation_risque IS NULL",
      "pourquoi": "Un pret sans montant ou sans notation ne peut etre ni suivi ni provisionne : c'est un angle mort dans le calcul du risque de credit de la banque.",
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
      "pourquoi": "Un montant negatif ou un taux aberrant fausse les agregats de risque et peut passer inapercu dans un reporting reglementaire (exigence d'exactitude BCBS 239).",
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
      "regle": "SELECT p.pret_id FROM prets p JOIN clients c ON p.client_id=c.client_id WHERE p.date_octroi < c.date_naissance + INTERVAL 18 YEAR",
      "pourquoi": "Un pret accorde avant la majorite du client trahit une donnee fausse ou une faille de controle a l'octroi : risque juridique et risque de fraude.",
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
      "regle": "SELECT client_id FROM (SELECT client_id, ROW_NUMBER() OVER (PARTITION BY nom,prenom,date_naissance,email ORDER BY client_id) AS rn FROM clients) WHERE rn > 1",
      "pourquoi": "Un meme client compte deux fois gonfle le portefeuille et fausse l'exposition au risque comme les obligations de connaissance client (KYC).",
      "severite": "Élevé",
      "statut": "NON CONFORME",
      "criticite": "Élevé",
      "exceptions": 25,
      "population": 1025,
      "taux": 2.44,
      "constat": "25 enregistrement(s) sur 1025 (2.44 %) en anomalie.",
      "recommandation": "Deployer une deduplication sur cle metier (nom, naissance, email) et un controle d'unicite a l'entree du referentiel client.",
      "exemples": [
        "CLI001017",
        "CLI001001",
        "CLI001015",
        "CLI001014",
        "CLI001002"
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
      "pourquoi": "Une donnee client trop ancienne peut ne plus refleter la realite (adresse, situation) : des decisions sont alors prises sur une base perimee.",
      "severite": "Modéré",
      "statut": "NON CONFORME",
      "criticite": "Modéré",
      "exceptions": 30,
      "population": 1025,
      "taux": 2.93,
      "constat": "30 enregistrement(s) sur 1025 (2.93 %) en anomalie.",
      "recommandation": "Definir un seuil de fraicheur par donnee et declencher une alerte automatique au-dela de la duree attendue.",
      "exemples": [
        "CLI000022",
        "CLI000028",
        "CLI000045",
        "CLI000077",
        "CLI000089"
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
      "id": "QUAL-006",
      "pilier": "Qualité",
      "entite": "prets",
      "libelle": "Validité du statut",
      "description": "Le statut du prêt doit appartenir au référentiel (EN_COURS, SOLDE, DEFAUT).",
      "regle": "SELECT pret_id FROM prets WHERE statut NOT IN ('EN_COURS','SOLDE','DEFAUT')",
      "pourquoi": "Un statut hors referentiel empeche tout suivi et fausse les etats de gestion : la nomenclature doit etre maitrisee.",
      "severite": "Modéré",
      "statut": "CONFORME",
      "criticite": "Conforme",
      "exceptions": 0,
      "population": 1510,
      "taux": 0.0,
      "constat": "Aucune anomalie detectee sur ce controle.",
      "recommandation": "",
      "exemples": [],
      "fiabilite": {
        "precision": 1.0,
        "rappel": 1.0,
        "f1": 1.0,
        "tp": 0,
        "fp": 0,
        "fn": 0
      }
    },
    {
      "id": "QUAL-007",
      "pilier": "Qualité",
      "entite": "prets",
      "libelle": "Intégrité référentielle client",
      "description": "Chaque prêt doit être rattaché à un client existant dans le référentiel.",
      "regle": "SELECT pret_id FROM prets WHERE client_id NOT IN (SELECT client_id FROM clients)",
      "pourquoi": "Un pret rattache a un client inexistant est une donnee orpheline : elle echappe au suivi et fausse l'exposition par client.",
      "severite": "Élevé",
      "statut": "CONFORME",
      "criticite": "Conforme",
      "exceptions": 0,
      "population": 1510,
      "taux": 0.0,
      "constat": "Aucune anomalie detectee sur ce controle.",
      "recommandation": "",
      "exemples": [],
      "fiabilite": {
        "precision": 1.0,
        "rappel": 1.0,
        "f1": 1.0,
        "tp": 0,
        "fp": 0,
        "fn": 0
      }
    },
    {
      "id": "GOUV-001",
      "pilier": "Gouvernance",
      "entite": "catalogue",
      "libelle": "Propriété des données (Data Owner)",
      "description": "Chaque donnée du périmètre doit avoir un Data Owner identifié.",
      "regle": "SELECT champ FROM catalogue WHERE data_owner IS NULL",
      "pourquoi": "Sans Data Owner identifie, personne n'est responsable de la qualite ni des acces a la donnee : c'est une exigence de base de la gouvernance (DAMA-DMBOK).",
      "severite": "Élevé",
      "statut": "NON CONFORME",
      "criticite": "Élevé",
      "exceptions": 2,
      "population": 16,
      "taux": 12.5,
      "constat": "2 enregistrement(s) sur 16 (12.5 %) en anomalie.",
      "recommandation": "Attribuer un Data Owner a chaque donnee critique et formaliser la responsabilite dans le catalogue de donnees.",
      "exemples": [
        "prets.taux",
        "clients.adresse"
      ],
      "fiabilite": {
        "precision": 1.0,
        "rappel": 1.0,
        "f1": 1.0,
        "tp": 2,
        "fp": 0,
        "fn": 0
      }
    },
    {
      "id": "GOUV-002",
      "pilier": "Gouvernance",
      "entite": "catalogue",
      "libelle": "Traçabilité (lineage)",
      "description": "Chaque donnée doit avoir un système source documenté (pas de rupture de lineage).",
      "regle": "SELECT champ FROM catalogue WHERE source_systeme IS NULL",
      "pourquoi": "Sans systeme source documente, impossible de tracer d'ou vient un chiffre : le lineage est indispensable pour fiabiliser un reporting reglementaire.",
      "severite": "Élevé",
      "statut": "NON CONFORME",
      "criticite": "Élevé",
      "exceptions": 2,
      "population": 16,
      "taux": 12.5,
      "constat": "2 enregistrement(s) sur 16 (12.5 %) en anomalie.",
      "recommandation": "Documenter le systeme source de chaque donnee et retablir le lineage de bout en bout (source vers reporting).",
      "exemples": [
        "prets.statut",
        "clients.date_collecte"
      ],
      "fiabilite": {
        "precision": 1.0,
        "rappel": 1.0,
        "f1": 1.0,
        "tp": 2,
        "fp": 0,
        "fn": 0
      }
    },
    {
      "id": "GOUV-003",
      "pilier": "Gouvernance",
      "entite": "prets",
      "libelle": "Conformité au référentiel",
      "description": "La notation de risque doit appartenir au référentiel officiel (A à E).",
      "regle": "SELECT pret_id FROM prets WHERE notation_risque IS NOT NULL AND notation_risque NOT IN ('A','B','C','D','E')",
      "pourquoi": "Une notation hors referentiel casse la comparabilite et l'agregation du risque : les indicateurs de risque deviennent non fiables.",
      "severite": "Modéré",
      "statut": "NON CONFORME",
      "criticite": "Modéré",
      "exceptions": 15,
      "population": 1510,
      "taux": 0.99,
      "constat": "15 enregistrement(s) sur 1510 (0.99 %) en anomalie.",
      "recommandation": "Contraindre la notation aux valeurs du referentiel officiel et rejeter toute valeur hors liste a la saisie.",
      "exemples": [
        "PRT000017",
        "PRT000066",
        "PRT000245",
        "PRT000264",
        "PRT000328"
      ],
      "fiabilite": {
        "precision": 1.0,
        "rappel": 1.0,
        "f1": 1.0,
        "tp": 15,
        "fp": 0,
        "fn": 0
      }
    },
    {
      "id": "GOUV-004",
      "pilier": "Gouvernance",
      "entite": "catalogue",
      "libelle": "Classification de sensibilité",
      "description": "Chaque donnée du catalogue doit avoir un niveau de sensibilité renseigné.",
      "regle": "SELECT champ FROM catalogue WHERE sensibilite IS NULL",
      "pourquoi": "Sans niveau de sensibilite, impossible d'appliquer les bonnes regles de protection et d'acces : la classification est le socle de la securite des donnees.",
      "severite": "Modéré",
      "statut": "CONFORME",
      "criticite": "Conforme",
      "exceptions": 0,
      "population": 16,
      "taux": 0.0,
      "constat": "Aucune anomalie detectee sur ce controle.",
      "recommandation": "",
      "exemples": [],
      "fiabilite": {
        "precision": 1.0,
        "rappel": 1.0,
        "f1": 1.0,
        "tp": 0,
        "fp": 0,
        "fn": 0
      }
    },
    {
      "id": "PROT-001",
      "pilier": "Protection",
      "entite": "clients",
      "libelle": "Base légale (consentement RGPD)",
      "description": "Chaque client doit disposer d'un consentement RGPD valide.",
      "regle": "SELECT client_id FROM clients WHERE consentement_rgpd = FALSE",
      "pourquoi": "Traiter des donnees personnelles sans base legale est une violation directe du RGPD, exposant la banque a un risque de sanction.",
      "severite": "Critique",
      "statut": "NON CONFORME",
      "criticite": "Critique",
      "exceptions": 20,
      "population": 1025,
      "taux": 1.95,
      "constat": "20 enregistrement(s) sur 1025 (1.95 %) en anomalie.",
      "recommandation": "Bloquer tout traitement sans base legale : recueillir ou regulariser le consentement avant exploitation des donnees.",
      "exemples": [
        "CLI000044",
        "CLI000064",
        "CLI000068",
        "CLI000290",
        "CLI000316"
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
      "id": "PROT-002",
      "pilier": "Protection",
      "entite": "clients",
      "libelle": "Respect de la durée de rétention",
      "description": "Aucune donnée client ne doit être conservée au-delà de la durée légale (10 ans).",
      "regle": "SELECT client_id FROM clients WHERE date_collecte < DATE '2026-09-01' - INTERVAL 3650 DAY",
      "pourquoi": "Conserver des donnees au-dela de la duree legale viole le principe de limitation de conservation du RGPD.",
      "severite": "Élevé",
      "statut": "NON CONFORME",
      "criticite": "Élevé",
      "exceptions": 20,
      "population": 1025,
      "taux": 1.95,
      "constat": "20 enregistrement(s) sur 1025 (1.95 %) en anomalie.",
      "recommandation": "Mettre en place une purge automatique des donnees dont la duree de conservation legale est depassee.",
      "exemples": [
        "CLI000014",
        "CLI000017",
        "CLI000048",
        "CLI000074",
        "CLI000239"
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
      "id": "PROT-003",
      "pilier": "Protection",
      "entite": "catalogue",
      "libelle": "Rétention des données personnelles définie",
      "description": "Chaque donnée personnelle (PII) doit avoir une durée de rétention définie.",
      "regle": "SELECT champ FROM catalogue WHERE is_pii = TRUE AND duree_retention_jours = -1",
      "pourquoi": "Une donnee personnelle sans duree de retention definie ne peut etre purgee dans les temps : non-conformite au RGPD par defaut.",
      "severite": "Modéré",
      "statut": "NON CONFORME",
      "criticite": "Modéré",
      "exceptions": 2,
      "population": 16,
      "taux": 12.5,
      "constat": "2 enregistrement(s) sur 16 (12.5 %) en anomalie.",
      "recommandation": "Definir et documenter une duree de retention pour chaque donnee personnelle du catalogue.",
      "exemples": [
        "clients.email",
        "clients.adresse"
      ],
      "fiabilite": {
        "precision": 1.0,
        "rappel": 1.0,
        "f1": 1.0,
        "tp": 2,
        "fp": 0,
        "fn": 0
      }
    },
    {
      "id": "PROT-004",
      "pilier": "Protection",
      "entite": "catalogue",
      "libelle": "Traçabilité des données personnelles",
      "description": "Chaque donnée personnelle (PII) doit avoir un système source identifié.",
      "regle": "SELECT champ FROM catalogue WHERE is_pii = TRUE AND source_systeme IS NULL",
      "pourquoi": "Une donnee personnelle sans systeme source identifie ne peut etre ni tracee ni securisee correctement : exigence de tracabilite du RGPD.",
      "severite": "Élevé",
      "statut": "CONFORME",
      "criticite": "Conforme",
      "exceptions": 0,
      "population": 16,
      "taux": 0.0,
      "constat": "Aucune anomalie detectee sur ce controle.",
      "recommandation": "",
      "exemples": [],
      "fiabilite": {
        "precision": 1.0,
        "rappel": 1.0,
        "f1": 1.0,
        "tp": 0,
        "fp": 0,
        "fn": 0
      }
    }
  ],
  "eval": {
    "precision": 1.0,
    "rappel": 1.0,
    "f1": 1.0,
    "tp": 206,
    "fp": 0,
    "fn": 0
  },
  "synthese": {
    "Critique": 2,
    "Élevé": 5,
    "Modéré": 4,
    "conformes": 4
  }
};