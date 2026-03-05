import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import dotenv # Import dotenv module
import os
dotenv.load_dotenv() # Load environment variables from .env file
def send_mail():
    # Email configuration
    sender_email = 'fridayro706@gmail.com'
    sender_password = os.getenv('EMAIL_PASSWORD')
    receiver_email = str(input("Enter receiver's email address: "))
    subject = str(input("Enter subject: "))
    print("Enter email body (press Ctrl+D or Ctrl+Z (Windows) to finish):")
    lines = []
    try:
        while True:
            line = input()
            lines.append(line)
    except EOFError:
        pass
    body = "\n".join(lines)

    # Create a multipart message and set headers
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = subject

    # Add body to email
    message.attach(MIMEText(body, 'plain'))

    # Connect to SMTP server
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print('Email sent successfully!')
    except smtplib.SMTPException as e:
        print('Error sending email:', str(e))

if __name__ == "__main__":
    send_mail()