import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

def send_email(message_details: dict):
    """
    Sends an email using Gmail's SMTP server with the details provided in the message_details dictionary.
    
    Parameters:
    -----------
    message_details : dict
        A dictionary containing the following keys:
        - 'subject' (str): The subject of the email.
        - 'body' (str): The plain-text content of the email.

    Example:
    --------
    message_details = {
        "subject": "Test Email",
        "body": "This is a test email from Python!"
    }

    send_email(message_details)

    Returns:
    --------
    None. Prints a success message if the email is sent successfully or a failure message otherwise.
    
    Notes:
    ------
    - This function uses Gmail's SMTP server to send emails. Make sure the sender email has 2-Step Verification enabled 
      and an app-specific password is used for authentication.
    - The 'password' should be the app password generated via your Google Account's security settings.
    """

    load_dotenv()
    # Create the email
    message = MIMEMultipart()
    message["From"] = os.getenv("sender_email")
    message["To"] = os.getenv("receiver_email")
    message["Subject"] = os.getenv("subject")

    # Attach the email body
    message.attach(MIMEText(message_details["body"], "plain"))

    # Attempt to send the email
    try:
        # Connect to Gmail SMTP server
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()  # Secure the connection with TLS
            server.login(message_details["sender_email"], message_details["password"])  # Log in to the server
            server.sendmail(
                message_details["sender_email"], 
                message_details["receiver_email"], 
                message.as_string()
            )  # Send the email
    except Exception as e:
        print(f"Failed to send email: {e}")
        return
    
    print("Email sent successfully!")