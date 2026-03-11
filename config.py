import os
from datetime import timedelta


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-change-in-production')

    # MySQL connection — update credentials as needed
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'mysql+pymysql://root:password@localhost/security_system'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    REMEMBER_COOKIE_DURATION = timedelta(days=14)
    SESSION_COOKIE_HTTPONLY   = True
    SESSION_COOKIE_SAMESITE   = 'Lax'
