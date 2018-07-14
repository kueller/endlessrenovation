import random
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash

import os
import ermail
import c3videoupload
import c3casemanager
from c3hyphenator import setup_moby, convert_lyrics
from c3videosubmit import verify, format_email 

from hidden import hidden_pages

app = Flask(__name__)
app.url_map.strict_slashes = False
app.register_blueprint(hidden_pages)
#app.secret_key = "no"

db_list = {
        "en": "/var/www/endrev/endrev/data/mhyph.txt",
        "jp": ""
}

with open("/var/www/endrev/endrev/data/lyrics", "r") as f:
    lyrics = f.read().split('\n')

@app.route("/")
def home():
    lyric = random.choice(lyrics)
    return render_template("lyric.html", lyric=lyric.encode('utf-8'))

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
            lang = request.form["lang"]
            formatted = convert_lyrics(text, lang, use_at, db_list[lang])
            flash(formatted)
            return redirect(url_for("text_page"))
        elif "new_word" in request.form:
            subject = "NEW WORD SUBMISSION - Lyric Hyphenator"
            body = "Suggestion:\n" + request.form["suggest"]
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
                r, status = c3videoupload.remove_case(key, case)
                if r == c3videoupload.SUCCESS:
                    flash(status, "info")
                else:
                    flash(status, "error")
            if "upload" in request.form:
                if "file" in request.files:
                    r, status = c3videoupload.upload(key, request.files["file"], case)
                    if r == c3videoupload.SUCCESS:
                        url = "http://endlessrenovation.com%s" % url_for("preview_file", filename=status)
                        flash("Video uploaded succesfully at:\n%s" % url, "info")
                    else:
                        flash(status, "error")
                else:
                    flash("No file specified.", "error")
        else:
            flash("Invalid user key.", "error")

        return redirect(url_for("video_upload"))

    return render_template("upload.html")

@app.route("/rb/preview/<filename>")
def preview_file(filename):
    return send_from_directory("/var/www/endrev/endrev/static/preview/", filename)

@app.route("/rb/user/<userkey>", methods=["POST", "GET"])
def profile(userkey):
    user = c3casemanager.get_user_from_key(userkey)

    if user is None:
        return render_template("blank.html", title="Invalid User")

    cases = c3casemanager.read_case_db()
    previews = c3casemanager.read_preview_db()

    user_cases = []
    for case in user["cases"] + user["completed"]:
        data = {}
        data["case"] = case
        case_type = c3casemanager.get_case_type(case)
        if case_type == "RBPV":
            data["info"] = c3casemanager.rbpv_clean_info(case)
            if case in previews:
                filename = os.path.basename(previews[case])
                data["preview"] = url_for("preview_file", filename=filename)
                user_cases.append(data)
            else:
                data["preview"] = None
                user_cases.insert(0, data)

    if request.method == 'POST':
        case = ''
        for entry in request.form:
            if entry.startswith("RB"):
                case = entry
                break

        if case != '':
            case_type = c3casemanager.get_case_type(case)
            c3casemanager.remove_case(case, case_type, userkey)
            return redirect(url_for("profile", userkey=userkey))

    return render_template("user.html", user=user, cases=user_cases)

if __name__ == "__main__":
    app.run(host="0.0.0.0")
