-- =====================================================================
-- PARKSLOT: Unified Relational SQLite Database Schema
-- Compatible with Python sqlite3 & Tkinter Desktop Architecture
-- =====================================================================

PRAGMA foreign_keys = ON;

-- 1. Admins Table
CREATE TABLE IF NOT EXISTS admins (
    admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    status TEXT CHECK(status IN ('Active', 'Inactive')) DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Owners Table (Parking Facility Owners)
CREATE TABLE IF NOT EXISTS owners (
    owner_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone_number TEXT NOT NULL,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    account_status TEXT CHECK(account_status IN ('Active', 'Inactive', 'Suspended')) DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Users Table (Drivers)
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone_number TEXT NOT NULL,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    account_status TEXT CHECK(account_status IN ('Active', 'Inactive', 'Suspended')) DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Vehicles Table
CREATE TABLE IF NOT EXISTS vehicles (
    vehicle_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    registration_number TEXT UNIQUE NOT NULL,
    vehicle_type TEXT CHECK(vehicle_type IN ('Car', 'Bike', 'Other')) NOT NULL,
    model TEXT,
    colour TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- 5. Parking Facilities Table
CREATE TABLE IF NOT EXISTS parking_facilities (
    facility_id INTEGER PRIMARY KEY AUTOINCREMENT,
    owner_id INTEGER,
    name TEXT NOT NULL,
    location TEXT NOT NULL,
    contact_number TEXT NOT NULL,
    total_slots INTEGER NOT NULL DEFAULT 0,
    opening_time TEXT DEFAULT '00:00',
    closing_time TEXT DEFAULT '23:59',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES owners(owner_id) ON DELETE SET NULL
);

-- 6. Parking Rates Table
CREATE TABLE IF NOT EXISTS parking_rates (
    rate_id INTEGER PRIMARY KEY AUTOINCREMENT,
    facility_id INTEGER NOT NULL,
    vehicle_type TEXT CHECK(vehicle_type IN ('Car', 'Bike', 'Other')) NOT NULL,
    rate_per_hour REAL NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(facility_id, vehicle_type),
    FOREIGN KEY (facility_id) REFERENCES parking_facilities(facility_id) ON DELETE CASCADE
);

-- 7. Parking Slots Table
CREATE TABLE IF NOT EXISTS parking_slots (
    slot_id INTEGER PRIMARY KEY AUTOINCREMENT,
    facility_id INTEGER NOT NULL,
    slot_number TEXT NOT NULL,
    vehicle_type TEXT CHECK(vehicle_type IN ('Car', 'Bike', 'Other')) NOT NULL,
    floor_zone TEXT DEFAULT 'Ground',
    current_status TEXT CHECK(current_status IN ('Available', 'Reserved', 'Occupied', 'Inactive')) DEFAULT 'Available',
    UNIQUE(facility_id, slot_number),
    FOREIGN KEY (facility_id) REFERENCES parking_facilities(facility_id) ON DELETE CASCADE
);

-- 8. Bookings Table
CREATE TABLE IF NOT EXISTS bookings (
    booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    vehicle_id INTEGER NOT NULL,
    slot_id INTEGER NOT NULL,
    booking_date TEXT NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    booking_status TEXT CHECK(booking_status IN ('Pending', 'Confirmed', 'Cancelled', 'Checked-in', 'Completed', 'Waitlisted')) DEFAULT 'Confirmed',
    cancellation_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id),
    FOREIGN KEY (slot_id) REFERENCES parking_slots(slot_id)
);

-- 9. Parking Sessions Table (Entry/Exit Tracking)
CREATE TABLE IF NOT EXISTS parking_sessions (
    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id INTEGER NOT NULL,
    actual_entry TIMESTAMP NOT NULL,
    actual_exit TIMESTAMP,
    session_status TEXT CHECK(session_status IN ('Active', 'Closed', 'Overdue')) DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES bookings(booking_id)
);

-- 10. Fees & Payments Table
CREATE TABLE IF NOT EXISTS fees_payments (
    payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    duration_hours REAL NOT NULL,
    rate_applied REAL NOT NULL,
    amount REAL NOT NULL,
    payment_status TEXT CHECK(payment_status IN ('Pending', 'Paid', 'Waived')) DEFAULT 'Paid',
    method TEXT CHECK(method IN ('Cash', 'Card', 'UPI', 'Manual Verification')) DEFAULT 'Cash',
    paid_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES parking_sessions(session_id)
);

-- 11. Overstay Events Table
CREATE TABLE IF NOT EXISTS overstay_events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    overdue_duration_minutes INTEGER NOT NULL,
    resolution_status TEXT CHECK(resolution_status IN ('Pending', 'Notified', 'Resolved')) DEFAULT 'Pending',
    notes TEXT,
    FOREIGN KEY (session_id) REFERENCES parking_sessions(session_id)
);

-- 12. Slot Reallocations Table
CREATE TABLE IF NOT EXISTS slot_reallocations (
    reallocation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id INTEGER NOT NULL,
    old_slot_id INTEGER NOT NULL,
    new_slot_id INTEGER NOT NULL,
    reason TEXT,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES bookings(booking_id),
    FOREIGN KEY (old_slot_id) REFERENCES parking_slots(slot_id),
    FOREIGN KEY (new_slot_id) REFERENCES parking_slots(slot_id)
);

-- 13. Waitlist Table
CREATE TABLE IF NOT EXISTS waitlist (
    waitlist_id INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id INTEGER NOT NULL,
    requested_start TEXT NOT NULL,
    requested_end TEXT NOT NULL,
    queue_status TEXT CHECK(queue_status IN ('Waiting', 'Promoted', 'Expired', 'Cancelled')) DEFAULT 'Waiting',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES bookings(booking_id)
);

-- 14. Admin Settings Table
CREATE TABLE IF NOT EXISTS admin_settings (
    setting_key TEXT PRIMARY KEY,
    setting_value TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for Fast Query Performance
CREATE INDEX IF NOT EXISTS idx_slots_facility_status ON parking_slots(facility_id, current_status);
CREATE INDEX IF NOT EXISTS idx_bookings_slot_time ON bookings(slot_id, booking_date, start_time, end_time);
CREATE INDEX IF NOT EXISTS idx_sessions_status ON parking_sessions(session_status);
CREATE INDEX IF NOT EXISTS idx_vehicles_reg ON vehicles(registration_number);

-- Default Initial Data / Seeds
-- SHA256 of "Admin@123": e86f78a8a3caf0b60d8e74e5942aa6d86dc150cd3c03338aef25b7d2d7e3acc7
INSERT OR IGNORE INTO admins (username, email, password_hash, status) 
VALUES ('admin', 'admin@parkslot.com', 'e86f78a8a3caf0b60d8e74e5942aa6d86dc150cd3c03338aef25b7d2d7e3acc7', 'Active');

INSERT OR IGNORE INTO admin_settings (setting_key, setting_value) VALUES 
('overstay_grace_period_mins', '15'),
('default_hourly_rate_car', '30.0'),
('default_hourly_rate_bike', '15.0'),
('system_contact_email', 'admin@parkslot.com');

