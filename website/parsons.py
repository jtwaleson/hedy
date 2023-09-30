from flask import g, jsonify
from flask_babel import gettext

from .website_module import WebsiteModule, route
from hedy_content import ParsonsProblem
from typing import DefaultDict


class ParsonsModule(WebsiteModule):
    def __init__(self, parsons: DefaultDict[str, ParsonsProblem]) -> None:
        super().__init__("parsons", __name__, url_prefix="/parsons")

        self.parsons = parsons

    @route("/get-exercise/<int:level>/<int:exercise>", methods=["GET"], defaults={'keyword_lang': None})
    @route("/get-exercise/<int:level>/<int:exercise>/<keyword_lang>", methods=["GET"])
    def get_parsons_exercise(self, level, exercise, keyword_lang):
        if exercise > self.parsons[g.lang].get_highest_exercise_level(level) or exercise < 1:
            return gettext("exercise_doesnt_exist"), 400
        if keyword_lang:
            exercise = self.parsons[g.lang].get_parsons_data_for_level_exercise(level, exercise, keyword_lang)
        else:
            exercise = self.parsons[g.lang].get_parsons_data_for_level_exercise(level, exercise, g.keyword_lang)
        return jsonify(exercise), 200
