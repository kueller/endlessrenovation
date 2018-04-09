import os
import json
import os.path
from werkzeug.utils import secure_filename

PREVIEW_PATH = "/var/www/endrev/endrev/static/preview"
ERR = -1
NOTFOUND = -2
EXISTS = -3
SUCCESS = 1

def clean_filename(filename):
    return secure_filename(filename.strip().replace(' ','_'))

def authenticate_user(user_key):
    try:
        with open("/var/www/endrev/endrev/data/users.json", "r") as f:
            text = f.read()
    except IOError:
        return False

    users = json.loads(text)
    
    return user_key.strip() in users

def read_preview_db():
    with open("%s/preview.db" % PREVIEW_PATH, "r") as f:
        text = f.read()

    db = {}

    if text.strip() == "":
        return db
    
    for line in text.split('\n'):
        case, filename = line.split("::")
        db[case] = filename

    return db

def write_preview_db(db):
    entries = []
    for case in db:
        entries.append(case + "::" + db[case]) 

    text = '\n'.join(entries)

    with open("%s/preview.db" % PREVIEW_PATH, "w") as f:
        f.write(text)

def remove_case(user_key, case):
    case = case.upper().strip()

    try:
        with open("/var/www/endrev/endrev/data/users.json", "r") as f:
            text = f.read()
    except IOError:
        return ERR

    users = json.loads(text)

    if case in users[user_key]["cases"]:
        users[user_key]["cases"].remove(case)
        try:
            with open("/var/www/endrev/endrev/data/users.json", "w") as f:
                f.write(json.dumps(users, indent=4))
        except IOError:
            return ERR

    try:
        db = read_preview_db()
    except IOError:
        return ERR

    if case not in db:
        return NOTFOUND

    path = db[case]

    if not os.path.isfile(path):
        return ERR

    del db[case]

    try:
        write_preview_db(db)
    except IOError:
        return ERR

    os.remove(path)
    return SUCCESS

def add_case(case, filename):
    case = case.upper().strip()

    try:
        db = read_preview_db()
    except IOError:
        return ERR

    if case in db:
        if os.path.isfile(db[case]):
            os.remove(db[case])

    db[case] = "%s/%s" % (PREVIEW_PATH, filename)

    try:
        write_preview_db(db)
    except IOError:
        return ERR

    return SUCCESS

def upload(user_key, video, case):
    if video.filename == "":
        return NOTFOUND

    if not video:
        return ERR

    filename = clean_filename(video.filename)

    try:
        with open("/var/www/endrev/endrev/data/users.json", "r") as f:
            text = f.read()
    except IOError:
        return ERR

    users = json.loads(text)

    if case in users[user_key]["cases"]:
        users[user_key]["cases"].remove(case)
        try:
            with open("/var/www/endrev/endrev/data/users.json", "w") as f:
                f.write(json.dumps(users, indent=4))
        except IOError:
            return ERR

    path = "%s/%s" % (PREVIEW_PATH, filename)
    if os.path.isfile(path):
        return EXISTS
    
    r = add_case(case, filename)
    if r != SUCCESS: return r

    video.save(path)
    return SUCCESS

    
