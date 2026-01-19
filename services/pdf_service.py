"""
Service PDF
Génération de documents PDF (ex: fiche de campagne).
"""

#Importation des bibliothèques
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from pathlib import Path


def exporter_selection_pdf(selection, annee_campagne):
    """Génère un PDF contenant la liste des variétés sélectionnées."""
    export_dir = Path("exports")
    export_dir.mkdir(exist_ok=True)

    pdf_path = export_dir / f"campagne_{annee_campagne}.pdf"

    doc = SimpleDocTemplate(str(pdf_path), pagesize=A4)
    styles = getSampleStyleSheet()

    elements = []
    elements.append(Paragraph(f"<b>Campagne {annee_campagne} – Sélection des variétés</b>", styles["Title"]))
    elements.append(Spacer(1, 20))

    for v in selection:
        ligne = (
            f"{v['nom']} – {v['couleur']}, {v['forme']}, {v['taille']}, {v['precocite']} "
            f"(semence {v['date_semence']})"
        )
        elements.append(Paragraph(ligne, styles["Normal"]))
        elements.append(Spacer(1, 8))

    doc.build(elements)
    return pdf_path