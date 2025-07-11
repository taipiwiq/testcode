from flask import Blueprint, render_template, request, redirect, url_for, session
from flask_login import login_required, current_user
from shared.models.users import User, Post, Genre,AnswerRecord, AnswerSession, Unit
from shared.db import db
from datetime import datetime

quiz_bp = Blueprint('quiz', __name__)


@quiz_bp.route('/home')
@login_required
def home():
    genres = Genre.query.all()
    return render_template('home.html', genres=genres, user=current_user)

# quiz.py または quiz_bp の中
@quiz_bp.route('/unit/<int:genre_id>')
@login_required
def unit(genre_id):
    genre = Genre.query.get_or_404(genre_id)
    units = Unit.query.filter_by(genre_id=genre_id).all()

    unit_post_map = {}
    for unit in units:
        first_post = Post.query.filter_by(unit_id=unit.id).order_by(Post.id.asc()).first()

        if first_post:
            unit_post_map[unit.id] = first_post.id

    return render_template('unit.html', genre=genre, units=units, unit_post_map=unit_post_map)

@quiz_bp.route('/quiz/<int:unit_id>/<int:genre_id>/<int:post_id>')
@login_required
def quiz(unit_id, genre_id,post_id):
    genre = Genre.query.get_or_404(genre_id)
    unit = Unit.query.get_or_404(unit_id)
    post= Post.query.get_or_404(post_id)

    all_posts = Post.query.filter_by(unit_id=unit_id).order_by(Post.id.asc()).all()
    total = len(all_posts)
    current_number = next((i + 1 for i, p in enumerate(all_posts) if p.id == post.id), 0)

    if current_number == 1:
        session['start_time'] = datetime.utcnow().isoformat()
        session['unit_id'] = unit_id

    return render_template('quiz.html', post=post, genre=genre, unit=unit, total=total, current_number=current_number)


@quiz_bp.route('/answer/<int:post_id>', methods=['POST'])
@login_required
def answer(post_id):
    selected = request.form['selected']
    post = Post.query.get_or_404(post_id)
    is_correct = (selected == post.answer)

    # 解答記録
    record = AnswerRecord(
        user_id=current_user.id,
        post_id=post.id,
        selected_answer=selected,
        is_correct=is_correct
    )

    db.session.add(record)
    db.session.commit()

    # 次の問題（同ジャンルに限定）
    next_post = Post.query.filter(Post.unit_id == post.unit_id, Post.id > post.id).order_by(Post.id.asc()).first()

    if next_post:
        return redirect(url_for('quiz.quiz', unit_id=post.unit_id, genre_id=post.unit.genre_id, post_id=next_post.id))
    else:
        return redirect(url_for('quiz.result',unit_id=post.unit_id))  # 最後ならマイページなど

@quiz_bp.route('/result_unit/<int:unit_id>')
@login_required
def result(unit_id):
    unit = Unit.query.get_or_404(unit_id)
    posts = Post.query.filter_by(unit_id=unit.id).all()
    post_ids = [p.id for p in posts]

    # 回答記録を取得
    records = AnswerRecord.query.filter(
        AnswerRecord.user_id == current_user.id,
        AnswerRecord.post_id.in_(post_ids)
    ).order_by(AnswerRecord.answered_at.desc()).limit(len(post_ids)).all()

    # 正答数
    correct = sum(1 for r in records if r.is_correct)
    total = len(records)

    # 間違えた問題のみ抽出
    incorrect_records = [r for r in records if not r.is_correct]

    # 時間計測
    start_time = session.get('start_time')
    elapsed = None

    if start_time:
        start = datetime.fromisoformat(start_time)
        end = datetime.utcnow()
        elapsed = datetime.utcnow() - start

        new_session = AnswerSession(
            user_id=current_user.id,
            unit_id=unit.id,
            started_at=start,
            ended_at=end,
            correct_count=correct,
            total_count=total
        )
        db.session.add(new_session)
        db.session.commit()

        session.pop('start_time', None)
        session.pop('unit_id', None)

    return render_template('result.html',
                        unit=unit, records=records,
                        total=total, correct=correct,
                        incorrect_records=incorrect_records,
                        elapsed=elapsed)

@quiz_bp.route('/history')
@login_required
def history():
    sessions = AnswerSession.query.filter_by(user_id=current_user.id).order_by(AnswerSession.started_at.desc()).all()
    return render_template('history.html', sessions=sessions)
