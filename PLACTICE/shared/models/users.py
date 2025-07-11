from flask_login import UserMixin
from shared.db import db
from datetime import datetime
import pytz

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(100), nullable=False)
    select1 = db.Column(db.String(40), nullable=False)
    select2 = db.Column(db.String(40), nullable=False)
    select3 = db.Column(db.String(40), nullable=False)
    select4 = db.Column(db.String(40), nullable=False)
    answer = db.Column(db.String(40), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(pytz.timezone('Asia/Tokyo')))

    # genre_id = db.Column(db.Integer, db.ForeignKey('genre.id'), nullable=False)
    unit_id = db.Column(db.Integer, db.ForeignKey('unit.id', ondelete='CASCADE'), nullable=False)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='player')


class AnswerRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

    selected_answer = db.Column(db.String(100), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)

    answered_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('Asia/Tokyo')))

    # リレーション（オプション）
    user = db.relationship('User', backref='answer_records')
    post = db.relationship('Post', backref='answer_records')


class AnswerSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    unit_id = db.Column(db.Integer, db.ForeignKey('unit.id'), nullable=False)
    started_at = db.Column(db.DateTime, nullable=False)
    ended_at = db.Column(db.DateTime, nullable=False)
    correct_count = db.Column(db.Integer, nullable=False)
    total_count = db.Column(db.Integer, nullable=False)

    user = db.relationship('User', backref='answer_sessions')
    unit = db.relationship('Unit', backref='answer_sessions')

class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15), unique=True, nullable=False)

    # posts = db.relationship('Post', backref='genre', lazy=True, cascade='all, delete')
    units = db.relationship('Unit', backref='genre', lazy=True, cascade='all, delete-orphan')

class Unit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)

    genre_id = db.Column(db.Integer, db.ForeignKey('genre.id'), nullable=False)
    posts = db.relationship('Post', backref='unit', cascade='all, delete-orphan', passive_deletes=True, lazy=True)