import pytest
from datetime import datetime, timedelta
from db import connect_to_db
from config import load_config
import mysql.connector
from mysql.connector import Error
from mysql.connector.errors import IntegrityError



# ---- Pomocná funkce pro vytvoření tabulek (jen v testovací DB) ----

def create_tables_if_not_exist(cursor):
    try:
        # USERS
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL,
                email VARCHAR(100) NOT NULL UNIQUE,
                password VARCHAR(100) NOT NULL,
                role ENUM('admin', 'user') NOT NULL DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # FACILITIES
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS facilities (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                location VARCHAR(100),
                description TEXT,
                available BOOLEAN DEFAULT TRUE
            )
        """)

        # RESERVATIONS
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reservations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                facility_id INT,
                date DATE NOT NULL,
                start_time TIME NOT NULL,
                end_time TIME NOT NULL,
                status ENUM('pending', 'confirmed', 'cancelled') DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (facility_id) REFERENCES facilities(id) ON DELETE CASCADE
            )
        """)

    except Error as e:
        print(f"❗ Chyba při vytváření tabulek: {e}")


# ---- FIXTURE pro připojení k testovací DB ----

@pytest.fixture(scope="module")
def db():
    config = load_config(testing=True)
    conn = connect_to_db(config)
    cursor = conn.cursor()
    create_tables_if_not_exist(cursor)  # vytvoření tabulek, pokud nejsou
    yield cursor
    conn.rollback()  # zruší všechny změny po testech
    cursor.close()
    conn.close()


# ---- FIXTURE pro seed dat ----

@pytest.fixture(autouse=True)
def seed_test_data(db):
    # Vyčisti tabulky
    db.execute("SET FOREIGN_KEY_CHECKS = 0")
    db.execute("TRUNCATE TABLE reservations")
    db.execute("TRUNCATE TABLE facilities")
    db.execute("TRUNCATE TABLE users")
    db.execute("SET FOREIGN_KEY_CHECKS = 1")

    # Vlož uživatele
    db.execute("""
        INSERT INTO users (id, username, email, password, role)
        VALUES (1, 'user1', 'user1@example.com', 'pass', 'user')
    """)

    # Vlož sportoviště
    db.execute("""
        INSERT INTO facilities (id, name, location, description, available)
        VALUES (1, 'Hřiště 1', 'Praha', 'Popis hřiště', TRUE)
    """)

    # Vlož rezervaci
    start = datetime.now() + timedelta(hours=1)
    end = start + timedelta(hours=2)
    db.execute("""
        INSERT INTO reservations (user_id, facility_id, date, start_time, end_time)
        VALUES (1, 1, %s, %s, %s)
    """, (start.date(), start.time(), end.time()))


# ---- TESTY ----

def test_email_not_null(db):
    db.execute("SELECT * FROM users WHERE email IS NULL")
    assert db.fetchall() == []

def test_email_not_empty(db):
    db.execute("SELECT * FROM users WHERE email = ''")
    assert db.fetchall() == []

def test_duplicate_email(db):
    db.execute("INSERT INTO users (username, email, password, role) VALUES ('Tester1', 'dup@example.com', 'pass', 'user')")
    with pytest.raises(IntegrityError):
        db.execute("INSERT INTO users (username, email, password, role) VALUES ('Tester2', 'dup@example.com', 'pass', 'user')")

def test_email_format(db):
    db.execute("SELECT email FROM users")
    for (email,) in db.fetchall():
        assert "@" in email and "." in email.split("@")[-1]

def test_role_enum(db):
    db.execute("SELECT role FROM users")
    for (role,) in db.fetchall():
        assert role in ['user', 'admin']

def test_created_at_valid_date(db):
    db.execute("SELECT created_at FROM users")
    for (created_at,) in db.fetchall():
        assert isinstance(created_at, datetime)

def test_facility_name_not_empty(db):
    db.execute("SELECT name FROM facilities")
    for (name,) in db.fetchall():
        assert name.strip() != ""

def test_facility_description_length(db):
    db.execute("SELECT description FROM facilities")
    for (desc,) in db.fetchall():
        assert len(desc) <= 65535  # TEXT má limit 64KB

def test_facility_available_boolean(db):
    db.execute("SELECT available FROM facilities")
    for (available,) in db.fetchall():
        assert available in (0, 1)

def test_reservation_foreign_keys(db):
    db.execute("SELECT id FROM users")
    user_ids = {u[0] for u in db.fetchall()}
    db.execute("SELECT id FROM facilities")
    facility_ids = {f[0] for f in db.fetchall()}
    db.execute("SELECT user_id, facility_id FROM reservations")
    for user_id, facility_id in db.fetchall():
        assert user_id in user_ids
        assert facility_id in facility_ids

def test_end_time_after_start_time(db):
    db.execute("SELECT start_time, end_time FROM reservations")
    for start, end in db.fetchall():
        assert end > start


def test_status_default_pending(db):
    # Přidání nové rezervace bez statusu
    start = datetime.now() + timedelta(hours=3)
    end = start + timedelta(hours=1)
    db.execute("""
        INSERT INTO reservations (user_id, facility_id, date, start_time, end_time)
        VALUES (1, 1, %s, %s, %s)
    """, (start.date(), start.time(), end.time()))
    db.execute("SELECT status FROM reservations ORDER BY id DESC LIMIT 1")
    (status,) = db.fetchone()
    assert status == 'pending'
