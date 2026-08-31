import os
import sys

# Ensure project root directory is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from backend.config import Config
from backend.database.db import db
from backend.routes.auth_routes import auth_bp
from backend.routes.trip_routes import trip_bp
from backend.routes.expense_routes import expense_bp
from backend.routes.settlement_routes import settlement_bp

def create_app():
    frontend_dir = os.path.join(PROJECT_ROOT, 'frontend')
    app = Flask(__name__, static_folder=frontend_dir, static_url_path='')
    app.config.from_object(Config)

    # Enable CORS for all routes
    CORS(app)

    # Ensure database folder exists
    db_folder = os.path.dirname(app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', ''))
    if db_folder and not os.path.exists(db_folder):
        os.makedirs(db_folder, exist_ok=True)

    # Initialize extensions
    db.init_app(app)

    # Register API Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(trip_bp)
    app.register_blueprint(expense_bp)
    app.register_blueprint(settlement_bp)

    # Serve Frontend UI
    @app.route('/')
    def serve_index():
        return send_from_directory(frontend_dir, 'index.html')

    @app.route('/<path:path>')
    def serve_static(path):
        if os.path.exists(os.path.join(frontend_dir, path)):
            return send_from_directory(frontend_dir, path)
        # Fallback to index.html for SPA routing
        return send_from_directory(frontend_dir, 'index.html')

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'message': 'Resource or endpoint not found'}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({'message': 'An internal server error occurred'}), 500

    with app.app_context():
        db.create_all()
        # Seed demo user and sample trips automatically if missing
        from backend.models.user import User
        from backend.database.seed import seed_database
        if not User.query.filter_by(email="demo@example.com").first():
            seed_database()

    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('PORT', 5000))
    print(f"Starting Trip Expense Management Server on http://127.0.0.1:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)