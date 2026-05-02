from datetime import datetime

import razorpay
from flask import Blueprint, current_app, flash, jsonify, make_response, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from flask_mail import Message
from razorpay.errors import SignatureVerificationError

from app import db, mail
from app.models import Booking, Service


booking = Blueprint('booking', __name__)


def _get_razorpay_client():
    key_id = current_app.config.get('RAZORPAY_KEY_ID')
    key_secret = current_app.config.get('RAZORPAY_KEY_SECRET')
    if not key_id or not key_secret:
        raise RuntimeError('Razorpay credentials are not configured.')
    return razorpay.Client(auth=(key_id, key_secret))


def send_sms(phone, message):
    try:
        from twilio.rest import Client

        sid = current_app.config.get('TWILIO_ACCOUNT_SID')
        token = current_app.config.get('TWILIO_AUTH_TOKEN')
        frm = current_app.config.get('TWILIO_PHONE')
        if sid and token and frm and phone:
            client = Client(sid, token)
            client.messages.create(body=message, from_=frm, to='+91' + phone)
    except Exception as exc:
        print('SMS Error:', exc)


def send_booking_emails(booking_record, service):
    """Send exactly one confirmation email to the client and one notification to admin."""
    sender_email = (current_app.config.get('MAIL_USERNAME') or '').strip()
    sender_password = (current_app.config.get('MAIL_PASSWORD') or '').strip()
    if not sender_email or not sender_password or 'app-password-here' in sender_password:
        print('Email skipped: MAIL_USERNAME/MAIL_PASSWORD not configured.')
        return

    booking_id = f'#V{booking_record.id:04d}'
    vehicle = ' '.join(p for p in [booking_record.car_brand, booking_record.car_model] if p) or 'N/A'
    customer_name = booking_record.customer_name or getattr(current_user, 'name', 'Customer')
    customer_email = ''
    if booking_record.customer and booking_record.customer.email:
        customer_email = booking_record.customer.email.strip()
    elif getattr(current_user, 'email', None):
        customer_email = current_user.email.strip()

    # ── 1. Client confirmation email ──────────────────────────────────────────
    if customer_email:
        client_body = (
            f"Dear {customer_name},\n\n"
            "Thank you for choosing Valtrion Car Services.\n\n"
            "Your booking has been successfully confirmed. Here are your details:\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"  Booking ID      : {booking_id}\n"
            f"  Service         : {service.name}\n"
            f"  Vehicle         : {vehicle}\n"
            f"  Car Number      : {booking_record.car_number or '-'}\n"
            f"  Scheduled       : {booking_record.preferred_date or '-'}\n"
            f"  Pickup Location : {booking_record.pickup_address or '-'}\n"
            f"  Payment Mode    : {booking_record.payment_method or '-'}\n"
            f"  Amount          : Rs. {int(booking_record.total_amount or 0)}\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Our team will be ready at the scheduled time and location.\n"
            "Please ensure availability for a smooth service experience.\n\n"
            "For any queries, reply to this email or call us at +91 9686681036.\n\n"
            "Best regards,\n"
            "Valtrion Car Services\n"
            "valtrionbookings@gmail.com | +91 9686681036"
        )
        try:
            msg = Message(
                subject='Booking Confirmed - Valtrion Car Services',
                recipients=[customer_email],
                body=client_body,
                sender=('Valtrion Car Services', sender_email),
            )
            mail.send(msg)
            print(f'Client confirmation email sent to {customer_email} for booking {booking_id}')
        except Exception as exc:
            print(f'Client email error for {booking_id}: {exc}')

    # ── 2. Admin notification email ───────────────────────────────────────────
    admin_body = (
        f"New booking received — {booking_id}\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"  Booking ID      : {booking_id}\n"
        f"  Customer Name   : {booking_record.customer_name or 'N/A'}\n"
        f"  Customer Email  : {customer_email or 'N/A'}\n"
        f"  Customer Phone  : {booking_record.customer_phone or 'N/A'}\n"
        f"  Service         : {service.name}\n"
        f"  Vehicle         : {vehicle}\n"
        f"  Car Number      : {booking_record.car_number or 'N/A'}\n"
        f"  Scheduled       : {booking_record.preferred_date or 'N/A'}\n"
        f"  Pickup Location : {booking_record.pickup_address or 'N/A'}\n"
        f"  Payment Method  : {booking_record.payment_method or 'N/A'}\n"
        f"  Amount          : Rs. {int(booking_record.total_amount or 0)}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Please review and contact the client as soon as possible.\n\n"
        "Regards,\nValtrion Booking System"
    )
    try:
        msg = Message(
            subject=f'New Booking {booking_id} — {service.name}',
            recipients=[sender_email],
            body=admin_body,
            sender=('Valtrion Booking System', sender_email),
        )
        mail.send(msg)
        print(f'Admin notification sent for booking {booking_id}')
    except Exception as exc:
        print(f'Admin email error for {booking_id}: {exc}')


def _save_booking(data, service, payment_method, payment_ref, payment_status, booking_status):
    new_booking = Booking(
        user_id=current_user.id,
        service_id=service.id,
        customer_name=data.get('name'),
        customer_phone=data.get('phone'),
        car_brand=data.get('car_brand'),
        car_model=data.get('car_model'),
        car_number=data.get('car_number'),
        fuel_type=data.get('fuel_type'),
        pickup_address=data.get('address'),
        preferred_date=data.get('date'),
        total_amount=service.price,
        status=booking_status,
        payment_status=payment_status,
        payment_method=payment_method,
        payment_ref=payment_ref or ''
    )
    db.session.add(new_booking)
    db.session.commit()

    send_sms(
        data.get('phone', ''),
        f"Hi {data.get('name')}! Valtrion booking confirmed. Service: {service.name}, Date: {data.get('date')}, Amount: Rs.{int(service.price)}. Booking #V{new_booking.id:04d}. Team Valtrion."
    )

    send_booking_emails(new_booking, service)

    return new_booking


@booking.route('/book/<int:service_id>')
@login_required
def book_service(service_id):
    service = Service.query.get_or_404(service_id)
    return render_template('booking.html', service=service, upi_id='dhanushkoti08-3@okicici')


@booking.route('/confirm-booking', methods=['POST'])
@login_required
def confirm_booking():
    try:
        data = request.get_json(silent=True) or {}
        service = Service.query.get_or_404(data.get('service_id'))
        payment_method = data.get('payment_method') or 'COD'
        booking_status = 'Confirmed' if payment_method != 'COD' else 'Pending'
        payment_status = 'Paid' if payment_method != 'COD' else 'COD'
        new_booking = _save_booking(
            data,
            service,
            payment_method,
            data.get('payment_ref', ''),
            payment_status,
            booking_status,
        )
        return jsonify({'success': True, 'booking_id': new_booking.id})
    except Exception as exc:
        print('Booking error:', exc)
        return jsonify({'success': False, 'error': str(exc)}), 500


@booking.route('/razorpay/create-order', methods=['POST'])
@login_required
def razorpay_create_order():
    try:
        data = request.get_json(silent=True) or {}
        service = Service.query.get_or_404(data.get('service_id'))
        client = _get_razorpay_client()
        order = client.order.create({
            'amount': int(round(float(service.price) * 100)),
            'currency': 'INR',
            'receipt': f'valtrion_{current_user.id}_{service.id}_{int(datetime.utcnow().timestamp())}',
            'payment_capture': 1,
        })
        return jsonify({
            'success': True,
            'order_id': order['id'],
            'amount': int(round(float(service.price) * 100)),
            'currency': 'INR',
            'key_id': current_app.config.get('RAZORPAY_KEY_ID'),
            'service_name': service.name,
            'customer_name': current_user.name,
            'customer_email': current_user.email,
            'customer_phone': current_user.phone,
        })
    except Exception as exc:
        print('Razorpay order error:', exc)
        return jsonify({'success': False, 'error': str(exc)}), 500


@booking.route('/razorpay/verify-payment', methods=['POST'])
@login_required
def razorpay_verify_payment():
    try:
        data = request.get_json(silent=True) or {}
        service = Service.query.get_or_404(data.get('service_id'))
        payment_id = (data.get('razorpay_payment_id') or '').strip()
        order_id = (data.get('razorpay_order_id') or '').strip()
        signature = (data.get('razorpay_signature') or '').strip()
        if not payment_id or not order_id or not signature:
            return jsonify({'success': False, 'error': 'Missing Razorpay payment details.'}), 400

        client = _get_razorpay_client()
        client.utility.verify_payment_signature({
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature,
        })

        new_booking = _save_booking(
            data,
            service,
            'Razorpay',
            f'{payment_id} | {order_id}',
            'Paid',
            'Confirmed',
        )
        return jsonify({'success': True, 'booking_id': new_booking.id})
    except SignatureVerificationError:
        return jsonify({'success': False, 'error': 'Payment signature verification failed.'}), 400
    except Exception as exc:
        print('Razorpay verify error:', exc)
        return jsonify({'success': False, 'error': str(exc)}), 500


@booking.route('/payment/success/<int:booking_id>')
@login_required
def payment_success(booking_id):
    booking_record = Booking.query.get_or_404(booking_id)
    return render_template('payment_success.html', booking=booking_record)


@booking.route('/cancel/<int:booking_id>')
@login_required
def cancel_booking(booking_id):
    booking_record = Booking.query.get_or_404(booking_id)
    if booking_record.user_id == current_user.id:
        booking_record.status = 'Cancelled'
        db.session.commit()
        flash('Booking cancelled.', 'warning')
    return redirect(url_for('main.dashboard'))


@booking.route('/invoice/<int:booking_id>')
@login_required
def download_invoice(booking_id):
    booking_record = Booking.query.get_or_404(booking_id)
    if booking_record.user_id != current_user.id and getattr(current_user, 'role', '') != 'admin':
        flash('Unauthorized', 'danger')
        return redirect(url_for('main.dashboard'))

    html = f"""<html><head><style>
    body{{font-family:Arial;padding:40px;background:#fff;color:#000;}}
    .row{{display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid #f0f0f0;}}
    .total{{display:flex;justify-content:space-between;padding:16px 0;font-size:22px;font-weight:bold;color:#0066FF;}}
    .badge{{background:#e6fff2;padding:4px 12px;border-radius:20px;color:#00aa55;font-weight:bold;font-size:13px;}}
    </style></head><body>
    <div style="text-align:center;border-bottom:3px solid #0066FF;padding-bottom:20px;margin-bottom:30px;">
    <div style="font-size:36px;font-weight:bold;color:#0066FF;letter-spacing:8px;">VALTRION</div>
    <p style="color:#666;">Expert Care for Every Car</p>
    <p style="font-size:18px;color:#333;">Invoice #{str(booking_record.id).zfill(4)}</p></div>
    <div class="row"><span>Customer</span><strong>{booking_record.customer_name}</strong></div>
    <div class="row"><span>Phone</span><strong>{booking_record.customer_phone}</strong></div>
    <div class="row"><span>Car</span><strong>{booking_record.car_brand} {booking_record.car_model} ({booking_record.fuel_type})</strong></div>
    <div class="row"><span>Car Number</span><strong>{booking_record.car_number or 'N/A'}</strong></div>
    <div class="row"><span>Service</span><strong>{booking_record.service.name}</strong></div>
    <div class="row"><span>Date</span><strong>{booking_record.preferred_date}</strong></div>
    <div class="row"><span>Address</span><strong>{booking_record.pickup_address}</strong></div>
    <div class="row"><span>Payment Method</span><strong>{booking_record.payment_method or 'UPI'}</strong></div>
    <div class="row"><span>Status</span><span class="badge">{booking_record.status}</span></div>
    <div class="row"><span>UPI / Ref</span><strong>{booking_record.payment_ref or 'dhanushkoti08-3@okicici'}</strong></div>
    <div class="row"><span>Date of Booking</span><strong>{booking_record.created_at.strftime('%d %b %Y')}</strong></div>
    <div class="total"><span>Total Amount</span><span>Rs. {int(booking_record.total_amount)}</span></div>
    <div style="text-align:center;margin-top:30px;color:#999;font-size:12px;line-height:1.8;">
    <strong style="color:#0066FF;">VALTRION Automotive Services</strong><br>
    valtrionbookings@gmail.com | +91 9686681036<br>
    30-Day Service Warranty | Transparent Pricing<br>Thank you for choosing Valtrion!</div>
    </body></html>"""
    response = make_response(html)
    response.headers['Content-Type'] = 'text/html'
    return response