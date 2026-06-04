import os
import smtplib
import ssl
from smtplib import SMTPAuthenticationError, SMTPException
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email(to_email, subject, message):
    SMTP_SERVER = os.getenv("SMTP_SERVER")
    SMTP_PORT = os.getenv("SMTP_PORT")  # Port 587 is typically used for TLS
    
    # Create the email
    msg = MIMEMultipart() 
    msg['From'] = 'itsupport.kweph@kwe.com'
    msg['To'] = to_email
    msg['Subject'] = subject

    # Email body
    body = message
    msg.attach(MIMEText(body, "html"))

    try:
        # Connect to the SMTP server without SSL/TLS
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.sendmail(msg['From'], msg['To'], msg.as_string())
    except Exception as e:
        print("Error:", e)