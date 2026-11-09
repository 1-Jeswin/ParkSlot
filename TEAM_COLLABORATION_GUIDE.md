# ParkSlot — Team Collaboration Guide

This guide explains how **3 teammates** can collaborate smoothly on the **ParkSlot** application, working on their respective modules independently while sharing the central SQLite database (`parkslot.db`).

---

## 👥 Module Distribution Among 3 Teammates

```
                          PARKSLOT
                 (Shared: parkslot.db + schema.sql)
                                |
        +-----------------------+-----------------------+
        |                       |                       |
   Teammate 1              Teammate 2              Teammate 3
   User / Driver           Facility Owner          System Administrator
   Module                  Module                  Module
   (user_module/)          (owner_module/)         (admin_module/)
   Run: python run_user.py Run: python run_owner.py Run: python run_admin.py
```

| Teammate | Assigned Module | Folder | Entry Command | Key Responsibility |
|:---|:---|:---|:---|:---|
| **Teammate 1** | **User (Driver)** | [`user_module/`](file:///c:/Users/Jeswin/OneDrive/Documents/ParkSlot/user_module) | `python run_user.py` | Driver registration, vehicle management, searching available slots, booking, viewing reservations, and tracking fee details. |
| **Teammate 2** | **Facility Owner** | [`owner_module/`](file:///c:/Users/Jeswin/OneDrive/Documents/ParkSlot/owner_module) | `python run_owner.py` | Owner registration, facility address & operating hours, slot creation & status, vehicle tariff setting, and revenue review. |
| **Teammate 3** | **Administrator** | [`admin_module/`](file:///c:/Users/Jeswin/OneDrive/Documents/ParkSlot/admin_module) | `python run_admin.py` | Central monitoring, vehicle entry check-in, exit check-out with billing, overstay scanning (15-min grace), conflict reallocation, and CSV reports. |

---

## 🚀 How to Run Each Module Separately

Each teammate can open a terminal in this directory and run their dedicated runner:

### For Teammate 1 (User / Driver):
```powershell
python run_user.py
```
* **Default Login:** `indrajith` / `User@123`
* Test vehicles already registered: `KL-01-AB-1234` (Car) and `KL-05-CD-5678` (Bike).

### For Teammate 2 (Facility Owner):
```powershell
python run_owner.py
```
* **Default Login:** `owner1` / `Owner@123`
* Test facility already registered: **Central Mall Parking Hub** (10 slots: A01–A05 for Cars, B01–B05 for Bikes).

### For Teammate 3 (Master Administrator):
```powershell
python run_admin.py
```
* **Default Login:** `admin` / `Admin@123`
* Central dashboard with live KPIs, Check-in, Check-out, Overstay alerts, and CSV exports.

---

## 🔄 End-to-End Cross-Module Workflow

To test how all three modules interact in real time:

1. **Owner Setup (Teammate 2):**
   - Run `python run_owner.py`.
   - Log in as `owner1`.
   - Go to **Manage Parking Slots** and ensure slots are `Available`.
   - Go to **Set Parking Rates** and confirm rates (e.g. ₹30/hr for Car, ₹15/hr for Bike).

2. **Driver Booking (Teammate 1):**
   - Run `python run_user.py`.
   - Log in as `indrajith`.
   - Click **Find Parking**, search for "Central Mall", and select an available slot (e.g. `A01`).
   - Click **Book Selected Slot Now**, choose vehicle `KL-01-AB-1234`, set booking time, and confirm.
   - Slot status automatically updates to `Reserved`!

3. **Admin Check-in (Teammate 3):**
   - Run `python run_admin.py`.
   - Log in as `admin`.
   - Click **Check-in (Vehicle Entry)**.
   - Enter `KL-01-AB-1234` or the Booking ID and click **Confirm Entry**.
   - Slot status changes to `Occupied`, and an active session starts!

4. **Admin Check-out & Fee Collection (Teammate 3):**
   - In Admin Console, click **Check-out (Vehicle Exit)**.
   - Select the active session for `KL-01-AB-1234`.
   - Click **Process Check-out & Collect Fee**.
   - Fee is computed based on actual hours × ₹30/hr; payment is recorded in `fees_payments`; slot reverts to `Available`.

5. **Driver & Owner Review:**
   - Teammate 1 opens **Fee Details** in `run_user.py` to view receipt breakdown.
   - Teammate 2 opens **Parking Records & Revenue** in `run_owner.py` to see their facility revenue update.
   - Teammate 3 opens **Reports & History** in `run_admin.py` to export the audit log to CSV.

---

## 🗄️ Shared Database Files (`shared/`)

- [`shared/database.py`](file:///c:/Users/Jeswin/OneDrive/Documents/ParkSlot/shared/database.py): Manages SQLite connection with `PRAGMA foreign_keys = ON;` and auto-initializes tables and test seeds.
- [`shared/config.py`](file:///c:/Users/Jeswin/OneDrive/Documents/ParkSlot/shared/config.py): Color scheme, typography, and database paths.
- [`shared/security.py`](file:///c:/Users/Jeswin/OneDrive/Documents/ParkSlot/shared/security.py): SHA-256 password hashing.
- [`shared/ui_helpers.py`](file:///c:/Users/Jeswin/OneDrive/Documents/ParkSlot/shared/ui_helpers.py): Reusable header bars, cards, and ttk themes.

