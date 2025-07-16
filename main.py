from repository import (
    get_all_users, get_all_facilities, get_all_reservations, add_user,
    add_facility, add_reservation, update_user_password, update_facility_availability,
    update_reservation_status, delete_user, delete_reservation
)

def menu():
    while True:
        print("\n 🏟️  SPRÁVA SPORTBOOKING DATABÁZE")
        print("1. Výpis všech uživatelů")
        print("2. Přidání uživatele")
        print("3. Výpis všech sportovišť")
        print("4. Přidání sportoviště")
        print("5. Vytvoření rezervace")
        print("6. Výpis rezervací")
        print("7. Změna statusu rezervace")
        print("8. Smazání uživatele")
        print("9. Smazání rezervace")
        print("0. Konec")
        
        volba = input("Zadej volbu: ")

        if volba == "1":
            vypis = get_all_users()
            print(vypis)
        elif volba == "2":
            username = input("Uživatelské jméno: ")
            email = input("Email: ")
            password = input("Heslo: ")
            add_user(username, email, password)
        elif volba == "3":
            get_all_facilities()
        elif volba == "4":
            name = input("Název sportoviště: ")
            description = input("Popis: ")
            available = input("Dostupné (True/False): ") == "True"
            add_facility(name, description, available)
        elif volba == "5":
            user_id = int(input("ID uživatele: "))
            facility_id = int(input("ID sportoviště: "))
            start = input("Začátek (YYYY-MM-DD HH:MM:SS): ")
            end = input("Konec (YYYY-MM-DD HH:MM:SS): ")
            add_reservation(user_id, facility_id, start, end)
        elif volba == "6":
            get_all_reservations()
        elif volba == "7":
            rid = int(input("ID rezervace: "))
            status = input("Nový status (pending/confirmed/cancelled): ")
            update_reservation_status(rid, status)
        elif volba == "8":
            vypis = get_all_users()
            print(vypis)
            uid = int(input("ID uživatele ke smazání: "))
            delete_user(uid)
        elif volba == "9":
            rid = int(input("ID rezervace ke smazání: "))
            delete_reservation(rid)
        elif volba == "0":
            print("Ukončuji aplikaci...")
            break
        else:
            print("Neplatná volba!")

if __name__ == "__main__":
    menu()
