import os
import requests
from dotenv import load_dotenv
from flask import jsonify

# Load environment variables from .env
load_dotenv()
RESEND_API_KEY = os.getenv("RESEND_API_KEY")

RESEND_API_URL = "https://api.resend.com/emails"
SENDER = "Valtrion Admin <onboarding@resend.dev>"

def send_booking_confirmation_email(
    to_email,
    client_name,
    client_phone,
    service,
    date,
    time,
    pickup_location,
    payment_mode
):
    if not RESEND_API_KEY:
        return jsonify({"success": False, "error": "Missing RESEND_API_KEY"}), 500

    subject = "Your Valtrion Booking Confirmation"
    html_content = f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;">
      <h2 style="color:#0066FF;">Valtrion Booking Confirmation</h2>
      <p>Dear <b>{client_name}</b>,</p>
      <p>Thank you for booking with Valtrion! Here are your booking details:</p>
      <table style="width:100%;border-collapse:collapse;">
        <tr><td style="padding:8px;border:1px solid #eee;"><b>Client Name</b></td><td style="padding:8px;border:1px solid #eee;">{client_name}</td></tr>
        <tr><td style="padding:8px;border:1px solid #eee;"><b>Phone Number</b></td><td style="padding:8px;border:1px solid #eee;">{client_phone}</td></tr>
        <tr><td style="padding:8px;border:1px solid #eee;"><b>Service</b></td><td style="padding:8px;border:1px solid #eee;">{service}</td></tr>
        <tr><td style="padding:8px;border:1px solid #eee;"><b>Date</b></td><td style="padding:8px;border:1px solid #eee;">{date}</td></tr>
        <tr><td style="padding:8px;border:1px solid #eee;"><b>Time</b></td><td style="padding:8px;border:1px solid #eee;">{time}</td></tr>
        <tr><td style="padding:8px;border:1px solid #eee;"><b>Pickup Location</b></td><td style="padding:8px;border:1px solid #eee;">{pickup_location}</td></tr>
        <tr><td style="padding:8px;border:1px solid #eee;"><b>Payment Mode</b></td><td style="padding:8px;border:1px solid #eee;">{payment_mode}</td></tr>
      </table>
      <p style="margin-top:24px;">We look forward to serving you.<br>— Valtrion Team</p>
    </div>
    """

    payload = {
        "from": SENDER,
        "to": [to_email],
        "subject": subject,
        "html": html_content
    }
    headers = {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        print("[Resend] Sending email to:", to_email)
        print("[Resend] Payload:", payload)
        print("[Resend] Headers:", headers)
        response = requests.post(RESEND_API_URL, json=payload, headers=headers, timeout=10)
        print("[Resend] Response:", response.status_code, response.text)
        if response.status_code == 200:
            return jsonify({"success": True, "message": "Confirmation email sent."}), 200
        else:
            return jsonify({"success": False, "error": response.text}), 500
    except Exception as e:
        print("[Resend] Exception:", str(e))
        return jsonify({"success": False, "error": str(e)}), 500
