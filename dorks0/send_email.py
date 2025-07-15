import smtplib
from email.message import EmailMessage
import os

# Email configuration
SENDER_EMAIL = "afzantpr123@gmail.com"           # <-- Your email
SENDER_PASSWORD = "nrzk fdox jnwz hyug"           # <-- App password (not normal password)
RECEIVER_EMAIL = "mrpilotking@gmail.com"     # <-- Friend's email

# File to attach
FILE_PATH = "dork_results.txt"

def send_email():
    if not os.path.exists(FILE_PATH):
        print("[!] Output file not found.")
        return

    msg = EmailMessage()
    msg["Subject"] = "Google Dork Results"
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL
    msg.set_content("Hi, please find the attached dork results file.\n\nSent automatically from Python.")

    # Attach the file
    with open(FILE_PATH, "rb") as file:
        file_data = file.read()
        file_name = os.path.basename(FILE_PATH)
        msg.add_attachment(file_data, maintype="application", subtype="octet-stream", filename=file_name)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
            smtp.send_message(msg)
            print("[+] Email sent successfully.")
    except Exception as e:
        print("[!] Failed to send email:", e)

if __name__ == "__main__":
    send_email()
