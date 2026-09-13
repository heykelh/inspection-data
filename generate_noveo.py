"""
INSPECTION DATA - Generateur du jeu de donnees NOVEO Banque.
Chaine de donnees du risque de credit : clients + prets.
Injecte des defauts controles et produit la verite terrain pour l'evaluation.
Deterministe (seed fixe) : le jeu est reproductible a l'identique.
"""
import os
import random
from datetime import date, timedelta

import pandas as pd
from faker import Faker

SEED = 42
REF_DATE = date(2026, 9, 1)      # date de la mission d'inspection
N_CLIENTS = 1000
PRETS_PAR_CLIENT_MAX = 2

NOTATIONS = ["A", "B", "C", "D", "E"]
STATUTS = ["EN_COURS", "SOLDE", "DEFAUT"]

random.seed(SEED)
Faker.seed(SEED)
fake = Faker("fr_FR")


def _rand_date(start: date, end: date) -> date:
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, max(delta, 0)))


def _majorite(naissance: date) -> date:
    return date(naissance.year + 18, naissance.month, min(naissance.day, 28))


def build():
    # ---- clients sains ----
    clients = []
    for i in range(1, N_CLIENTS + 1):
        prenom = fake.first_name()
        nom = fake.last_name()
        naissance = _rand_date(date(1955, 1, 1), date(2004, 1, 1))
        email = f"{prenom}.{nom}.{i}@example.com".lower().replace(" ", "")
        clients.append({
            "client_id": f"CLI{i:06d}",
            "nom": nom,
            "prenom": prenom,
            "date_naissance": naissance,
            "email": email,
            "adresse": fake.address().replace("\n", ", "),
            "consentement_rgpd": True,
            "date_collecte": _rand_date(date(2018, 1, 1), REF_DATE),
            "date_maj": _rand_date(REF_DATE - timedelta(days=180), REF_DATE),
        })

    # ---- prets sains ----
    prets = []
    pid = 0
    for c in clients:
        for _ in range(random.randint(1, PRETS_PAR_CLIENT_MAX)):
            pid += 1
            debut = max(_majorite(c["date_naissance"]), date(2015, 1, 1))
            prets.append({
                "pret_id": f"PRT{pid:06d}",
                "client_id": c["client_id"],
                "montant": round(random.uniform(2000, 60000), 2),
                "taux": round(random.uniform(0.5, 8.0), 2),
                "date_octroi": _rand_date(debut, REF_DATE),
                "statut": random.choice(STATUTS),
                "notation_risque": random.choice(NOTATIONS),
            })

    clients_df = pd.DataFrame(clients)
    prets_df = pd.DataFrame(prets)
    gt = []  # verite terrain : (entite, id, control_id)

    # ================= INJECTION DES DEFAUTS =================
    idx = list(prets_df.index)
    random.shuffle(idx)

    # QUAL-001 : completude (montant ou notation manquants)
    q1_montant, q1_notation = idx[:20], idx[20:40]
    prets_df.loc[q1_montant, "montant"] = None
    prets_df.loc[q1_notation, "notation_risque"] = None
    for ix in q1_montant + q1_notation:
        gt.append({"entite": "prets", "id": prets_df.at[ix, "pret_id"], "control_id": "QUAL-001"})

    # QUAL-002 : validite des bornes (montant <= 0 ou taux hors [0, 25])
    rest = idx[40:]
    q2_montant, q2_taux = rest[:15], rest[15:30]
    prets_df.loc[q2_montant, "montant"] = [round(random.uniform(-5000, -100), 2) for _ in q2_montant]
    prets_df.loc[q2_taux, "taux"] = [random.choice([-2.5, 27.0, 31.5, 42.0]) for _ in q2_taux]
    for ix in q2_montant + q2_taux:
        gt.append({"entite": "prets", "id": prets_df.at[ix, "pret_id"], "control_id": "QUAL-002"})

    # QUAL-003 : coherence temporelle (octroi avant la majorite du client)
    q3 = rest[30:50]
    for ix in q3:
        cid = prets_df.at[ix, "client_id"]
        naiss = clients_df.loc[clients_df.client_id == cid, "date_naissance"].iloc[0]
        prets_df.at[ix, "date_octroi"] = date(naiss.year + random.randint(5, 16), naiss.month, min(naiss.day, 28))
        gt.append({"entite": "prets", "id": prets_df.at[ix, "pret_id"], "control_id": "QUAL-003"})

    # QUAL-005 : fraicheur (date_maj > 365 jours avant la mission)
    cidx = list(clients_df.index)
    random.shuffle(cidx)
    q5 = cidx[:30]
    clients_df.loc[q5, "date_maj"] = [_rand_date(date(2019, 1, 1), REF_DATE - timedelta(days=400)) for _ in q5]
    for ix in q5:
        gt.append({"entite": "clients", "id": clients_df.at[ix, "client_id"], "control_id": "QUAL-005"})

    # QUAL-004 : unicite (doublons clients, identite copiee, nouvel identifiant)
    dups = []
    for k, pos in enumerate(random.sample(range(N_CLIENTS), 25), start=1):
        src = clients_df.iloc[pos]
        new_id = f"CLI{N_CLIENTS + k:06d}"
        dups.append({
            "client_id": new_id,
            "nom": src["nom"], "prenom": src["prenom"],
            "date_naissance": src["date_naissance"], "email": src["email"],
            "adresse": src["adresse"], "consentement_rgpd": True,
            "date_collecte": _rand_date(date(2020, 1, 1), REF_DATE),
            "date_maj": _rand_date(REF_DATE - timedelta(days=120), REF_DATE),
        })
        gt.append({"entite": "clients", "id": new_id, "control_id": "QUAL-004"})
    clients_df = pd.concat([clients_df, pd.DataFrame(dups)], ignore_index=True)

    # ---- typage des dates puis ecriture ----
    for col in ["date_naissance", "date_collecte", "date_maj"]:
        clients_df[col] = pd.to_datetime(clients_df[col])
    prets_df["date_octroi"] = pd.to_datetime(prets_df["date_octroi"])

    os.makedirs("data", exist_ok=True)
    clients_df.to_csv("data/clients.csv", index=False)
    prets_df.to_csv("data/prets.csv", index=False)
    gt_df = pd.DataFrame(gt)
    gt_df.to_csv("data/ground_truth.csv", index=False)

    return clients_df, prets_df, gt_df


if __name__ == "__main__":
    c, p, g = build()
    print(f"NOVEO genere : {len(c)} clients, {len(p)} prets, {len(g)} anomalies injectees.")
