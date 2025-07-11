from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from shared.db import db
from shared.models import users 
from shared.auth import auth_bp, login_manager
from quiz_app.main import quiz_bp
from jinja2 import ChoiceLoader, FileSystemLoader
import os

def quiz_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.urandom(24)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


    app.jinja_loader = ChoiceLoader([
        FileSystemLoader('quiz_app/templates'),
        FileSystemLoader('shared/templates'),
    ])

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    app.register_blueprint(auth_bp)
    app.register_blueprint(quiz_bp)

    return app