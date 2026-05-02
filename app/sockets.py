from flask_login import current_user
from flask_socketio import emit, join_room
from datetime import timezone, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from app import db
from app.models import ChatMessage, User


try:
    IST = ZoneInfo('Asia/Kolkata')
except ZoneInfoNotFoundError:
    # Fallback for environments where tzdata package is missing.
    IST = timezone(timedelta(hours=5, minutes=30))


def register_sockets(socketio):

    def _format_chat_time(dt):
        # Chat timestamps are stored as naive UTC in DB; render consistently in IST.
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(IST).strftime('%I:%M %p')

    def _format_message(msg):
        return {
            'id': msg.id,
            'user_id': msg.user_id,
            'sender': msg.sender,
            'message': msg.message,
            'time': _format_chat_time(msg.created_at),
            'created_at': msg.created_at.isoformat()
        }

    def _thread_preview(user_id):
        user = User.query.get(user_id)
        if not user:
            return None

        latest = ChatMessage.query.filter_by(user_id=user_id).order_by(ChatMessage.created_at.desc()).first()
        unread = ChatMessage.query.filter_by(user_id=user_id, sender='customer', is_read=False).count()

        return {
            'user_id': user.id,
            'name': user.name,
            'phone': user.phone,
            'latest_message': latest.message if latest else '',
            'latest_sender': latest.sender if latest else None,
            'latest_time': _format_chat_time(latest.created_at) if latest else '',
            'unread': unread
        }

    @socketio.on('join')
    def on_join(data):
        room = (data or {}).get('room')
        if room:
            join_room(room)

    @socketio.on('join_chat')
    def join_chat():
        if not current_user.is_authenticated:
            return

        if current_user.role == 'admin':
            join_room('admins')
        else:
            join_room(f'user_{current_user.id}')

    @socketio.on('customer_send_message')
    def handle_customer_message(data):
        if not current_user.is_authenticated or current_user.role == 'admin':
            return

        user_id = current_user.id
        message_text = ((data or {}).get('message') or '').strip()
        if not message_text:
            return

        msg = ChatMessage(user_id=user_id, message=message_text, sender='customer', is_read=False)
        db.session.add(msg)
        db.session.commit()

        payload = _format_message(msg)
        preview = _thread_preview(user_id)
        emit('chat_message', payload, room=f'user_{user_id}')
        emit('chat_message', payload, room='admins')
        if preview:
            emit('chat_thread_update', preview, room='admins')

    @socketio.on('admin_send_message')
    def handle_admin_reply(data):
        if not current_user.is_authenticated or current_user.role != 'admin':
            return

        user_id = (data or {}).get('user_id')
        message_text = ((data or {}).get('message') or '').strip()
        if not user_id or not message_text:
            return

        user = User.query.get(user_id)
        if not user:
            return

        msg = ChatMessage(user_id=user_id, message=message_text, sender='admin', is_read=False)
        db.session.add(msg)
        db.session.commit()

        payload = _format_message(msg)
        preview = _thread_preview(user_id)
        emit('chat_message', payload, room=f'user_{user_id}')
        emit('chat_message', payload, room='admins')
        if preview:
            emit('chat_thread_update', preview, room='admins')