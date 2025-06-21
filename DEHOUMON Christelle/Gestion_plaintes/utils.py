import os
from fpdf import FPDF
from models import Complaint
from datetime import datetime

def generate_pdf_report(complaints, filename="rapport_toutes_plaintes.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    # Titre
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Rapport des Plaintes Étudiantes", ln=True, align='C')
    pdf.ln(10)

    # Date actuelle
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 8, f"Généré le : {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True)
    pdf.ln(10)

    # Statistiques globales
    total_complaints = len(complaints)
    resolved = Complaint.query.filter_by(status='traité').count()
    pending = total_complaints - resolved

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"Statistiques Générales", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 8, f"Total des plaintes : {total_complaints}", ln=True)
    pdf.cell(0, 8, f"Plaintes traitées : {resolved}", ln=True)
    pdf.cell(0, 8, f"Plaintes en attente : {pending}", ln=True)
    pdf.ln(10)

    # Contenu des plaintes
    for c in complaints:
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, f"Plainte N°{c.id} - {c.complaint_type}", ln=True)
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 8, f"Nom : {c.first_name} {c.last_name}", ln=True)
        pdf.cell(0, 8, f"ID Étudiant : {c.student_id}", ln=True)
        pdf.cell(0, 8, f"Bâtiment : {c.building_number}", ln=True)
        pdf.multi_cell(0, 8, f"Description : {c.description}")  # Description complète
        pdf.ln(2)  # Ajoute un espace après la description

        # Affichage du statut
        if c.status == 'traité':
            pdf.set_text_color(0, 128, 0)  # Vert pour "traité"
        else:
            pdf.set_text_color(178, 34, 34)  # Rouge pour "non traité"
        pdf.cell(0, 8, f"Statut : {c.status}", ln=True)
        pdf.set_text_color(0, 0, 0)  # Réinitialiser la couleur du texte

        pdf.cell(0, 8, f"Date soumise : {c.date_submitted.strftime('%d/%m/%Y %H:%M')}", ln=True)
        pdf.set_line_width(0.5)
        pdf.line(pdf.get_x(), pdf.get_y(), pdf.w - pdf.get_x(), pdf.get_y())  # Ligne horizontale
        pdf.ln(10)

    output_dir = os.path.join('reports', 'pdf')
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, filename)

    pdf.output(file_path)
    return file_path