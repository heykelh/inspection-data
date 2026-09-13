# INSPECTION DATA

Simulation d'une mission d'inspection Data sur une banque de detail fictive (NOVEO Banque),
calquee sur les trois etapes d'une mission d'Inspection Generale : cadrage, investigations, debriefing.

Perimetre : la chaine de donnees du risque de credit (clients et prets).
L'inspection detecte les anomalies de qualite, les chiffre, les note par criticite,
et produit un registre de constats avec recommandations.

## Principe

Les controles sont des regles codees (SQL). Le code detecte, compte et note ;
un jeu de test a verite terrain mesure la fiabilite du moteur (precision, rappel, F1).

## Lancer

python -m venv .venv
..venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py
