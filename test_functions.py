import pytest
from db import connect_to_db
from datetime import datetime, timedelta, date, time
from repository import (
    get_all_users, get_all_facilities, get_all_reservations, add_user,
    add_facility, add_reservation, update_user_password, update_facility_availability,
    update_reservation_status, delete_user, delete_reservation
)

# Fixture: připojení k testovací databázi
@pytest.fixture
def db_conn():
    conn = connect_to_db(testing=True)  # ✅ důležité!
    yield conn
    conn.close()

# Fixture: vyčištění dat před každým testem
@pytest.fixture(autouse=True)
def clear_test_data(db_conn):
    cursor = db_conn.cursor()
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    cursor.execute("TRUNCATE TABLE reservations")
    cursor.execute("TRUNCATE TABLE users")
    cursor.execute("TRUNCATE TABLE facilities")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    db_conn.commit()
    cursor.close()

# Test: přidání uživatele
def test_add_user(db_conn):
    add_user("TestUser", "test@example.com", "pass123", "user", conn=db_conn)
    users = get_all_users(conn=db_conn)
    assert any(user[1] == "TestUser" for user in users)

# Test: výpis uživatelů
def test_get_all_users(db_conn):
    add_user("AnotherUser", "another@example.com", "pass456", "user", conn=db_conn)
    users = get_all_users(conn=db_conn)
    assert len(users) > 0

# Test: smazání uživatele
def test_delete_user(db_conn):
    add_user("DeleteUser", "del@example.com", "pass", conn=db_conn)
    users = get_all_users(conn=db_conn)
    user_id = next(u[0] for u in users if u[1] == "DeleteUser")
    delete_user(user_id, conn=db_conn)
    users_after = get_all_users(conn=db_conn)
    assert all(u[0] != user_id for u in users_after)

# Test: přidání sportoviště
def test_add_facility(db_conn):
    add_facility("Hřiště A", "Popis hřiště A", True, conn=db_conn)
    facilities = get_all_facilities(conn=db_conn)
    assert any(f[1] == "Hřiště A" for f in facilities)

# Test: výpis sportovišť
def test_get_all_facilities(db_conn):
    add_facility("Hřiště B", "Popis B", True, conn=db_conn)
    facilities = get_all_facilities(conn=db_conn)
    assert len(facilities) > 0

# Test: přidání a výpis rezervace
def test_add_and_get_reservation(db_conn):
    add_user("ResUser", "res@example.com", "pass", conn=db_conn)
    add_facility("Hřiště R", "Rezervace test", True, conn=db_conn)

    user_id = get_all_users(conn=db_conn)[0][0]
    facility_id = get_all_facilities(conn=db_conn)[0][0]
    today = date.today()
    add_reservation(user_id, facility_id, today, time(10, 0), time(11, 0), conn=db_conn)
    reservations = get_all_reservations(conn=db_conn)
    assert any(r[1] == "ResUser" for r in reservations)

# Test: změna stavu rezervace
def test_update_reservation_status(db_conn):
    add_user("StatusUser", "status@example.com", "pass", conn=db_conn)
    add_facility("Hřiště S", "Status test", True, conn=db_conn)
    user_id = get_all_users(conn=db_conn)[0][0]
    facility_id = get_all_facilities(conn=db_conn)[0][0]
    today = date.today()
    add_reservation(user_id, facility_id, today, time(12, 0), time(13, 0), conn=db_conn)

    reservation_id = get_all_reservations(conn=db_conn)[0][0]
    update_reservation_status(reservation_id, "confirmed", conn=db_conn)
    updated = get_all_reservations(conn=db_conn)[0]
    assert updated[-1] == "confirmed"

# Test: smazání rezervace
def test_delete_reservation(db_conn):
    add_user("DelUser", "delres@example.com", "pass", conn=db_conn)
    add_facility("Hřiště D", "Delete test", True, conn=db_conn)
    user_id = get_all_users(conn=db_conn)[0][0]
    facility_id = get_all_facilities(conn=db_conn)[0][0]
    today = date.today()
    add_reservation(user_id, facility_id, today, time(14, 0), time(15, 0), conn=db_conn)

    reservation_id = get_all_reservations(conn=db_conn)[0][0]
    delete_reservation(reservation_id, conn=db_conn)
    reservations = get_all_reservations(conn=db_conn)
    assert all(r[0] != reservation_id for r in reservations)