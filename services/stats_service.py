"""
Services Stats
--------------
Fonctions utilitaires pour charger et préparer des données statistiques
(depuis la base SQLite).
"""

#Importation des bibliothèques
from services import db

#-----------------------------------------
# FONCTIONS
#-----------------------------------------


#Fonction qui compte le nombre de lignes par valeur pour une colonne donnée
def compter_par_colonne(df_variete, nom_colonne):
    return df_variete[nom_colonne].value_counts().reset_index()

