from flask import Blueprint, render_template, request, jsonify, abort
from connect_db import db as dbutil
import json

bp = Blueprint('reviews', __name__)


@bp.route('/')
@bp.route('/movies')
def list_movies():
    tag = request.args.get('tag', '').strip()
    if tag:
        # Filter by tag (comma separated) using LIKE on wrapped string
        like_val = f"%,{tag},%"
        rows = dbutil.sql_fetchall_params(
            "SELECT title, slug, excerpt, cover_image, rating, published_at, tags FROM movie_reviews "
            "WHERE tags IS NOT NULL AND CONCAT(',', REPLACE(tags, ' ', ''), ',') LIKE %s "
            "ORDER BY published_at DESC, id DESC",
            (like_val,),
        )
    else:
        rows = dbutil.sql_fetchall(
            "SELECT title, slug, excerpt, cover_image, rating, published_at, tags FROM movie_reviews ORDER BY published_at DESC, id DESC"
        )
    reviews = []
    for r in rows or []:
        item = dict(r)
        try:
            item['rating'] = float(item.get('rating') or 0)
        except Exception:
            item['rating'] = 0.0
        if item.get('published_at') is not None:
            item['published_at'] = str(item['published_at'])
        # Prepare tags list
        tags_val = item.get('tags')
        if isinstance(tags_val, str):
            item['tags_list'] = [t.strip() for t in tags_val.split(',') if t.strip()]
        else:
            item['tags_list'] = []
        reviews.append(item)
    return render_template('reviews/list.html', reviews=reviews, category='movies', selected_tag=tag)


@bp.route('/movies/<slug>')
def detail_movie(slug):
    safe_slug = slug.replace("'", "''")
    row = dbutil.sql_fetchone(f"SELECT * FROM movie_reviews WHERE slug='{safe_slug}'")
    if not row:
        abort(404)
    review = dict(row)
    try:
        review['rating'] = float(review.get('rating') or 0)
    except Exception:
        review['rating'] = 0.0
    if review.get('published_at') is not None:
        review['published_at'] = str(review['published_at'])
    if isinstance(review.get('tags'), str):
        review['tags'] = [t.strip() for t in review['tags'].split(',') if t.strip()]
    try:
        body = json.loads(review.get('body') or '[]')
        review['body'] = body if isinstance(body, list) else [str(body)]
    except Exception:
        review['body'] = [review['body']] if review.get('body') else []
    return render_template('reviews/detail.html', review=review)


# --- CRUD API ---
@bp.post('/api/reviews/movies')
def api_create_movie_review():
    data = request.get_json(silent=True) or {}
    required = ['title', 'slug', 'excerpt', 'rating', 'published_at']
    if not all(k in data for k in required):
        return jsonify({"error": "missing required fields"}), 400
    sql = (
        "INSERT INTO movie_reviews (title, slug, excerpt, cover_image, rating, tags, body, published_at) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    )
    params = (
        data.get('title'),
        data.get('slug'),
        data.get('excerpt'),
        data.get('cover_image'),
        float(data.get('rating', 0)),
        ','.join(data.get('tags', [])) if isinstance(data.get('tags'), list) else (data.get('tags') or None),
        json.dumps(data.get('body', []), ensure_ascii=False),
        data.get('published_at'),
    )
    try:
        dbutil.sql_commit(sql, params)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    return jsonify({"status": "created", "slug": data.get('slug')}), 201


@bp.patch('/api/reviews/movies/<slug>')
def api_update_movie_review(slug):
    data = request.get_json(silent=True) or {}
    fields = []
    params = []
    for key in ['title', 'excerpt', 'cover_image', 'rating', 'tags', 'body', 'published_at']:
        if key in data:
            fields.append(f"{key}=%s")
            if key == 'rating':
                params.append(float(data[key]))
            elif key == 'tags' and isinstance(data[key], list):
                params.append(','.join(data[key]))
            elif key == 'body' and isinstance(data[key], list):
                params.append(json.dumps(data[key], ensure_ascii=False))
            else:
                params.append(data[key])
    if not fields:
        return jsonify({"error": "no fields to update"}), 400
    sql = "UPDATE movie_reviews SET " + ", ".join(fields) + " WHERE slug=%s"
    params.append(slug)
    try:
        dbutil.sql_commit(sql, tuple(params))
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    return jsonify({"status": "updated"})


@bp.delete('/api/reviews/movies/<slug>')
def api_delete_movie_review(slug):
    sql = "DELETE FROM movie_reviews WHERE slug=%s"
    try:
        dbutil.sql_commit(sql, (slug,))
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    return jsonify({"status": "deleted"})
