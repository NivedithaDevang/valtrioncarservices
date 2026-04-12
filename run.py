from app import create_app, socketio, db
from app.sockets import register_sockets

app = create_app()
register_sockets(socketio)


def _init_db():
    with app.app_context():
        db.create_all()


_init_db()

if __name__ == '__main__':
    socketio.run(app, debug=True)