import random

from flask import Blueprint, render_template

from app.config import ANTLERS_LYRICS_FILE

home = Blueprint("home", __name__)

with open(ANTLERS_LYRICS_FILE, "r", encoding="utf-8") as f:
    lyrics = f.read().split("\n")


@home.route("/")
def landing():
    lyric = random.choice(lyrics)
    return render_template("lyric.html", lyric=lyric)


@home.route("/sort")
def antlers_sort():
    return render_template("sort.html")


@home.route("/lego")
def lego():
    return render_template("lego.html")
