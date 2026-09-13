import os, random
from datetime import date, timedelta
import pandas as pd
from faker import Faker

SEED = 42
REF_DATE = date(2026, 9, 1)
N_CLIENTS = 1000
PRETS_PAR_CLIENT_MAX = 2
NOTATIONS = ["A", "B", "C", "D", "E"]
STATUTS = ["EN_COURS", "SOLDE", "DEFAUT"]
random.seed(SEED); Faker.seed(SEED)
fake = Faker("fr_FR")

def _rand_date(start, end):
    return start + timedelta(days=random.randint(0, max((end - start).days, 0)))
def _majorite(n):
    return date(n.year + 18, n.month, min(n.day, 28))

# --- catalogue de donnees (couche metadonnees, pilote la gouvernance/protection) ---
# duree_retention_jours = -1  => retention non definie
CATALOGUE = [
 {"champ":"prets.pret_id","entite":"prets","sensibilite":"Interne","data_owner":"Direction des Risques","data_steward":"Steward Credit","source_systeme":"Octroi","duree_retention_jours":3650,"is_pii":False},
 {"champ":"prets.client_id","entite":"prets","sensibilite":"Interne","data_owner":"Direction des Risques","data_steward":"Steward Credit","source_systeme":"Octroi","duree_retention_jours":3650,"is_pii":False},
 {"champ":"prets.montant","entite":"prets","sensibilite":"Confidentielle","data_owner":"Direction des Risques","data_steward":"Steward Credit","source_systeme":"Core Banking","duree_retention_jours":3650,"is_pii":False},
 {"champ":"prets.taux","entite":"prets","sensibilite":"Confidentielle","data_owner":None,"data_steward":"Steward Credit","source_systeme":"Core Banking","duree_retention_jours":3650,"is_pii":False},
 {"champ":"prets.date_octroi","entite":"prets","sensibilite":"Interne","data_owner":"Direction des Risques","data_steward":"Steward Credit","source_systeme":"Octroi","duree_retention_jours":3650,"is_pii":False},
 {"champ":"prets.statut","entite":"prets","sensibilite":"Interne","data_owner":"Direction des Risques","data_steward":"Steward Credit","source_systeme":None,"duree_retention_jours":3650,"is_pii":False},
 {"champ":"prets.notation_risque","entite":"prets","sensibilite":"Confidentielle","data_owner":"Direction des Risques","data_steward":"Steward Modeles","source_systeme":"Moteur de notation","duree_retention_jours":3650,"is_pii":False},
 {"champ":"clients.client_id","entite":"clients","sensibilite":"Interne","data_owner":"Direction Clientele","data_steward":"Steward Client","source_systeme":"CRM","duree_retention_jours":3650,"is_pii":False},
 {"champ":"clients.nom","entite":"clients","sensibilite":"PII","data_owner":"Direction Clientele","data_steward":"Steward Client","source_systeme":"CRM","duree_retention_jours":1825,"is_pii":True},
 {"champ":"clients.prenom","entite":"clients","sensibilite":"PII","data_owner":"Direction Clientele","data_steward":"Steward Client","source_systeme":"CRM","duree_retention_jours":1825,"is_pii":True},
 {"champ":"clients.date_naissance","entite":"clients","sensibilite":"PII","data_owner":"Direction Clientele","data_steward":"Steward Client","source_systeme":"CRM","duree_retention_jours":1825,"is_pii":True},
 {"champ":"clients.email","entite":"clients","sensibilite":"PII","data_owner":"Direction Clientele","data_steward":"Steward Client","source_systeme":"CRM","duree_retention_jours":-1,"is_pii":True},
 {"champ":"clients.adresse","entite":"clients","sensibilite":"PII","data_owner":None,"data_steward":"Steward Client","source_systeme":"CRM","duree_retention_jours":-1,"is_pii":True},
 {"champ":"clients.consentement_rgpd","entite":"clients","sensibilite":"Confidentielle","data_owner":"DPO","data_steward":"Steward Conformite","source_systeme":"CRM","duree_retention_jours":1825,"is_pii":False},
 {"champ":"clients.date_collecte","entite":"clients","sensibilite":"Interne","data_owner":"DPO","data_steward":"Steward Conformite","source_systeme":None,"duree_retention_jours":1825,"is_pii":False},
 {"champ":"clients.date_maj","entite":"clients","sensibilite":"Interne","data_owner":"Direction Clientele","data_steward":"Steward Client","source_systeme":"CRM","duree_retention_jours":1825,"is_pii":False},
]

def build():
    clients = []
    for i in range(1, N_CLIENTS + 1):
        prenom = fake.first_name(); nom = fake.last_name()
        naissance = _rand_date(date(1955,1,1), date(2004,1,1))
        email = f"{prenom}.{nom}.{i}@example.com".lower().replace(" ", "")
        clients.append({"client_id": f"CLI{i:06d}","nom":nom,"prenom":prenom,
            "date_naissance":naissance,"email":email,"adresse":fake.address().replace("\n",", "),
            "consentement_rgpd":True,"date_collecte":_rand_date(date(2018,1,1),REF_DATE),
            "date_maj":_rand_date(REF_DATE - timedelta(days=180), REF_DATE)})
    prets = []; pid = 0
    for c in clients:
        for _ in range(random.randint(1, PRETS_PAR_CLIENT_MAX)):
            pid += 1
            debut = max(_majorite(c["date_naissance"]), date(2015,1,1))
            prets.append({"pret_id":f"PRT{pid:06d}","client_id":c["client_id"],
                "montant":round(random.uniform(2000,60000),2),"taux":round(random.uniform(0.5,8.0),2),
                "date_octroi":_rand_date(debut, REF_DATE),"statut":random.choice(STATUTS),
                "notation_risque":random.choice(NOTATIONS)})
    clients_df = pd.DataFrame(clients); prets_df = pd.DataFrame(prets); gt = []

    # ===== defauts sur les prets =====
    idx = list(prets_df.index); random.shuffle(idx)
    q1_m, q1_n = idx[:20], idx[20:40]
    prets_df.loc[q1_m,"montant"]=None; prets_df.loc[q1_n,"notation_risque"]=None
    for ix in q1_m+q1_n: gt.append({"entite":"prets","id":prets_df.at[ix,"pret_id"],"control_id":"QUAL-001"})
    rest = idx[40:]; q2_m, q2_t = rest[:15], rest[15:30]
    prets_df.loc[q2_m,"montant"]=[round(random.uniform(-5000,-100),2) for _ in q2_m]
    prets_df.loc[q2_t,"taux"]=[random.choice([-2.5,27.0,31.5,42.0]) for _ in q2_t]
    for ix in q2_m+q2_t: gt.append({"entite":"prets","id":prets_df.at[ix,"pret_id"],"control_id":"QUAL-002"})
    q3 = rest[30:50]
    for ix in q3:
        cid = prets_df.at[ix,"client_id"]
        naiss = clients_df.loc[clients_df.client_id==cid,"date_naissance"].iloc[0]
        prets_df.at[ix,"date_octroi"]=date(naiss.year+random.randint(5,16),naiss.month,min(naiss.day,28))
        gt.append({"entite":"prets","id":prets_df.at[ix,"pret_id"],"control_id":"QUAL-003"})
    # GOUV-003 : notation hors referentiel (non nulle)
    q_gouv3 = rest[50:65]
    prets_df.loc[q_gouv3,"notation_risque"]=[random.choice(["F","Z"]) for _ in q_gouv3]
    for ix in q_gouv3: gt.append({"entite":"prets","id":prets_df.at[ix,"pret_id"],"control_id":"GOUV-003"})

    # ===== defauts sur les clients =====
    cidx = list(clients_df.index); random.shuffle(cidx)
    q5 = cidx[:30]
    clients_df.loc[q5,"date_maj"]=[_rand_date(date(2019,1,1),REF_DATE - timedelta(days=400)) for _ in q5]
    for ix in q5: gt.append({"entite":"clients","id":clients_df.at[ix,"client_id"],"control_id":"QUAL-005"})
    # PROT-001 : consentement RGPD absent
    p1 = cidx[30:50]
    clients_df.loc[p1,"consentement_rgpd"]=False
    for ix in p1: gt.append({"entite":"clients","id":clients_df.at[ix,"client_id"],"control_id":"PROT-001"})
    # PROT-002 : retention depassee (collecte tres ancienne)
    p2 = cidx[50:70]
    clients_df.loc[p2,"date_collecte"]=[_rand_date(date(2010,1,1),date(2015,12,31)) for _ in p2]
    for ix in p2: gt.append({"entite":"clients","id":clients_df.at[ix,"client_id"],"control_id":"PROT-002"})
    # QUAL-004 : doublons clients
    dups = []
    for k, pos in enumerate(random.sample(range(N_CLIENTS),25), start=1):
        src = clients_df.iloc[pos]; new_id = f"CLI{N_CLIENTS+k:06d}"
        dups.append({"client_id":new_id,"nom":src["nom"],"prenom":src["prenom"],
            "date_naissance":src["date_naissance"],"email":src["email"],"adresse":src["adresse"],
            "consentement_rgpd":True,"date_collecte":_rand_date(date(2020,1,1),REF_DATE),
            "date_maj":_rand_date(REF_DATE - timedelta(days=120), REF_DATE)})
        gt.append({"entite":"clients","id":new_id,"control_id":"QUAL-004"})
    clients_df = pd.concat([clients_df, pd.DataFrame(dups)], ignore_index=True)

    # ===== catalogue + verite terrain gouvernance/protection =====
    cat_df = pd.DataFrame(CATALOGUE)
    for row in CATALOGUE:
        if row["data_owner"] is None:
            gt.append({"entite":"catalogue","id":row["champ"],"control_id":"GOUV-001"})
        if row["source_systeme"] is None:
            gt.append({"entite":"catalogue","id":row["champ"],"control_id":"GOUV-002"})
        if row["is_pii"] and row["duree_retention_jours"] == -1:
            gt.append({"entite":"catalogue","id":row["champ"],"control_id":"PROT-003"})

    for col in ["date_naissance","date_collecte","date_maj"]:
        clients_df[col]=pd.to_datetime(clients_df[col])
    prets_df["date_octroi"]=pd.to_datetime(prets_df["date_octroi"])

    os.makedirs("data", exist_ok=True)
    clients_df.to_csv("data/clients.csv", index=False)
    prets_df.to_csv("data/prets.csv", index=False)
    cat_df.to_csv("data/catalogue.csv", index=False)
    gt_df = pd.DataFrame(gt); gt_df.to_csv("data/ground_truth.csv", index=False)
    return clients_df, prets_df, cat_df, gt_df

if __name__ == "__main__":
    c,p,cat,g = build()
    print(f"NOVEO : {len(c)} clients, {len(p)} prets, {len(cat)} champs catalogue, {len(g)} anomalies injectees.")
