import pickle

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

    return from_email, to_email, subject, date, plain.strip(), html.strip(), filenames


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
