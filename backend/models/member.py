from datetime import datetime
from backend.database.db import db

class TripMember(db.Model):
    __tablename__ = 'trip_members'

    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    expenses_paid = db.relationship('Expense', backref='paid_by_member', lazy=True)
    expense_shares = db.relationship('ExpenseShare', backref='member', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'trip_id': self.trip_id,
            'name': self.name,
            'email': self.email or '',
            'user_id': self.user_id,
            'joined_at': self.joined_at.isoformat() if self.joined_at else None
        }
