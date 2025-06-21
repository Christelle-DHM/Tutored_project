# models.py - Définition du modèle de la base de données

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Complaint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    student_id = db.Column(db.String(50), nullable=False)
    building_number = db.Column(db.String(10), nullable=False)
    complaint_type = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='non traité')
    date_submitted = db.Column(db.DateTime, default=datetime.utcnow)
    is_priority = db.Column(db.Boolean, default=False)

    def to_dict(self):
        """Convertit la plainte en dictionnaire pour JSON ou PDF"""
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'student_id': self.student_id,
            'building_number': self.building_number,
            'complaint_type': self.complaint_type,
            'description': self.description,
            'status': self.status,
            'date_submitted': self.date_submitted.strftime('%d/%m/%Y %H:%M') if self.date_submitted else '',
            'is_priority': self.is_priority
        }

