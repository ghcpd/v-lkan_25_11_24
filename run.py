from app import create_app
from app.models import UserDatabase

app = create_app()

if __name__ == '__main__':
    try:
        print('Initializing database and starting Flask app...')
        UserDatabase.init_db()
        # Run without the reloader to avoid background process confusion on Windows
        print('Starting Flask app on http://127.0.0.1:5000 (only bound to localhost)')
        app.run(debug=True, host='127.0.0.1', port=5000, use_reloader=False)
    except Exception as e:
        import traceback
        traceback.print_exc()
        print('\nFailed to start the server. Press Enter to exit...')
        try:
            input()
        except Exception:
            pass
