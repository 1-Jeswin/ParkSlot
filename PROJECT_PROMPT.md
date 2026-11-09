# Antigravity AI Project Creation Prompt & Instructions

Use this file to guide Antigravity AI in generating, scaffolding, and executing the **ParkSlot** application codebase.

---

## 🎯 Quick-Start AI Prompt

Copy and paste the following prompt directly into your Antigravity chat:

```markdown
You are an expert full-stack Python software engineer. Please implement the **ParkSlot** system based on the detailed functional specifications in `PROJECT_SPECIFICATION.md` and database schema in `schema.sql`.

Follow these engineering principles:
1. **Architecture:** Use a clean, modular MVC/layered desktop structure (`main.py`, `database/`, `models/`, `controllers/`, `views/`, `utils/`).
2. **GUI Framework:** Standard Python `tkinter` and `ttk` with clean, modern styling (or `customtkinter` if available).
3. **Database:** SQLite3 using parameterized queries to strictly prevent SQL injection, with `PRAGMA foreign_keys = ON;`.
4. **Implementation Phases:**
   - Initialize database with `schema.sql` and default seed data.
   - Build the main Portal Launcher allowing entry to User, Owner, and Admin modules.
   - Implement the complete User Module (Registration, Login, Vehicles, Slot Search, Booking, My Bookings, Fee Details).
   - Implement the complete Owner Module (Registration, Login, Facility Registration, Slot Management, Hourly Tariffs, Booking Logs).
   - Implement the complete Admin Module (Dashboard with live KPIs, Check-in, Check-out with fee calculation, Overstay Detection with 15-minute grace period, Conflict Reallocation, Audit Reports).
5. **Quality & Safety:** Hash all passwords (SHA-256 / bcrypt), enforce time window overlap checks on slots, maintain strict separation between slot status and booking status, and add helpful error dialogs.
```

---

## 📋 Architectural Directives for Antigravity AI

### 1. State Separation Rule
- **Slot Status:** Tracks physical slot state (`Available`, `Reserved`, `Occupied`, `Inactive`).
- **Booking Status:** Tracks reservation lifecycle (`Pending`, `Confirmed`, `Checked-in`, `Completed`, `Cancelled`, `Waitlisted`).
- **Never conflate these two states into a single database field.**

### 2. Overlapping Booking Verification Query
When validating a new reservation for `slot_id` from `new_start` to `new_end` on `booking_date`:
```sql
SELECT COUNT(*) FROM bookings
WHERE slot_id = ?
  AND booking_date = ?
  AND booking_status IN ('Confirmed', 'Checked-in')
  AND NOT (end_time <= ? OR start_time >= ?);
```
If count > 0, the slot is unavailable for that window.

### 3. Check-in & Check-out Protocol
- **Check-in:**
  1. Record `actual_entry = CURRENT_TIMESTAMP` in `parking_sessions`.
  2. Set `bookings.booking_status = 'Checked-in'`.
  3. Set `parking_slots.current_status = 'Occupied'`.
- **Check-out:**
  1. Record `actual_exit = CURRENT_TIMESTAMP` in `parking_sessions`.
  2. Compute billable duration in hours: `ceil(duration_minutes / 60.0)` with minimum 1 hour.
  3. Look up tariff from `parking_rates` for facility and vehicle type.
  4. Create record in `fees_payments`.
  5. Set `bookings.booking_status = 'Completed'`.
  6. Revert `parking_slots.current_status = 'Available'`.

### 4. Overstay Detection Logic
Every 60 seconds (or upon opening Admin Dashboard / Overstay Monitor), execute:
```sql
SELECT 
    ps.session_id,
    b.booking_id,
    v.registration_number,
    ps.actual_entry,
    b.end_time,
    ROUND((strftime('%s', 'now') - strftime('%s', b.booking_date || ' ' || b.end_time)) / 60.0) AS overdue_minutes
FROM parking_sessions ps
JOIN bookings b ON ps.booking_id = b.booking_id
JOIN vehicles v ON b.vehicle_id = v.vehicle_id
WHERE ps.session_status = 'Active'
  AND datetime('now') > datetime(b.booking_date || ' ' || b.end_time, '+' || (SELECT setting_value FROM admin_settings WHERE setting_key = 'overstay_grace_period_mins') || ' minutes');
```

