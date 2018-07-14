import os
import json
import random

def read_user_db():
    try:
        with open("/var/www/endrev/endrev/data/users.json", "r") as f:
            text = f.read()
    except IOError:
        return None

    users = json.loads(text)
    return users

def write_user_db(users):
    with open("/var/www/endrev/endrev/data/users.json", "w") as f:
        f.write(json.dumps(users, indent=4))

def read_preview_db():
    with open("/var/www/endrev/endrev/static/preview/preview.db", "r") as f:
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

    with open("/var/www/endrev/endrev/static/preview/preview.db", "w") as f:
        f.write(text.strip())
        
def read_case_db():
    try:
        with open("/var/www/endrev/endrev/data/cases.json", "r") as f:
            text = f.read()
    except IOError:
        return None

    cases = json.loads(text)
    return cases

def write_case_db(cases):
    with open("/var/www/endrev/endrev/data/cases.json", "w") as f:
        f.write(json.dumps(cases, indent=4))

def get_user_from_key(secret_key):
    users = read_user_db()
    if users == None: return None

    if secret_key in users:
        return users[secret_key]

    return None

def new_case_code(case_type):
    cases = read_case_db()

    if len(cases[case_type]) > 0:
        match = True
        while match:
            caseno = random.randint(1000,9999)
            match = False
            if "%s-%d" % (case_type, caseno) in cases[case_type]:
                match = True
    else:
        caseno = random.randint(1000,9999)

    return "%s-%d" % (case_type, caseno)

def get_case_type(case):
    return case.split('-')[0]

def add_new_case(case, case_type, user_key, msgbody):
    cases = read_case_db()
    users = read_user_db()

    users[user_key]["cases"].append(case)
    cases[case_type][case] = {"assignee": user_key, "info": msgbody}

    write_user_db(users)
    write_case_db(cases)

def remove_case(case, case_type, user_key):
    cases = read_case_db()
    users = read_user_db()
    previews = read_preview_db()

    if user_key not in users:
        return

    if case not in users[user_key]["cases"] + users[user_key]["completed"]:
        return

    if case not in cases[case_type]:
        return

    if case in users[user_key]["cases"]:
        users[user_key]["cases"].remove(case)
    elif case in users[user_key]["completed"]:
        users[user_key]["completed"].remove(case)

    del cases[case_type][case]

    write_user_db(users)
    write_case_db(cases)

    if case in previews:
        if not os.path.isfile(previews[case]):
            return
        os.remove(previews[case])
        del previews[case]
        write_preview_db(previews)

def rbpv_clean_info(case):
    cases = read_case_db()
    info = cases["RBPV"][case]["info"]

    tok = info.split('\n')
    for i in range(len(tok)):
        if tok[i].startswith("CASE:"):
            tok.pop(i)
            break

    info = '\n'.join(tok)
    return info.replace('\n\n', '\n').split('\n')
