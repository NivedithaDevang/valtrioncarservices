from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_socketio import SocketIO
from config import Config

db         = SQLAlchemy()
login_manager = LoginManager()
bcrypt     = Bcrypt()
mail       = Mail()
socketio   = SocketIO()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*", async_mode='threading')

    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    from app.routes.main import main
    from app.routes.auth import auth
    from app.routes.booking import booking
    from app.routes.admin import admin
    from app.routes.profile import profile

    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(booking)
    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(profile)

    return app