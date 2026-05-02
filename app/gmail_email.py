import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
from flask import jsonify

# Load environment variables from .env
load_dotenv()
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

def send_booking_confirmation_email(
    to_email,
    client_name,
    service,
    date,
    time,
    pickup_location,
    payment_mode
):
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        return jsonify({"success": False, "error": "Missing Gmail credentials"}), 500

    subject = "Your Valtrion Booking Confirmation"
    html_content = f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;">
      <h2 style="color:#0066FF;">Valtrion Booking Confirmation</h2>
      <p>Dear <b>{client_name}</b>,</p>
      <p>Thank you for booking with Valtrion! Here are your booking details:</p>
      <table style="width:100%;border-collapse:collapse;">
        <tr><td style="padding:8px;border:1px solid #eee;"><b>Client Name</b></td><td style="padding:8px;border:1px solid #eee;">{client_name}</td></tr>
        <tr><td style="padding:8px;border:1px solid #eee;"><b>Service</b></td><td style="padding:8px;border:1px solid #eee;">{service}</td></tr>
        <tr><td style="padding:8px;border:1px solid #eee;"><b>Date</b></td><td style="padding:8px;border:1px solid #eee;">{date}</td></tr>
        <tr><td style="padding:8px;border:1px solid #eee;"><b>Time</b></td><td style="padding:8px;border:1px solid #eee;">{time}</td></tr>
        <tr><td style="padding:8px;border:1px solid #eee;"><b>Pickup Location</b></td><td style="padding:8px;border:1px solid #eee;">{pickup_location}</td></tr>
        <tr><td style="padding:8px;border:1px solid #eee;"><b>Payment Mode</b></td><td style="padding:8px;border:1px solid #eee;">{payment_mode}</td></tr>
      </table>
      <p style="margin-top:24px;">We look forward to serving you.<br>— Valtrion Team</p>
    </div>
    """

    try:
        msg = MIMEMultipart()
        msg['From'] = f"Valtrion Admin <{GMAIL_USER}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(html_content, 'html'))

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_USER, to_email, msg.as_string())

        return jsonify({"success": True, "message": "Confirmation email sent."}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
