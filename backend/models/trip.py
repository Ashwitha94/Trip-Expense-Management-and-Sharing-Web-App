from datetime import datetime
from backend.database.db import db

class Trip(db.Model):
    __tablename__ = 'trips'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    destination = db.Column(db.String(150), nullable=False)
    start_date = db.Column(db.String(20), nullable=False)
    end_date = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(255), nullable=True, default='images/mountains.jpg')
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    members = db.relationship('TripMember', backref='trip', lazy=True, cascade='all, delete-orphan')
    expenses = db.relationship('Expense', backref='trip', lazy=True, cascade='all, delete-orphan')

    def to_dict(self, include_counts=False):
        data = {
            'id': self.id,
            'name': self.name,
            'destination': self.destination,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'description': self.description or '',
            'image_url': self.image_url or 'images/mountains.jpg',
            'created_by': self.created_by,
            'creator_name': self.creator.name if self.creator else 'Unknown',
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        if include_counts:
            data['members_count'] = len(self.members)
            data['expenses_count'] = len(self.expenses)
            data['total_expense_amount'] = sum(e.amount for e in self.expenses)
        return data
