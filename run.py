from app import create_app
from app.models import UserDatabase
from werkzeug.serving import make_server

app = create_app()

if __name__ == '__main__':
    UserDatabase.init_db()
    # Use a deterministic WSGI server to avoid reloader/thread issues on Windows
    host = '0.0.0.0'
    port = 5000
    server = make_server(host, port, app)
    print(f" * Serving Flask app 'app' via werkzeug.make_server on http://{host}:{port} (Press CTRL+C to quit)")
    server.serve_forever()
