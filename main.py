import socket
import time

from logger import setup_logger
from utils.email import process_message, get_imap_client, send_email

from imapclient import IMAPClient
from email import policy
from email.parser import BytesParser

from constants import MAILBOX, ONLY_ANSWER_TO_EMAIL


logger = setup_logger()


def idle_loop():
    client = get_imap_client()

    info = client.select_folder(MAILBOX, readonly=True)
    last_uid = info[b"UIDNEXT"] - 1
    logger.info("Initial UIDNEXT=%s → starting last_uid=%s", info[b"UIDNEXT"], last_uid)

    logger.info("Entering IDLE loop…")
    while True:
        try:
            logger.info(">> IDLE start")
            client.idle()
            notifications = client.idle_check(timeout=29 * 60)
            client.idle_done()
            logger.info("<< IDLE returned: %r", notifications)

            if any(n[1] == b"EXISTS" for n in notifications):
                logger.info("EXISTS detected; searching for UIDs > %s", last_uid)
                new_uids = client.search(["UID", f"{last_uid+1}:*"])
                logger.info("Search result: %s", new_uids)

                for uid in new_uids:
                    logger.info("Fetching UID %s…", uid)
                    data = client.fetch(uid, ["RFC822"])
                    raw = data[uid][b"RFC822"]
                    msg = BytesParser(policy=policy.default).parsebytes(raw)
                    (
                        from_email,
                        to_email,
                        subject,
                        date,
                        plain,
                        html,
                        filenames,
                    ) = process_message(msg)
                    print("\n ===== New email detected =====\n")
                    logger.info("From: %s", from_email)
                    logger.info("To: %s", to_email)
                    logger.info("Subject: %s", subject)
                    logger.info("Date: %s", date)
                    logger.info("Filenames: %s", filenames)
                    logger.info("Plain: %s", plain)
                    logger.info("html: %s", html)
                    print("============================\n")
                    exact_from_email = from_email.split()[-1].replace("<", "").replace(">", "").strip() # Extract the email address from the "From" header
                    if exact_from_email == ONLY_ANSWER_TO_EMAIL:
                        logger.info("Answering to %s", to_email)
                        send_email(
                            to_addrs=ONLY_ANSWER_TO_EMAIL,
                            subject="I have received your email",
                            body="I have received your email",
                        )
                    else:
                        logger.info("Not answering to %s", to_email)
                if new_uids:
                    last_uid = max(new_uids)
                    logger.info("Updated last_uid → %s", last_uid)

        except (socket.error, IMAPClient.Error) as e:
            logger.error("Connection dropped: %s", e, exc_info=True)
            try:
                client.logout()
            except:
                pass
            time.sleep(5)
            client = get_imap_client()
            info = client.select_folder(MAILBOX, readonly=True)
            last_uid = info[b"UIDNEXT"] - 1
            logger.info("Reconnected; reset last_uid=%s", last_uid)

        time.sleep(1)


if __name__ == "__main__":
    idle_loop()
