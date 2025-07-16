from flask import Flask, jsonify, request
from db import connect_to_db
from repository import (
    add_user, delete_user, get_user_by_id,
    add_facility, get_facilities_by_id, delete_facility,
    delete_reservation, add_reservation)
from datetime import time, date, timedelta, datetime

app = Flask(__name__)

# Metody pro tabulku users

# GET /users/<id> – získání konkrétního uživatele podle ID
@app.route('/users/<int:user_id>', methods=['GET'])
def api_get_user_by_id(user_id):
    conn = connect_to_db()
    user = get_user_by_id(user_id, conn=conn)
    conn.close()

    if user:
        return jsonify(user)
    else:
        return jsonify({"error": "Uživatel nenalezen"}), 404

# GET /users – výpis uživatelů s možností filtrování přes query parametry
@app.route('/users', methods=['GET'])
def api_get_users():
    conn = connect_to_db()
    cursor = conn.cursor(dictionary=True)

    base_query = "SELECT * FROM users WHERE 1=1"
    values = []

    # Možné filtry – podle názvu sloupců v tabulce
    filters = {
        "username": request.args.get("username"),
        "email": request.args.get("email"),
        "role": request.args.get("role")
    }

    for column, value in filters.items():
        if value:
            base_query += f" AND {column} = %s"
            values.append(value)

    cursor.execute(base_query, values)
    users = cursor.fetchall()

    conn.close()
    return jsonify(users)


# POST /users – přidání uživatele
@app.route('/users', methods=['POST'])
def api_add_user():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'user')

    if not username or not email or not password:
        return jsonify({'error': 'Chybějící data'}), 400

    conn = connect_to_db()
    add_user(username, email, password, conn=conn)
    conn.close()
    return jsonify({'message': 'Uživatel přidán'}), 201

# DELETE /users/<id> – smazání uživatele
@app.route('/users/<int:user_id>', methods=['DELETE'])
def api_delete_user(user_id):
    conn = connect_to_db()
    delete_user(user_id, conn=conn)
    conn.close()
    return jsonify({'message': f'Uživatel {user_id} smazán'}), 200

# PUT /users/<id> – úplná aktualizace uživatele
@app.route('/users/<int:user_id>', methods=['PUT'])
def api_update_user(user_id):
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'error': 'Chybějící data'}), 400

    conn = connect_to_db()
    cursor = conn.cursor()

    query = """
    UPDATE users
    SET username = %s, email = %s, password = %s
    WHERE id = %s
    """
    cursor.execute(query, (username, email, password, user_id))
    conn.commit()
    conn.close()

    return jsonify({'message': f'Uživatel {user_id} aktualizován'}), 200

# PATCH /users/<id> – částečná aktualizace uživatele
@app.route('/users/<int:user_id>', methods=['PATCH'])
def api_patch_user(user_id):
    data = request.get_json()
    conn = connect_to_db()
    cursor = conn.cursor()

    updates = []
    values = []

    if "username" in data:
        updates.append("username = %s")
        values.append(data["username"])

    if "email" in data:
        updates.append("email = %s")
        values.append(data["email"])

    if "password" in data:
        updates.append("password = %s")
        values.append(data["password"])

    if "role" in data:
        updates.append("role = %s")
        values.append(data["role"])

    if not updates:
        return jsonify({"error": "Nezadána žádná data k aktualizaci"}), 400

    values.append(user_id)
    query = f"UPDATE users SET {', '.join(updates)} WHERE id = %s"
    cursor.execute(query, values)
    conn.commit()
    conn.close()

    return jsonify({"message": f"Uživatel {user_id} byl aktualizován"}), 200

# Metody pro tabulku Facilities

# GET /facilities – výpis sportovist s možností filtrování přes query parametry
@app.route('/facilities', methods=['GET'])
def api_get_facilities():
    conn = connect_to_db()
    cursor = conn.cursor(dictionary=True)

    base_query = "SELECT * FROM facilities WHERE 1=1"
    values = []

    # Možné filtry – podle názvu sloupců v tabulce
    filters = {
        "name": request.args.get("name"),
    }

    for column, value in filters.items():
        if value:
            base_query += f" AND {column} = %s"
            values.append(value)

    cursor.execute(base_query, values)
    facility = cursor.fetchall()

    conn.close()
    return jsonify(facility)

# GET /facilities/<id> – získání konkrétního sportoviště podle ID
@app.route('/facilities/<int:facility_id>', methods=['GET'])
def api_get_facility_by_id(facility_id):
    conn = connect_to_db()
    facility = get_facilities_by_id(facility_id, conn=conn)
    conn.close()

    if facility:
        return jsonify(facility)
    else:
        return jsonify({"error": "Uživatel nenalezen"}), 404

# POST /facilities – přidání sportoviště
@app.route('/facilities', methods=['POST'])
def api_add_facility():
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    available = data.get('available', True)

    if not name or description is None:
        return jsonify({'error': 'Chybí název nebo popis sportoviště'}), 400

    conn = connect_to_db()
    add_facility(name, description, available, conn=conn)
    conn.close()

    return jsonify({'message': 'Sportoviště přidáno'}), 201


# PUT /facilities/<id> – úplná aktualizace
@app.route('/facilities/<int:facility_id>', methods=['PUT'])
def api_update_facility(facility_id):
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    available = data.get('available', True)

    if not name or description is None:
        return jsonify({'error': 'Chybí název nebo popis'}), 400

    conn = connect_to_db()
    cursor = conn.cursor()
    query = "UPDATE facilities SET name = %s, description = %s, available = %s WHERE id = %s"
    cursor.execute(query, (name, description, available, facility_id))
    conn.commit()
    conn.close()

    return jsonify({'message': f'Sportoviště {facility_id} bylo aktualizováno'}), 200


# PATCH /facilities/<id> – částečná aktualizace
@app.route('/facilities/<int:facility_id>', methods=['PATCH'])
def api_patch_facility(facility_id):
    data = request.get_json()
    updates = []
    values = []

    for field in ['name', 'location', 'description', 'available']:
        if field in data:
            updates.append(f"{field} = %s")
            values.append(data[field])

    if not updates:
        return jsonify({'error': 'Nejsou poskytnuta žádná data pro aktualizaci'}), 400

    values.append(facility_id)

    conn = connect_to_db()
    cursor = conn.cursor()

    cursor.execute(
        f"UPDATE facilities SET {', '.join(updates)} WHERE id = %s", values
    )
    conn.commit()
    conn.close()
    return jsonify({'message': f'Sportoviště {facility_id} aktualizováno (částečně)'})

# DELETE /facilities/<id> – smazání sportoviště
@app.route('/facilities/<int:facility_id>', methods=['DELETE'])
def api_delete_facility(facility_id):
    conn = connect_to_db()
    delete_facility(facility_id, conn=conn)
    conn.close()
    return jsonify({'message': f'Sportoviště {facility_id} bylo smazáno'}), 200

# Funkce pro tabulku reservations

# GET /reservations – výpis všech rezervací s možností filtrování
@app.route('/reservation', methods=['GET'])
def api_get_reservations():
    conn = connect_to_db()
    cursor = conn.cursor(dictionary=True)

    base_query = "SELECT * FROM reservation WHERE 1=1"
    values = []

    filters = {
        "user_id": request.args.get("user_id"),
        "facility_id": request.args.get("facility_id"),
        "date": request.args.get("date"),
        "status": request.args.get("status")
    }

    for column, value in filters.items():
        if value:
            base_query += f" AND {column} = %s"
            values.append(value)

    cursor.execute(base_query, values)
    reservations = cursor.fetchall()

    # Převod časových objektů (time, date, datetime, timedelta) na řetězce
    for r in reservations:
        for k, v in r.items():
            if isinstance(v, (time, date, datetime, timedelta)):
                r[k] = str(v)

    conn.close()
    return jsonify(reservations)

# GET /reservations/<id>
@app.route('/reservation/<int:reservation_id>', methods=['GET'])
def api_get_reservation_by_id(reservation_id):
    conn = connect_to_db()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM reservation WHERE id = %s"
    cursor.execute(query, (reservation_id,))
    reservation = cursor.fetchone()

    conn.close()

    if reservation:
        # Převedeme všechny datetime/time/date/timedelta na string
        for k, v in reservation.items():
            if isinstance(v, (date, time, datetime, timedelta)):
                reservation[k] = str(v)

        return jsonify(reservation)
    else:
        return jsonify({'error': 'Rezervace nenalezena'}), 404

# POST /reservations
@app.route('/reservations', methods=['POST'])
def api_add_reservation():
    data = request.get_json()

    user_id = data.get('user_id')
    facility_id = data.get('facility_id')
    date_ = data.get('date')  # Např. '2025-07-01'
    start_time = data.get('start_time')  # Např. '14:00:00'
    end_time = data.get('end_time')      # Např. '15:00:00'
    status = data.get('status', 'pending')

    # Ověření povinných polí
    if not all([user_id, facility_id, date_, start_time, end_time]):
        return jsonify({'error': 'Chybějící data'}), 400

    # Spojení date + time do formátu 'YYYY-MM-DD HH:MM:SS'
    start = f"{date_} {start_time}"
    end = f"{date_} {end_time}"

    conn = connect_to_db()
    add_reservation(user_id, facility_id, start, end, status, conn=conn)
    conn.close()

    return jsonify({'message': 'Rezervace přidána'}), 201

@app.route('/reservations/<int:reservation_id>', methods=['DELETE'])
def api_delete_reservation(reservation_id):
    conn = connect_to_db()
    delete_reservation(reservation_id, conn=conn)
    conn.close()
    return jsonify({'message': f'Rezervace {reservation_id} byla smazána'}), 200

if __name__ == '__main__':
    app.run(debug=True)
