from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_mail import Mail
from dotenv import load_dotenv
import os

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
mail = Mail()

def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config.from_object('app.config.Config')
    CORS(app, resources={r"/api/*": {"origins": os.getenv('CORS_ORIGINS', '*')}})
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)

    from app import auth, routes, web  # noqa: E402
    app.register_blueprint(auth.bp, url_prefix='/api/auth')
    app.register_blueprint(routes.bp, url_prefix='/api')
    app.register_blueprint(web.web_bp)

    return app
