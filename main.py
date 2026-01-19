"""
Page principale de l’application Streamlit (page d’accueil).
Elle sert à définir la configuration globale de l’application, 
afficher le titre et un message d’accueil
"""

#bibliothèque pour l'interface Streamlit
import streamlit as st

# Configuration globale de l'application
st.set_page_config(page_title="TomatoCycle", layout="wide")

# Titre affiché sur la page d'accueil
st.title("TomatoCycle 🍅")

# Texte
st.write("Bienvenue !")


#Navigation vers les autres pages
st.subheader("Navigation")

st.page_link(
    "pages/catalogue.py",
    label="📚 Catalogue",
    help="Explorer les variétés de tomates (filtres, recherche, détails)"
)

st.page_link(
    "pages/stats.py",
    label="📊 Statistiques",
    help="Vue globale sur la répartition des variétés"
)

st.page_link(
    "pages/campagne.py",
    label="📊 Campagne",
    help="Camapgne annuelle"
)
