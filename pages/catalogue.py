"""
Page Catalogue :
Cette page affiche le catalogue complet des variétés de tomates.
"""

#Importation des bibliothèques
from pathlib import Path
import streamlit as st
import sqlite3
import pandas as pd

from services import stats_service as serv

st.title("Catalogue 🍅")

PROJECT_ROOT = Path(__file__).resolve().parents[1] 
DB_PATH = PROJECT_ROOT / "data" / "tomatocycle.db"

@st.cache_data
def load_catalogue():
    with sqlite3.connect(str(DB_PATH)) as conn:
        return pd.read_sql_query("SELECT * FROM variete LIMIT 50", conn)

df = load_catalogue()
st.dataframe(
    df,
    use_container_width=True,
    column_config={
        "image_url": st.column_config.ImageColumn(
            "Image",
            help="Photo de la variété"
        ),
    },
)
