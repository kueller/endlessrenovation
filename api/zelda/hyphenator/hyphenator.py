from flask import Blueprint, request, abort, jsonify
from flask_expects_json import expects_json

from api.zelda.hyphenator.en_insert_word import load_en_db_lines, en_insert_word
from api.zelda.hyphenator.es_insert_word import load_es_db_lines, es_insert_word
from api.zelda.hyphenator.fr_insert_word import load_fr_db_lines, fr_insert_word
from api.zelda.hyphenator.request_validation import HYPHENATOR_REQUEST_VALIDATION
from app.config import API_KEY_ADMIN
from app.rb.hyphenator.c3hyphenator import setup_db
from app.rb.rb import DB_LIST
from utils.validation import api_validate

hyphenator = Blueprint("hyph", __name__, url_prefix="/hyph")


DATABASED_LANGUAGES = ("en", "fr", "es")


def _load_db_lines(lang):
    if lang == "en":
        return load_en_db_lines()
    elif lang == "fr":
        return load_fr_db_lines()
    elif lang == "es":
        return load_es_db_lines()


def _insert_word_by_lang(word: str, hyphenation: str, lang: str, overwrite: bool):
    db = setup_db(lang, DB_LIST[lang])

    if overwrite:
        if word not in db or word.lower() not in db:
            return {"word": word, "result": "not in database", "line": -1}
    else:
        if word in db or word.lower() in db:
            return {
                "word": word,
                "result": f"exists in database as {db[word]}",
                "line": -1,
            }

    db_lines = _load_db_lines(lang)

    line = -1
    try:
        if lang == "en":
            line = en_insert_word(word, hyphenation, db_lines)
        elif lang == "fr":
            line = fr_insert_word(word, hyphenation, db_lines)
        elif lang == "es":
            line = es_insert_word(word, hyphenation, db_lines)
        result = "success"
    except Exception as e:
        result = str(e)

    return {"word": word, "result": result, "line": line}


@hyphenator.route("/word", methods=["PUT"])
@api_validate(API_KEY_ADMIN)
@expects_json(HYPHENATOR_REQUEST_VALIDATION)
def hyphenator_add_word():
    params = request.get_json()

    lang = params["language"].lower().strip()
    if lang not in DATABASED_LANGUAGES:
        abort(400, "Unsupported language")

    results = []

    for word_data in params["words"]:
        result = _insert_word_by_lang(
            word=word_data["word"],
            hyphenation=word_data["hyphenation"],
            lang=lang,
            overwrite=False,
        )

        results.append(result)

    return jsonify({"results": results})


@hyphenator.route("/word", methods=["PATCH"])
@api_validate(API_KEY_ADMIN)
@expects_json(HYPHENATOR_REQUEST_VALIDATION)
def hyphenator_edit_word():
    params = request.get_json()

    lang = params["language"].lower().strip()
    if lang not in DATABASED_LANGUAGES:
        abort(400, "Unsupported language")

    results = []

    for word_data in params["words"]:
        result = _insert_word_by_lang(
            word=word_data["word"],
            hyphenation=word_data["hyphenation"],
            lang=lang,
            overwrite=True,
        )

        results.append(result)

    return jsonify({"results": results})
