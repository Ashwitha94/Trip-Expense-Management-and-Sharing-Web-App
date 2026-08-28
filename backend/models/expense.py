from datetime import datetime
from backend.database.db import db

class Expense(db.Model):
    __tablename__ = 'expenses'

    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False, default='Other')
    paid_by_member_id = db.Column(db.Integer, db.ForeignKey('trip_members.id'), nullable=False)
    expense_date = db.Column(db.String(20), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    shares = db.relationship('ExpenseShare', backref='expense', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'trip_id': self.trip_id,
            'title': self.title,
            'amount': round(self.amount, 2),
            'category': self.category,
            'paid_by_member_id': self.paid_by_member_id,
            'paid_by_name': self.paid_by_member.name if self.paid_by_member else 'Unknown',
            'expense_date': self.expense_date,
            'notes': self.notes or '',
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'shares': [share.to_dict() for share in self.shares]
        }

class ExpenseShare(db.Model):
    __tablename__ = 'expense_shares'

    id = db.Column(db.Integer, primary_key=True)
    expense_id = db.Column(db.Integer, db.ForeignKey('expenses.id'), nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey('trip_members.id'), nullable=False)
    share_amount = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'expense_id': self.expense_id,
            'member_id': self.member_id,
            'member_name': self.member.name if self.member else 'Unknown',
            'share_amount': round(self.share_amount, 2)
        }
