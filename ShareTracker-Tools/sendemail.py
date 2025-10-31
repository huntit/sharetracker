# Utility to send email using an SMTP server
# https://mljar.com/blog/python-send-email/
import os
import smtplib
from email.message import EmailMessage

# email_login and email_password are set in the .env file for local environment variables
# and excluded using .gitignore for GitHub
from dotenv import load_dotenv
load_dotenv()
email_login = os.getenv('email_login')
email_password = os.getenv('email_password')
email_address = "reports@huntit.com.au"
smtp_server = "mail.huntit.com.au"
smtp_port = 587

def send_email(to, subject, message):
    try:
        if email_address is None or email_password is None:
            # no email address or password
            # something is not configured properly
            print("Error sending email - did you set email address and password correctly?")
            # print length of email_address string
            print(f"Length of email address: {len(email_address)}")
            # print length of email_password string
            print(f"Length of password: {len(email_password)}")

            return False

        # create email
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = email_address
        msg['To'] = to
        msg.set_content(message)

        # send email using STARTTLS
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email_login, email_password)
        server.send_message(msg)
        server.quit()
        return True

    except Exception as e:
        print("Problem during send email")
        print(str(e))
    return False