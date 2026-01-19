"""
Chargement des données en base de données

Ce script a pour rôle de :
- créer les tables de la base (via schemas.sql)
- lire le fichier JSON des variétés
- insérer / mettre à jour les données en base SQLite
"""

# ----------------------------------------------------------
# Import des librairies
# ----------------------------------------------------------

import json               
import sqlite3             
from pathlib import Path   
import random


# ----------------------------------------------------------
# Définition des chemins du projet
# ----------------------------------------------------------

# Dossier où se trouve ce fichier 
BASE_DIR = Path(__file__).resolve().parent

# Chemin vers la base de données SQLite
DB_PATH = BASE_DIR / "../data/tomatocycle.db"

# Chemin vers le fichier SQL de création des tables
SCHEMA_PATH = BASE_DIR / "schema.sql"

# Chemin vers le fichier JSON contenant toutes les variétés
JSON_PATH = BASE_DIR / "../data/varietes_all.json"


# ----------------------------------------------------------
# Script principal
# ----------------------------------------------------------

if __name__ == "__main__":

    #Connexion à la base de données
    #Si le fichier n'existe pas, SQLite le crée automatiquement.
    connexion = sqlite3.connect(DB_PATH)

    cursor = connexion.cursor()

    #Création des tables (selon schemas.sql)
    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
    cursor.executescript(schema_sql)

    print("schéma de la base chargé")

    #Chargement des données JSON
    varietes = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    print(f"{len(varietes)} variétés chargées depuis le JSON")


    # Remplissage date_semence
    # Chargement modulé pour : 20 en 2020, 10 en 2021, le reste aléatoire entre 2022 et 2025
    n = len(varietes)
    forced_years = ["2020"] * min(20, n) + ["2021"] * min(10, max(0, n - 20))
    remaining = n - len(forced_years)
    random_years = [str(random.randint(2022, 2025)) for _ in range(remaining)]

    years = forced_years + random_years
    random.shuffle(years)

    for v, y in zip(varietes, years):
        v["date_semence"] = y

    #On vide la table avant insertion (provisoire pour éviter les doublons)
    cursor.execute("DELETE FROM variete;")

    #Insertion / mise à jour des données
    cursor.executemany(
        """
        INSERT INTO variete (
            id_source,
            nom,
            couleur,
            forme,
            taille,
            precocite,
            descriptif,
            notes_gustatives,
            date_semence,
            image_url
        ) VALUES (
            :id_source,
            :nom,
            :couleur,
            :forme,
            :taille,
            :precocite,
            :descriptif,
            :notes_gustatives,
            :date_semence,
            :image_url
        );
        """,
        varietes
    )

    # On valide définitivement les changements
    connexion.commit()

    print("données insérées / mises à jour")

    #Vérification
    cursor.execute("SELECT COUNT(*) FROM variete;")
    nb = cursor.fetchone()[0]

    print("nombre de variétés en base :", nb)

    #Fermeture de la connexion
    connexion.close()
    print("connexion fermée — import terminé")