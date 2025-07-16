import pytest
from app import app
from db import connect_to_db, load_config
from datetime import datetime, timedelta

@pytest.fixture(scope="module")
def client():
    # Přepnutí na testovací DB
    config = load_config(testing=True)
    conn = connect_to_db(config)

    # Vyčištění tabulek
    cursor = conn.cursor()
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    cursor.execute("TRUNCATE TABLE reservations")
    cursor.execute("TRUNCATE TABLE facilities")
    cursor.execute("TRUNCATE TABLE users")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    conn.commit()

    # Seed dat
    cursor.execute("""
        INSERT INTO users (username, email, password, role)
        VALUES ('seeduser', 'seed@example.com', 'pass', 'user');
     """)
    cursor.execute("""
        INSERT INTO facilities (id, name, location, description, available)
        VALUES (1, 'Test Hřiště', 'Brno', 'Testovací popis', TRUE)
    """)
    start = datetime.now() + timedelta(hours=1)
    end = start + timedelta(hours=2)
    cursor.execute("""
        INSERT INTO reservations (user_id, facility_id, date, start_time, end_time)
        VALUES (1, 1, %s, %s, %s)
    """, (start.date(), start.time(), end.time()))

    conn.commit()
    cursor.close()
    conn.close()

    # Flask test client
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_get_users(client):
    response = client.get('/users')
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)

def test_get_user_by_id(client):
    response = client.get('/users/1')
    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == 1
    assert "username" in data

def test_get_user_not_found(client):
    response = client.get('/users/9999')
    assert response.status_code == 404
    assert "error" in response.get_json()

def test_post_user_missing_data(client):
    response = client.post('/users', json={"username": "test"})
    assert response.status_code == 400
    assert 'error' in response.get_json()

def test_post_user_success(client):
    user_data = {
        "username": "test_user",
        "email": "test@example.com",
        "password": "secret",
        "role": "user"
    }
    response = client.post('/users', json=user_data)
    assert response.status_code == 201
    assert 'message' in response.get_json()

def test_delete_user(client):
    # Nejprve přidáme nového uživatele
    response = client.post('/users', json={
        "username": "delete_me",
        "email": "deleteme@example.com",
        "password": "xxx",
        "role": "user"
    })
    assert response.status_code == 201

    # Pak ho smažeme
    users = client.get('/users', query_string={"email": "deleteme@example.com"}).get_json()
    user_id = users[0]["id"]
    response = client.delete(f"/users/{user_id}")
    assert response.status_code == 200
    assert "message" in response.get_json()

def test_get_facility_by_id(client):
    response = client.get('/facilities/1')
    assert response.status_code == 200
    assert "name" in response.get_json()

def test_get_facility_not_found(client):
    response = client.get('/facilities/9999')
    assert response.status_code == 404

def test_post_facility_success(client):
    response = client.post('/facilities', json={
        "name": "Nové hřiště",
        "location": "Brno",
        "description": "Testovací hřiště",
        "available": True
    })
    assert response.status_code == 201
    assert "message" in response.get_json()

def test_post_facility_missing_data(client):
    response = client.post('/facilities', json={"name": "Jen jméno"})
    assert response.status_code == 400
    assert "error" in response.get_json()

# def test_get_reservations(client):
#     response = client.get('/reservations')
#     assert response.status_code == 200 or response.status_code == 405  # pokud žádná není
#     assert isinstance(response.get_json(), list)

def test_get_reservation_by_id(client):
    response = client.get('/reservations/1')
    assert response.status_code == 200 or response.status_code == 405  # pokud žádná není

# def test_post_reservation_success(client):
#     response = client.post('/reservations', json={
#         "user_id": 1,
#         "facility_id": 1,
#         "start_time": "09:00:00",
#         "end_time": "10:00:00",
#         "status": "pending"
#     })
#     assert response.status_code == 201
#     assert "message" in response.get_json()

def test_post_reservation_invalid_data(client):
    # Chybí `user_id` a další
    response = client.post('/reservations', json={
        "date": "2025-07-01",
        "start_time": "09:00:00"
    })
    assert response.status_code == 400
    assert "error" in response.get_json()

# def test_delete_reservation(client):
#     # Přidej rezervaci, pak smaž
#     res = client.post('/reservations', json={
#         "user_id": 1,
#         "facility_id": 1,
#         "date": "2025-07-01",
#         "start_time": "11:00:00",
#         "end_time": "12:00:00"
#     })
#     assert res.status_code == 201

#     all_res = client.get('/reservations').get_json()
#     new_res_id = all_res[-1]["ID"]
#     response = client.delete(f"/reservations/{new_res_id}")
#     assert response.status_code == 200
#     assert "message" in response.get_json()
