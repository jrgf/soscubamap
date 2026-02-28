from flask import Blueprint

map_bp = Blueprint("map", __name__, template_folder="../../templates/map")

from . import routes  # noqa: E402,F401
