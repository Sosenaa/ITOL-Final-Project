import sqlite3
from database import get_db_connection
import datetime
import smtplib
from flask import url_for
from dotenv import load_dotenv
import os
import resend

load_dotenv()

resend.api_key = os.getenv("RESEND_API_KEY")

def createResetLink(email, token):
     resetLink = url_for('password_reset', token=token, _external=True)
     #Create link only if email exists
     sendResetLink(email, resetLink)

def sendResetLink(email, resetLink):
     subject = f"Password reset"
     body = resetLink
     receiver = email

     r = resend.Emails.send({
     "from": 'onboarding@resend.dev',
     "to": receiver,
     "subject": subject,
     "html": body
     })











