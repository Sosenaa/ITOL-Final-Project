import os
import sqlite3
from database import get_db_connection
import datetime
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
                              LEFT JOIN users ON tasks.user_id = users.id
                              WHERE tasks.due_date = ?""", (todayDate,)).fetchall()

     resend.api_key = os.getenv("RESEND_API_KEY")
     if not resend.api_key:
          raise RuntimeError("RESEND_API_KEY Missing")

     from_email = os.getenv("FROM_EMAIL", "onboarding@resend.dev")
     email_sent = 0
                            
     for r in reminders:
          subject = f"Task: {r['title']} is due today"
          body = f"Task: {r['description']}"
          receiver = r['email']

          r = resend.Emails.send({
          "from": from_email,
          "to": [receiver],
          "subject": subject,
          "html": body
          })
          email_sent += 1
     conn.close()
     return email_sent