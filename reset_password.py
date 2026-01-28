import sqlite3
from email.mime.text import MIMEText
from database import get_db_connection
import datetime
import smtplib
from flask import url_for
from dotenv import load_dotenv
import os

load_dotenv()

sender = os.getenv("EMAIL_USER")
password = os.getenv("EMAIL_PASS")


def createResetLink(email, token):
     resetLink = url_for('password_reset', token=token, _external=True)
     #Create link only if email exists
     sendResetLink(email, resetLink)

def sendResetLink(email, resetLink):
     subject = f"Password reset"
     body = resetLink
     receiver = email

     msg = MIMEText(body)
     msg["Subject"] = subject
     msg["From"] = sender
     msg["To"] = receiver
     with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp_server:
          smtp_server.login(sender, password)
          smtp_server.sendmail(sender, receiver, msg.as_string())
          print(f"Message sent to ", receiver)