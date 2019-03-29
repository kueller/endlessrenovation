import os
import json
import os.path
import c3casemanager
from werkzeug.utils import secure_filename

PREVIEW_PATH = "/var/www/endrev/endrev/static/preview"
ERR = -1
NOTFOUND = -2
EXISTS = -3
SUCCESS = 1

def clean_filename(filename):
    return secure_filename(filename.strip().replace(' ','_'))

def authenticate_user(user_key):
    users = c3casemanager.read_user_db()
    return user_key.strip() in users

def remove_case(user_key, case):
    case = case.upper().strip()

    try:
        db = c3casemanager.read_preview_db()
    except IOError:
        return [ERR, "There was an error processing your request."]

    if case not in db:
        return [NOTFOUND, "Case number did not match any video."]

    path = db[case]

    if not os.path.isfile(path):
        return [ERR, "There was an error processing your request."]

    del db[case]

    try:
        c3.casemanager.write_preview_db(db)
    except IOError:
        return [ERR, "There was an error processing your request."]

    users = c3casemanager.read_user_db()

    if case in users[user_key]["cases"]:
        users[user_key]["cases"].remove(case)
        try:
            with open("/var/www/endrev/endrev/data/users.json", "w") as f:
                f.write(json.dumps(users, indent=4))
        except IOError:
            return [ERR, "There was an error processing your request."]

    os.remove(path)
    return [SUCCESS, "Case %s removed succesfully." % case]

def add_case(case, filename):
    case = case.upper().strip()

    try:
        db = c3casemanager.read_preview_db()
    except IOError:
        return [ERR, "There was an error processing your upload."]

    if case in db:
        if os.path.isfile(db[case]):
            os.remove(db[case])

    db[case] = "%s/%s" % (PREVIEW_PATH, filename)

    try:
        c3casemanager.write_preview_db(db)
    except IOError:
        return [ERR, "There was an error processing your upload."]

    return [SUCCESS, ""]

def upload(user_key, video, case):
    if video.filename == "":
        return [NOTFOUND, "No file specified."]

    if not video:
        return [ERR, "There was an error processing your upload."]

    filename = clean_filename(video.filename)

    path = "%s/%s" % (PREVIEW_PATH, filename)
    if os.path.isfile(path):
        return [EXISTS, "File with that name already exists on the server."]
    
    cases = c3casemanager.read_case_db()
    case_t = c3casemanager.get_case_type(case)
    if case_t in cases and case in cases[case_t]:
        cases[case_t][case]["status"] = "closed"
        c3casemanager.write_case_db(cases)
    else:
        return [ERR, "Case does not exist."]

    r = add_case(case, filename)
    if r[0] != SUCCESS: return r

    users = c3casemanager.read_user_db()
    if case in users[user_key]["cases"]:
        users[user_key]["cases"].remove(case)
        users[user_key]["completed"].append(case)
        c3casemanager.write_user_db(users)

    video.save(path)
    return [SUCCESS, filename]

    
