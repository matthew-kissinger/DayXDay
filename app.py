import openai
import os
import cryptography
import datetime
import glob
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from flask import Flask, request, render_template, redirect, url_for, session
from encryption import encrypt, decrypt
from config import OPENAI_API_KEY, DEFAULT_PASSWORD, SECRET_KEY, SALT, SENDGRID_API_KEY
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dailyscrape import get_current_date, get_history_event_of_the_day, get_weather, get_top_news_stories, get_stock_market_news

app = Flask(__name__)

app.secret_key = SECRET_KEY
openai.api_key = OPENAI_API_KEY

notes = []

CLASSIFICATIONS = [
  "Unclassified",
  "Personal",
  "Work",
  "Health",
  "Finance",
  "Errands",
  "Goals",
  "Education",
  "Hobbies",
  "Travel",
  "Family",
  "Relationships",
  "Social",
  "Home Maintenance",
  "Inspiration",
  "Reminders",
  "Events",
  "Books",
  "Movies",
  "Recipes",
]


def classify_note(note):
  response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{
      "role":
      "system",
      "content":
      f"You are an AI trained to classify a note into one of the following categories: {', '.join(CLASSIFICATIONS)}. If a note does not fit any classification, respond 'Unclassified'. Examples: Buying groceries -> 'Errands', Doctor's appointment -> 'Category: Health'."
    }, {
      "role": "user",
      "content": f"Note: {note}"
    }])
  classification = response['choices'][0]['message']['content']
  print(classification)
  return classification


def get_summary_string():
  summary = []

  current_date = get_current_date()
  summary.append(f"Today's date: {current_date}")

  event_of_the_day = get_history_event_of_the_day()
  summary.append(f"Today in history: {event_of_the_day}")

  weather = get_weather()
  summary.append(weather)

  summary.append("\nTop tech news stories:")
  top_stories = get_top_news_stories()
  for story in top_stories:
    summary.append(f"{story['title']} - {story['link']}")

  summary.append("\nStock market news:")
  stock_stories = get_stock_market_news()
  for story in stock_stories:
    summary.append(f"{story['title']} - {story['link']}")

  return "\n".join(summary)


def generate_report(decrypted_notes):
  summary_string = get_summary_string()

  context = f"Generate a personalized daily briefing for Matthew. You will be given context that includes the date, a historical event, tech news, market news, and personal categorized notes that Matthew takes throughout the day. Use the context to greet Matthew. Give an interesting summary of the weather, news, and historical event. Then organize and modify Matthews notes in an easily ingestible format without changing the meaning of the notes. End with a relavent motivational quote.  Context:\n{summary_string}\n"

  for category, notes_list in decrypted_notes.items():
    if notes_list:
      context += f"{category}:\n"
      context += "\n".join(notes_list) + "\n"

  response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{
      "role":
      "system",
      "content":
      "You are a helpful assistant that generates personalized briefing given context."
    }, {
      "role": "user",
      "content": context
    }])
  report = response['choices'][0]['message']['content']
  print("Generated report:", report)  # Debugging print statement
  return report


def save_note_to_file(classification, encrypted_note):
  # Parse the classification string
  if ":" in classification:
    parsed_classification = classification.split(":")[1].strip()
  else:
    parsed_classification = classification.strip()

  # Replace spaces with underscores and remove the period (.) from the end if present
  parsed_classification = parsed_classification.replace(" ", "_").rstrip(".")

  # Create the file name without punctuation
  file_name = f"{parsed_classification}_notes.txt"

  # Save the encrypted_message to the file
  with open(file_name, "a") as file:
    file.write(f"{encrypted_note.decode()}\n")


def load_notes_from_files():
  decrypted_notes = {classification: [] for classification in CLASSIFICATIONS}

  for classification in CLASSIFICATIONS:
    file_name = f"{classification}_notes.txt"

    if os.path.exists(file_name):
      with open(file_name, "r") as file:
        encrypted_notes = file.readlines()

      for encrypted_note in encrypted_notes:
        encrypted_note = encrypted_note.strip(
        )  # Strip newline characters and whitespaces
        if encrypted_note:  # Check if the encrypted note is not empty
          try:
            decrypted_note = decrypt(encrypted_note, DEFAULT_PASSWORD, SALT)

            # Remove classification part from decrypted_note
            note_parts = decrypted_note.split(":")
            if len(note_parts) > 1:
              note_content = ":".join(note_parts[2:]).strip()
            else:
              note_content = decrypted_note

            decrypted_notes[classification].append(note_content)
          except cryptography.fernet.InvalidToken:
            print(f"Error decrypting note from {file_name}: {encrypted_note}")
  print(decrypted_notes)
  return decrypted_notes


def save_report(report):
  timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
  file_name = f"reports/report_{timestamp}.txt"

  encrypted_report, _ = encrypt(report, DEFAULT_PASSWORD,
                                SALT)  # Encrypt the report

  with open(file_name, "wb") as file:
    file.write(encrypted_report)  # Save the encrypted report to a file


def load_generated_reports():
  reports = []
  for file in glob.glob("reports/report_*.txt"):
    with open(file, "rb") as f:
      encrypted_report = f.read()
    try:
      decrypted_report = decrypt(encrypted_report, DEFAULT_PASSWORD, SALT)
      reports.append((file, decrypted_report))
    except cryptography.fernet.InvalidToken:
      print(f"Error decrypting report: {file}")
  return sorted(reports, key=lambda x: x[0], reverse=True)


def save_notes_to_files(decrypted_notes, modified_category):
  file_name = f"{modified_category}_notes.txt"

  # Clear the file content
  open(file_name, "w").close()

  for note in decrypted_notes[modified_category]:
    encrypted_note, _ = encrypt(
      note, DEFAULT_PASSWORD, SALT)  # Encrypt the note without classification
    save_note_to_file(modified_category, encrypted_note)


def daily_report():
  decrypted_notes = load_notes_from_files()
  report = generate_report(decrypted_notes)
  save_report(report)  # Save the generated report to a file
  send_report_email(report)  # Send the email with the report text
  print("Report generated, saved, and emailed")  # Debugging print statement


def send_report_email(report_text):
  message = Mail(
    from_email='matt.m.kissinger@gmail.com',  # Replace with your email address
    to_emails=
    'matt.m.kissinger@gmail.com',  # Replace with the recipient's email address
    subject='Your Daily Report',
    html_content=
    f'<strong>Your daily report is ready.</strong><br><pre>{report_text}</pre>'
  )
  try:
    sg = SendGridAPIClient(SENDGRID_API_KEY)
    response = sg.send(message)
    print(response.status_code)
    print(response.body)
    print(response.headers)
  except Exception as e:
    print(e)


@app.before_first_request
def init_scheduler():
  scheduler = BackgroundScheduler()

  hour = 18  # Set the hour to 17 (5 PM in 24-hour format)
  minute = 0  # Set the minute to 40

  trigger = CronTrigger(hour=hour, minute=minute, timezone='UTC')
  scheduler.add_job(daily_report, trigger=trigger)
  scheduler.start()


@app.route("/login", methods=["GET", "POST"])
def login():
  if request.method == "POST":
    password = request.form["password"]
    if password == DEFAULT_PASSWORD:
      session.permanent = True
      session["authenticated"] = True
      return redirect(url_for("home"))
    else:
      return render_template("login.html",
                             error="Invalid password. Please try again.")

  return render_template("login.html", error=None)


@app.route("/")
def index():
  if session.get("authenticated"):
    return redirect(url_for("home"))
  else:
    return redirect(url_for("login"))


@app.route("/home", methods=["GET", "POST"])
def home():
  if "authenticated" not in session or not session["authenticated"]:
    return redirect(url_for("login"))

  if request.method == "POST":
    note = request.form["note"]
    classification = classify_note(note)

    # Remove classification part from the note
    note_parts = note.split(":")
    if len(note_parts) > 2:
      note_content = ":".join(note_parts[2:]).strip()
    else:
      note_content = note

    encrypted_note, _ = encrypt(f"{classification}: {note_content}",
                                DEFAULT_PASSWORD, SALT)
    save_note_to_file(classification, encrypted_note)
    return redirect(url_for("home"))

  decrypted_notes = load_notes_from_files()
  generated_reports = load_generated_reports(
  )  # Load the list of generated reports
  return render_template("home.html",
                         notes=decrypted_notes,
                         reports=generated_reports)


@app.route("/generate_report", methods=["GET", "POST"])
def report():
  if "authenticated" not in session or not session["authenticated"]:
    return redirect(url_for("login"))

  if request.method == "POST":
    decrypted_notes = load_notes_from_files()
    report = generate_report(decrypted_notes)
    save_report(report)  # Save the generated report to a file
    print("Report :", report)  # Debugging print statement
    return render_template("report.html", report=report)

  return render_template("report.html", report=None)


@app.route("/view_report/<path:report_file>")
def view_report(report_file):
  if "authenticated" not in session or not session["authenticated"]:
    return redirect(url_for("login"))

  file_path = os.path.join("reports", report_file)
  try:
    with open(file_path, "rb") as f:
      encrypted_report = f.read()
    decrypted_report = decrypt(encrypted_report, DEFAULT_PASSWORD, SALT)
    return render_template("report.html", report=decrypted_report)
  except FileNotFoundError:
    return "File not found", 404


@app.route("/mark_complete", methods=["POST"])
def mark_complete():
  if "authenticated" not in session or not session["authenticated"]:
    return redirect(url_for("login"))

  category = request.form["category"]
  note_index = int(request.form["note_index"])

  # Load notes from files, remove the specific note from the category and save the notes back to files
  decrypted_notes = load_notes_from_files()
  if 0 <= note_index < len(decrypted_notes[category]):
    del decrypted_notes[category][note_index]
    save_notes_to_files(decrypted_notes, category)

  return redirect(url_for("home"))


if __name__ == "__main__":
  init_scheduler()
  app.run(host="0.0.0.0", port=8080)
