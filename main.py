import socket
import time
import re
from email.utils import parsedate_to_datetime

from agent.EmailAgent import invoke_email_agent
from logger import setup_logger
from utils.email import process_message, get_imap_client, send_email

from imapclient import IMAPClient
from email import policy
from email.parser import BytesParser

from constants import MAILBOX, ONLY_ANSWER_TO_EMAIL
from utils.parse import extract_from_file


logger = setup_logger()


import asyncio

async def idle_loop():
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
                        file_urls,
                    ) = process_message(msg)
                    print("\n ===== New email detected =====\n")
                    logger.info("From: %s", from_email)
                    logger.info("To: %s", to_email)
                    logger.info("Subject: %s", subject)
                    logger.info("Date: %s", date)
                    logger.info("File URLs: %s", file_urls)
                    logger.info("Plain: %s", plain)
                    logger.info("html: %s", html)
                    print("============================\n")
                    
                    # Convert date header to datetime object
                    try:
                        parsed_date = parsedate_to_datetime(str(date))
                    except Exception as e:
                        logger.warning("Failed to parse date '%s': %s", date, e)
                        # Fallback to current date
                        import datetime
                        parsed_date = datetime.datetime.now()
                    
                    exact_from_email = from_email.split()[-1].replace("<", "").replace(">", "").strip() # Extract the email address from the "From" header
                    if exact_from_email == ONLY_ANSWER_TO_EMAIL:
                        # Combine email metadata with content
                        email_input = f"""From: {from_email}
To: {to_email}
Subject: {subject}
Date: {parsed_date.strftime("%Y-%m-%d %H:%M:%S")}

Email Body:
{plain or html or "No email body content"}"""

                        if file_urls:
                            logger.info("Extracting text from files: %s", file_urls)
                            extracted_texts = []
                            for file_url in file_urls:
                                logger.info("Processing file: %s", file_url)
                                extracted_text = extract_from_file(file_url)
                                logger.info("Extracted text: %s", extracted_text[:100])
                                extracted_texts.append(f"--- Attachment: {file_url} ---\n{extracted_text}")
                                # Save for debugging
                                with open("tmp/extracted_text.txt", "w") as f:
                                    f.write(extracted_text)
                            
                            # Combine email content with all extracted file contents
                            text = email_input + "\n\nAttachments:\n" + "\n\n".join(extracted_texts)
                        else:
                            text = email_input
                            logger.info("No files; using email content only")

                        logger.info("Combined input length: %d characters", len(text))
                        logger.info("Combined input preview: %s", text[:200] + "..." if len(text) > 200 else text)
                        logger.info("Answering to %s", to_email)
                        result = await invoke_email_agent(
                            input_text=text,
                            user_name=exact_from_email,
                            current_date=parsed_date.strftime("%Y-%m-%d"),
                            show_reasoning=True,
                        )
                        
                        if result is not None:
                            # Parse the agent response to extract subject and body
                            subject, body = parse_agent_response(result.final_output)
                            logger.info("Parsed subject: %s", subject)
                            logger.info("Parsed body: %s", body[:100] + "..." if len(body) > 100 else body)
                            
                            send_email(
                                to_addrs=ONLY_ANSWER_TO_EMAIL,
                                subject=subject,
                                body=body,
                            )
                        else:
                            logger.info("No response from agent - email processing aborted")
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
def parse_agent_response(response_text: str) -> tuple[str, str]:
    """
    Parse the agent response to extract subject and body from XML-like tags.
    Expected format: <subject>...</subject><body>...</body>
    
    Returns:
        tuple[str, str]: (subject, body) - defaults to generic values if parsing fails
    """
    if not response_text:
        return "Email Processed", "Your email has been processed."
    
    # Extract subject
    subject_match = re.search(r'<subject>(.*?)</subject>', response_text, re.DOTALL)
    subject = subject_match.group(1).strip() if subject_match else "Email Processed"
    
    # Extract body
    body_match = re.search(r'<body>(.*?)</body>', response_text, re.DOTALL)
    body = body_match.group(1).strip() if body_match else response_text
    
    return subject, body

if __name__ == "__main__":
    asyncio.run(idle_loop())
