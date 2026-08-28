import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key_change_me')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'default_jwt_secret_key_change_me')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
    
    # SQLite Database URI
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL', 
        f"sqlite:///{os.path.join(BASE_DIR, 'database', 'trip_expense.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
