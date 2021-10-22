import email
import hashlib
import smtplib
from email.header import Header
from email.mime.text import MIMEText

from app.config import (
    MAIL_ADMIN,
    MAIL_HASHFILE,
    MAIL_USERNAME,
    MAIL_SERVER,
    MAIL_PORT,
    MAIL_PASSWORD,
)


def send(recipient, subject, body):
    if recipient == "self":
        recipient = MAIL_ADMIN

    intro = "This is a message from the Task Request Automated Network " "System."

    body = "%s\n\n%s" % (intro, body)

    # Simple message format for hashing
    msg = "%s\n%s\n\n%s" % (recipient, subject, body)
    hash = hashlib.md5(msg.encode("utf-8")).hexdigest()

    try:
        with open(MAIL_HASHFILE, "r") as f:
            hashlist = [line.strip() for line in f.read().split("\n")]
    except IOError:
        return -1

    if hash in hashlist:
        return 1
    hashlist.append(hash)

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = Header(subject, "utf-8")
    msg["From"] = MAIL_USERNAME
    msg["To"] = recipient

    try:
        mail = smtplib.SMTP_SSL(MAIL_SERVER, MAIL_PORT)
        mail.ehlo()
        mail.login(MAIL_USERNAME, MAIL_PASSWORD)
        mail.sendmail(MAIL_USERNAME, recipient, msg.as_string())
        mail.quit()
    except email.errors.MessageError:
        print("Message Error")
        return -1
    except smtplib.SMTPRecipientsRefused:
        print("SMTP Error")
        return -1

    try:
        with open(MAIL_HASHFILE, "w") as f:
            f.write("\n".join(hashlist))
    except IOError:
        return 1

    return 0
