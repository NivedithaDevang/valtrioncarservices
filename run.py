import os

try:
    from gevent import monkey
    monkey.patch_all()
except Exception:
    # Render will still boot, but websocket support is best when gevent is available.
    pass

from app import create_app, socketio, db
from app.sockets import register_sockets

app = create_app()
register_sockets(socketio)


def _init_db():
    with app.app_context():
        db.create_all()


_init_db()


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() in ('1', 'true', 'yes')
    socketio.run(app, host='0.0.0.0', port=port, debug=debug, use_reloader=False)