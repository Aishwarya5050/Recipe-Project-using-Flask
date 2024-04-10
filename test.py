import pytest
from app import app, db, User

@pytest.fixture
def client():
    app.config['TESTING'] = True
    client = app.test_client()

   
    with app.app_context():
        db.create_all()
        yield client
        db.drop_all()

def test_registration(client):

    response = client.post('/register', data={'username': 'test_user', 'password': 'test_password'})
    assert response.status_code == 302

    with app.app_context():
        user = User.query.filter_by(username='test_user').first()
        assert user is not None
