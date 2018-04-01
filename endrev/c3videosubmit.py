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

    name = form["name-input"].strip()
    song = form["song-input"].strip()
    dl_link = form["dl-link"].strip()
    date = form["datepicker"].strip()
    comments = form["comments"].strip()

    subject = "NEW VIDEO SUBMISSION FROM: \"%s\"" % name

    body = "Request by: %s\nDownload: %s\n\n" % (name, dl_link)
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

    return [subject, body]
