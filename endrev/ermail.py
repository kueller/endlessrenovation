import email
import smtplib
import hashlib

from email.MIMEMultipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header

import mailinfo

HASHFILE = "/var/www/endrev/endrev/data/mail.hash"

def send(recipient, subject, body):
    if recipient == "self":
        recipient = mailinfo.ADMIN

    intro = ("This is a message from the Task Request Automated Network "
            "System.")

    body = "%s\n\n%s" % (intro, body)

    # Simple message format for hashing
    msg = "%s\n\n%s" % (subject, body)
    hash = hashlib.md5(msg.encode('utf-8')).hexdigest()

    try:
        with open(HASHFILE, 'r') as f:
            hashlist = [line.strip() for line in f.read().split('\n')]
    except IOError:
        return -1 

    if hash in hashlist: return 1
    hashlist.append(hash)

    msg = MIMEText(body, 'plain', 'utf-8')
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = mailinfo.USERNAME
    msg['To'] = recipient

    try:
        mail = smtplib.SMTP_SSL(mailinfo.SERVER, mailinfo.PORT)
        mail.ehlo()
        mail.login(mailinfo.USERNAME, mailinfo.PASSWORD)
        mail.sendmail(mailinfo.USERNAME, recipient, msg.as_string())
        mail.quit()
    except email.errors.MessageError:
        print("Message Error")
        return -1
    except smtplib.SMTPRecipientsRefused:
        print("SMTP Error")
        return -1

    try: 
        with open(HASHFILE, 'w') as f:
            f.write('\n'.join(hashlist))
    except IOError:
        return 1

    return 0
