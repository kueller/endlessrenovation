from flask import Blueprint

from api.sylvia.beatleboard.beatleboard import beatleboard

sylvia_api = Blueprint("sylvia", __name__, url_prefix="/sylvia")
sylvia_api.register_blueprint(beatleboard)
