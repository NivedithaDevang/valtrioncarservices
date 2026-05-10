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
    # Gmail SMTP — requires a 16-character App Password (not your regular Gmail password).
    # Steps to generate one:
    #   1. Enable 2-Step Verification on the Gmail account.
    #   2. Go to Google Account → Security → App Passwords.
    #   3. Create an app password (select "Mail" + "Other") and paste the 16-char code below
    #      or set it in the MAIL_PASSWORD environment variable.
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'valtrionbookings@gmail.com'
    # IMPORTANT: Replace the placeholder below with a real Gmail App Password (16 chars, no spaces).
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'jfqi bfcm ywgw ckgg'
    MAIL_DEFAULT_SENDER = ('Valtrion Car Services', os.environ.get('MAIL_USERNAME') or 'valtrionbookings@gmail.com')
    RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID') or 'rzp_test_SdosjjqDxSV9ZW'
    RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET') or 'RqCcMZpIZDCXDSjzkKao6wxT'
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID') or ''
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN') or ''
    TWILIO_PHONE = os.environ.get('TWILIO_PHONE') or ''
