"""
Page Campagne
Cette page permet de générer une sélection annuelle de variétés de tomates
à cultiver pour une campagne donnée.

La sélection repose sur deux principes :
- Une priorité temporelle : les variétés avec les semences les plus anciennes
   sont sélectionnées en premier afin d’éviter leur perte.
- Une recherche de diversité : lorsque plusieurs variétés ont la même priorité
   (même année de semence), un arbre de décision est utilisé pour équilibrer
   les caractéristiques (couleur, forme, taille, précocité).
"""

#Importation des bibliothèques
from collections import defaultdict, Counter
import streamlit as st
import pandas as pd
import plotly.express as px


from services import db as db
from services import pdf_service as pdfserv

#-----------------------------------------
# FONCTIONS
#-----------------------------------------

#-----------------------------------------
# ARBRE DES CARACTERISTIQUES
#-----------------------------------------

# Construction d'un arbre de catégories
def construire_arbre(varietes):
    """
    arbre à 4 niveaux à partir des variétés.
    couleur
        └── forme
              └── taille
                    └── précocité
                          └── [liste de variétés]
    """

    #On crée les niveaux
    #La fonction lambda avec defautdict permet de créer un sous dictionnaire automatiquement si il n'existe pas
    arbre = defaultdict(
        lambda: defaultdict(
            lambda: defaultdict(
                lambda: defaultdict(list)
            )
        )
    )

    # On parcourt toutes les variétés
    for v in varietes:
        couleur = v["couleur"]
        forme = v["forme"]
        taille = v["taille"]
        precocite = v["precocite"]

        # On place la variété dans la bonne "branche" de l'arbre
        arbre[couleur][forme][taille][precocite].append(v)

    return arbre

#Fonction qui parcourt les feuilles de l'arbre
def parcourir_feuilles(arbre):
    for couleur, niveau_forme in arbre.items():
        for forme, niveau_taille in niveau_forme.items():
            for taille, niveau_precocite in niveau_taille.items():
                for precocite, liste_varietes in niveau_precocite.items():
                    yield couleur, forme, taille, precocite, liste_varietes


#Fonction pour afficher l'arbre
def afficher_arbre(arbre):
    for couleur, niveau_forme in arbre.items():
        st.markdown(f"### Couleur : {couleur}")

        for forme, niveau_taille in niveau_forme.items():
            st.markdown(f"- **Forme** : {forme}")

            for taille, niveau_precocite in niveau_taille.items():
                st.markdown(f"  - Taille : {taille}")

                for precocite, liste_varietes in niveau_precocite.items():
                    st.markdown(
                        f"    - Précocité : {precocite} "
                        f"({len(liste_varietes)} variétés)"
                    )



# ----------------------------------------------------------
# COMPTEURS DE DIVERSITE
# ----------------------------------------------------------

#On compte la diversité des caractéristiques
def initialiser_compteurs():
    return {
        "couleur": Counter(),
        "forme": Counter(),
        "taille": Counter(),
        "precocite": Counter(),
    }

#Mise à jour des compteurs
def mettre_a_jour_compteurs(compteurs, variete):
    compteurs["couleur"][variete["couleur"]] += 1
    compteurs["forme"][variete["forme"]] += 1
    compteurs["taille"][variete["taille"]] += 1
    compteurs["precocite"][variete["precocite"]] += 1

#Calcul d'un score de présence
def score_feuille(compteurs, couleur, forme, taille, precocite):
    """
    Score d'une feuille = "à quel point ces caractéristiques sont déjà présentes".
    Plus le score est petit, plus la feuille est intéressante pour équilibrer.
    """
    return (
        compteurs["couleur"][couleur]
        + compteurs["forme"][forme]
        + compteurs["taille"][taille]
        + compteurs["precocite"][precocite]
    )


# ----------------------------------------------------------
# SELECTION
# ----------------------------------------------------------

#Sélection des variétés
def selectionner_dans_annee(varietes_annee, nb_a_prendre, compteurs):
    selection = []
    arbre = construire_arbre(varietes_annee)

    while len(selection) < nb_a_prendre:
        meilleure_feuille = None
        meilleur_score = None

        #On cherche la feuille non vide avec le plus petit score
        for couleur, forme, taille, precocite, liste_varietes in parcourir_feuilles(arbre):
            if not liste_varietes:
                continue

            s = score_feuille(compteurs, couleur, forme, taille, precocite)
            if meilleur_score is None or s < meilleur_score:
                meilleur_score = s
                meilleure_feuille = liste_varietes

        #Sécurité (ne devrait pas arriver)
        if meilleure_feuille is None:
            break

        #On prend une variété dans la meilleure feuille
        variete = meilleure_feuille.pop()
        selection.append(variete)
        mettre_a_jour_compteurs(compteurs, variete)

    return selection


# ----------------------------------------------------------
# SELECTION COMPLETE CAMPAGNE 2026
# ----------------------------------------------------------

def selectionner_campagne(df_variete, objectif=40, annee_campagne=2026, duree_vie=6):
    """
    Remplit une sélection de variétés pour l'année de campagne.
    """
    df = df_variete.copy()

    # date_semence est du TEXT -> on convertit en int
    df["annee_semence"] = df["date_semence"].astype(int)
    df["age_semence"] = annee_campagne - df["annee_semence"]

    # On trie par année (plus ancien d'abord)
    df = df.sort_values(["annee_semence", "nom"], ascending=[True, True])

    selection = []
    compteurs = initialiser_compteurs()

    # Années présentes dans la base, triées de la plus ancienne à la plus récente
    annees = sorted(df["annee_semence"].unique())

    for annee in annees:
        if len(selection) >= objectif:
            break

        df_annee = df[df["annee_semence"] == annee]
        varietes_annee = df_annee.to_dict(orient="records")

        places_restantes = objectif - len(selection)

        # Si on peut tout prendre, on prend tout (priorité temporelle)
        if len(varietes_annee) <= places_restantes:
            for variete in varietes_annee:
                selection.append(variete)
                mettre_a_jour_compteurs(compteurs, variete)
        else:
            # Sinon, on choisit une partie avec l'arbre (diversité globale)
            selection_partielle = selectionner_dans_annee(varietes_annee, places_restantes, compteurs)
            selection.extend(selection_partielle)

    # Info "urgente" : semences dont l'âge dépasse la durée de vie
    nb_trop_vieux = int((df["age_semence"] > duree_vie).sum())
    return selection, nb_trop_vieux


#-----------------------------------------
# INTERFACE
#-----------------------------------------

st.title("Campagne 2026")

#Charger les variétés depuis la base
df_variete = db.charger_donnees()

#Paramètres
objectif = 40
annee_campagne = 2026 

#On lance la sélection
selection, nb_trop_vieux = selectionner_campagne(
    df_variete,
    objectif=objectif,
    annee_campagne=annee_campagne,
    duree_vie=6
)

#Affichage des variétés sélectionnées
st.dataframe([
    {
        "nom": v["nom"],
        "date_semence": v["date_semence"],
        "couleur": v["couleur"],
        "forme": v["forme"],
        "taille": v["taille"],
        "precocite": v["precocite"],
    }
    for v in selection
])

#Exportation en pdf
if st.button("📄 Exporter la sélection en PDF"):
    pdf_path = pdfserv.exporter_selection_pdf(selection, annee_campagne)
    st.success(f"PDF généré : {pdf_path}")


#Affichage de la répartition des couleurs
st.subheader("Répartition des couleurs (campagne)")

df_selection = pd.DataFrame(selection)
df_couleurs = (
    df_selection["couleur"]
    .value_counts()
    .reset_index()
)
df_couleurs.columns = ["couleur", "nombre"]
fig = px.pie(df_couleurs, names="couleur", values="nombre", title="Répartition des couleurs")
st.plotly_chart(fig, use_container_width=True)


#Affichage arbre
with st.expander("Afficher l'arbre"):
    varietes_candidates = df_variete.to_dict(orient="records")
    arbre = construire_arbre(varietes_candidates)
    afficher_arbre(arbre)