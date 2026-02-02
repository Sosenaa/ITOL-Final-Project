from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, abort, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os
from database import get_db_connection, create_tables, DATABASE
import csv
from datetime import datetime, timedelta
import secrets
from email.mime.text import MIMEText
from reset_password import sendResetLink, createResetLink
import re
from dotenv import load_dotenv
import secrets
from email_reminder import send_due_reminders

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", secrets.token_hex(32))


#for PRODUCTION change SESSION_COOKIE_SECURE=True & SESSION_COOKIE_SAMESITE='None',
app.config.update(
     SESSION_COOKIE_SECURE=False,
     SESSION_COOKIE_SAMESITE='Lax',
     SESSION_COOKIE_HTTPONLY=True
     )

with app.app_context():
     create_tables()

from functools import wraps
def login_required(f):
     @wraps(f)
     def decorated_function(*args, **kwargs):
          if "user_id" not in session:
               flash("You need to be logged in to access this page", "error")
               return redirect(url_for('login'))
          return f(*args, **kwargs)
     return decorated_function

@app.route("/")
def index():
     return redirect(url_for("register"))

@app.route("/login", methods=["GET", "POST"])
def login():
     if request.method == "POST":
          username = request.form["username"].lower()
          password = request.form["password"]

          conn = get_db_connection()
          user = conn.execute("SELECT id, username, password_hash FROM users WHERE username =? ", (username,)).fetchone()
          conn.close()

          #check if password is correct
          if user and check_password_hash(user["password_hash"], password):
               session["user_id"] = user["id"]
               session["username"] = user["username"]
               flash("Login has been successful", "success")
               return redirect(url_for('dashboard'))
          else:
               flash("Email or password are incorrect, please try again", "error")
               return render_template("login.html")
     return render_template("login.html")

@app.route("/dashboard")
@login_required
def dashboard():
     user_id = session.get("user_id")
     conn = get_db_connection()
     tasks = conn.execute("SELECT * FROM tasks WHERE user_id = ?", (user_id,)).fetchall()
     conn.close()
     return render_template("dashboard.html", username=session.get("username"), tasks=tasks)

@app.route("/create_task", methods=['GET', 'POST'])
@login_required
def create_task():
     if request.method == "POST":
          user_id = session.get("user_id")
          title = request.form["title"]
          description = request.form["description"]
          date = request.form["due_date"]
          status = request.form["status"]

          if (len(title) > 100 or len(description) > 500 or not date or not status):
               flash("Something went wrong, please try again", "error")
          else:
               conn = get_db_connection()
               cursor = conn.cursor()
               cursor.execute("INSERT INTO tasks (user_id, title, description, due_date, status) VALUES (?,?,?,?,?)", (user_id, title, description,date,status))
               conn.commit()

               #update activity log
               task_id = cursor.lastrowid
               log_activity(user_id, "Created", task_id, title)
               
               conn.close()
               flash("Task has been added succesffullu!", "success")
               return redirect(url_for('dashboard'))

     return render_template("create_task.html")

@app.route("/edit_task/<int:task_id>", methods=['GET','POST'])
@login_required
def edit_task(task_id):
     if request.method == "GET":
          conn = get_db_connection()
          task = conn.execute("SELECT * FROM tasks WHERE id = ? AND user_id = ?", (task_id, session["user_id"])).fetchone()
          conn.close()
          return render_template("edit_task.html", task=task)
     
     if request.method == "POST":
          conn = get_db_connection()
          title = request.form["title"]
          description = request.form["description"]
          due_date = request.form["due_date"]
          status = request.form["status"]
          user_id = session["user_id"]

          if (len(title) > 100 or len(description) > 500 or not due_date or not status):
               flash("Something went wrong, please try again", "error")
          else:
               conn.execute("UPDATE tasks SET title = ?, description = ?, due_date =? , status = ?  WHERE id = ? AND user_id = ?", (title, description, due_date, status, task_id, user_id))
               conn.commit()
               log_activity(user_id, "Updated", task_id, title)
               conn.close()
               return redirect(url_for('dashboard'))
     return render_template("dashboard.html")



@app.route("/delete_task/<int:task_id>", methods=["POST"])
@login_required
def delete_task(task_id):
          if request.method == "POST":
               conn = get_db_connection()
               user_id = session.get("user_id")

               if user_id is None:
                    conn.close()
                    return redirect(url_for("Login"))
               
               try:
                    task_row = conn.execute("SELECT title FROM tasks WHERE id = ? AND user_id = ?", (task_id, user_id)).fetchone()
                    task_detele = conn.execute("DELETE FROM tasks WHERE id = ? AND user_id = ? ", (task_id, user_id))

                    if task_detele.rowcount > 0:
                         conn.commit()
                         log_activity(user_id, "Deleted", task_id, task_row["title"])
                    else: 
                         flash("Task not fund", "error") 
               except Exception as e:
                    flash(f"There is an Error: {e}", "error")
               finally:
                    conn.close()
          return redirect(url_for("dashboard"))

@app.route("/export")
@login_required
def export():
     conn = get_db_connection()
     user_id = session["user_id"]
     tasks = conn.execute("SELECT * FROM tasks WHERE user_id = ?", (user_id,)).fetchall()
     taskIndex = 0
     if len(tasks) > 0:
          with open("tasks_file.csv", mode="w", newline="") as tasks_file:
               task_writer = csv.writer(tasks_file)

               for task in tasks:

                    task_writer.writerow(["Title - ", task["title"]])
                    task_writer.writerow(["Description - ", task["description"]])
                    task_writer.writerow(["Due Date - ", task["due_date"]])
                    task_writer.writerow(["Status - ", task["status"]])
                    task_writer.writerow("")  # Empty line between tasks
     
               log_activity(user_id, "Downloaded", task_title="Task List")
          conn.close()
          return send_file("tasks_file.csv", as_attachment=True)
     else:
          conn.close()
          flash("No task to export" "error")
          return redirect(url_for("dashboard"))
     
     
@app.route("/logout")
def logout():
     session.clear()
     return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
     if request.method == "POST":
          username = request.form["username"].lower()
          email = request.form["email"]
          password = request.form["password"]
          confirm_password = request.form["confirm_password"]

          #Password requirements + validation
          pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$#%])[A-Za-z\d@$#%]{6,20}$"
          reg = re.compile(pattern)
          match = re.search(pattern, password)

          #basic server side validation
          if not username or not email or not password or not confirm_password:
               flash("Information missing, please complete all fields", "error")
               return render_template("register.html")
          
     
          if password != confirm_password:
               flash("Passwords do not match", "error")
               return render_template("register.html")
          
          if not match:
               flash("""
                         1. Have at least one number
                         2. Have at least one uppercase letter
                         3. Have at least one lowercase letter
                         4. Have at least one special character ($, @, #, %)
                         5. Be between 6 and 20 characters in length
                     """)
               return render_template("register.html")
          

          password_hash = generate_password_hash(password)

          conn = get_db_connection()
          try:
               existingUser = conn.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email)).fetchone()
               #Check if user already exists before adding to database
               if existingUser:
                    flash("User name or email is already taken, please try again", "error")
                    return render_template("register.html")
               
               #Add user to database
               conn.execute("INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)", (username, email, password_hash))
               conn.commit()
               flash("Registration completed successfully", "success")
               return render_template("login.html")
          
          except sqlite3.IntegrityError:
               flash("There has been an error, please try again", "error")
               return render_template("register.html")
          finally:
               conn.close()
     return render_template("register.html")

@app.route("/password_reminder", methods=["GET", "POST"])
def password_reminder():
     if request.method == "POST":
          email = request.form["email"]
          conn = get_db_connection()

          user = conn.execute("SELECT id, email FROM users WHERE email = ?", (email,)).fetchone()
          if user: 
               token = secrets.token_urlsafe(32)
               expiresAt = datetime.now() + timedelta(hours=1)

               conn.execute("INSERT INTO tokens (token, expires_at, user_id) VALUES (?, ? ,?)", (token, expiresAt, user['id']))
               conn.commit()
               createResetLink(user['email'],token)

     return render_template("password_reminder.html")

@app.route("/password_reset", methods=["GET", "POST"])
def password_reset():
     conn = get_db_connection()
     token_value = request.args.get("token")

     if not token_value:
          conn.close()
          flash("Invalid or missing token.", "error")
          return redirect(url_for("password_reminder"))
     
     token = conn.execute("SELECT tokenValid, expires_at, user_id FROM tokens WHERE token = ?", (token_value,)).fetchone()
     
     if token is None:
          conn.close()
          flash("Invalid or expired token.", "error")
          return redirect(url_for("password_reminder"))
     
     currentTime = datetime.now()
     expiresAt = datetime.fromisoformat(token['expires_at'])


     if expiresAt > currentTime and token['tokenValid'] == 1:
          userId = token['user_id']
          if request.method == "POST":
               newPassword = request.form['new_password']

               #Password requirements + validation
               pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$#%])[A-Za-z\d@$#%]{6,20}$"
               reg = re.compile(pattern)
               match = re.search(pattern, newPassword)
               
               if not match:
                    flash("""
                              1. Have at least one number
                              2. Have at least one uppercase letter
                              3. Have at least one lowercase letter
                              4. Have at least one special character ($, @, #, %)
                              5. Be between 6 and 20 characters in length
                         """)
                    return render_template("register.html")
          

               hashPassword = generate_password_hash(newPassword)

               conn.execute("UPDATE users SET password_hash = ? WHERE id = ?", (hashPassword, userId,))
               print("Password has been changed")
               conn.execute("UPDATE tokens SET tokenValid = 0 WHERE token = ?", (token_value,))
               conn.commit()
               conn.close()
               flash("Password has been changed.", "success")
               return redirect(url_for("login"))
     else:
          flash("Token has expired.", "error")
          return redirect(url_for("dashboard"))

     return render_template("password_reset.html")

@app.post("/cron/send-reminders")
def cron_send_reminders():
     expected = os.getenv("CRON_SECRET")
     got = request.headers.get("X-CRON-SECRET")
     if not got or got != expected:
          abort(401)
     
     emails_sent = send_due_reminders()
     return jsonify({"status": "ok", "emails_sent": emails_sent})

def log_activity(user_id, action, task_id=None, task_title=None):
     conn = get_db_connection()
     conn.execute(
          "INSERT INTO activity_log (user_id, action, task_id, task_title) VALUES (?,?,?,?)",(user_id, action, task_id, task_title) 
     )
     conn.commit()
     conn.close()

@app.route("/activity_log")
@login_required
def activity_log():
     user_id = session["user_id"]
     conn = get_db_connection()
     logs = conn.execute("" \
     "SELECT action, task_id, task_title, timestamp " \
     "FROM activity_log " \
     "WHERE user_id = ? " \
     "ORDER BY timestamp DESC " \
     "LIMIT 50", (user_id,)).fetchall()
     conn.close()

     return render_template("activity_log.html", logs=logs)


if __name__ == "__main__":
     
     port = int(os.environ.get("PORT", 10000))
     app.run(host="0.0.0.0", port=port, debug=True)

     #app.run(debug=True)