from flask import Blueprint

main_blueprint = Blueprint("main", __name__, template_folder="templates")

from . import views
