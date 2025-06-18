import os
from dotenv import load_dotenv

load_dotenv()

MAILBOX = "INBOX"
HOST = "imap.gmail.com"
USER = os.getenv("EMAIL_USER")
ONLY_ANSWER_TO_EMAIL = os.getenv("EMAIL_USER")
