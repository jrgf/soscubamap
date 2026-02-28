from flask import render_template
from flask_login import login_required
from app.services.authz import role_required
from . import admin_bp


@admin_bp.route("/")
@login_required
@role_required("administrador")
def dashboard():
    return render_template("admin/dashboard.html")
