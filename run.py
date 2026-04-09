from app import create_app, socketio, db
from app.sockets import register_sockets

app = create_app()
register_sockets(socketio)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True)