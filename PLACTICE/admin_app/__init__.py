from flask import Flask
# from flask_migrate import Migrate
# from flask_sqlalchemy import SQLAlchemy
from shared.db import db
from shared.auth import auth_bp, login_manager
from admin_app.main import admin_bp
from jinja2 import ChoiceLoader, FileSystemLoader
import os

def admin_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.urandom(24)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # DATABASE_URL = postgres://...（postgresql://plactice_db_user:TTkrtCpERistIJ4L0IkAJICimiJXgVxn@dpg-d1kk45mmcj7s73cqll90-a/plactice_db)

    app.jinja_loader = ChoiceLoader([
        FileSystemLoader('admin_app/templates'),
        FileSystemLoader('shared/templates'),
    ])

    db.init_app(app)
    # Migrate(app,db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    
    return app