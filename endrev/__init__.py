import random
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, abort

import os
import ermail
import c3videoupload
import c3casemanager
from c3hyphenator import setup_moby, convert_lyrics
from c3videosubmit import verify, format_email 

from urlparse import urlparse, urljoin
from hidden import hidden_pages
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user

class User(UserMixin):
    def __init__(self, secret_key, user):
        self.id = secret_key
        self.user = user

    def is_active(self):
        return True

    def is_authenticated(self):
        return True

app = Flask(__name__)
app.url_map.strict_slashes = False
app.register_blueprint(hidden_pages)
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True
#app.secret_key = "no"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

db_list = {
        "en": "/var/www/endrev/endrev/data/mhyph.txt",
        "fr": "/var/www/endrev/endrev/data/db_fr.txt",
        "jp": "/var/www/endrev/endrev/data/mhyph.txt"
}

with open("/var/www/endrev/endrev/data/lyrics", "r") as f:
    lyrics = f.read().split('\n')

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc

@login_manager.user_loader
def load_user(user_key):
    users = c3casemanager.read_user_db()
    if user_key not in users:
        return None
    return User(user_key, users[user_key])

@app.route("/")
def home():
    lyric = random.choice(lyrics)
    return render_template("lyric.html", lyric=lyric.encode('utf-8'))

@app.route("/sort")
def antlers_sort():
    return render_template("sort.html")

@app.route("/lego")
def lego():
    return render_template("lego.html")

@app.route("/rb")
def rb():
    return render_template("rblanding.html")

@app.route("/rb/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        user_key = request.form["user_key"].strip()
        if c3videoupload.authenticate_user(user_key):
            user = c3casemanager.get_user_from_key(user_key)
            login_user(User(user_key, user))
            next = request.args.get("next")

            if not is_safe_url(next):
                return redirect(url_for("rb"))

            return redirect(next or url_for("rb"))
        else:
            flash("Invalid key.", "error")
            return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/rb/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("rb"))

@app.route("/rb/hyph", methods=["POST", "GET"])
def hyphenate(lang=None):
    lang = request.args.get("lang")

    formatted = ''
    if request.method == 'POST':
        if "submit" in request.form:
            text = request.form["lyrics"]
            use_at = "no-at-sign" not in request.form
            lang = request.form["lang"]
            formatted = convert_lyrics(text, lang, use_at, db_list[lang])
            flash(formatted)
            return redirect(url_for("hyphenate", lang=lang))
        elif "new_word" in request.form:
            subject = "NEW WORD SUBMISSION - Lyric Hyphenator"
            body = "Suggestion:\n" + request.form["suggest"]
            ermail.send("self", subject, body)
            return redirect(url_for("hyphenate", lang=None))

    return render_template("hyphenator.html", selected=lang)

@app.route("/rb/submit", methods=["POST", "GET"])
def video_submit():
    if request.method == 'POST':
        return render_template("video.html")
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
@login_required
def video_upload():
    if request.method == "POST":
        case = request.form["case-code"]
        if case.strip() == "":
            flash("No case code entered.", "error")
            return redirect(url_for("video_upload"))
        if "file" in request.files:
            r, status = c3videoupload.upload(current_user.id, request.files["file"], case)
            if r == c3videoupload.SUCCESS:
                url = "http://endlessrenovation.com%s" % url_for("preview_file", filename=status)
                flash("Video uploaded succesfully at:\n%s" % url, "info")
            else:
                flash(status, "error")
        else:
            flash("No file specified.", "error")

        return redirect(url_for("video_upload"))

    return render_template("upload.html", user=current_user.user)

@app.route("/rb/preview/<filename>")
def preview_file(filename):
    return send_from_directory("/var/www/endrev/endrev/static/preview/", filename)

@app.route("/rb/case/<caseno>", methods=["POST", "GET"])
@login_required
def single_case(caseno):
    caseno = caseno.upper()
    case = c3casemanager.get_case_from_code(caseno)

    if case is None:
        abort(404)

    case_t = c3casemanager.get_case_type(caseno)
    if case["assignee"] == "":
        assignee = "None"
    else:
        assignee = c3casemanager.get_user_from_key(case["assignee"])["name"]

    if case_t == "RBPV":
        previews = c3casemanager.read_preview_db()
        if caseno in previews:
            filename = os.path.basename(previews[caseno])
            case["preview_link"] = url_for("preview_file", filename=filename)
        else:
            case["preview_link"] = None

    if request.method == 'POST':
        if "delete" in request.form:
            c3casemanager.remove_case(caseno) 
            return redirect(url_for("rb"))
        elif "reassign" in request.form:
            c3casemanager.reassign_case(caseno, current_user.id)
            return redirect(url_for("single_case", caseno=caseno))
        elif "open" in request.form:
            c3casemanager.set_case_open(caseno)
            return redirect(url_for("single_case", caseno=caseno))
        elif "close" in request.form:
            c3casemanager.set_case_closed(caseno)
            return redirect(url_for("single_case", caseno=caseno))

    return render_template("case.html", user=current_user.user, caseno=caseno, case_t=case_t, 
            assignee=assignee, case=case)

@app.route("/rb/cases")
@login_required
def case_list():
    cases = c3casemanager.read_case_db()
    users = c3casemanager.read_user_db()

    return render_template("allcases.html", cases=cases, users=users)

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
            return redirect(url_for("profile", userkey=userkey))

    return render_template("user.html", user=user, cases=user_cases)

if __name__ == "__main__":
    app.run(host="0.0.0.0")
