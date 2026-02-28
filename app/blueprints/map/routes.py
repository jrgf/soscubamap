from decimal import Decimal
import secrets
import json
from flask import render_template, current_app, redirect, url_for, request, flash
from flask_login import current_user

from app.models.category import Category
from app.models.post import Post
from app.models.user import User
from app.models.role import Role
from app.models.site_setting import SiteSetting
from app.models.location_report import LocationReport
from app.models.post_revision import PostRevision
from app.extensions import db
from . import map_bp


@map_bp.route("/")
def dashboard():
    categories = Category.query.order_by(Category.id.asc()).all()
    posts = Post.query.filter_by(status="approved").all()
    return render_template(
        "map/dashboard.html",
        categories=categories,
        posts=posts,
        google_maps_api_key=current_app.config.get("GOOGLE_MAPS_API_KEY"),
    )


@map_bp.route("/nuevo", methods=["GET", "POST"])
def new_post():
    categories = Category.query.order_by(Category.id.asc()).all()
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        category_id = request.form.get("category_id")
        latitude = request.form.get("latitude", "").strip()
        longitude = request.form.get("longitude", "").strip()
        address = request.form.get("address", "").strip()
        province = request.form.get("province", "").strip()
        municipality = request.form.get("municipality", "").strip()
        polygon_geojson = request.form.get("polygon_geojson", "").strip()
        links = request.form.getlist("links[]")
        links = [link.strip() for link in links if link.strip()]

        if not title or not description or not category_id or not latitude or not longitude:
            flash("Completa todos los campos obligatorios.", "error")
            return redirect(url_for("map.new_post"))

        try:
            lat = Decimal(latitude)
            lng = Decimal(longitude)
        except Exception:
            flash("Latitud/longitud inválidas.", "error")
            return redirect(url_for("map.new_post"))

        author_id = None
        if current_user.is_authenticated:
            author_id = current_user.id
        else:
            # Create a one-off anonymous user for this report
            anon_user = User(email=f"anon+{secrets.token_hex(6)}@local")
            anon_user.set_password(secrets.token_urlsafe(16))
            anon_user.ensure_anon_code()
            default_role = Role.query.filter_by(name="colaborador").first()
            if default_role:
                anon_user.roles.append(default_role)
            db.session.add(anon_user)
            db.session.flush()
            author_id = anon_user.id

        moderation_setting = SiteSetting.query.filter_by(key="moderation_enabled").first()
        moderation_enabled = True
        if moderation_setting:
            moderation_enabled = moderation_setting.value == "true"

        post = Post(
            title=title,
            description=description,
            category_id=int(category_id),
            latitude=lat,
            longitude=lng,
            address=address or None,
            province=province or None,
            municipality=municipality or None,
            polygon_geojson=polygon_geojson or None,
            links_json=json.dumps(links) if links else None,
            author_id=author_id,
        )
        post.status = "pending" if moderation_enabled else "approved"
        db.session.add(post)
        db.session.commit()

        if moderation_enabled:
            flash("Reporte enviado a moderación.", "success")
        else:
            flash("Reporte publicado.", "success")
        return redirect(url_for("map.dashboard"))

    preset_lat = request.args.get("lat", "")
    preset_lng = request.args.get("lng", "")
    moderation_setting = SiteSetting.query.filter_by(key="moderation_enabled").first()
    moderation_enabled = True
    if moderation_setting:
        moderation_enabled = moderation_setting.value == "true"

    return render_template(
        "map/new_post.html",
        categories=categories,
        preset_lat=preset_lat,
        preset_lng=preset_lng,
        moderation_enabled=moderation_enabled,
    )


@map_bp.route("/donar")
def donate():
    return render_template("map/donate.html")


@map_bp.route("/acerca")
def about():
    return render_template("map/about.html")


@map_bp.route("/reportar-ubicacion/<int:post_id>", methods=["GET", "POST"])
def report_location(post_id):
    post = Post.query.get_or_404(post_id)
    submitted = False
    if request.method == "POST":
        message = request.form.get("message", "").strip()
        if not message:
            flash("Describe por qué la ubicación es incorrecta.", "error")
        else:
            db.session.add(LocationReport(post_id=post.id, message=message))
            db.session.commit()
            submitted = True
    return render_template("map/report_location.html", post=post, submitted=submitted)


@map_bp.route("/reporte/<int:post_id>/historial")
def post_history(post_id):
    post = Post.query.get_or_404(post_id)
    revisions = PostRevision.query.filter_by(post_id=post.id).order_by(PostRevision.created_at.desc()).all()
    latest_reason = None
    if revisions:
        latest_reason = revisions[0].reason
    links = []
    if post.links_json:
        try:
            links = json.loads(post.links_json)
        except Exception:
            links = []
    rev_links = {}
    for rev in revisions:
        if rev.links_json:
            try:
                rev_links[rev.id] = json.loads(rev.links_json)
            except Exception:
                rev_links[rev.id] = []
        else:
            rev_links[rev.id] = []

    return render_template(
        "map/post_history.html",
        post=post,
        revisions=revisions,
        links=links,
        rev_links=rev_links,
        latest_reason=latest_reason,
    )


@map_bp.route("/reportes")
def reports():
    selected_province = request.args.get("provincia", "").strip()
    selected_municipality = request.args.get("municipio", "").strip()

    query = Post.query.filter_by(status="approved")
    if selected_province:
        query = query.filter_by(province=selected_province)
    if selected_municipality:
        query = query.filter_by(municipality=selected_municipality)

    posts = query.order_by(Post.created_at.desc()).all()

    provinces = (
        db.session.query(Post.province)
        .filter(Post.province.isnot(None))
        .distinct()
        .order_by(Post.province.asc())
        .all()
    )
    provinces = [p[0] for p in provinces if p[0]]

    municipalities = (
        db.session.query(Post.municipality)
        .filter(Post.municipality.isnot(None))
        .distinct()
        .order_by(Post.municipality.asc())
        .all()
    )
    municipalities = [m[0] for m in municipalities if m[0]]

    return render_template(
        "map/reports.html",
        posts=posts,
        provinces=provinces,
        municipalities=municipalities,
        selected_province=selected_province,
        selected_municipality=selected_municipality,
    )
