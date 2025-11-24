from app import create_app

app = create_app()
with app.test_client() as c:
    resp = c.get('/')
    print('STATUS', resp.status_code)
    print(resp.data.decode()[:200])
