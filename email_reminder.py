import os
import sqlite3
from database import get_db_connection
import datetime
import time
import resend

def send_due_reminders() -> int:
     #get connection to database
     conn = get_db_connection()
     todayDate = datetime.date.today().isoformat()


     reminders = conn.execute("""
                              SELECT tasks.id, 
                                   tasks.title, 
                                   tasks.description, 
                                   tasks.due_date, 
                                   tasks.status, 
                                   users.email
                              FROM tasks
                              JOIN users ON tasks.user_id = users.id
                              WHERE tasks.due_date <= ? AND users.email IS NOT NULL""", (todayDate,)).fetchall()

     resend.api_key = os.getenv("RESEND_API_KEY")
     if not resend.api_key:
          raise RuntimeError("RESEND_API_KEY Missing")

     from_email = os.getenv("FROM_EMAIL", "onboarding@resend.dev")
     emails_sent = 0
                            
     for r in reminders:
          receiver = r['email']
          subject = f"Task: {r['title']} is due today"
          body = f"Task: {r['description']}"
          

          resend.Emails.send({
          "from": from_email,
          "to": [receiver],
          "subject": subject,
          "html": body
          })

          emails_sent += 1

          time.sleep(0.6)
     conn.close()
     return emails_sent