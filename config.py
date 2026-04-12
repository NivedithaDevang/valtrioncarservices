import os


def _default_db_uri():
    # Vercel file system is read-only except /tmp.
    if os.environ.get('VERCEL') == '1':
        return 'sqlite:////tmp/valtrion.db'
    return 'sqlite:///valtrion.db'


def _database_uri():
    uri = os.environ.get('DATABASE_URL')
    if not uri:
        return _default_db_uri()
    if uri.startswith('postgres://'):
        return uri.replace('postgres://', 'postgresql://', 1)
    return uri

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'valtrion-secret-key-2024'
    SQLALCHEMY_DATABASE_URI = _database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('EMAIL_USER')
    MAIL_PASSWORD = os.environ.get('EMAIL_PASS')
    RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID') or 'rzp_test_your_key_here'
    RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET') or 'your_secret_here'
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID') or ''
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN') or ''
    TWILIO_PHONE = os.environ.get('TWILIO_PHONE') or ''