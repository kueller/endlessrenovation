import datetime

from flask import Blueprint, request, jsonify, abort
from flask_expects_json import expects_json

from api.sylvia.beatleboard.request_validation import (
    BEATLEBOARD_ADD_TEMPLATE,
    BEATLEBOARD_SONG_ADD_TEMPLATE,
    BEATLEBOARD_SEARCH_SONGS_TEMPLATE,
)
from app.config import API_KEY_SYLVIA
from endrev import db
from models.beatleboard.BeatleboardScore import BeatleboardScore
from models.beatleboard.BeatleboardSong import BeatleboardSong
from models.beatleboard.BeatleboardUser import BeatleboardUser
from utils.validation import api_validate

beatleboard = Blueprint("beatleboard", __name__, url_prefix="/beatleboard")


@beatleboard.route("/score", methods=["POST"])
@api_validate(API_KEY_SYLVIA)
@expects_json(BEATLEBOARD_ADD_TEMPLATE)
def beatleboard_new_entry():
    params = request.get_json()

    if len(params.get("instruments")) == 0:
        abort(400, "At least one instrument score must be submitted.")

    user = BeatleboardUser.get_by_userid(params.get("uploader-id"))
    if not user:
        user = BeatleboardUser(
            username=params.get("uploader-name"),
            display_name="",
            userid=params.get("uploader-id"),
        )
        db.session.add(user)
        db.session.commit()

    if user.username != params.get("uploader-name"):
        user.username = params.get("uploader-name")

    song = BeatleboardSong.get(params.get("song-id"))
    if not song:
        abort(400, "Invalid song ID.")

    new_score = BeatleboardScore(
        score=params.get("score"),
        song_id=params.get("song-id"),
        image_proof=params.get("proof"),
        uploader_id=user.id,
    )

    for instrument in params.get("instruments"):
        instrument_user_id = None
        if "id" in params["instruments"][instrument]:
            instrument_user = BeatleboardUser.get_by_userid(
                params["instruments"][instrument]["id"]
            )
            if not instrument_user:
                instrument_user = BeatleboardUser(
                    username=params["instruments"][instrument]["username"],
                    display_name="",
                    userid=params["instruments"][instrument]["id"],
                )
                db.session.add(instrument_user)
                db.session.commit()
            instrument_user_id = instrument_user.id

        if instrument == "gtr":
            new_score.gtr_id = instrument_user_id
            new_score.gtr_username = params["instruments"]["gtr"]["username"]
        elif instrument == "drums":
            new_score.drums_id = instrument_user_id
            new_score.drums_username = params["instruments"]["drums"]["username"]
        elif instrument == "bass":
            new_score.bass_id = instrument_user_id
            new_score.bass_username = params["instruments"]["bass"]["username"]
        elif instrument == "vox":
            new_score.vox_id = instrument_user_id
            new_score.vox_username = params["instruments"]["vox"]["username"]
        elif instrument == "harms":
            new_score.harms_id = instrument_user_id
            new_score.harms_username = params["instruments"]["harms"]["username"]

    db.session.add(new_score)
    db.session.commit()

    return jsonify({"message": "success", "id": 1}), 200


@beatleboard.route("/song", methods=["POST"])
@api_validate(API_KEY_SYLVIA)
@expects_json(BEATLEBOARD_SONG_ADD_TEMPLATE)
def beatleboard_add_song():
    params = request.get_json()

    try:
        release_date = datetime.date.fromisoformat(params.get("released"))
    except ValueError:
        abort(400)

    new_song = BeatleboardSong(
        id=params.get("id"),
        name=params.get("name"),
        album=params.get("album"),
        artist=params.get("artist"),
        released=release_date,
    )

    db.session.add(new_song)
    db.session.commit()

    return "", 200


@beatleboard.route("/songs", methods=["GET"])
@api_validate(API_KEY_SYLVIA)
@expects_json(BEATLEBOARD_SEARCH_SONGS_TEMPLATE)
def beatleboard_search_songs():
    params = request.get_json()

    song_results = BeatleboardSong.get_all_by_name(
        params.get("query"), visible_only=True
    )
    album_results = BeatleboardSong.get_all_by_album(
        params.get("query"), visible_only=True
    )

    results = list(set(song_results) | set(album_results))
    return jsonify({"results": [result.to_json() for result in results]})
