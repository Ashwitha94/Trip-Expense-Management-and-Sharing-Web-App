from backend.routes.auth_routes import auth_bp
from backend.routes.trip_routes import trip_bp
from backend.routes.expense_routes import expense_bp
from backend.routes.settlement_routes import settlement_bp

__all__ = ['auth_bp', 'trip_bp', 'expense_bp', 'settlement_bp']
