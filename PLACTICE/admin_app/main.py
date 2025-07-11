from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from shared.models.users import Post, User, AnswerRecord, Genre, Unit
from shared.db import db
from shared.auth import roles_required

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/home')
@login_required
@roles_required('admin')
def home():
    return render_template('home.html')

@admin_bp.route('/users')
@login_required
@roles_required('admin')
def users():
    users = User.query.all()
    return render_template('users.html', users=users)

@admin_bp.route('/update_role/<int:user_id>', methods=['POST'])
@login_required
@roles_required('admin')
def update_role(user_id):
    user = User.query.get_or_404(user_id)
    new_role = request.form.get('role')

    if user.id == current_user.id:
        return "自分自身のロールは変更できません", 403

    if user.role == 'admin' and new_role != 'admin':
        admin_count = User.query.filter_by(role='admin').count()
        if admin_count <= 1:
            return "最後の管理者のロールは変更できません", 403
        
        if user.role == 'admin' and new_role == 'player':
            return "他の管理者を変更することはできません", 403

    if new_role in ['admin', 'player']:
        user.role = new_role
        db.session.commit()
    return redirect(url_for('admin.users'))

@admin_bp.route('/genre')
@login_required
@roles_required('admin')
def genre_list():
    genres = Genre.query.all()
    return render_template('genre.html', genres=genres)

@admin_bp.route('/posts')
@login_required
@roles_required('admin')
def posts():
    posts = Post.query.all()
    return render_template('posts.html', posts=posts)

@admin_bp.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
@roles_required('admin')
def delete_user(user_id):
    user = User.query.get_or_404(user_id)

    if user.role == 'admin':
        admin_count = User.query.filter_by(role='admin').count()
        if admin_count <= 1:
            return "最後の管理者は削除できません", 403
        
    if user.id == current_user.id:
        return "自分自身は削除できません", 403
    
    if user.role == 'admin':
            return "他の管理者を削除することはできません", 403

    AnswerRecord.query.filter_by(user_id=user.id).delete()
    
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('admin.users'))

@admin_bp.route('/delete_post/<int:post_id>', methods=['POST'])
@login_required
@roles_required('admin')
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    unit = Unit.query.get_or_404(post.unit_id)
    genre_id = unit.genre.id

    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('admin.unit_home', genre_id=genre_id, unit_id=unit.id))


@admin_bp.route('/unit/<int:genre_id>', methods=['GET','POST'])
@login_required
@roles_required('admin')
def unit_list(genre_id):
    genre = Genre.query.get_or_404(genre_id)
    units = Unit.query.filter_by(genre_id=genre_id).all()

    if request.method == 'POST':
        unit_name = request.form.get('name')
        new_unit = Unit(name=unit_name, genre_id=genre.id)

        db.session.add(new_unit)
        db.session.commit()
        return redirect(url_for('admin.unit_list', genre_id=genre_id))
    return render_template('unit.html', genre=genre, units=units)

@admin_bp.route('/unit_home/<int:unit_id>/<int:genre_id>', methods=['GET','POST'])
@login_required
@roles_required('admin')
def unit_home(unit_id, genre_id):
        genre = Genre.query.get_or_404(genre_id)
        unit = Unit.query.get_or_404(unit_id)
        posts = Post.query.filter_by(unit_id=unit_id).all()
        return render_template('unit_home.html', genre=genre, unit=unit, posts=posts)

@admin_bp.route('/unit/edit/<int:genre_id>', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def unit_edit(genre_id):
    genre = Genre.query.get_or_404(genre_id)
    units = Unit.query.filter_by(genre_id=genre_id).all()

    if request.method == 'POST':
        for unit in units:
            new_name = request.form.get(f'name_{unit.id}')

            if new_name:
                unit.name = new_name

        db.session.commit()
        return redirect(url_for('admin.unit_list', genre_id=genre_id))
    return render_template('unit_update.html', genre=genre, units=units)

@admin_bp.route('/delete_unit/<int:id>', methods=['POST'])
@login_required
@roles_required('admin')
def delete_unit(id):
    unit = Unit.query.get_or_404(id)
    genre_id=unit.genre_id

    db.session.delete(unit)
    db.session.commit()
    return redirect(url_for('admin.unit_list', genre_id=genre_id))

@admin_bp.route('/create/<int:unit_id>', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def create(unit_id):
    unit = Unit.query.get_or_404(unit_id)

    if request.method == 'POST':
        question = request.form.get('question')
        select1 = request.form.get('select1')
        select2 = request.form.get('select2')
        select3 = request.form.get('select3')
        select4 = request.form.get('select4')
        answer = request.form.get('answer')

        if answer not in [select1, select2, select3, select4]:
            error = "正答は選択肢のいずれかと一致している必要があります。"
            return render_template("create.html", unit=unit, error=error,
                                    question=question, select1=select1, select2=select2,
                                    select3=select3, select4=select4, answer=answer)

    if request.method == 'POST':
        post = Post(
            question = request.form.get('question'),
            select1 = request.form.get('select1'),
            select2 = request.form.get('select2'),
            select3 = request.form.get('select3'),
            select4 = request.form.get('select4'),
            answer = request.form.get('answer'),
            unit_id=unit_id
        )
        
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('admin.unit_home', genre_id = unit.genre_id, unit_id = unit.id))
    return render_template("create.html", unit=unit)

@admin_bp.route('/<int:id>/update', methods=['GET','POST'])
@login_required
@roles_required('admin')
def update(id):
    post = Post.query.get(id)
    question = request.form.get('question')
    select1 = request.form.get('select1')
    select2 = request.form.get('select2')
    select3 = request.form.get('select3')
    select4 = request.form.get('select4')
    answer = request.form.get('answer')

    if answer not in [select1, select2, select3, select4]:
            error = "正答は選択肢のいずれかと一致している必要があります。"
            return render_template("update.html", error=error,
                                    question=question, select1=select1, select2=select2,
                                    select3=select3, select4=select4, answer=answer, post=post)

    if request.method == 'POST':
        post.question = request.form.get('question')
        post.select1 = request.form.get('select1')
        post.select2 = request.form.get('select2')
        post.select3 = request.form.get('select3')
        post.select4 = request.form.get('select4')
        post.answer = request.form.get('answer')
        db.session.commit()

        return redirect(url_for('admin.unit_home', genre_id=post.unit.genre_id, unit_id=post.unit.id))
    return render_template('update.html', post = post)

@admin_bp.route('/show-users')
@login_required
@roles_required('admin')
def show_users():
    users = User.query.all()
    return '<br>'.join([f"ID: {u.id} | ユーザー名: {u.username} | パスワード: {u.password}" for u in users])

@admin_bp.route('/genre_create', methods=['GET','POST'])
@login_required
@roles_required('admin')
def genre_create():
    if request.method == 'POST':
        genre_name = request.form.get('name')
        
        if genre_name:
            new_genre = Genre(name=genre_name)
            
            db.session.add(new_genre)
            db.session.commit()
            return redirect('/genre')
    return render_template('genre_create.html')

@admin_bp.route('/genre/edit', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def genre_edit():
    genres = Genre.query.all()

    if request.method == 'POST':
        for genre in genres:
            new_name = request.form.get(f'name_{genre.id}')

            if new_name:
                genre.name = new_name

        db.session.commit()
        return redirect('/genre')

    return render_template('genre_update.html', genres=genres)


@admin_bp.route('/delete_genre/<int:id>', methods=['POST'])
@login_required
@roles_required('admin')
def delete_genre(id):
    genre = Genre.query.get_or_404(id)

    db.session.delete(genre)
    db.session.commit()
    return redirect(url_for('admin.genre_list'))