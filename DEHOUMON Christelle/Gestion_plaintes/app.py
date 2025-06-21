# app.py - Application principale Flask
# Gère les routes, la logique métier, l'authentification admin, et les exports PDF

from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from models import db, Complaint
from utils import generate_pdf_report
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'bit#CS_departure&clef'

# Configuration de la base de données
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "instance", "complaints.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Création du dossier instance si inexistant
if not os.path.exists(os.path.join(basedir, "instance")):
    os.makedirs(os.path.join(basedir, "instance"))

# Initialisation de la base
db.init_app(app)

# Catégories automatiques
CATEGORIES = {
    "Électricité": ["électricité", "electricite", "courant", "lumière", "lumiere", "prise", "câble", "cable", "panne"],
    "Plomberie": ["eau", "fuite", "canalisation", "wc", "robinet", "plomberie", "douche", "lavabo",],
    "Sécurité": ["sécurité", "securite", "voleur", "verrou", "porte", "fenêtre", "fenetre"],
    "Nettoyage": ["poubelle", "sale", "nettoyage", "déchet", "dechet", "poussière", "poussiere", "ordures"],
    "Harcèlement": ["harcèlement", "harcelement", "agression", "intimidation", "menace"],
    "Internet": ["internet", "wi-fi", "bande-passante", "bug", "connexion"],
    "Materiel": ["refregirateur", "réfrégirateur","frigo", "congelateur", "congélateur", "chaise", "table", "ventilo","ventilateur","brasseur"],
    "Autres": []
}


def detect_category(description):
    """Détecte automatiquement la catégorie de la plainte en ignorant la casse et en normalisant"""
    description = description.lower()  # Convertir en minuscule pour comparaison uniforme

    # Normalisation des caractères accentués pour une meilleure correspondance
    description = description.replace('é', 'e').replace('è', 'e').replace('ê', 'e')
    description = description.replace('à', 'a').replace('â', 'a')
    description = description.replace('ç', 'c')
    description = description.replace('ù', 'u').replace('û', 'u')
    description = description.replace('î', 'i').replace('ï', 'i')
    description = description.replace('ô', 'o')

    for category, keywords in CATEGORIES.items():
        for keyword in keywords:
            if keyword in description:
                return category
    return "Autres"


@app.route('/')
def index():
    """Redirige vers l'accueil utilisateur ou admin selon connexion"""
    if session.get('admin_logged_in'):
        return redirect(url_for('admin_index'))
    return redirect(url_for('index_user'))


@app.route('/user')
def index_user():
    """Page d'accueil utilisateur"""
    if session.get('admin_logged_in'):
        return redirect(url_for('admin_index'))
    return render_template('index_user.html')


@app.route('/add', methods=['GET', 'POST'])
def add_complaint():
    """Formulaire pour ajouter une nouvelle plainte"""
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        student_id = request.form['student_id']
        building_number = request.form['building_number']
        description = request.form['description']

        complaint_type = detect_category(description)
        is_priority = complaint_type == "Harcèlement"

        new_complaint = Complaint(
            first_name=first_name,
            last_name=last_name,
            student_id=student_id,
            building_number=building_number,
            complaint_type=complaint_type,
            description=description,
            is_priority=is_priority
        )
        db.session.add(new_complaint)
        db.session.commit()

        return redirect(url_for('index_user'))

    return render_template('add_complaint.html')


@app.route('/track', methods=['GET', 'POST'])
def track_complaint():
    """Permet à un étudiant de retrouver ses plaintes par son ID"""
    complaints = []
    error = None
    if request.method == 'POST':
        student_id = request.form['student_id']
        complaints = Complaint.query.filter_by(student_id=student_id).all()
        if not complaints:
            error = "Aucune plainte trouvée."
    return render_template('track_complaint.html', complaints=complaints, error=error)


ADMIN_PASSWORD = 'cs27conception'


@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    """Connexion administrateur simple avec mot de passe statique"""
    if request.method == 'POST':
        password = request.form['password']
        if password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_index'))
        else:
            flash("Mot de passe incorrect")
    return render_template('login.html')


@app.route('/admin/logout')
def logout():
    """Déconnecter l'administrateur"""
    session.pop('admin_logged_in', None)
    return redirect(url_for('index_user'))


@app.route('/admin')
def admin_index():
    """Accueil administrateur"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))
    return render_template('admin_index.html')


@app.route('/admin/dashboard')
def admin_dashboard():
    """Tableau de bord admin : statistiques globales"""
    if not session.get('admin_logged_in'):
        flash("Accès refusé.")
        return redirect(url_for('login'))

    total = Complaint.query.count()
    resolved = Complaint.query.filter_by(status='traité').count()
    pending = total - resolved

    # Tri par nombre de plaintes décroissant (seulement les non traitées)

    by_type = db.session.query(Complaint.complaint_type, db.func.count(Complaint.id)) \
        .filter(Complaint.status != 'traité') \
        .group_by(Complaint.complaint_type) \
        .order_by(db.func.count(Complaint.id).desc()).all()

    by_building = db.session.query(Complaint.building_number, db.func.count(Complaint.id)) \
        .filter(Complaint.status != 'traité') \
        .group_by(Complaint.building_number) \
        .order_by(db.func.count(Complaint.id).desc()).all()

    return render_template('admin_dashboard.html',
                           total=total,
                           resolved=resolved,
                           pending=pending,
                           by_type=by_type,
                           by_building=by_building)


@app.route('/admin/filter/<status>')
def filter_complaints_by_status(status):
    """Affiche les plaintes selon leur statut (traité / non traité)"""
    if not session.get('admin_logged_in'):
        flash("Accès refusé.")
        return redirect(url_for('login'))

    complaints = Complaint.query.filter_by(status=status).all()

    # Redirection vers une nouvelle page qui affichera ces plaintes filtrées
    return render_template('filtered_complaints.html', complaints=complaints, status=status)


@app.route('/admin/categories')
def view_categories():
    """Affiche le panneau de choix des catégories"""
    if not session.get('admin_logged_in'):
        flash("Accès refusé.")
        return redirect(url_for('login'))

    # Obtenir toutes les catégories avec le nombre de plaintes
    categories = db.session.query(Complaint.complaint_type, db.func.count(Complaint.id)) \
        .group_by(Complaint.complaint_type) \
        .order_by(db.func.count(Complaint.id).desc()).all()

    return render_template('categories_panel.html', categories=categories)


@app.route('/admin/filter/category/<category>')
def filter_complaints_by_category(category):
    """Affiche les plaintes d'une catégorie spécifique"""
    if not session.get('admin_logged_in'):
        flash("Accès refusé.")
        return redirect(url_for('login'))

    complaints = Complaint.query.filter_by(complaint_type=category).all()

    return render_template('filtered_complaints.html', complaints=complaints, status=f"catégorie {category}")


@app.route('/admin/view')
def view_complaints():
    """Liste paginée de toutes les plaintes (interface admin)"""
    if not session.get('admin_logged_in'):
        flash("Accès refusé.")
        return redirect(url_for('login'))

    page = request.args.get('page', 1, type=int)
    complaints = Complaint.query.paginate(page=page, per_page=10)
    return render_template('view_complaints.html', complaints=complaints)


@app.route('/admin/mark_as_done/<int:complaint_id>')
def mark_as_done(complaint_id):
    """Marquer une plainte comme traitée"""
    if not session.get('admin_logged_in'):
        flash("Accès refusé.")
        return redirect(url_for('login'))

    complaint = Complaint.query.get_or_404(complaint_id)
    complaint.status = 'traité'
    db.session.commit()
    return redirect(url_for('view_complaints'))


@app.route('/admin/change_status/<int:complaint_id>', methods=['GET', 'POST'])
def change_status(complaint_id):
    """Modifier uniquement le statut d'une plainte"""
    if not session.get('admin_logged_in'):
        flash("Accès refusé.")
        return redirect(url_for('login'))

    complaint = Complaint.query.get_or_404(complaint_id)

    if request.method == 'POST':
        complaint.status = request.form['status']
        db.session.commit()
        flash("Statut mis à jour.")
        return redirect(url_for('view_complaints'))

    return render_template('change_status.html', complaint=complaint)


@app.route('/admin/export/pdf/all')
def export_all_complaints_pdf():
    """Exporter toutes les plaintes en PDF"""
    if not session.get('admin_logged_in'):
        flash("Accès refusé.")
        return redirect(url_for('login'))

    complaints = Complaint.query.all()
    file_path = generate_pdf_report(complaints, filename="rapport_toutes_plaintes.pdf")
    return send_file(file_path, as_attachment=True)


@app.route('/admin/export/pdf/<int:complaint_id>')
def export_one_complaint_pdf(complaint_id):
    """Exporter une seule plainte en PDF"""
    if not session.get('admin_logged_in'):
        flash("Accès refusé.")
        return redirect(url_for('login'))

    complaint = Complaint.query.get_or_404(complaint_id)
    file_path = generate_pdf_report([complaint], filename=f"plainte_{complaint.id}.pdf")
    return send_file(file_path, as_attachment=True)


@app.context_processor
def inject_current_year():
    return {'current_year': datetime.now().year}


# Lancement de l'app Flask
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Recrée les tables avec le schéma actuel
    app.run(debug=True, host='0.0.0.0')
