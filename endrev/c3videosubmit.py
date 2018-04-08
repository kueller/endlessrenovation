import json
import random

def list_replace(l, q, r):
    return [r if x == q else x for x in l]

def verify(form):
    if form["name-input"].strip() == '':
        return [1, "Missing name field."]
    elif form["song-input"].strip() == '':
        return [1, "Missing song info field."]
    elif form["dl-link"].strip() == '':
        return [1, "Missing download link."]
    elif form["datepicker"].strip() == '':
        return [1, "Date required."]
    elif not any([x.startswith("ck") for x in form]):
        return [1, "Need at least one instrument to record!"]

    return [0, None]

def new_case_code():
    with open("/var/www/endrev/endrev/preview/preview.db", "r") as f:
        text = f.read()

    if text.strip() != "":
        match = True
        while match:
            caseno = random.randint(1000,9999)
            match = False
            for line in text.split('\n'):
                if line.startswith("RBPV-%d" % caseno):
                    match = True
    else:
        caseno = random.randint(1000,9999)

    return "RBPV-%d" % caseno

def decide_recipient(instruments, game_type):
    try:
        with open("/var/www/endrev/endrev/data/users.json", "r") as f:
            text = f.read()
    except IOError:
        return ["", ""]

    users = json.loads(text)
    valids = {}

    for user in users:
        print(user)
        if "PRO-K" in instruments and users[user]["pro_gtr_only"]:
            print("Error 1")
            continue

        if any(x in instruments for x in ("PRO-G", "PRO-B")) and users[user]["pro_key_only"]:
            print("Error 2")
            continue

        if len([x for x in instruments if x.startswith("PRO")]) > users[user]["num_pro"]:
            print("Error 3")
            continue

        if game_type != users[user]["game_type"]:
            print("Error 4")
            continue

        valids[user] = users[user]

    if len(valids) == 0:
        return ["", ""]

    min_user = ""
    min_amt  = 1000000

    for user in valids:
        if len(valids[user]["cases"]) < min_amt:
           min_amt = len(valids[user]["cases"])
           min_user = user

    try:
        case = new_case_code()
    except IOError:
        return ["", ""]

    users[min_user]["cases"].append(case)

    try:
        with open("/var/www/endrev/endrev/data/users.json", "w") as f:
            f.write(json.dumps(users, indent=4))
    except IOError:
        return ["", ""]

    return [valids[min_user]["email"], case]

def format_email(form):
    instruments = []

    if "ck-gtr" in form: instruments.append("G")
    if "ck-bass" in form: instruments.append("B")
    if "ck-drums" in form: instruments.append("D")
    if "ck-keys" in form: instruments.append("K")
    if "ck-vox" in form: instruments.append("V")

    all_insts = sorted(instruments) == ["B", "D", "G", "K", "V"]

    if form["pro-select"] == "keys":
        instruments = list_replace(instruments, "K", "PRO-K")
    elif form["pro-select"] == "gtr":
        instruments = list_replace(instruments, "G", "PRO-G")
    elif form["pro-select"] == "bass":
        instruments = list_replace(instruments, "B", "PRO-B")

    recipient, case = decide_recipient(instruments, "std")

    name = form["name-input"].strip()
    song = form["song-input"].strip()
    dl_link = form["dl-link"].strip()
    date = form["datepicker"].strip()
    comments = form["comments"].strip()

    subject = "NEW VIDEO SUBMISSION FROM: \"%s\"" % name

    body = "Request by: %s\nDownload: %s\n\n" % (name, dl_link)
    body += "CASE: %s\n\n" % case
    body += "INFO:\n%s\n" % song
    body += "Vocalist: %s\n" % form["gender-select"]

    body += "Instruments: %s\n" % '/'.join(instruments)

    if all_insts:
        body += "Requires ALL INSTRUMENTS MODE.\n\n"
    else:
        body += "All Instruments Mode not required.\n"
        body += "Preferred Venue Type: "
        if form["venue-select"] == "idgaf":
            body += "They don't care.\n\n"
        else:
            body += form["venue-select"] + "\n\n"

    body += "NEEDED BY: %s\n\n" % date

    body += "Additional comments:\n%s" % comments

    return [recipient, subject, body]
