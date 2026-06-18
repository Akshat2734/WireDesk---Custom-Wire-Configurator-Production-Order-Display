import pytest
from app import create_app
from online_version.model.order_sql import db, OrdersDB

@pytest.fixture
def client():
    # Configure the app for testing with an in-memory database
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    # Override replica bind to also use the memory DB during testing
    app.config['SQLALCHEMY_BINDS'] = {'replica': 'sqlite:///:memory:'}
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all() # Build temporary tables
            yield client
            db.drop_all() # Destroy temporary tables

def test_view_orders_empty(client):
    """Ensure the GET route returns a 200 OK and an empty list initially."""
    response = client.get('/view_orders')
    assert response.status_code == 200
    assert response.get_json() == []

def test_create_order_requires_idempotency_key(client):
    """Ensure the POST route rejects requests missing the idempotency header."""
    # Note: In a real test, you would mock the JWT token here
    response = client.post('/create_order', json={"wire_type": "house_wire"})
    assert response.status_code == 400
    assert "Missing X-Idempotency-Key" in response.get_json()["error"]