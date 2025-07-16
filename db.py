import mysql.connector
from mysql.connector import Error
from config import load_config

def connect_to_db(config=None, testing=False):
    if config is None:
        config = load_config(testing=testing)

    if testing and "test" not in config["database"].lower():
        raise RuntimeError("❌ VAROVÁNÍ: Při testování musíš použít testovací databázi!")

    try:
        conn = mysql.connector.connect(**config)
        if conn.is_connected():
            print(f"✅ Připojení k databázi '{config['database']}' bylo úspěšné.")
            return conn
    except Error as e:
        print(f"❗ Chyba při připojení: {e}")
        return None

