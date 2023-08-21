import os

from flask import (
    Blueprint,
    render_template,
    request,
    url_for,
    flash,
    send_from_directory,
)
from flask_login import (
    login_user,
    login_required,
    logout_user,
    UserMixin,
    current_user,
    LoginManager,
)
from werkzeug.exceptions import abort
from werkzeug.utils import redirect

from app.config import HYPH_DB_EN, HYPH_DB_FR, HYPH_DB_JP, HYPH_DB_ES
from app.rb import c3videoupload, c3casemanager
from app.rb.c3videosubmit import verify, format_email
from app.rb.hyphenator.c3hyphenator import convert_lyrics
from endrev import login_manager
from mail import ermail
from utils.url import is_safe_url

rb = Blueprint("rb", __name__, template_folder="templates/rb")

DB_LIST = {
    "en": HYPH_DB_EN,
    "fr": HYPH_DB_FR,
    "jp": HYPH_DB_JP,
    "es": HYPH_DB_ES,
}


class RBUser(UserMixin):
    def __init__(self, secret_key, user):
        self.id = secret_key
        self.user = user

    def is_active(self):
        return True

    def is_authenticated(self):
        return True


@login_manager.user_loader
def load_user(user_key):
    users = c3casemanager.read_user_db()
    if user_key not in users:
        return None
    return RBUser(user_key, users[user_key])


@rb.route("/")
def rb_landing():
    return render_template("rb/rblanding.html")


@rb.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_key = request.form["user_key"].strip()
        if c3videoupload.authenticate_user(user_key):
            user = c3casemanager.get_user_from_key(user_key)
            login_user(RBUser(user_key, user))
            next = request.args.get("next")

            if not is_safe_url(next):
                return redirect(url_for("rb"))

            return redirect(next or url_for("rb"))
        else:
            flash("Invalid key.", "error")
            return redirect(url_for("login"))

    return render_template("rb/login.html")


@rb.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("rb"))


@rb.route("/hyph", methods=["POST", "GET"])
def hyphenate(lang=None):
    lang = request.args.get("lang")

    formatted = ""
    if request.method == "POST":
        if "submit" in request.form:
            text = request.form["lyrics"]
            use_at = "no-at-sign" not in request.form
            lang = request.form["lang"]
            formatted = convert_lyrics(text, lang, use_at, DB_LIST[lang])
            flash(formatted)
            return redirect(url_for("rb.hyphenate", lang=lang))
        elif "new_word" in request.form:
            subject = "NEW WORD SUBMISSION - Lyric Hyphenator"
            body = "Suggestion:\n" + request.form["suggest"]
            ermail.send("self", subject, body)
            return redirect(url_for("rb.hyphenate", lang=None))

    return render_template("rb/hyphenator.html", selected=lang)


@rb.route("/submit", methods=["POST", "GET"])
def video_submit():
    if request.method == "POST":
        err, status = verify(request.form)
        if err == 0:
            recipients, subject, body = format_email(request.form)
            for recipient in recipients:
                err = ermail.send(recipient, subject, body)
                if err < 0:
                    break

            if err >= 0:
                flash("Your submission has been processed.", "info")
            else:
                flash("An error occured trying to process your request.", "error")
        else:
            flash(status, "error")

        return redirect(url_for("video_submit"))

    return render_template("rb/video.html")


@rb.route("/upload", methods=["POST", "GET"])
@login_required
def video_upload():
    if request.method == "POST":
        case = request.form["case-code"]
        if case.strip() == "":
            flash("No case code entered.", "error")
            return redirect(url_for("video_upload"))
        if "file" in request.files:
            r, status = c3videoupload.upload(
                current_user.id, request.files["file"], case
            )
            if r == c3videoupload.SUCCESS:
                url = "http://endlessrenovation.com%s" % url_for(
                    "preview_file", filename=status
                )
                flash("Video uploaded succesfully at:\n%s" % url, "info")
            else:
                flash(status, "error")
        else:
            flash("No file specified.", "error")

        return redirect(url_for("video_upload"))

    return render_template("rb/upload.html", user=current_user.user)


@rb.route("/preview/<filename>")
def preview_file(filename):
    return send_from_directory("/var/www/endrev/endrev/static/preview/", filename)


@rb.route("/case/<caseno>", methods=["POST", "GET"])
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

    if request.method == "POST":
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

    return render_template(
        "rb/case.html",
        user=current_user.user,
        caseno=caseno,
        case_t=case_t,
        assignee=assignee,
        case=case,
    )


@rb.route("/cases")
@login_required
def case_list():
    cases = c3casemanager.read_case_db()
    users = c3casemanager.read_user_db()

    return render_template("rb/allcases.html", cases=cases, users=users)


@rb.route("/user/<userkey>", methods=["POST", "GET"])
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

    if request.method == "POST":
        case = ""
        for entry in request.form:
            if entry.startswith("RB"):
                case = entry
                break

        if case != "":
            case_type = c3casemanager.get_case_type(case)
            return redirect(url_for("profile", userkey=userkey))

    return render_template("rb/user.html", user=user, cases=user_cases)
