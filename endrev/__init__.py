import random
from flask import Flask, render_template, request, redirect, url_for

import ermail
from c3hyphenator import setup_moby, convert_lyrics
from c3videosubmit import verify, format_email 

app = Flask(__name__)
app.url_map.strict_slashes = False

moby = setup_moby("/var/www/endrev/endrev/data/mhyph.txt")

with open("/var/www/endrev/endrev/data/lyrics", "r") as f:
    lyrics = f.read().split('\n')

@app.route("/")
def home():
    lyric = random.choice(lyrics)
    return render_template("lyric.html", lyric=lyric.encode('utf-8'))

@app.route("/tardis")
def tardis():
    return render_template("tardis.html")

@app.route("/sort")
def antlers_sort():
    return render_template("sort.html")

@app.route("/enit")
def enit():
    return render_template("enit.html")

@app.route("/lego")
def lego():
    return render_template("lego.html")

@app.route("/rb")
def rb():
    return render_template("rblanding.html")

@app.route("/rb/hyph", methods=["POST", "GET"])
def text_page():
    formatted = ''
    if request.method == 'POST':
        if "submit" in request.form:
            text = request.form["lyrics"]
            formatted = convert_lyrics(text, moby)
        elif "new_word" in request.form:
            subject = "NEW WORD SUBMISSION"
            body = request.form["suggest"]
            ermail.send(subject, body)
            redirect(url_for("text_page"))

    return render_template("hyphenator.html", new_lyrics=formatted)

@app.route("/rb/submit", methods=["POST", "GET"])
def video_submit():
    status = ''
    statcolor = "red"
    if request.method == 'POST':
        err, status = verify(request.form)
        if err == 0:
            subject, body = format_email(request.form)
            err = ermail.send(subject, body)

            if err >= 0: 
                status = "Your submission has been processed."
                statcolor = "green"
            else: 
                status = "An error occured trying to process your request."

        redirect(url_for("video_submit"))

    return render_template("video.html", status=status, statcolor=statcolor)

if __name__ == "__main__":
    app.run(host="0.0.0.0")
