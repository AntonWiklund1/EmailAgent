import pickle
import base64
import smtplib
from email.message import EmailMessage

from logger import setup_logger
from imapclient import IMAPClient
from google.auth.transport.requests import Request
from constants import HOST, USER, MAILBOX


logger = setup_logger()


def process_message(msg) -> tuple[str, str, str, str, str, str, list[str]]:

    from_email = msg["From"]
    to_email = msg["To"]
    subject = msg["Subject"]
    date = msg["Date"]

    # Extract text parts
    plain, html = None, None
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_disposition() == "attachment":
                continue
            ctype = part.get_content_type()
            if ctype == "text/plain" and plain is None:
                plain = part.get_content()
            elif ctype == "text/html" and html is None:
                html = part.get_content()
    else:
        if msg.get_content_type() == "text/plain":
            plain = msg.get_content()
        elif msg.get_content_type() == "text/html":
            html = msg.get_content()

    # Save attachments and collect filenames
    filenames = []
    for part in msg.iter_attachments():
        filename = part.get_filename()
        content = part.get_content()
        with open(filename, "wb") as f:
            f.write(content)
        logger.info("Saved attachment: %s", filename)
        filenames.append(filename)

    return from_email, to_email, subject, date, plain, html, filenames


def get_imap_client():
    logger.info("Loading token.pickle…")
    with open("token.pickle", "rb") as f:
        creds = pickle.load(f)

    if creds.expired and creds.refresh_token:
        logger.info("Token expired; refreshing…")
        creds.refresh(Request())
        logger.info("Refresh complete; new expiry=%s", creds.expiry)

    logger.info("Connecting to %s…", HOST)
    client = IMAPClient(HOST, ssl=True)
    logger.info("Authenticating via XOAUTH2 for %s", USER)
    client.oauth2_login(USER, creds.token)
    logger.info("Selecting folder %r…", MAILBOX)
    client.select_folder(MAILBOX, readonly=True)
    return client


def generate_oauth2_string(user, access_token):
    """
    Generate the base64-encoded OAuth2 authentication string for SMTP/XOAUTH2.
    """
    auth_string = f"user={user}\x01auth=Bearer {access_token}\x01\x01"
    return base64.b64encode(auth_string.encode()).decode()


def send_email(*, to_addrs, subject, body, html=None):
    """
    Send an email via Gmail SMTP using XOAUTH2.
    to_addrs: recipient or list of recipients
    subject: email subject
    body: plain-text body
    html: optional HTML body
    """
    # refresh token if needed
    with open("token.pickle", "rb") as f:
        creds = pickle.load(f)
    if creds.expired and creds.refresh_token:
        logger.info("Refreshing SMTP token…")
        creds.refresh(Request())

    access_token = creds.token
    auth_string = generate_oauth2_string(USER, access_token)

    # build the email message
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = USER
    msg["To"] = to_addrs
    msg.set_content(body)
    if html:
        msg.add_alternative(html, subtype="html")

    logger.info("Connecting to SMTP server smtp.gmail.com:587…")
    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        # authenticate with OAuth2
        smtp.docmd("AUTH", "XOAUTH2 " + auth_string)
        smtp.send_message(msg)
    logger.info("Email sent to %s", to_addrs)
