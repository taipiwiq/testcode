from flask import Blueprint, render_template, request, redirect, url_for, abort
from flask_login import login_user, logout_user, login_required, LoginManager, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from shared.models.users import User
from shared.db import db
from functools import wraps

auth_bp = Blueprint('auth', __name__)
login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@auth_bp.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if User.query.filter_by(username=username).first():
            return render_template('signup.html', unique_error="そのユーザー名はすでに登録されています")
        
        role = 'admin' if User.query.count() == 0 else 'player'

        user = User(username=username, password=generate_password_hash(password, method='pbkdf2:sha256'), role=role)

        db.session.add(user)
        db.session.commit()
        return redirect('/')
    return render_template('signup.html')

@auth_bp.route('/', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user is None:
            return render_template('login.html', name_error='ユーザー名が違います')
        
        if check_password_hash(user.password, password):
            login_user(user)
            return redirect('/home')
        else:
            return render_template('login.html', pass_error='パスワードが違います')
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')

@auth_bp.route('/really', methods=['GET','POST'])
@login_required
def really():
    return render_template('really.html')

def roles_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(403)  # 未ログイン
            if current_user.role not in roles:
                abort(403)  # 権限なし
            return view_func(*args, **kwargs)
        return wrapper
    return decorator