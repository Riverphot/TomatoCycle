"""
Page Stats :
Cette page affiche des statistiques globales sur le catalogue de variétés
de tomates (répartition par couleur, forme, taille, précocité, etc.).
"""

#Importation des bibliothèques
import streamlit as st
import plotly.express as px

from services import db
from services import stats_service as serv


#-----------------------------------------
# CREATION DES GRAPHES
#-----------------------------------------

df_variete = db.charger_donnees()

#On compte par couleur
df_couleur = serv.compter_par_colonne(df_variete, "couleur")
df_couleur.columns = ["couleur", "nombre"]  

#Création du graphique en camembert
fig_couleur = px.pie(df_couleur, names="couleur", values="nombre", title="Répartition des variétés par couleur")


#-----------------------------------------
# INTERFACE
#-----------------------------------------


#Configuration de la page
st.title("📊 Statistiques du catalogue")

st.write(
    "Cette page présentera des graphiques sur la répartition des variétés "
    "par couleur, forme, taille et précocité."
)

#Affichage du graphique de répartition par couleur
st.plotly_chart(fig_couleur, use_container_width=True)
st.dataframe(df_couleur)
