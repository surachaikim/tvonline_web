from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps
from connect_db import db as dbutil
import json
import os

bp = Blueprint('admin', __name__, url_prefix='/admin')


def is_logged_in():
    return session.get('admin_logged_in') is True


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not is_logged_in():
            return redirect(url_for('admin.login', next=request.path))
        return f(*args, **kwargs)
    return wrapper


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password', '')
        expected = os.getenv('ADMIN_PASSWORD', 'admin123')
        if password == expected:
            session['admin_logged_in'] = True
            next_url = request.args.get('next') or url_for('admin.dashboard')
            return redirect(next_url)
        flash('รหัสผ่านไม่ถูกต้อง', 'danger')
    return render_template('admin/login.html')


@bp.get('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin.login'))


@bp.get('/')
@login_required
def dashboard():
    return redirect(url_for('admin.reviews_list'))


@bp.get('/reviews')
@login_required
def reviews_list():
    q = request.args.get('q', '').strip()
    page = max(int(request.args.get('page', 1) or 1), 1)
    per_page = 12
    offset = (page - 1) * per_page
    if q:
        rows = dbutil.sql_fetchall_params(
            "SELECT id, title, slug, rating, published_at FROM movie_reviews WHERE title LIKE %s OR slug LIKE %s ORDER BY published_at DESC, id DESC LIMIT %s OFFSET %s",
            (f"%{q}%", f"%{q}%", per_page, offset),
        )
        total_row = dbutil.sql_fetchone_params(
            "SELECT COUNT(*) AS c FROM movie_reviews WHERE title LIKE %s OR slug LIKE %s",
            (f"%{q}%", f"%{q}%"),
        ) or {'c': 0}
    else:
        rows = dbutil.sql_fetchall_params(
            "SELECT id, title, slug, rating, published_at FROM movie_reviews ORDER BY published_at DESC, id DESC LIMIT %s OFFSET %s",
            (per_page, offset),
        )
        total_row = dbutil.sql_fetchone("SELECT COUNT(*) AS c FROM movie_reviews") or {'c': 0}
    total = total_row.get('c', 0)
    return render_template('admin/reviews_list.html', items=rows or [], q=q, page=page, per_page=per_page, total=total)


@bp.route('/reviews/create', methods=['GET', 'POST'])
@login_required
def reviews_create():
    if request.method == 'POST':
        data = {
            'title': request.form.get('title','').strip(),
            'slug': request.form.get('slug','').strip(),
            'excerpt': request.form.get('excerpt','').strip(),
            'cover_image': request.form.get('cover_image','').strip(),
            'rating': float(request.form.get('rating') or 0),
            'tags': request.form.get('tags','').strip(),
            'body': request.form.get('body','').strip(),
            'published_at': request.form.get('published_at','').strip(),
        }
        # normalize
        tags = ','.join([t.strip() for t in data['tags'].split(',') if t.strip()]) if data['tags'] else None
        try:
            body_json = json.dumps([p.strip() for p in data['body'].split('\n') if p.strip()], ensure_ascii=False)
            sql = (
                "INSERT INTO movie_reviews (title, slug, excerpt, cover_image, rating, tags, body, published_at) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            )
            params = (
                data['title'], data['slug'], data['excerpt'], data['cover_image'] or None,
                data['rating'], tags, body_json, data['published_at']
            )
            dbutil.sql_commit(sql, params)
            flash('บันทึกเรียบร้อย', 'success')
            return redirect(url_for('admin.reviews_list'))
        except Exception as e:
            flash(f'บันทึกล้มเหลว: {e}', 'danger')
    return render_template('admin/review_form.html', item=None)


@bp.route('/reviews/<slug>/edit', methods=['GET', 'POST'])
@login_required
def reviews_edit(slug):
    item = dbutil.sql_fetchone_params("SELECT * FROM movie_reviews WHERE slug=%s", (slug,))
    if not item:
        return redirect(url_for('admin.reviews_list'))
    if request.method == 'POST':
        data = {
            'title': request.form.get('title','').strip(),
            'excerpt': request.form.get('excerpt','').strip(),
            'cover_image': request.form.get('cover_image','').strip(),
            'rating': float(request.form.get('rating') or 0),
            'tags': request.form.get('tags','').strip(),
            'body': request.form.get('body','').strip(),
            'published_at': request.form.get('published_at','').strip(),
        }
        tags = ','.join([t.strip() for t in data['tags'].split(',') if t.strip()]) if data['tags'] else None
        body_json = json.dumps([p.strip() for p in data['body'].split('\n') if p.strip()], ensure_ascii=False)
        fields = ["title=%s","excerpt=%s","cover_image=%s","rating=%s","tags=%s","body=%s","published_at=%s"]
        params = (data['title'], data['excerpt'], data['cover_image'] or None, data['rating'], tags, body_json, data['published_at'], slug)
        try:
            dbutil.sql_commit("UPDATE movie_reviews SET "+", ".join(fields)+" WHERE slug=%s", params)
            flash('แก้ไขเรียบร้อย', 'success')
            return redirect(url_for('admin.reviews_list'))
        except Exception as e:
            flash(f'แก้ไขล้มเหลว: {e}', 'danger')
    # prepare body text
    try:
        body_list = json.loads(item.get('body') or '[]')
        item['body_text'] = "\n\n".join(body_list) if isinstance(body_list, list) else str(body_list)
    except Exception:
        item['body_text'] = item.get('body') or ''
    return render_template('admin/review_form.html', item=item)


@bp.post('/reviews/<slug>/delete')
@login_required
def reviews_delete(slug):
    try:
        dbutil.sql_commit("DELETE FROM movie_reviews WHERE slug=%s", (slug,))
        flash('ลบเรียบร้อย', 'success')
    except Exception as e:
        flash(f'ลบล้มเหลว: {e}', 'danger')
    return redirect(url_for('admin.reviews_list'))


@bp.route('/import', methods=['GET', 'POST'])
@login_required
def import_json():
    preview = None
    if request.method == 'POST':
        file = request.files.get('file')
        if not file:
            flash('กรุณาเลือกไฟล์ .json', 'warning')
        else:
            try:
                payload = json.load(file)
                preview = payload if isinstance(payload, list) else [payload]
                if request.form.get('confirm') == 'yes':
                    inserted = 0
                    for item in preview:
                        try:
                            sql = (
                                "INSERT IGNORE INTO movie_reviews (title, slug, excerpt, cover_image, rating, tags, body, published_at) "
                                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                            )
                            params = (
                                item.get('title'), item.get('slug'), item.get('excerpt'), item.get('cover_image'),
                                float(item.get('rating', 0) or 0),
                                ','.join(item.get('tags', [])) if isinstance(item.get('tags'), list) else (item.get('tags') or None),
                                json.dumps(item.get('body', []), ensure_ascii=False),
                                item.get('published_at'),
                            )
                            dbutil.sql_commit(sql, params)
                            inserted += 1
                        except Exception:
                            continue
                    flash(f'นำเข้า {inserted} รายการ', 'success')
                    return redirect(url_for('admin.reviews_list'))
            except Exception as e:
                flash(f'ไฟล์ไม่ถูกต้อง: {e}', 'danger')
    return render_template('admin/import.html', preview=preview)
