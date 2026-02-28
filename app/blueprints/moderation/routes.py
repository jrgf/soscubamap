from flask import render_template, redirect, url_for, flash
from flask_login import login_required

from app.extensions import db
from app.models.post import Post
from app.services.authz import role_required
from . import moderation_bp


@moderation_bp.route("/")
@login_required
@role_required("moderador", "administrador")
def dashboard():
    pending = Post.query.filter_by(status="pending").order_by(Post.created_at.desc()).all()
    return render_template("moderation/dashboard.html", pending=pending)


@moderation_bp.route("/aprobar/<int:post_id>", methods=["POST"])
@login_required
@role_required("moderador", "administrador")
def approve(post_id):
    post = Post.query.get_or_404(post_id)
    post.status = "approved"
    db.session.commit()
    flash("Reporte aprobado.", "success")
    return redirect(url_for("moderation.dashboard"))


@moderation_bp.route("/rechazar/<int:post_id>", methods=["POST"])
@login_required
@role_required("moderador", "administrador")
def reject(post_id):
    post = Post.query.get_or_404(post_id)
    post.status = "rejected"
    db.session.commit()
    flash("Reporte rechazado.", "success")
    return redirect(url_for("moderation.dashboard"))
