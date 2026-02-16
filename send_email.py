import os
import smtplib
from email.message import EmailMessage
from email.utils import formataddr
from pathlib import Path
from dotenv import load_dotenv

PORT = 587
EMAIL_SERVER = "smtp.gmail.com" # port and server address for Gmail

# load and read environment variables (sender email, password, and club details)
current_dir = Path(__file__).resolve().parent if "__file__" in locals() else Path.cwd()
envars = current_dir / ".env"
load_dotenv(envars)

sender_email = os.getenv("EMAIL")
sender_password = os.getenv("PASSWORD")
email_subject = os.getenv("email_subject")
email_from = os.getenv("email_from")

def send_email(receiver_email, name):
    # create base email
    msg = EmailMessage()
    msg["Subject"] = email_subject
    msg["From"] = formataddr((email_from,f"{sender_email}"))
    msg["To"] = receiver_email

    # load outreach email template from html file
    email_template = Path("email_template.html").read_text(encoding="utf-8")
    email_body = email_template.format(name = name)

    msg.set_content(email_body, subtype = "html") # add email template to email

    with smtplib.SMTP(EMAIL_SERVER, PORT) as server: # send email with SMTP server
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
    
if __name__ == "__main__": # test
    send_email(
        receiver_email = sender_email,
        name = "Bob",
    )