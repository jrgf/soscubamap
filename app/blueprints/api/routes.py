from flask import jsonify, request, make_response
import json
import secrets
from flask_login import current_user

from app.extensions import db
from app.models.comment import Comment
from app.models.user import User
from app.models.role import Role

from app.models.post import Post
from app.models.category import Category
from . import api_bp


@api_bp.route("/health")
def health():
    return jsonify({"status": "ok"})


@api_bp.route("/categories")
def categories():
    items = Category.query.order_by(Category.id.asc()).all()
    return jsonify(
        [
            {"id": c.id, "name": c.name, "slug": c.slug, "description": c.description}
            for c in items
        ]
    )


@api_bp.route("/posts")
def posts():
    category_id = request.args.get("category_id")
    limit = request.args.get("limit")
    query = Post.query.filter_by(status="approved")
    if category_id:
        query = query.filter_by(category_id=int(category_id))

    query = query.order_by(Post.created_at.desc())
    if limit:
        try:
            query = query.limit(int(limit))
        except ValueError:
            pass

    items = query.all()
    return jsonify(
        [
            {
                "id": p.id,
                "title": p.title,
                "description": p.description,
                "latitude": float(p.latitude),
                "longitude": float(p.longitude),
                "address": p.address,
                "province": p.province,
                "municipality": p.municipality,
                "created_at": p.created_at.isoformat(),
                "anon": f"Anon-{p.author.anon_code}" if p.author and p.author.anon_code else "Anon",
                "polygon_geojson": p.polygon_geojson,
                "links": json.loads(p.links_json) if p.links_json else [],
                "verify_count": p.verify_count or 0,
                "category": {
                    "id": p.category.id,
                    "name": p.category.name,
                    "slug": p.category.slug,
                },
            }
            for p in items
        ]
    )


def _get_or_create_anon_user():
    if current_user.is_authenticated:
        return current_user
    anon_user = User(email=f"anon+{secrets.token_hex(6)}@local")
    anon_user.set_password(secrets.token_urlsafe(16))
    anon_user.ensure_anon_code()
    default_role = Role.query.filter_by(name="colaborador").first()
    if default_role:
        anon_user.roles.append(default_role)
    db.session.add(anon_user)
    db.session.flush()
    return anon_user


@api_bp.route("/posts/<int:post_id>/verify", methods=["POST"])
def verify_post(post_id):
    post = Post.query.get_or_404(post_id)
    cookie_key = f"verified_{post_id}"
    if request.cookies.get(cookie_key):
        return jsonify({"ok": False, "verify_count": post.verify_count or 0})

    post.verify_count = (post.verify_count or 0) + 1
    db.session.commit()

    resp = make_response(jsonify({"ok": True, "verify_count": post.verify_count}))
    resp.set_cookie(cookie_key, "1")
    return resp


@api_bp.route("/posts/<int:post_id>/comments", methods=["GET", "POST"])
def comments(post_id):
    post = Post.query.get_or_404(post_id)
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        body = (data.get("body") or "").strip()
        if not body:
            return jsonify({"ok": False, "error": "Comentario vacío."}), 400

        user = _get_or_create_anon_user()
        label = f"Anon-{user.anon_code}" if user and user.anon_code else "Anon"
        comment = Comment(post_id=post.id, author_id=user.id, author_label=label, body=body)
        db.session.add(comment)
        db.session.commit()

    items = (
        Comment.query.filter_by(post_id=post.id)
        .order_by(Comment.created_at.desc())
        .all()
    )
    return jsonify(
        [
            {
                "id": c.id,
                "author": c.author_label or "Anon",
                "body": c.body,
                "created_at": c.created_at.isoformat(),
                "upvotes": c.upvotes or 0,
                "downvotes": c.downvotes or 0,
                "score": (c.upvotes or 0) - (c.downvotes or 0),
            }
            for c in items
        ]
    )


@api_bp.route("/comments/<int:comment_id>/vote", methods=["POST"])
def vote_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    data = request.get_json(silent=True) or {}
    value = data.get("value")
    if value not in (1, -1):
        return jsonify({"ok": False, "error": "Voto inválido."}), 400

    cookie_key = f"comment_vote_{comment_id}"
    if request.cookies.get(cookie_key):
        return jsonify(
            {
                "ok": False,
                "upvotes": comment.upvotes or 0,
                "downvotes": comment.downvotes or 0,
                "score": (comment.upvotes or 0) - (comment.downvotes or 0),
            }
        )

    if value == 1:
        comment.upvotes = (comment.upvotes or 0) + 1
    else:
        comment.downvotes = (comment.downvotes or 0) + 1
    db.session.commit()

    resp = make_response(
        jsonify(
            {
                "ok": True,
                "upvotes": comment.upvotes or 0,
                "downvotes": comment.downvotes or 0,
                "score": (comment.upvotes or 0) - (comment.downvotes or 0),
            }
        )
    )
    resp.set_cookie(cookie_key, "1")
    return resp
