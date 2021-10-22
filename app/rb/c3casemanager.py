import os
import json
import random

UNASSIGNED = "aaaa"


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
        text = f.read().strip()

    db = {}

    if text.strip() == "":
        return db

    for line in text.split("\n"):
        case, filename = line.split("::")
        db[case] = filename

    return db


def write_preview_db(db):
    entries = []
    for case in db:
        entries.append(case + "::" + db[case])

    text = "\n".join(entries)

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


def get_case_type(case):
    return case.split("-")[0]


def get_case_from_code(caseno):
    cases = read_case_db()
    case_t = get_case_type(caseno)

    if case_t not in cases:
        return None
    if caseno not in cases[case_t]:
        return None

    return cases[case_t][caseno]


def get_user_from_key(secret_key):
    users = read_user_db()
    if users == None:
        return None

    if secret_key in users:
        return users[secret_key]

    return None


def case_exists(cases, caseno):
    case_t = get_case_type(caseno)

    return case_t in cases and caseno in cases[case_t]


def new_case_code(case_type):
    cases = read_case_db()

    if len(cases[case_type]) > 0:
        match = True
        while match:
            caseno = random.randint(1000, 9999)
            match = False
            if "%s-%d" % (case_type, caseno) in cases[case_type]:
                match = True
    else:
        caseno = random.randint(1000, 9999)

    return "%s-%d" % (case_type, caseno)


def add_new_case(case, case_type, user_key, msgbody, data):
    cases = read_case_db()
    users = read_user_db()

    users[user_key]["cases"].append(case)
    baseinfo = {"assignee": user_key, "info": msgbody, "status": "open"}
    cases[case_type][case] = baseinfo.copy()
    cases[case_type][case].update(data)

    write_user_db(users)
    write_case_db(cases)


def remove_case(caseno):
    cases = read_case_db()
    users = read_user_db()
    previews = read_preview_db()

    case_t = get_case_type(caseno)

    if caseno not in cases[case_t]:
        return

    user_key = cases[case_t][caseno]["assignee"]

    if user_key not in users:
        return

    if caseno not in users[user_key]["cases"] + users[user_key]["completed"]:
        return

    if caseno in users[user_key]["cases"]:
        users[user_key]["cases"].remove(caseno)
    elif caseno in users[user_key]["completed"]:
        users[user_key]["completed"].remove(caseno)

    del cases[case_t][caseno]

    write_user_db(users)
    write_case_db(cases)

    if caseno in previews:
        if not os.path.isfile(previews[caseno]):
            return
        os.remove(previews[caseno])
        del previews[caseno]
        write_preview_db(previews)


def set_case_open(caseno):
    users = read_user_db()
    cases = read_case_db()

    case_t = get_case_type(caseno)
    if not case_exists(cases, caseno):
        return

    if cases[case_t][caseno]["status"] != "closed":
        return

    assignee = cases[case_t][caseno]["assignee"]
    if assignee not in users:
        return

    cases[case_t][caseno]["status"] = "open"

    if caseno in users[assignee]["completed"]:
        users[assignee]["completed"].remove(caseno)
    else:
        return

    users[assignee]["cases"].append(caseno)

    write_user_db(users)
    write_case_db(cases)


def set_case_closed(caseno):
    users = read_user_db()
    cases = read_case_db()

    case_t = get_case_type(caseno)
    if not case_exists(cases, caseno):
        return

    if cases[case_t][caseno]["status"] != "open":
        return

    assignee = cases[case_t][caseno]["assignee"]
    if assignee not in users:
        return

    cases[case_t][caseno]["status"] = "closed"

    if caseno in users[assignee]["cases"]:
        users[assignee]["cases"].remove(caseno)
        users[assignee]["completed"].append(caseno)
    else:
        return

    write_user_db(users)
    write_case_db(cases)


def reassign_case(caseno, new_user_key):
    users = read_user_db()
    cases = read_case_db()

    if new_user_key not in users:
        return

    case_t = get_case_type(caseno)
    if not case_exists(cases, caseno):
        return

    assignee = cases[case_t][caseno]["assignee"]

    if assignee == new_user_key:
        return

    if assignee != "none":
        if assignee not in users:
            return

        if caseno in users[assignee]["cases"]:
            users[assignee]["cases"].remove(caseno)
        elif caseno in users[assignee]["completed"]:
            users[assignee]["completed"].remove(caseno)
        else:
            return

    status = cases[case_t][caseno]["status"]

    if status == "open":
        users[new_user_key]["cases"].append(caseno)
    elif status == "closed":
        users[new_user_key]["completed"].append(caseno)

    cases[case_t][caseno]["assignee"] = new_user_key

    write_user_db(users)
    write_case_db(cases)


def rbpv_clean_info(case):
    cases = read_case_db()
    info = cases["RBPV"][case]["info"]

    tok = info.split("\n")
    for i in range(len(tok)):
        if tok[i].startswith("CASE:"):
            tok.pop(i)
            break

    info = "\n".join(tok)
    return info.replace("\n\n", "\n").split("\n")
