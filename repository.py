from db import connect_to_db

def get_all_users(conn=None):
    """
    Vrátí seznam všech uživatelů z tabulky users.
    Pokud není předáno připojení (conn), funkce si vytvoří vlastní.
    """
    close_conn = False
    if conn is None:
        conn = connect_to_db()
        close_conn = True

    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email FROM users")
    results = cursor.fetchall()

    cursor.close()
    if close_conn:
        conn.close()

    return results

def get_all_facilities(conn=None):
    close_conn = False
    if conn is None:
        conn = connect_to_db()
        close_conn = True
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, available FROM facilities")
    results = cursor.fetchall()
    print("--- Sportoviště ---")
    for facility_id, name, available in results:
        dostupnost = "ANO" if available else "NE"
        print(f"ID: {facility_id}, Název: {name}, Dostupné: {dostupnost}")
    cursor.close()
    if close_conn:
        conn.close()
    return results

def get_all_reservations(conn=None):
    close_conn = False
    if conn is None:
        conn = connect_to_db()
        close_conn = True
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, user_id, facility_id, start_time, end_time, status 
        FROM reservation
    """)
    results = cursor.fetchall()
    print("--- Rezervace ---")
    for res_id, user_id, facility_id, start, end, status in results:
        print(f"ID: {res_id}, Uživatel: {user_id}, Sportoviště: {facility_id}, Od: {start}, Do: {end}, Stav: {status}")
    cursor.close()
    if close_conn:
        conn.close()
    return results

def add_user(username, email, password, role='user', conn=None):
    close_conn = False
    if conn is None:
        conn = connect_to_db()
        close_conn = True

    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, %s)",
        (username, email, password, role)
    )
    conn.commit()
    print("✅ Uživatel přidán.")
    cursor.close()
    if close_conn:
        conn.close()

def add_facility(name, description, available=True, conn=None):
    close_conn = False
    if conn is None:
        conn = connect_to_db()
        close_conn = True

    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO facilities (name, description, available) VALUES (%s, %s, %s)",
        (name, description, available)
    )
    conn.commit()
    print("✅ Sportoviště přidáno.")
    cursor.close()
    if close_conn:
        conn.close()

def add_reservation(user_id, facility_id, start_time, end_time, status="pending", conn=None):
    close_conn = False
    if conn is None:
        conn = connect_to_db()
        close_conn = True

    cursor = conn.cursor()
    query = """
        INSERT INTO reservations (user_id, facility_id, start_time, end_time, status)
        VALUES (%s, %s, %s, %s, %s)
    """
    data = (user_id, facility_id, start_time, end_time, status)
    cursor.execute(query, data)
    conn.commit()
    print("✅ Rezervace přidána.")
    cursor.close()
    if close_conn:
        conn.close()

user_list = [
    ("jirka", "jirka@email.cz", "pw123", "user"),
    ("katka", "katka@email.cz", "pw456", "admin")
]

def add_multiple_users(user_list, conn=None):
    close_conn = False
    if conn is None:
        conn = connect_to_db()
        close_conn = True

    cursor = conn.cursor()
    query = "INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, %s)"
    cursor.executemany(query, user_list)
    conn.commit()
    print(f"✅ Vloženo {cursor.rowcount} uživatelů.")
    cursor.close()
    if close_conn:
        conn.close()

def update_user_password(user_id, new_password, conn=None):
    close_conn = False
    if conn is None:
        conn = connect_to_db()
        close_conn = True

    cursor = conn.cursor()
    query = "UPDATE users SET password = %s WHERE id = %s"
    cursor.execute(query, (new_password, user_id))

    conn.commit()
    print("🔐 Heslo uživatele bylo aktualizováno.")

    cursor.close()
    if close_conn:
        conn.close()

def update_facility_availability(facility_id, is_available, conn=None):
    close_conn = False
    if conn is None:
        conn = connect_to_db()
        close_conn = True

    cursor = conn.cursor()
    query = "UPDATE facilitie SET available = %s WHERE id = %s"
    cursor.execute(query, (is_available, facility_id))

    conn.commit()
    print("📍 Stav dostupnosti sportoviště byl změněn.")

    cursor.close()
    if close_conn:
        conn.close()

def update_reservation_status(reservation_id, new_status, conn=None):
    close_conn = False
    if conn is None:
        conn = connect_to_db()
        close_conn = True

    cursor = conn.cursor()
    query = "UPDATE reservation SET status = %s WHERE id = %s"
    cursor.execute(query, (new_status, reservation_id))

    conn.commit()
    print(f"📦 Stav rezervace byl změněn na '{new_status}'.")

    cursor.close()
    if close_conn:
        conn.close()

def delete_user(user_id, conn=None):
    close_conn = False
    if conn is None:
        conn = connect_to_db()
        close_conn = True

    cursor = conn.cursor()
    query = "DELETE FROM users WHERE id = %s"
    data = (user_id,)
    cursor.execute(query, data)
    conn.commit()
    print(f"🗑️ Uživatel s ID {user_id} byl smazán.")
    cursor.close()

    if close_conn:
        conn.close()

def delete_reservation(reservation_id, conn=None):
    close_conn = False
    if conn is None:
        conn = connect_to_db()
        close_conn = True

    cursor = conn.cursor()
    query = "DELETE FROM reservation WHERE id = %s"
    data = (reservation_id,)
    cursor.execute(query, data)
    conn.commit()
    print(f"📦 Rezervace s ID {reservation_id} byla smazána.")
    cursor.close()

    if close_conn:
        conn.close()

# Přidáné funkce 
def get_user_by_id(user_id, conn=None):
    close_conn = False
    if conn is None:
        conn = connect_to_db()
        close_conn = True

    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM users WHERE id = %s"
    cursor.execute(query, (user_id,))
    user = cursor.fetchone()
    cursor.close()

    if close_conn:
        conn.close()

    return user

def get_facilities_by_id(facility_id, conn=None):
    close_conn = False
    if conn is None:
        conn = connect_to_db()
        close_conn = True

    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM facilities WHERE id = %s"
    cursor.execute(query, (facility_id,))
    facility = cursor.fetchone()
    cursor.close()

    if close_conn:
        conn.close()

    return facility

def delete_facility(facility_id, conn=None):
    close_conn = False
    if conn is None:
        conn = connect_to_db()
        close_conn = True

    cursor = conn.cursor()
    query = "DELETE FROM facilities WHERE id = %s"
    cursor.execute(query, (facility_id,))
    conn.commit()
    print(f"🗑️ Sportoviště s ID {facility_id} bylo smazáno.")
    cursor.close()

    if close_conn:
        conn.close()


def get_filtered_reservations(user_id=None, facility_id=None, date=None, status=None, conn=None):
    close_conn = False
    if conn is None:
        conn = connect_to_db()
        close_conn = True

    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM reservations WHERE 1=1"
    values = []

    if user_id:
        query += " AND user_id = %s"
        values.append(user_id)
    if facility_id:
        query += " AND facility_id = %s"
        values.append(facility_id)
    if date:
        query += " AND date = %s"
        values.append(date)
    if status:
        query += " AND status = %s"
        values.append(status)

    cursor.execute(query, values)
    results = cursor.fetchall()

    cursor.close()
    if close_conn:
        conn.close()

    return results
