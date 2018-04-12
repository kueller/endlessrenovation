import random
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash

import ermail
import c3videoupload
from c3hyphenator import setup_moby, convert_lyrics
from c3videosubmit import verify, format_email 

app = Flask(__name__)
app.url_map.strict_slashes = False
app.secret_key = "no"

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
            use_at = "no-at-sign" not in request.form
            formatted = convert_lyrics(text, moby, use_at)
            flash(formatted)
            return redirect(url_for("text_page"))
        elif "new_word" in request.form:
            subject = "NEW WORD SUBMISSION"
            body = request.form["suggest"]
            ermail.send("self", subject, body)
            return redirect(url_for("text_page"))

    return render_template("hyphenator.html")

@app.route("/rb/submit", methods=["POST", "GET"])
def video_submit():
    if request.method == 'POST':
        err, status = verify(request.form)
        if err == 0:
            recipient, subject, body = format_email(request.form)
            err = ermail.send(recipient, subject, body)

            if err >= 0: 
                flash("Your submission has been processed.", "info")
            else: 
                flash("An error occured trying to process your request.", "error")
        else:
            flash(status, "error")

        return redirect(url_for("video_submit"))

    return render_template("video.html")

@app.route("/rb/upload", methods=["POST", "GET"])
def video_upload():
    if request.method == "POST":
        if c3videoupload.authenticate_user(request.form["user-key"]):
            key = request.form["user-key"]
            case = request.form["case-code"]
            if case.strip() == "":
                flash("No case code entered.", "error")
                return redirect(url_for("video_upload"))
            if "clear" in request.form:
                r = c3videoupload.remove_case(key, case)
                if r == c3videoupload.ERR:
                    flash("There was an error processing your request.", "error")
                elif r ==  c3videoupload.NOTFOUND:
                    flash("Case number did not match any video.", "error")
                elif r == c3videoupload.SUCCESS:
                    flash("Case removed succesfully.", "info")
            if "upload" in request.form:
                if "file" in request.files:
                    r = c3videoupload.upload(key, request.files["file"], case)
                    if r == c3videoupload.ERR:
                        flash("There was an error processing your upload.")
                    elif r == c3videoupload.NOTFOUND:
                        flash("No file specified.", "error")
                    elif r == c3videoupload.EXISTS:
                        flash("File with that name exists on the server already.", "error")
                    elif r == c3videoupload.SUCCESS:
                        cleanfile = c3videoupload.clean_filename(request.files["file"].filename)
                        url = "http://endlessrenovation.com%s" % url_for("preview_file", filename=cleanfile)
                        flash("Video uploaded succesfully at: %s" % url, "info")
                else:
                    flash("No file specified.", "error")
        else:
            flash("Invalid user key.", "error")

        return redirect(url_for("video_upload"))

    return render_template("upload.html")

@app.route("/rb/preview/<filename>")
def preview_file(filename):
    return send_from_directory("/var/www/endrev/endrev/static/preview/", filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0")
