import sqlite3
from email.mime.text import MIMEText
from database import get_db_connection
import datetime
import smtplib
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

sender = "k.sosnowski1695@gmail.com"
password = "xrrqbifpexojzxno"

for r in reminders:
     subject = f"Task: {r['title']} is due today"
     body = f"Task: {r['description']}"
     receiver = r['email']


     msg = MIMEText(body)
     msg["Subject"] = subject
     msg["From"] = sender
     msg["To"] = receiver
     with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp_server:
          smtp_server.login(sender, password)
          smtp_server.sendmail(sender, receiver, msg.as_string())
          print(f"Message sent to ", receiver)