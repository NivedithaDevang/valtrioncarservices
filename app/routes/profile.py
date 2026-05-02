from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db, bcrypt
from app.models import Booking, ChatMessage
from datetime import timezone, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

profile = Blueprint('profile', __name__)
try:
    IST = ZoneInfo('Asia/Kolkata')
except ZoneInfoNotFoundError:
    IST = timezone(timedelta(hours=5, minutes=30))


def _format_chat_time(dt):
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(IST).strftime('%I:%M %p')

@profile.route('/profile')
@login_required
def view_profile():
    bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.created_at.desc()).all()
    return render_template('profile.html', user=current_user, bookings=bookings)

@profile.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    data = request.json
    current_user.name    = data.get('name', current_user.name)
    current_user.phone   = data.get('phone', current_user.phone)
    current_user.email   = data.get('email', current_user.email)
    current_user.address = data.get('address', current_user.address)
    db.session.commit()
    return jsonify({'success': True})

@profile.route('/profile/change-password', methods=['POST'])
@login_required
def change_password():
    data = request.json
    if not bcrypt.check_password_hash(current_user.password, data.get('current_password','')):
        return jsonify({'success': False, 'error': 'Current password is wrong'})
    current_user.password = bcrypt.generate_password_hash(data.get('new_password')).decode('utf-8')
    db.session.commit()
    return jsonify({'success': True})

@profile.route('/chat/history')
@login_required
def chat_history():
    msgs = ChatMessage.query.filter_by(user_id=current_user.id).order_by(ChatMessage.created_at.asc()).all()
    ChatMessage.query.filter_by(user_id=current_user.id, sender='admin', is_read=False).update({'is_read': True})
    db.session.commit()
    return jsonify([
        {
            'id': m.id,
            'user_id': m.user_id,
            'sender': m.sender,
            'message': m.message,
            'time': _format_chat_time(m.created_at),
            'created_at': m.created_at.isoformat()
        }
        for m in msgs
    ])

