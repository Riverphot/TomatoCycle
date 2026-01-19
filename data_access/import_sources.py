"""
Import / Scraping des sources

Ce fichier vise à :
- Scraper le catalogue des variétés depuis le site Jardins de Tomates
- Source principale : https://jardinsdetomates.fr/
- Catalogue : https://jardinsdetomates.fr/collection_liste/

Ce module sert à extraire les données,
puis à relier les données à la base de données..
"""

#--------------------------------------------------------------
#Importation des librairies
#--------------------------------------------------------------
import httpx #Remplace request (headers trop long)
from bs4 import BeautifulSoup
import json
from pathlib import Path
import re


#--------------------------------------------------------------
#VARIABLES 
#--------------------------------------------------------------

#Adresse du catalogue
CATALOG_URL = "https://jardinsdetomates.fr/collection_liste/"

# Header HTTP (pour ressembler à un navigateur)
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/121.0.0.0 Safari/537.36"
    )
}



#--------------------------------------------------------------
#SCRAPPING DES DONNEES SUR LE SITE
#--------------------------------------------------------------

# Endpoint AJAX (Site sous WordPress avec plugin "WooCommerce Product Table")
AJAX_URL = "https://jardinsdetomates.fr/wp-admin/admin-ajax.php"


#Fonction d'extraction du Token AJAX (nécessaire pour lire les listes de produits)
def extract_rest_nonce(soup: BeautifulSoup) -> str:
    """
    Extrait la valeur 'restNonce' depuis le HTML (présent dans un JSON de config WP).
    """
    html = str(soup)
    m = re.search(r'"restNonce"\s*:\s*"([^"]+)"', html)
    if not m:
        raise RuntimeError("restNonce introuvable dans la page.")
    return m.group(1)


#Fonction de connexion au site (Va chercher une page web et renvoie une "soupe" BeautifulSoup)
def fetch_soup(url: str) -> BeautifulSoup:
    r = httpx.get(url, headers=HEADERS, follow_redirects=True, timeout=30.0)
    r.raise_for_status()
    return BeautifulSoup(r.text, "html.parser")


#Fonctions de parsing du HTML et du AJAX (afin de ne conserver que les infos utiles sans surcharge html)
def extract_text_from_html(html_fragment: str) -> str | None:
    """Extrait le texte lisible d’un fragment HTML (ex: <a>...</a>)."""
    if not html_fragment:
        return None
    s = BeautifulSoup(html_fragment, "html.parser")
    txt = s.get_text(" ", strip=True)
    return txt or None

def first_img_src(html_fragment: str) -> str | None:
    """Récupère le src du premier <img src="..."> trouvé dans un fragment HTML."""
    if not html_fragment:
        return None
    s = BeautifulSoup(html_fragment, "html.parser")
    img = s.find("img", src=True)
    return img["src"] if img else None


#Fonction qui permet d'extraire l'identifiant produit (via wooCommerce)
def extract_product_id_from_name_html(name_html: str) -> int | None:
    if not name_html:
        return None
    s = BeautifulSoup(name_html, "html.parser")
    a = s.find("a", attrs={"data-product_id": True})
    if not a:
        return None
    try:
        return int(a["data-product_id"])
    except ValueError:
        return None


#Mapping JSON AJAX vers dictionnaire Variete
def parse_variete_from_row(row: dict) -> dict:
    """
    On extrait :
    - id_source : identifiant WooCommerce (data-product_id)
    - nom, couleur, forme, taille, précocité, descriptif, notes gustatives
    - image_url, source_url
    """
    name_html = row.get("name")

    return {
        "id_source": extract_product_id_from_name_html(name_html),
        "nom": extract_text_from_html(name_html),
        "couleur": extract_text_from_html(row.get("tax:pa_couleurs")),
        "forme": extract_text_from_html(row.get("tax:pa_formes")),
        "taille": extract_text_from_html(row.get("tax:pa_masses")),
        "precocite": extract_text_from_html(row.get("tax:pa_precocite")),
        "descriptif": extract_text_from_html(row.get("summary")),
        "notes_gustatives": extract_text_from_html(row.get("tax:pa_notes-gustatives")),
        "image_url": first_img_src(row.get("image")),
    }


#--------------------------------------------------------------
#STOCKAGE EN JSON
#--------------------------------------------------------------

#Fonction de sauvegarde des données scrappées dans un fichier json
def save_json(data: list[dict], filepath: str) -> None:
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)



#--------------------------------------------------------------
# EXPORT COMPLET DU CATALOGUE DES VARIÉTÉS EN JSON
#--------------------------------------------------------------

if __name__ == "__main__":
    #On charge notre page catalogue
    soup = fetch_soup(CATALOG_URL)

    #On trouve l'identifiant de la table HTML
    table = soup.find("table", id=True)
    table_id = table.get("id")

    #On récupére le token AJAX (nonce WordPress)
    ajax_token = extract_rest_nonce(soup)

    #Paramètres de pagination
    page_size = 200
    start = 0
    draw = 1

    #Liste Python qui contiendra les variétés
    varietes = []

    #Première requête AJAX (récupère les premières variétés et le nombre total de variétés)
    payload = {
        "action": "wcpt_load_products",
        "_ajax_nonce": ajax_token,
        "table_id": table_id,
        "draw": draw,
        "start": start,
        "length": page_size,
    }
    r = httpx.post(AJAX_URL, data=payload, headers=HEADERS, timeout=30.0)
    r.raise_for_status()
    j = r.json()

    #On récupère le nombre total de variétés disponibles sur le site
    total = int(j.get("recordsTotal", 0))
    print("total variétés:", total)

    #Traitement de la première page
    for row in j["data"]:
        varietes.append(parse_variete_from_row(row))
    start += page_size
    draw += 1
    print(f"progress: {len(varietes)}/{total}")

    #On boucle sur les pages suivantes
    while start < total:
        payload = {
            "action": "wcpt_load_products",
            "_ajax_nonce": ajax_token,
            "table_id": table_id,
            "draw": draw,
            "start": start,
            "length": page_size,
        }

        r = httpx.post(AJAX_URL, data=payload, headers=HEADERS, timeout=30.0)
        r.raise_for_status()
        j = r.json()

        for row in j["data"]:
            varietes.append(parse_variete_from_row(row))

        start += page_size
        draw += 1
        print(f"progress: {len(varietes)}/{total}")

    #Sauvegarde dans un fichier JSON
    outpath = Path("../data/varietes_all.json")
    outpath.parent.mkdir(parents=True, exist_ok=True)

    outpath.write_text(
        json.dumps(varietes, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print(f"export OK : {len(varietes)} variétés -> {outpath}")