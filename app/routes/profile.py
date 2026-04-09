from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db, bcrypt
from app.models import Booking

profile = Blueprint('profile', __name__)

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

@profile.route('/chat/history/<int:user_id>')
@login_required
def chat_history(user_id):
    from app.models import ChatMessage
    msgs = ChatMessage.query.filter_by(user_id=user_id).order_by(ChatMessage.created_at.asc()).all()
    return jsonify([{'sender': m.sender, 'message': m.message, 'time': m.created_at.strftime('%I:%M %p')} for m in msgs])