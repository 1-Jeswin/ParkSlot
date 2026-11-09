import sqlite3
import os
from shared.config import DB_PATH, SCHEMA_PATH
from shared.security import hash_password

def get_db_connection():
    """Returns a SQLite connection with foreign key enforcement and row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    """Initializes the database using schema.sql and seeds demo accounts if empty."""
    conn = get_db_connection()
    cursor = conn.cursor()

    if os.path.exists(SCHEMA_PATH):
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            cursor.executescript(f.read())
    else:
        raise FileNotFoundError(f"Schema file not found at {SCHEMA_PATH}")

    # Seed Default Admin if not present
    cursor.execute("SELECT admin_id FROM admins WHERE username = 'admin';")
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO admins (username, email, password_hash, status) VALUES (?, ?, ?, ?);",
            ("admin", "admin@parkslot.com", hash_password("Admin@123"), "Active")
        )

    # Seed Default Owner if not present
    cursor.execute("SELECT owner_id FROM owners WHERE username = 'owner1';")
    if not cursor.fetchone():
        cursor.execute(
            """INSERT INTO owners (full_name, email, phone_number, username, password_hash, account_status)
               VALUES (?, ?, ?, ?, ?, ?);""",
            ("John Doe", "john@parkinghub.com", "9876543210", "owner1", hash_password("Owner@123"), "Active")
        )
        owner_id = cursor.lastrowid

        # Seed sample facility
        cursor.execute(
            """INSERT INTO parking_facilities (owner_id, name, location, contact_number, total_slots, opening_time, closing_time)
               VALUES (?, ?, ?, ?, ?, ?, ?);""",
            (owner_id, "Central Mall Parking Hub", "MG Road, City Center", "9876543210", 10, "06:00", "23:00")
        )
        facility_id = cursor.lastrowid

        # Seed parking rates
        cursor.execute(
            "INSERT OR REPLACE INTO parking_rates (facility_id, vehicle_type, rate_per_hour) VALUES (?, ?, ?);",
            (facility_id, "Car", 30.0)
        )
        cursor.execute(
            "INSERT OR REPLACE INTO parking_rates (facility_id, vehicle_type, rate_per_hour) VALUES (?, ?, ?);",
            (facility_id, "Bike", 15.0)
        )

        # Seed slots: A01 to A05 (Cars), B01 to B05 (Bikes)
        for i in range(1, 6):
            cursor.execute(
                """INSERT INTO parking_slots (facility_id, slot_number, vehicle_type, floor_zone, current_status)
                   VALUES (?, ?, ?, ?, ?);""",
                (facility_id, f"A0{i}", "Car", "Ground Floor", "Available")
            )
        for i in range(1, 6):
            cursor.execute(
                """INSERT INTO parking_slots (facility_id, slot_number, vehicle_type, floor_zone, current_status)
                   VALUES (?, ?, ?, ?, ?);""",
                (facility_id, f"B0{i}", "Bike", "Basement 1", "Available")
            )

    # Seed Default User (Indrajith) if not present
    cursor.execute("SELECT user_id FROM users WHERE username = 'indrajith';")
    if not cursor.fetchone():
        cursor.execute(
            """INSERT INTO users (full_name, email, phone_number, username, password_hash, account_status)
               VALUES (?, ?, ?, ?, ?, ?);""",
            ("Indrajith Nair", "indrajith@example.com", "9123456789", "indrajith", hash_password("User@123"), "Active")
        )
        user_id = cursor.lastrowid

        # Seed sample vehicles
        cursor.execute(
            """INSERT INTO vehicles (user_id, registration_number, vehicle_type, model, colour)
               VALUES (?, ?, ?, ?, ?);""",
            (user_id, "KL-01-AB-1234", "Car", "Maruti Swift", "White")
        )
        cursor.execute(
            """INSERT INTO vehicles (user_id, registration_number, vehicle_type, model, colour)
               VALUES (?, ?, ?, ?, ?);""",
            (user_id, "KL-05-CD-5678", "Bike", "Honda Activa", "Black")
        )

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully at:", DB_PATH)

