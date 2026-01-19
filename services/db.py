"""
Service d'accès à la base de données 
Ce module centralise toutes les fonctions liées :
- à la connexion à la base de données 
- au chargement des données utilisées par l'application
"""

#Importation des bibliothèques
import os
from pathlib import Path
import sqlite3
import pandas as pd

#Variables
# Chemin "racine projet" (TomatoCycle/)
ROOT = Path(__file__).resolve().parents[1]

# Base par défaut : TomatoCycle/data/tomatocycle.db
DEFAULT_DB_PATH = ROOT / "data" / "tomatocycle.db"

# Si la variable d'environnement est définie, on l'utilise, sinon on prend le chemin par défaut
DB_PATH = Path(os.getenv("TOMATOCYCLE_DB_PATH", str(DEFAULT_DB_PATH)))


#-----------------------------------------
# FONCTIONS
#-----------------------------------------

#On charge les données
def charger_donnees():
    """
    Charge la table 'variete' depuis la base SQLite
    et la retourne sous forme de DataFrame pandas.
    """
    connexion = sqlite3.connect(str(DB_PATH))
    df_variete = pd.read_sql_query("SELECT * FROM variete", connexion)
    connexion.close()
    return df_variete