from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, make_response
from flask_login import login_required, current_user
from app import db
from app.models import Booking, Service
from datetime import datetime

booking = Blueprint('booking', __name__)

def send_sms(phone, message):
    try:
        from twilio.rest import Client
        from flask import current_app
        sid   = current_app.config.get('TWILIO_ACCOUNT_SID')
        token = current_app.config.get('TWILIO_AUTH_TOKEN')
        frm   = current_app.config.get('TWILIO_PHONE')
        if sid and token and frm:
            client = Client(sid, token)
            client.messages.create(body=message, from_=frm, to='+91' + phone)
    except Exception as e:
        print("SMS Error:", e)

@booking.route('/book/<int:service_id>')
@login_required
def book_service(service_id):
    service = Service.query.get_or_404(service_id)
    return render_template('booking.html', service=service)

@booking.route('/confirm-booking', methods=['POST'])
@login_required
def confirm_booking():
    try:
        data = request.json
        service = Service.query.get_or_404(data.get('service_id'))
        new_booking = Booking(
            user_id        = current_user.id,
            service_id     = service.id,
            customer_name  = data.get('name'),
            customer_phone = data.get('phone'),
            car_brand      = data.get('car_brand'),
            car_model      = data.get('car_model'),
            car_number     = data.get('car_number'),
            fuel_type      = data.get('fuel_type'),
            pickup_address = data.get('address'),
            preferred_date = data.get('date'),
            total_amount   = service.price,
            status         = 'Confirmed' if data.get('payment_method') != 'COD' else 'Pending',
            payment_status = 'Paid' if data.get('payment_method') != 'COD' else 'COD',
            payment_method = data.get('payment_method'),
            payment_ref    = data.get('payment_ref', '')
        )
        db.session.add(new_booking)
        db.session.commit()
        send_sms(data.get('phone',''), f"Hi {data.get('name')}! Valtrion booking confirmed. Service: {service.name}, Date: {data.get('date')}, Amount: Rs.{int(service.price)}. Booking #V{new_booking.id:04d}. Team Valtrion.")
        return jsonify({'success': True, 'booking_id': new_booking.id})
    except Exception as e:
        print("Booking error:", e)
        return jsonify({'success': False, 'error': str(e)}), 500

@booking.route('/payment/success/<int:booking_id>')
@login_required
def payment_success(booking_id):
    b = Booking.query.get_or_404(booking_id)
    return render_template('payment_success.html', booking=b)

@booking.route('/cancel/<int:booking_id>')
@login_required
def cancel_booking(booking_id):
    b = Booking.query.get_or_404(booking_id)
    if b.user_id == current_user.id:
        b.status = 'Cancelled'
        db.session.commit()
        flash('Booking cancelled.', 'warning')
    return redirect(url_for('main.dashboard'))

@booking.route('/invoice/<int:booking_id>')
@login_required
def download_invoice(booking_id):
    b = Booking.query.get_or_404(booking_id)
    if b.user_id != current_user.id and current_user.role != 'admin':
        flash('Unauthorized', 'danger')
        return redirect(url_for('main.dashboard'))
    html = f"""<html><head><style>
    body{{font-family:Arial;padding:40px;background:#fff;color:#000;}}
    .logo{{font-size:36px;font-weight:bold;color:#0066FF;letter-spacing:8px;}}
    .row{{display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid #f0f0f0;}}
    .total{{display:flex;justify-content:space-between;padding:16px 0;font-size:22px;font-weight:bold;color:#0066FF;}}
    .badge{{background:#e6fff2;padding:4px 12px;border-radius:20px;color:#00aa55;font-weight:bold;font-size:13px;}}
    </style></head><body>
    <div style="text-align:center;border-bottom:3px solid #0066FF;padding-bottom:20px;margin-bottom:30px;">
    <div class="logo">VALTRION</div>
    <p style="color:#666;">Expert Care for Every Car</p>
    <p style="font-size:18px;color:#333;">Invoice #{str(b.id).zfill(4)}</p></div>
    <div class="row"><span>Customer</span><strong>{b.customer_name}</strong></div>
    <div class="row"><span>Phone</span><strong>{b.customer_phone}</strong></div>
    <div class="row"><span>Car</span><strong>{b.car_brand} {b.car_model} ({b.fuel_type})</strong></div>
    <div class="row"><span>Car Number</span><strong>{b.car_number or 'N/A'}</strong></div>
    <div class="row"><span>Service</span><strong>{b.service.name}</strong></div>
    <div class="row"><span>Date</span><strong>{b.preferred_date}</strong></div>
    <div class="row"><span>Address</span><strong>{b.pickup_address}</strong></div>
    <div class="row"><span>Payment Method</span><strong>{b.payment_method or 'UPI'}</strong></div>
    <div class="row"><span>Status</span><span class="badge">{b.status}</span></div>
    <div class="row"><span>UPI / Ref</span><strong>{b.payment_ref or 'dhanushkoti08-3@okicici'}</strong></div>
    <div class="row"><span>Date of Booking</span><strong>{b.created_at.strftime('%d %b %Y')}</strong></div>
    <div class="total"><span>Total Amount</span><span>Rs. {int(b.total_amount)}</span></div>
    <div style="text-align:center;margin-top:30px;color:#999;font-size:12px;line-height:1.8;">
    <strong style="color:#0066FF;">VALTRION Automotive Services</strong><br>
    valtrionblore@gmail.com | +91 9876543210<br>
    30-Day Service Warranty | Transparent Pricing<br>Thank you for choosing Valtrion!</div>
    </body></html>"""
    response = make_response(html)
    response.headers['Content-Type'] = 'text/html'
    return response