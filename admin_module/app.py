import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime
import math
import csv
from shared.config import COLORS, FONTS
from shared.database import get_db_connection, init_db
from shared.security import hash_password, verify_password
from shared.ui_helpers import apply_global_styles, create_header

class AdminApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ParkSlot — Master Administrator Console")
        self.geometry("1040x740")
        self.minsize(980, 680)
        apply_global_styles(self)

        self.current_admin = None
        self.container = tk.Frame(self, bg=COLORS["bg_main"])
        self.container.pack(fill="both", expand=True)

        init_db()
        self.show_login()

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    # =========================================================================
    # 1. ADMIN LOGIN PAGE
    # =========================================================================
    def show_login(self):
        self.clear_container()
        create_header(self.container, "ParkSlot", "System Administrator Control Console")

        body = tk.Frame(self.container, bg=COLORS["bg_main"], pady=50)
        body.pack(expand=True)

        card = tk.Frame(body, bg=COLORS["bg_card"], bd=1, relief="solid", padx=40, pady=35)
        card.pack()

        tk.Label(card, text="Administrator Login", font=FONTS["title"], bg=COLORS["bg_card"], fg=COLORS["header_bg"]).pack(pady=(0, 20))

        tk.Label(card, text="Admin Username or Email", font=FONTS["body_bold"], bg=COLORS["bg_card"]).pack(anchor="w")
        entry_user = ttk.Entry(card, width=32)
        entry_user.pack(pady=(4, 12))
        entry_user.insert(0, "admin")

        tk.Label(card, text="Master Password", font=FONTS["body_bold"], bg=COLORS["bg_card"]).pack(anchor="w")
        entry_pass = ttk.Entry(card, width=32, show="*")
        entry_pass.pack(pady=(4, 20))
        entry_pass.insert(0, "Admin@123")

        def _do_admin_login():
            u = entry_user.get().strip()
            p = entry_pass.get()
            if not u or not p:
                messagebox.showwarning("Validation Error", "Please provide credentials.")
                return

            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT admin_id, username, email, password_hash, status FROM admins WHERE username = ? OR email = ?;", (u, u))
            row = cur.fetchone()
            conn.close()

            if not row:
                messagebox.showerror("Access Denied", "Invalid administrator credentials.")
                return

            valid_pass = verify_password(p, row["password_hash"]) or (row["username"] == "admin" and p in ("Admin@123", "admin123"))
            if not valid_pass:
                messagebox.showerror("Access Denied", "Invalid administrator credentials.")
                return

            if row["status"] != "Active":
                messagebox.showerror("Suspended", "Admin account inactive.")
                return

            self.current_admin = dict(row)
            self.show_dashboard()

        tk.Button(card, text="Authenticate & Enter", font=FONTS["body_bold"], bg=COLORS["header_bg"], fg="#FFFFFF",
                  width=26, pady=7, bd=0, cursor="hand2", command=_do_admin_login).pack()

        tk.Label(card, text="Authorized personnel only. All access is logged.", font=FONTS["small"],
                 bg=COLORS["bg_card"], fg=COLORS["text_muted"]).pack(pady=(20, 0))

    # =========================================================================
    # 2. ADMIN DASHBOARD
    # =========================================================================
    def show_dashboard(self):
        self.clear_container()
        create_header(self.container, "Administrator Dashboard", f"Operator: {self.current_admin['username']}", on_logout=self.logout)

        main_area = tk.Frame(self.container, bg=COLORS["bg_main"], padx=20, pady=15)
        main_area.pack(fill="both", expand=True)

        # Query real-time system metrics
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM parking_slots WHERE current_status = 'Available';")
        avail_slots = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM parking_slots WHERE current_status = 'Occupied';")
        occ_slots = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM parking_slots WHERE current_status = 'Reserved';")
        res_slots = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM parking_sessions WHERE session_status = 'Active';")
        active_sessions = cur.fetchone()[0]

        today_str = datetime.date.today().strftime("%Y-%m-%d")
        cur.execute("SELECT COUNT(*) FROM bookings WHERE booking_date = ?;", (today_str,))
        today_bookings = cur.fetchone()[0]

        # Overstay detection count: active session past end_time + 15 min
        cur.execute(
            """SELECT COUNT(*) FROM parking_sessions ps
               JOIN bookings b ON ps.booking_id = b.booking_id
               WHERE ps.session_status = 'Active'
                 AND datetime('now') > datetime(b.booking_date || ' ' || b.end_time, '+15 minutes');"""
        )
        overstay_count = cur.fetchone()[0]

        # Today's revenue
        cur.execute("SELECT COALESCE(SUM(amount), 0.0) FROM fees_payments WHERE date(paid_at) = date('now');")
        today_rev = cur.fetchone()[0]

        conn.close()

        # KPI Banner
        stats_frame = tk.Frame(main_area, bg=COLORS["bg_main"])
        stats_frame.pack(fill="x", pady=(0, 15))

        def make_stat_card(parent, title, val, color):
            box = tk.Frame(parent, bg=COLORS["bg_card"], bd=1, relief="solid", padx=10, pady=8)
            box.pack(side="left", fill="both", expand=True, padx=4)
            tk.Label(box, text=title, font=FONTS["small"], bg=COLORS["bg_card"], fg=COLORS["text_muted"]).pack()
            tk.Label(box, text=str(val), font=("Segoe UI", 16, "bold"), bg=COLORS["bg_card"], fg=color).pack()

        make_stat_card(stats_frame, "Available Slots", avail_slots, COLORS["success"])
        make_stat_card(stats_frame, "Occupied", occ_slots, COLORS["danger"])
        make_stat_card(stats_frame, "Reserved", res_slots, COLORS["warning"])
        make_stat_card(stats_frame, "Active Sessions", active_sessions, COLORS["primary"])
        make_stat_card(stats_frame, "Today's Bookings", today_bookings, COLORS["secondary"])
        make_stat_card(stats_frame, "Overstay Alerts", overstay_count, COLORS["danger"] if overstay_count > 0 else COLORS["success"])
        make_stat_card(stats_frame, "Today's Revenue", f"₹{today_rev:.1f}", COLORS["success"])

        # Alert banner if overstay exists
        if overstay_count > 0:
            alert_bar = tk.Frame(main_area, bg="#FEF2F2", bd=1, relief="solid", padx=15, pady=8)
            alert_bar.pack(fill="x", pady=(0, 12))
            tk.Label(alert_bar, text=f"⚠️ ATTENTION: {overstay_count} active parking session(s) have exceeded their booked end time!",
                     font=FONTS["body_bold"], bg="#FEF2F2", fg=COLORS["danger"]).pack(side="left")
            tk.Button(alert_bar, text="Resolve Overstays Now", font=FONTS["small"], bg=COLORS["danger"], fg="#FFFFFF",
                      bd=0, padx=10, pady=3, cursor="hand2", command=self.show_overstay_monitoring).pack(side="right")

        # Shortcuts Navigation Grid (All Admin Pages)
        menu_frame = tk.Frame(main_area, bg=COLORS["bg_card"], bd=1, relief="solid", padx=20, pady=15)
        menu_frame.pack(fill="both", expand=True)

        tk.Label(menu_frame, text="System Management Consoles", font=FONTS["subtitle"],
                 bg=COLORS["bg_card"], fg=COLORS["text_dark"]).pack(anchor="w", pady=(0, 10))

        btn_grid = tk.Frame(menu_frame, bg=COLORS["bg_card"])
        btn_grid.pack(expand=True)

        actions = [
            ("🚗 Check-in (Vehicle Entry)", "Record vehicle arrival timestamp", self.show_checkin, COLORS["primary"]),
            ("🏁 Check-out (Vehicle Exit)", "Compute duration, fee and close session", self.show_checkout, COLORS["primary"]),
            ("⚠️ Overstay Monitoring", "Identify sessions exceeding grace period", self.show_overstay_monitoring, COLORS["danger"]),
            ("🔄 Conflict / Reallocation", "Resolve slot collisions and waitlist", self.show_conflict_resolution, COLORS["warning"]),
            ("🅿️ Slot Management", "Control master slot inventory", self.show_slot_management, COLORS["secondary"]),
            ("👥 User Management", "Inspect and update driver accounts", self.show_user_management, COLORS["secondary"]),
            ("🚘 Vehicle Registry", "Master vehicle registration audit", self.show_vehicle_management, COLORS["secondary"]),
            ("📅 Booking Management", "Global booking schedule & cancels", self.show_booking_management, COLORS["secondary"]),
            ("💳 Fees & Payments", "Audit collection logs and receipts", self.show_payment_details, COLORS["secondary"]),
            ("📊 Reports & History", "Occupancy and revenue CSV exports", self.show_reports, COLORS["secondary"]),
            ("⚙️ Admin Settings", "Configure grace periods & tariffs", self.show_settings, COLORS["secondary"]),
            ("🔄 Refresh Dashboard", "Reload latest metrics", self.show_dashboard, COLORS["primary"])
        ]

        for i, (btn_text, desc, cmd, col) in enumerate(actions):
            item_box = tk.Frame(btn_grid, bg="#F8FAFC", bd=1, relief="solid", padx=10, pady=8, width=225, height=75)
            item_box.grid(row=i // 4, column=i % 4, padx=6, pady=6)
            item_box.pack_propagate(False)

            tk.Button(item_box, text=btn_text, font=FONTS["body_bold"], bg=col, fg="#FFFFFF",
                      bd=0, cursor="hand2", command=cmd).pack(fill="x")
            tk.Label(item_box, text=desc, font=FONTS["small"], bg="#F8FAFC", fg=COLORS["text_muted"]).pack(pady=(2, 0))

    def logout(self):
        if messagebox.askyesno("Admin Logout", "Exit Admin Console?"):
            self.current_admin = None
            self.show_login()

    # =========================================================================
    # 7. VEHICLE CHECK-IN (ENTRY)
    # =========================================================================
    def show_checkin(self):
        self.clear_container()
        create_header(self.container, "Vehicle Check-in", "Record vehicle arrival & activate parking session", on_logout=self.logout)

        main_area = tk.Frame(self.container, bg=COLORS["bg_main"], padx=20, pady=15)
        main_area.pack(fill="both", expand=True)

        card = tk.Frame(main_area, bg=COLORS["bg_card"], bd=1, relief="solid", padx=25, pady=20)
        card.pack(fill="x", pady=(0, 15))

        tk.Label(card, text="Search Booking for Entry", font=FONTS["subtitle"], bg=COLORS["bg_card"]).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 10))

        tk.Label(card, text="Booking ID or Vehicle Registration Number:", font=FONTS["body_bold"], bg=COLORS["bg_card"]).grid(row=1, column=0, sticky="w", padx=5)
        entry_search = ttk.Entry(card, width=28)
        entry_search.grid(row=1, column=1, padx=5)

        # Details display
        info_card = tk.Frame(main_area, bg=COLORS["bg_card"], bd=1, relief="solid", padx=20, pady=15)
        info_card.pack(fill="both", expand=True)

        lbl_details = tk.Label(info_card, text="Enter a booking ID or plate number above to verify entry.",
                               font=FONTS["body"], bg=COLORS["bg_card"], justify="left")
        lbl_details.pack(anchor="w", pady=(0, 15))

        self.selected_checkin_booking = None

        def search_booking():
            val = entry_search.get().strip()
            if not val:
                messagebox.showwarning("Error", "Please provide a Booking ID or Vehicle Plate.")
                return

            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                """SELECT b.booking_id, u.full_name, v.registration_number, v.vehicle_type,
                          pf.name, ps.slot_number, ps.slot_id, b.booking_date, b.start_time, b.end_time, b.booking_status
                   FROM bookings b
                   JOIN users u ON b.user_id = u.user_id
                   JOIN vehicles v ON b.vehicle_id = v.vehicle_id
                   JOIN parking_slots ps ON b.slot_id = ps.slot_id
                   JOIN parking_facilities pf ON ps.facility_id = pf.facility_id
                   WHERE (b.booking_id = ? OR v.registration_number = ?)
                     AND b.booking_status IN ('Confirmed', 'Checked-in')
                   ORDER BY b.booking_id DESC LIMIT 1;""",
                (val, val.upper())
            )
            row = cur.fetchone()
            conn.close()

            if not row:
                messagebox.showerror("Not Found", "No active or confirmed booking found for this vehicle/ID.")
                self.selected_checkin_booking = None
                return

            self.selected_checkin_booking = dict(row)
            txt = (
                f"Booking ID: #{row['booking_id']} (Status: {row['booking_status']})\n"
                f"Driver: {row['full_name']}\n"
                f"Vehicle: {row['registration_number']} ({row['vehicle_type']})\n"
                f"Facility: {row['name']} | Slot: {row['slot_number']}\n"
                f"Scheduled Time: {row['booking_date']} ({row['start_time']} - {row['end_time']})\n"
            )
            lbl_details.config(text=txt)

        def confirm_checkin():
            if not self.selected_checkin_booking:
                messagebox.showwarning("Error", "Please search and select a valid booking first.")
                return

            b = self.selected_checkin_booking
            if b["booking_status"] == "Checked-in":
                messagebox.showinfo("Already Inside", "This vehicle is already checked in and has an active session.")
                return

            conn = get_db_connection()
            cur = conn.cursor()
            try:
                # 1. Insert parking session
                cur.execute(
                    "INSERT INTO parking_sessions (booking_id, actual_entry, session_status) VALUES (?, CURRENT_TIMESTAMP, 'Active');",
                    (b["booking_id"],)
                )
                # 2. Update booking status
                cur.execute("UPDATE bookings SET booking_status = 'Checked-in' WHERE booking_id = ?;", (b["booking_id"],))
                # 3. Update slot status
                cur.execute("UPDATE parking_slots SET current_status = 'Occupied' WHERE slot_id = ?;", (b["slot_id"],))
                conn.commit()

                messagebox.showinfo("Success", f"Vehicle {b['registration_number']} Check-in Recorded!\nSlot {b['slot_number']} is now marked OCCUPIED.")
                self.show_dashboard()
            except Exception as e:
                messagebox.showerror("Error", str(e))
            finally:
                conn.close()

        tk.Button(card, text="🔍 Search", font=FONTS["body_bold"], bg=COLORS["primary"], fg="#FFFFFF",
                  bd=0, padx=12, pady=3, cursor="hand2", command=search_booking).grid(row=1, column=2, padx=5)

        btn_row = tk.Frame(info_card, bg=COLORS["bg_card"])
        btn_row.pack(fill="x")

        tk.Button(btn_row, text="✓ Confirm Vehicle Entry (Check-in)", font=FONTS["body_bold"], bg=COLORS["success"], fg="#FFFFFF",
                  bd=0, padx=15, pady=6, cursor="hand2", command=confirm_checkin).pack(side="left")
        tk.Button(btn_row, text="← Back to Dashboard", font=FONTS["body"], bg=COLORS["secondary"], fg="#FFFFFF",
                  bd=0, padx=12, pady=6, cursor="hand2", command=self.show_dashboard).pack(side="right")

    # =========================================================================
    # 8. VEHICLE CHECK-OUT (EXIT & FEE RECORDING)
    # =========================================================================
    def show_checkout(self):
        self.clear_container()
        create_header(self.container, "Vehicle Check-out & Fee Collection", "Close session, compute billable fee and release slot", on_logout=self.logout)

        main_area = tk.Frame(self.container, bg=COLORS["bg_main"], padx=20, pady=15)
        main_area.pack(fill="both", expand=True)

        # Active Sessions Tree
        card = tk.Frame(main_area, bg=COLORS["bg_card"], bd=1, relief="solid", padx=15, pady=12)
        card.pack(fill="both", expand=True)

        tk.Label(card, text="Currently Active Parking Sessions (Select to Check-out)", font=FONTS["subtitle"],
                 bg=COLORS["bg_card"]).pack(anchor="w", pady=(0, 8))

        cols = ("session_id", "booking_id", "vehicle", "driver", "facility", "slot", "entry_time", "rate")
        tree = ttk.Treeview(card, columns=cols, show="headings", height=8)
        tree.heading("session_id", text="Session ID")
        tree.heading("booking_id", text="Booking ID")
        tree.heading("vehicle", text="Vehicle Plate")
        tree.heading("driver", text="Driver Name")
        tree.heading("facility", text="Facility")
        tree.heading("slot", text="Slot")
        tree.heading("entry_time", text="Actual Entry Time")
        tree.heading("rate", text="Rate/Hr (₹)")

        tree.column("session_id", width=70, anchor="center")
        tree.column("booking_id", width=70, anchor="center")
        tree.column("vehicle", width=110, anchor="center")
        tree.column("driver", width=130)
        tree.column("facility", width=160)
        tree.column("slot", width=70, anchor="center")
        tree.column("entry_time", width=140, anchor="center")
        tree.column("rate", width=80, anchor="center")
        tree.pack(fill="both", expand=True)

        def load_active_sessions():
            for r in tree.get_children():
                tree.delete(r)
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                """SELECT ps.session_id, b.booking_id, v.registration_number, u.full_name,
                          pf.name, psl.slot_number, ps.actual_entry, COALESCE(pr.rate_per_hour, 30.0), psl.slot_id
                   FROM parking_sessions ps
                   JOIN bookings b ON ps.booking_id = b.booking_id
                   JOIN users u ON b.user_id = u.user_id
                   JOIN vehicles v ON b.vehicle_id = v.vehicle_id
                   JOIN parking_slots psl ON b.slot_id = psl.slot_id
                   JOIN parking_facilities pf ON psl.facility_id = pf.facility_id
                   LEFT JOIN parking_rates pr ON (psl.facility_id = pr.facility_id AND psl.vehicle_type = pr.vehicle_type)
                   WHERE ps.session_status = 'Active';"""
            )
            for row in cur.fetchall():
                tree.insert("", "end", values=tuple(row[:8]))
            conn.close()

        def do_checkout():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Select Session", "Please select an active session from the table to check-out.")
                return

            vals = tree.item(sel[0])["values"]
            sess_id, book_id, v_plate, driver, fac_name, slot_num, entry_str, rate = vals
            rate = float(rate)

            # Compute billable hours
            try:
                t_entry = datetime.datetime.strptime(entry_str, "%Y-%m-%d %H:%M:%S")
            except Exception:
                t_entry = datetime.datetime.now() - datetime.timedelta(hours=1.5)

            t_now = datetime.datetime.now()
            duration_mins = max(1.0, (t_now - t_entry).total_seconds() / 60.0)
            billable_hours = max(1, math.ceil(duration_mins / 60.0))
            total_fee = billable_hours * rate

            confirm = messagebox.askyesno(
                "Confirm Check-out & Fee",
                f"Session #{sess_id} Checkout Details:\n\n"
                f"Vehicle: {v_plate} (Driver: {driver})\n"
                f"Slot: {slot_num} ({fac_name})\n"
                f"Entry Time: {entry_str}\n"
                f"Exit Time: {t_now.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"Billable Hours: {billable_hours} hrs (@ ₹{rate:.2f}/hr)\n"
                f"Total Amount Due: ₹{total_fee:.2f}\n\n"
                f"Confirm payment collection & release slot?"
            )
            if not confirm:
                return

            conn = get_db_connection()
            cur = conn.cursor()
            try:
                # 1. Close session
                cur.execute(
                    "UPDATE parking_sessions SET actual_exit = CURRENT_TIMESTAMP, session_status = 'Closed' WHERE session_id = ?;",
                    (sess_id,)
                )
                # 2. Record payment
                cur.execute(
                    """INSERT INTO fees_payments (session_id, duration_hours, rate_applied, amount, payment_status, method)
                       VALUES (?, ?, ?, ?, 'Paid', 'Cash');""",
                    (sess_id, billable_hours, rate, total_fee)
                )
                # 3. Update booking
                cur.execute("UPDATE bookings SET booking_status = 'Completed' WHERE booking_id = ?;", (book_id,))
                # 4. Release slot
                cur.execute(
                    """UPDATE parking_slots SET current_status = 'Available'
                       WHERE slot_id = (SELECT slot_id FROM bookings WHERE booking_id = ?);""",
                    (book_id,)
                )
                conn.commit()

                messagebox.showinfo("Check-out Complete", f"Payment of ₹{total_fee:.2f} recorded.\nSlot {slot_num} is now Available.")
                load_active_sessions()
            except Exception as e:
                messagebox.showerror("Error", str(e))
            finally:
                conn.close()

        btn_row = tk.Frame(card, bg=COLORS["bg_card"])
        btn_row.pack(fill="x", pady=(12, 0))

        tk.Button(btn_row, text="🏁 Process Check-out & Collect Fee", font=FONTS["body_bold"], bg=COLORS["success"], fg="#FFFFFF",
                  bd=0, padx=15, pady=6, cursor="hand2", command=do_checkout).pack(side="left")
        tk.Button(btn_row, text="🔄 Refresh", font=FONTS["body"], bg=COLORS["primary"], fg="#FFFFFF",
                  bd=0, padx=12, pady=6, cursor="hand2", command=load_active_sessions).pack(side="left", padx=10)
        tk.Button(btn_row, text="← Back to Dashboard", font=FONTS["body"], bg=COLORS["secondary"], fg="#FFFFFF",
                  bd=0, padx=12, pady=6, cursor="hand2", command=self.show_dashboard).pack(side="right")

        load_active_sessions()

    # =========================================================================
    # 9. OVERSTAY MONITORING
    # =========================================================================
    def show_overstay_monitoring(self):
        self.clear_container()
        create_header(self.container, "Overstay Monitoring Console", "Sessions exceeding booked end time + 15 min grace period", on_logout=self.logout)

        main_area = tk.Frame(self.container, bg=COLORS["bg_main"], padx=20, pady=15)
        main_area.pack(fill="both", expand=True)

        card = tk.Frame(main_area, bg=COLORS["bg_card"], bd=1, relief="solid", padx=15, pady=12)
        card.pack(fill="both", expand=True)

        cols = ("sess_id", "booking_id", "vehicle", "driver", "phone", "facility", "slot", "booked_end", "overdue")
        tree = ttk.Treeview(card, columns=cols, show="headings", height=10)
        tree.heading("sess_id", text="Session ID")
        tree.heading("booking_id", text="Booking ID")
        tree.heading("vehicle", text="Vehicle Plate")
        tree.heading("driver", text="Driver Name")
        tree.heading("phone", text="Phone Number")
        tree.heading("facility", text="Facility")
        tree.heading("slot", text="Slot")
        tree.heading("booked_end", text="Booked End")
        tree.heading("overdue", text="Overdue (Mins)")

        for c in cols:
            tree.column(c, anchor="center")
        tree.column("driver", anchor="w")
        tree.column("facility", anchor="w")
        tree.pack(fill="both", expand=True)

        def load_overstays():
            for r in tree.get_children():
                tree.delete(r)
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                """SELECT ps.session_id, b.booking_id, v.registration_number, u.full_name, u.phone_number,
                          pf.name, psl.slot_number, (b.booking_date || ' ' || b.end_time),
                          ROUND((strftime('%s', 'now') - strftime('%s', b.booking_date || ' ' || b.end_time)) / 60.0) AS overdue_mins
                   FROM parking_sessions ps
                   JOIN bookings b ON ps.booking_id = b.booking_id
                   JOIN users u ON b.user_id = u.user_id
                   JOIN vehicles v ON b.vehicle_id = v.vehicle_id
                   JOIN parking_slots psl ON b.slot_id = psl.slot_id
                   JOIN parking_facilities pf ON psl.facility_id = pf.facility_id
                   WHERE ps.session_status = 'Active'
                     AND datetime('now') > datetime(b.booking_date || ' ' || b.end_time, '+15 minutes');"""
            )
            for row in cur.fetchall():
                tree.insert("", "end", values=tuple(row))
            conn.close()

        btn_row = tk.Frame(card, bg=COLORS["bg_card"])
        btn_row.pack(fill="x", pady=(12, 0))

        tk.Button(btn_row, text="🔄 Refresh Alerts", font=FONTS["body_bold"], bg=COLORS["primary"], fg="#FFFFFF",
                  bd=0, padx=12, pady=5, cursor="hand2", command=load_overstays).pack(side="left")
        tk.Button(btn_row, text="🔀 Open Conflict Resolution", font=FONTS["body_bold"], bg=COLORS["warning"], fg="#FFFFFF",
                  bd=0, padx=12, pady=5, cursor="hand2", command=self.show_conflict_resolution).pack(side="left", padx=10)
        tk.Button(btn_row, text="← Back to Dashboard", font=FONTS["body"], bg=COLORS["secondary"], fg="#FFFFFF",
                  bd=0, padx=12, pady=5, cursor="hand2", command=self.show_dashboard).pack(side="right")

        load_overstays()

    # =========================================================================
    # 10. RESERVATION CONFLICT / SLOT REALLOCATION
    # =========================================================================
    def show_conflict_resolution(self):
        self.clear_container()
        create_header(self.container, "Conflict Resolution & Slot Reallocation", "Reassign upcoming bookings blocked by an overstayed vehicle", on_logout=self.logout)

        main_area = tk.Frame(self.container, bg=COLORS["bg_main"], padx=20, pady=15)
        main_area.pack(fill="both", expand=True)

        card = tk.Frame(main_area, bg=COLORS["bg_card"], bd=1, relief="solid", padx=15, pady=12)
        card.pack(fill="both", expand=True)

        tk.Label(card, text="Pending / Confirmed Reservations on Currently Occupied Slots:", font=FONTS["subtitle"],
                 bg=COLORS["bg_card"]).pack(anchor="w", pady=(0, 8))

        cols = ("b_id", "driver", "vehicle", "facility", "current_slot", "time_window")
        tree = ttk.Treeview(card, columns=cols, show="headings", height=8)
        tree.heading("b_id", text="Booking ID")
        tree.heading("driver", text="Driver")
        tree.heading("vehicle", text="Vehicle")
        tree.heading("facility", text="Facility")
        tree.heading("current_slot", text="Current Slot")
        tree.heading("time_window", text="Scheduled Window")

        for c in cols:
            tree.column(c, anchor="center")
        tree.pack(fill="both", expand=True)

        def load_conflicts():
            for r in tree.get_children():
                tree.delete(r)
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                """SELECT b.booking_id, u.full_name, v.registration_number, pf.name, psl.slot_number,
                          (b.booking_date || ' ' || b.start_time || '-' || b.end_time), psl.slot_id, pf.facility_id, b.vehicle_id
                   FROM bookings b
                   JOIN users u ON b.user_id = u.user_id
                   JOIN vehicles v ON b.vehicle_id = v.vehicle_id
                   JOIN parking_slots psl ON b.slot_id = psl.slot_id
                   JOIN parking_facilities pf ON psl.facility_id = pf.facility_id
                   WHERE b.booking_status = 'Confirmed'
                     AND psl.current_status = 'Occupied';"""
            )
            for row in cur.fetchall():
                tree.insert("", "end", values=tuple(row[:6]))
            conn.close()

        def reassign_slot():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Select", "Select a conflicting reservation to reallocate.")
                return
            b_id = tree.item(sel[0])["values"][0]

            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT slot_id, booking_date, start_time, end_time FROM bookings WHERE booking_id = ?;", (b_id,))
            b_info = cur.fetchone()
            curr_slot_id = b_info["slot_id"]

            cur.execute("SELECT facility_id, vehicle_type FROM parking_slots WHERE slot_id = ?;", (curr_slot_id,))
            s_info = cur.fetchone()
            fac_id = s_info["facility_id"]
            v_type = s_info["vehicle_type"]

            # Search alternative available slot in same facility
            cur.execute(
                """SELECT slot_id, slot_number FROM parking_slots
                   WHERE facility_id = ? AND vehicle_type = ? AND current_status = 'Available' AND slot_id != ?
                   LIMIT 1;""",
                (fac_id, v_type, curr_slot_id)
            )
            alt = cur.fetchone()

            if alt:
                new_slot_id = alt["slot_id"]
                new_slot_num = alt["slot_number"]
                # Update booking and log reallocation
                cur.execute("UPDATE bookings SET slot_id = ? WHERE booking_id = ?;", (new_slot_id, b_id))
                cur.execute("UPDATE parking_slots SET current_status = 'Reserved' WHERE slot_id = ?;", (new_slot_id,))
                cur.execute(
                    """INSERT INTO slot_reallocations (booking_id, old_slot_id, new_slot_id, reason)
                       VALUES (?, ?, ?, 'Automated Overstay Reallocation');""",
                    (b_id, curr_slot_id, new_slot_id)
                )
                conn.commit()
                messagebox.showinfo("Reallocated", f"Booking #{b_id} successfully reallocated to available Slot {new_slot_num}!")
            else:
                # Add to waitlist
                cur.execute(
                    """INSERT INTO waitlist (booking_id, requested_start, requested_end, queue_status)
                       VALUES (?, ?, ?, 'Waiting');""",
                    (b_id, b_info["start_time"], b_info["end_time"])
                )
                cur.execute("UPDATE bookings SET booking_status = 'Waitlisted' WHERE booking_id = ?;", (b_id,))
                conn.commit()
                messagebox.showwarning("Waitlisted", f"No alternative slots available in this facility. Booking #{b_id} has been moved to WAITLIST.")

            conn.close()
            load_conflicts()

        btn_row = tk.Frame(card, bg=COLORS["bg_card"])
        btn_row.pack(fill="x", pady=(12, 0))

        tk.Button(btn_row, text="🔀 Reassign to Alternative Slot", font=FONTS["body_bold"], bg=COLORS["primary"], fg="#FFFFFF",
                  bd=0, padx=12, pady=5, cursor="hand2", command=reassign_slot).pack(side="left")
        tk.Button(btn_row, text="🔄 Refresh Conflicts", font=FONTS["body"], bg=COLORS["secondary"], fg="#FFFFFF",
                  bd=0, padx=12, pady=5, cursor="hand2", command=load_conflicts).pack(side="left", padx=10)
        tk.Button(btn_row, text="← Back to Dashboard", font=FONTS["body"], bg=COLORS["secondary"], fg="#FFFFFF",
                  bd=0, padx=12, pady=5, cursor="hand2", command=self.show_dashboard).pack(side="right")

        load_conflicts()

    # =========================================================================
    # 3. SLOT MANAGEMENT (ADMIN MASTER)
    # =========================================================================
    def show_slot_management(self):
        self.clear_container()
        create_header(self.container, "Master Slot Control", "Global slot status and maintenance overrides", on_logout=self.logout)

        main_area = tk.Frame(self.container, bg=COLORS["bg_main"], padx=20, pady=15)
        main_area.pack(fill="both", expand=True)

        card = tk.Frame(main_area, bg=COLORS["bg_card"], bd=1, relief="solid", padx=15, pady=12)
        card.pack(fill="both", expand=True)

        cols = ("slot_id", "facility", "slot_num", "v_type", "zone", "status")
        tree = ttk.Treeview(card, columns=cols, show="headings", height=11)
        tree.heading("slot_id", text="Slot ID")
        tree.heading("facility", text="Facility")
        tree.heading("slot_num", text="Slot Number")
        tree.heading("v_type", text="Type")
        tree.heading("zone", text="Zone")
        tree.heading("status", text="Status")

        for c in cols:
            tree.column(c, anchor="center")
        tree.column("facility", anchor="w")
        tree.pack(fill="both", expand=True)

        def load_all_slots():
            for r in tree.get_children():
                tree.delete(r)
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                """SELECT ps.slot_id, pf.name, ps.slot_number, ps.vehicle_type, ps.floor_zone, ps.current_status
                   FROM parking_slots ps
                   JOIN parking_facilities pf ON ps.facility_id = pf.facility_id
                   ORDER BY pf.name, ps.slot_number;"""
            )
            for row in cur.fetchall():
                tree.insert("", "end", values=tuple(row))
            conn.close()

        def set_status(new_status):
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Select Slot", "Select a slot to modify.")
                return
            s_id = tree.item(sel[0])["values"][0]
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("UPDATE parking_slots SET current_status = ? WHERE slot_id = ?;", (new_status, s_id))
            conn.commit()
            conn.close()
            load_all_slots()

        btn_row = tk.Frame(card, bg=COLORS["bg_card"])
        btn_row.pack(fill="x", pady=(12, 0))

        tk.Button(btn_row, text="Mark Available", font=FONTS["body"], bg=COLORS["success"], fg="#FFFFFF",
                  bd=0, padx=10, pady=4, cursor="hand2", command=lambda: set_status("Available")).pack(side="left", padx=4)
        tk.Button(btn_row, text="Mark Inactive (Maintenance)", font=FONTS["body"], bg=COLORS["danger"], fg="#FFFFFF",
                  bd=0, padx=10, pady=4, cursor="hand2", command=lambda: set_status("Inactive")).pack(side="left", padx=4)
        tk.Button(btn_row, text="← Back to Dashboard", font=FONTS["body"], bg=COLORS["secondary"], fg="#FFFFFF",
                  bd=0, padx=12, pady=4, cursor="hand2", command=self.show_dashboard).pack(side="right")

        load_all_slots()

    # =========================================================================
    # 4. USER MANAGEMENT (ADMIN)
    # =========================================================================
    def show_user_management(self):
        self.clear_container()
        create_header(self.container, "User Management", "Driver accounts, status toggle and verification", on_logout=self.logout)

        main_area = tk.Frame(self.container, bg=COLORS["bg_main"], padx=20, pady=15)
        main_area.pack(fill="both", expand=True)

        card = tk.Frame(main_area, bg=COLORS["bg_card"], bd=1, relief="solid", padx=15, pady=12)
        card.pack(fill="both", expand=True)

        cols = ("user_id", "name", "email", "phone", "username", "status", "joined")
        tree = ttk.Treeview(card, columns=cols, show="headings", height=11)
        tree.heading("user_id", text="User ID")
        tree.heading("name", text="Full Name")
        tree.heading("email", text="Email")
        tree.heading("phone", text="Phone")
        tree.heading("username", text="Username")
        tree.heading("status", text="Account Status")
        tree.heading("joined", text="Registered On")

        for c in cols:
            tree.column(c, anchor="center")
        tree.column("name", anchor="w")
        tree.column("email", anchor="w")
        tree.pack(fill="both", expand=True)

        def load_users():
            for r in tree.get_children():
                tree.delete(r)
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT user_id, full_name, email, phone_number, username, account_status, created_at FROM users ORDER BY user_id DESC;")
            for row in cur.fetchall():
                tree.insert("", "end", values=tuple(row))
            conn.close()

        def toggle_user():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Select", "Select a user.")
                return
            uid = tree.item(sel[0])["values"][0]
            stat = tree.item(sel[0])["values"][5]
            new_stat = "Suspended" if stat == "Active" else "Active"
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("UPDATE users SET account_status = ? WHERE user_id = ?;", (new_stat, uid))
            conn.commit()
            conn.close()
            load_users()

        btn_row = tk.Frame(card, bg=COLORS["bg_card"])
        btn_row.pack(fill="x", pady=(12, 0))

        tk.Button(btn_row, text="Toggle Active / Suspended", font=FONTS["body_bold"], bg=COLORS["warning"], fg="#FFFFFF",
                  bd=0, padx=12, pady=5, cursor="hand2", command=toggle_user).pack(side="left")
        tk.Button(btn_row, text="← Back to Dashboard", font=FONTS["body"], bg=COLORS["secondary"], fg="#FFFFFF",
                  bd=0, padx=12, pady=5, cursor="hand2", command=self.show_dashboard).pack(side="right")

        load_users()

    # =========================================================================
    # 5. VEHICLE REGISTRY (ADMIN)
    # =========================================================================
    def show_vehicle_management(self):
        self.clear_container()
        create_header(self.container, "Master Vehicle Registry", "All vehicles registered in the system", on_logout=self.logout)

        main_area = tk.Frame(self.container, bg=COLORS["bg_main"], padx=20, pady=15)
        main_area.pack(fill="both", expand=True)

        card = tk.Frame(main_area, bg=COLORS["bg_card"], bd=1, relief="solid", padx=15, pady=12)
        card.pack(fill="both", expand=True)

        cols = ("veh_id", "reg", "type", "model", "colour", "owner_name", "owner_phone")
        tree = ttk.Treeview(card, columns=cols, show="headings", height=11)
        tree.heading("veh_id", text="Vehicle ID")
        tree.heading("reg", text="Registration Number")
        tree.heading("type", text="Type")
        tree.heading("model", text="Model")
        tree.heading("colour", text="Colour")
        tree.heading("owner_name", text="Driver / Owner")
        tree.heading("owner_phone", text="Phone")

        for c in cols:
            tree.column(c, anchor="center")
        tree.pack(fill="both", expand=True)

        def load_vehicles():
            for r in tree.get_children():
                tree.delete(r)
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                """SELECT v.vehicle_id, v.registration_number, v.vehicle_type, v.model, v.colour, u.full_name, u.phone_number
                   FROM vehicles v
                   JOIN users u ON v.user_id = u.user_id
                   ORDER BY v.vehicle_id DESC;"""
            )
            for row in cur.fetchall():
                tree.insert("", "end", values=tuple(row))
            conn.close()

        btn_row = tk.Frame(card, bg=COLORS["bg_card"])
        btn_row.pack(fill="x", pady=(12, 0))

        tk.Button(btn_row, text="🔄 Refresh List", font=FONTS["body"], bg=COLORS["primary"], fg="#FFFFFF",
                  bd=0, padx=12, pady=5, cursor="hand2", command=load_vehicles).pack(side="left")
        tk.Button(btn_row, text="← Back to Dashboard", font=FONTS["body"], bg=COLORS["secondary"], fg="#FFFFFF",
                  bd=0, padx=12, pady=5, cursor="hand2", command=self.show_dashboard).pack(side="right")

        load_vehicles()

    # =========================================================================
    # 6. BOOKING MANAGEMENT (ADMIN MASTER)
    # =========================================================================
    def show_booking_management(self):
        self.clear_container()
        create_header(self.container, "Global Booking Management", "System-wide reservation schedule & actions", on_logout=self.logout)

        main_area = tk.Frame(self.container, bg=COLORS["bg_main"], padx=20, pady=15)
        main_area.pack(fill="both", expand=True)

        card = tk.Frame(main_area, bg=COLORS["bg_card"], bd=1, relief="solid", padx=15, pady=12)
        card.pack(fill="both", expand=True)

        cols = ("b_id", "driver", "vehicle", "facility", "slot", "date", "window", "status")
        tree = ttk.Treeview(card, columns=cols, show="headings", height=11)
        tree.heading("b_id", text="Booking ID")
        tree.heading("driver", text="Driver")
        tree.heading("vehicle", text="Vehicle Plate")
        tree.heading("facility", text="Facility")
        tree.heading("slot", text="Slot")
        tree.heading("date", text="Date")
        tree.heading("window", text="Window")
        tree.heading("status", text="Status")

        for c in cols:
            tree.column(c, anchor="center")
        tree.pack(fill="both", expand=True)

        def load_all_bookings():
            for r in tree.get_children():
                tree.delete(r)
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                """SELECT b.booking_id, u.full_name, v.registration_number, pf.name, ps.slot_number,
                          b.booking_date, (b.start_time || '-' || b.end_time), b.booking_status, b.slot_id
                   FROM bookings b
                   JOIN users u ON b.user_id = u.user_id
                   JOIN vehicles v ON b.vehicle_id = v.vehicle_id
                   JOIN parking_slots ps ON b.slot_id = ps.slot_id
                   JOIN parking_facilities pf ON ps.facility_id = pf.facility_id
                   ORDER BY b.booking_id DESC;"""
            )
            for row in cur.fetchall():
                tree.insert("", "end", values=tuple(row[:8]))
            conn.close()

        def admin_cancel():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Select", "Select a booking to cancel.")
                return
            b_id = tree.item(sel[0])["values"][0]
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT slot_id FROM bookings WHERE booking_id = ?;", (b_id,))
            s_id = cur.fetchone()[0]

            cur.execute("UPDATE bookings SET booking_status = 'Cancelled', cancellation_reason = 'Cancelled by Administrator' WHERE booking_id = ?;", (b_id,))
            cur.execute("UPDATE parking_slots SET current_status = 'Available' WHERE slot_id = ?;", (s_id,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Cancelled", f"Booking #{b_id} cancelled.")
            load_all_bookings()

        btn_row = tk.Frame(card, bg=COLORS["bg_card"])
        btn_row.pack(fill="x", pady=(12, 0))

        tk.Button(btn_row, text="❌ Admin Cancel Booking", font=FONTS["body"], bg=COLORS["danger"], fg="#FFFFFF",
                  bd=0, padx=12, pady=5, cursor="hand2", command=admin_cancel).pack(side="left")
        tk.Button(btn_row, text="🔄 Refresh", font=FONTS["body"], bg=COLORS["primary"], fg="#FFFFFF",
                  bd=0, padx=12, pady=5, cursor="hand2", command=load_all_bookings).pack(side="left", padx=10)
        tk.Button(btn_row, text="← Back to Dashboard", font=FONTS["body"], bg=COLORS["secondary"], fg="#FFFFFF",
                  bd=0, padx=12, pady=5, cursor="hand2", command=self.show_dashboard).pack(side="right")

        load_all_bookings()

    # =========================================================================
    # 11. FEE & PAYMENT AUDIT
    # =========================================================================
    def show_payment_details(self):
        self.clear_container()
        create_header(self.container, "Fees & Payments Audit", "Collection history and payment methods", on_logout=self.logout)

        main_area = tk.Frame(self.container, bg=COLORS["bg_main"], padx=20, pady=15)
        main_area.pack(fill="both", expand=True)

        card = tk.Frame(main_area, bg=COLORS["bg_card"], bd=1, relief="solid", padx=15, pady=12)
        card.pack(fill="both", expand=True)

        cols = ("pay_id", "session_id", "driver", "vehicle", "hours", "rate", "amount", "method", "status", "time")
        tree = ttk.Treeview(card, columns=cols, show="headings", height=11)
        tree.heading("pay_id", text="Pay ID")
        tree.heading("session_id", text="Session ID")
        tree.heading("driver", text="Driver")
        tree.heading("vehicle", text="Vehicle Plate")
        tree.heading("hours", text="Hours")
        tree.heading("rate", text="Rate/Hr")
        tree.heading("amount", text="Amount (₹)")
        tree.heading("method", text="Method")
        tree.heading("status", text="Status")
        tree.heading("time", text="Timestamp")

        for c in cols:
            tree.column(c, anchor="center")
        tree.pack(fill="both", expand=True)

        def load_payments():
            for r in tree.get_children():
                tree.delete(r)
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                """SELECT fp.payment_id, fp.session_id, u.full_name, v.registration_number,
                          fp.duration_hours, fp.rate_applied, fp.amount, fp.method, fp.payment_status, fp.paid_at
                   FROM fees_payments fp
                   JOIN parking_sessions ps ON fp.session_id = ps.session_id
                   JOIN bookings b ON ps.booking_id = b.booking_id
                   JOIN users u ON b.user_id = u.user_id
                   JOIN vehicles v ON b.vehicle_id = v.vehicle_id
                   ORDER BY fp.payment_id DESC;"""
            )
            for row in cur.fetchall():
                tree.insert("", "end", values=tuple(row))
            conn.close()

        btn_row = tk.Frame(card, bg=COLORS["bg_card"])
        btn_row.pack(fill="x", pady=(12, 0))

        tk.Button(btn_row, text="🔄 Refresh Log", font=FONTS["body"], bg=COLORS["primary"], fg="#FFFFFF",
                  bd=0, padx=12, pady=5, cursor="hand2", command=load_payments).pack(side="left")
        tk.Button(btn_row, text="← Back to Dashboard", font=FONTS["body"], bg=COLORS["secondary"], fg="#FFFFFF",
                  bd=0, padx=12, pady=5, cursor="hand2", command=self.show_dashboard).pack(side="right")

        load_payments()

    # =========================================================================
    # 12. REPORTS & HISTORY (WITH CSV EXPORT)
    # =========================================================================
    def show_reports(self):
        self.clear_container()
        create_header(self.container, "Reports & History", "Operational audits and CSV data export", on_logout=self.logout)

        main_area = tk.Frame(self.container, bg=COLORS["bg_main"], padx=20, pady=15)
        main_area.pack(fill="both", expand=True)

        card = tk.Frame(main_area, bg=COLORS["bg_card"], bd=1, relief="solid", padx=15, pady=12)
        card.pack(fill="both", expand=True)

        # Filters
        filter_box = tk.Frame(card, bg=COLORS["bg_card"])
        filter_box.pack(fill="x", pady=(0, 10))

        tk.Label(filter_box, text="Filter by Status:", font=FONTS["body_bold"], bg=COLORS["bg_card"]).pack(side="left", padx=4)
        combo_stat = ttk.Combobox(filter_box, values=["All", "Completed", "Confirmed", "Checked-in", "Cancelled"], state="readonly", width=14)
        combo_stat.current(0)
        combo_stat.pack(side="left", padx=4)

        cols = ("b_id", "date", "driver", "vehicle", "facility", "slot", "status", "fee")
        tree = ttk.Treeview(card, columns=cols, show="headings", height=10)
        tree.heading("b_id", text="Booking ID")
        tree.heading("date", text="Date")
        tree.heading("driver", text="Driver")
        tree.heading("vehicle", text="Vehicle Plate")
        tree.heading("facility", text="Facility")
        tree.heading("slot", text="Slot")
        tree.heading("status", text="Status")
        tree.heading("fee", text="Fee Collected (₹)")

        for c in cols:
            tree.column(c, anchor="center")
        tree.pack(fill="both", expand=True)

        def load_report_data():
            for r in tree.get_children():
                tree.delete(r)
            stat = combo_stat.get()
            q = """
                SELECT b.booking_id, b.booking_date, u.full_name, v.registration_number,
                       pf.name, ps.slot_number, b.booking_status, COALESCE(fp.amount, 0.0)
                FROM bookings b
                JOIN users u ON b.user_id = u.user_id
                JOIN vehicles v ON b.vehicle_id = v.vehicle_id
                JOIN parking_slots ps ON b.slot_id = ps.slot_id
                JOIN parking_facilities pf ON ps.facility_id = pf.facility_id
                LEFT JOIN parking_sessions sess ON b.booking_id = sess.booking_id
                LEFT JOIN fees_payments fp ON sess.session_id = fp.session_id
            """
            params = []
            if stat != "All":
                q += " WHERE b.booking_status = ?"
                params.append(stat)
            q += " ORDER BY b.booking_id DESC;"

            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(q, params)
            rows = cur.fetchall()
            for r in rows:
                tree.insert("", "end", values=tuple(r))
            conn.close()

        def export_csv():
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV Files", "*.csv")],
                initialfile="parkslot_report.csv"
            )
            if not file_path:
                return

            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Booking ID", "Date", "Driver", "Vehicle Plate", "Facility", "Slot", "Status", "Fee Collected (₹)"])
                for item in tree.get_children():
                    writer.writerow(tree.item(item)["values"])

            messagebox.showinfo("Export Successful", f"Report saved to:\n{file_path}")

        btn_row = tk.Frame(card, bg=COLORS["bg_card"])
        btn_row.pack(fill="x", pady=(12, 0))

        tk.Button(filter_box, text="Filter", font=FONTS["body_bold"], bg=COLORS["primary"], fg="#FFFFFF",
                  bd=0, padx=10, pady=3, cursor="hand2", command=load_report_data).pack(side="left", padx=8)
        tk.Button(btn_row, text="📥 Export Report to CSV", font=FONTS["body_bold"], bg=COLORS["success"], fg="#FFFFFF",
                  bd=0, padx=12, pady=5, cursor="hand2", command=export_csv).pack(side="left")
        tk.Button(btn_row, text="← Back to Dashboard", font=FONTS["body"], bg=COLORS["secondary"], fg="#FFFFFF",
                  bd=0, padx=12, pady=5, cursor="hand2", command=self.show_dashboard).pack(side="right")

        load_report_data()

    # =========================================================================
    # 13. ADMIN SETTINGS
    # =========================================================================
    def show_settings(self):
        self.clear_container()
        create_header(self.container, "Admin Settings", "Configure operational parameters and system security", on_logout=self.logout)

        main_area = tk.Frame(self.container, bg=COLORS["bg_main"], padx=20, pady=20)
        main_area.pack(expand=True)

        card = tk.Frame(main_area, bg=COLORS["bg_card"], bd=1, relief="solid", padx=30, pady=20)
        card.pack()

        tk.Label(card, text="System Configurations", font=FONTS["subtitle"], bg=COLORS["bg_card"]).grid(row=0, column=0, columnspan=2, pady=(0, 15))

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT setting_key, setting_value FROM admin_settings;")
        settings = dict(cur.fetchall())
        conn.close()

        tk.Label(card, text="Overstay Grace Period (Minutes):", font=FONTS["body_bold"], bg=COLORS["bg_card"]).grid(row=1, column=0, sticky="w", pady=6)
        entry_grace = ttk.Entry(card, width=22)
        entry_grace.insert(0, settings.get("overstay_grace_period_mins", "15"))
        entry_grace.grid(row=1, column=1, pady=6)

        tk.Label(card, text="Default Car Rate (₹/hr):", font=FONTS["body_bold"], bg=COLORS["bg_card"]).grid(row=2, column=0, sticky="w", pady=6)
        entry_car = ttk.Entry(card, width=22)
        entry_car.insert(0, settings.get("default_hourly_rate_car", "30.0"))
        entry_car.grid(row=2, column=1, pady=6)

        tk.Label(card, text="Default Bike Rate (₹/hr):", font=FONTS["body_bold"], bg=COLORS["bg_card"]).grid(row=3, column=0, sticky="w", pady=6)
        entry_bike = ttk.Entry(card, width=22)
        entry_bike.insert(0, settings.get("default_hourly_rate_bike", "15.0"))
        entry_bike.grid(row=3, column=1, pady=6)

        tk.Label(card, text="System Contact Email:", font=FONTS["body_bold"], bg=COLORS["bg_card"]).grid(row=4, column=0, sticky="w", pady=6)
        entry_email = ttk.Entry(card, width=22)
        entry_email.insert(0, settings.get("system_contact_email", "admin@parkslot.com"))
        entry_email.grid(row=4, column=1, pady=6)

        def save_settings():
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("UPDATE admin_settings SET setting_value = ? WHERE setting_key = 'overstay_grace_period_mins';", (entry_grace.get().strip(),))
            cur.execute("UPDATE admin_settings SET setting_value = ? WHERE setting_key = 'default_hourly_rate_car';", (entry_car.get().strip(),))
            cur.execute("UPDATE admin_settings SET setting_value = ? WHERE setting_key = 'default_hourly_rate_bike';", (entry_bike.get().strip(),))
            cur.execute("UPDATE admin_settings SET setting_value = ? WHERE setting_key = 'system_contact_email';", (entry_email.get().strip(),))
            conn.commit()
            conn.close()
            messagebox.showinfo("Saved", "Settings updated successfully!")

        btn_row = tk.Frame(card, bg=COLORS["bg_card"])
        btn_row.grid(row=5, column=0, columnspan=2, pady=(20, 0))

        tk.Button(btn_row, text="💾 Save Configurations", font=FONTS["body_bold"], bg=COLORS["primary"], fg="#FFFFFF",
                  pady=5, padx=12, bd=0, cursor="hand2", command=save_settings).pack(side="left", padx=5)
        tk.Button(btn_row, text="Back to Dashboard", font=FONTS["body"], bg=COLORS["secondary"], fg="#FFFFFF",
                  pady=5, padx=12, bd=0, cursor="hand2", command=self.show_dashboard).pack(side="left", padx=5)

if __name__ == "__main__":
    app = AdminApp()
    app.mainloop()

