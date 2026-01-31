import os
import sqlite3
from email.mime.text import MIMEText
from database import get_db_connection
import datetime
import smtplib
import resend


#get connection to database
conn = get_db_connection()
#get todays date (yyyy - mm -- dd)
todayDate = datetime.date.today()

#get tasks that are due today and retrive an email recepiant
reminders = conn.execute("""
                         SELECT tasks.id, 
                              tasks.title, 
                              tasks.description, 
                              tasks.due_date, 
                              tasks.status, 
                              users.email
                         FROM tasks
                         LEFT JOIN users ON tasks.user_id = users.id
                         WHERE tasks.due_date = ?""", (todayDate,)).fetchall()

resend.api_key = "re_NLq5z42u_8aChM8nuu5aPAd4PxAYsZVGi"





for r in reminders:
     subject = f"Task: {r['title']} is due today"
     body = f"Task: {r['description']}"
     receiver = r['email']

     r = resend.Emails.send({
     "from": "onboarding@resend.dev",
     "to": receiver,
     "subject": subject,
     "html": body
     })
