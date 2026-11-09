# ParkSlot — Master Administrator Module

> **Assigned Team Member:** Teammate 3  
> **Tech Stack:** Python 3.10+, Tkinter, SQLite  
> **Entry Point:** Run `python run_admin.py` from project root.

---

## 🎯 Scope & Screens Included (13 Screens)

1. **Admin Login Page:** Authentication against `admins` table.
2. **Admin Dashboard:** Central command center displaying live system KPIs (Available, Occupied, Reserved, Active Sessions, Today's Bookings, Overstay Alerts, Today's Revenue) and fast shortcuts to all 12 modules.
3. **Master Slot Control:** System-wide slot inventory, maintenance status toggle (`Available` / `Inactive`).
4. **User Management:** Inspect driver accounts, view joined date, and toggle account status (`Active` / `Suspended`).
5. **Vehicle Registry:** Global searchable list of all registered vehicles and owners.
6. **Booking Management:** Master reservation schedule with admin cancellation controls.
7. **Vehicle Check-in (Entry):** Search booking or plate, verify arrival eligibility, activate parking session, mark slot `Occupied`.
8. **Vehicle Check-out (Exit & Billing):** Live active sessions table, duration computation, fee calculation based on configured hourly rate, payment recording, and slot release to `Available`.
9. **Overstay Monitoring:** Automated scanner detecting active sessions exceeding booked end time + 15 minute grace period.
10. **Conflict Resolution / Slot Reallocation:** Automatically reassign upcoming reservations to alternative available slots in the facility, or place on the waitlist.
11. **Fees & Payments Audit:** Complete transaction log of all recorded parking fees and methods.
12. **Reports & History:** Comprehensive operational reporting with status filtering and one-click **CSV export**.
13. **Admin Settings:** Global system parameters (overstay grace period, default hourly car/bike rates, contact email).

---

## 🔑 Pre-seeded Test Credentials

- **Username:** `admin`
- **Password:** `Admin@123`

