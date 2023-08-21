from flask import Blueprint

from api.sylvia.beatleboard.beatleboard import beatleboard
from api.zelda.hyphenator.hyphenator import hyphenator

sylvia_api = Blueprint("sylvia", __name__, url_prefix="/sylvia")
sylvia_api.register_blueprint(beatleboard)

zelda_api = Blueprint("zelda", __name__, url_prefix="/zelda")
zelda_api.register_blueprint(hyphenator)
