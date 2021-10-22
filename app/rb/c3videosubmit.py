import re
import json
import random

from app.rb import c3casemanager


def list_replace(l, q, r):
    return [r if x == q else x for x in l]


def verify(form):
    if form["name-input"].strip() == "":
        return [1, "Missing name field."]
    elif form["song-input"].strip() == "":
        return [1, "Missing song info field."]
    elif form["dl-link"].strip() == "":
        return [1, "Missing download link."]
    elif form["datepicker"].strip() == "":
        return [1, "Date required."]
    elif not any([x.startswith("ck") for x in form]):
        return [1, "Need at least one instrument to record!"]

    return [0, None]


def get_all_emails():
    users = c3casemanager.read_user_db()

    # but her
    emails = []

    for user in users:
        if re.search(
            "^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$", users[user]["email"]
        ):
            emails.append(users[user]["email"])

    return emails


def decide_recipient(instruments, game_type):
    users = c3casemanager.read_user_db()
    valids = {}

    for user in users:
        if "PRO-K" in instruments and users[user]["pro_gtr_only"]:
            continue

        if (
            any(x in instruments for x in ("PRO-G", "PRO-B"))
            and users[user]["pro_key_only"]
        ):
            continue

        if (
            len([x for x in instruments if x.startswith("PRO")])
            > users[user]["num_pro"]
        ):
            continue

        if game_type != users[user]["game_type"]:
            continue

        valids[user] = users[user]

    if len(valids) == 0:
        return ["", ""]

    min_user = ""
    min_amt = 1000000

    for user in valids:
        if len(valids[user]["cases"]) < min_amt:
            min_amt = len(valids[user]["cases"])
            min_user = user

    try:
        case = c3casemanager.new_case_code("RBPV")
    except IOError:
        return ["", ""]

    return [valids[min_user]["email"], case, min_user]


def format_email(form):
    instruments = []

    if "ck-gtr" in form:
        instruments.append("G")
    if "ck-bass" in form:
        instruments.append("B")
    if "ck-drums" in form:
        instruments.append("D")
    if "ck-keys" in form:
        instruments.append("K")
    if "ck-vox" in form:
        instruments.append("V")

    all_insts = sorted(instruments) == ["B", "D", "G", "K", "V"]

    if form["pro-select"] == "keys":
        instruments = list_replace(instruments, "K", "PRO-K")
    elif form["pro-select"] == "gtr":
        instruments = list_replace(instruments, "G", "PRO-G")
    elif form["pro-select"] == "bass":
        instruments = list_replace(instruments, "B", "PRO-B")

    # recipient, case, user_key = decide_recipient(instruments, "std")
    recipients = get_all_emails()

    try:
        case = c3casemanager.new_case_code("RBPV")
    except IOError:
        return ["", "", ""]

    name = form["name-input"].strip()
    song = form["song-input"].strip()
    dl_link = form["dl-link"].strip()
    date = form["datepicker"].strip()
    comments = form["comments"].strip()

    subject = 'NEW VIDEO SUBMISSION FROM: "%s"' % name

    body = "Request by: %s\nDownload: %s\n\n" % (name, dl_link)
    body += "CASE: %s\n\n" % case
    body += "INFO:\n%s\n" % song
    body += "Vocalist: %s\n" % form["gender-select"]

    body += "Instruments: %s\n" % "/".join(instruments)

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

    data = {}
    data["requested_by"] = name
    data["download_link"] = dl_link
    data["title"] = song
    data["vocalist"] = form["gender-select"]
    data["instruments"] = "/".join(instruments)
    data["all_insts"] = all_insts
    data["venue_type"] = form["venue-select"]
    data["due_by"] = date
    data["comments"] = comments

    c3casemanager.add_new_case(case, "RBPV", c3casemanager.UNASSIGNED, body, data)
    c3casemanager.set_case_open(case)

    return [recipients, subject, body]
