from flask_socketio import emit, join_room
from flask_login import current_user
from app.models import ChatMessage, User
from app import db
from datetime import datetime

def register_sockets(socketio):

    @socketio.on('join')
    def on_join(data):
        room = data.get('room')
        join_room(room)

    @socketio.on('customer_message')
    def handle_customer_msg(data):
        user_id = data.get('user_id')
        msg_text = data.get('message', '').strip()
        if not msg_text:
            return
        msg = ChatMessage(user_id=user_id, message=msg_text, sender='customer')
        db.session.add(msg)
        db.session.commit()
        emit('new_customer_message', {
            'user_id': user_id,
            'message': msg_text,
            'time': datetime.utcnow().strftime('%I:%M %p'),
            'msg_id': msg.id
        }, room='admin_room')
        emit('message_sent', {
            'message': msg_text,
            'time': datetime.utcnow().strftime('%I:%M %p'),
            'msg_id': msg.id
        }, room=f'user_{user_id}')

    @socketio.on('admin_reply')
    def handle_admin_reply(data):
        user_id = data.get('user_id')
        msg_text = data.get('message', '').strip()
        if not msg_text:
            return
        msg = ChatMessage(user_id=user_id, message=msg_text, sender='admin')
        db.session.add(msg)
        db.session.commit()
        emit('admin_message', {
            'message': msg_text,
            'time': datetime.utcnow().strftime('%I:%M %p'),
            'msg_id': msg.id
        }, room=f'user_{user_id}')
        emit('reply_sent', {
            'user_id': user_id,
            'message': msg_text,
            'time': datetime.utcnow().strftime('%I:%M %p')
        }, room='admin_room')