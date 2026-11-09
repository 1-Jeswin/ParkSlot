import tkinter as tk
from tkinter import ttk, messagebox
from shared.config import COLORS, FONTS
from shared.database import get_db_connection, init_db
from shared.security import hash_password, verify_password
from shared.ui_helpers import apply_global_styles, create_header

class OwnerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ParkSlot — Parking Facility Owner Portal")
        self.geometry("980x700")
        self.minsize(920, 620)
        apply_global_styles(self)

        self.current_owner = None  # Holds logged-in owner dict
        self.container = tk.Frame(self, bg=COLORS["bg_main"])
        self.container.pack(fill="both", expand=True)

        init_db()
        self.show_welcome()

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    # =========================================================================
    # 1. OWNER WELCOME PAGE
    # =========================================================================
    def show_welcome(self):
        self.clear_container()
        create_header(self.container, "ParkSlot", "Facility Owner & Operations Management")

        body = tk.Frame(self.container, bg=COLORS["bg_main"], pady=40)
        body.pack(expand=True)

        card = tk.Frame(body, bg=COLORS["bg_card"], bd=1, relief="solid", padx=40, pady=30)
        card.pack()

        tk.Label(card, text="Owner Management Portal", font=("Segoe UI", 20, "bold"),
                 bg=COLORS["bg_card"], fg=COLORS["primary"]).pack(pady=(0, 10))
        tk.Label(card, text="Register parking facilities, configure slots, set custom tariffs,\nand view real-time booking logs and earnings.",
                 font=FONTS["body"], bg=COLORS["bg_card"], fg=COLORS["text_muted"], justify="center").pack(pady=(0, 25))

        btn_box = tk.Frame(card, bg=COLORS["bg_card"])
        btn_box.pack(pady=10)

        tk.Button(btn_box, text="Owner Login", font=FONTS["body_bold"], bg=COLORS["primary"], fg="#FFFFFF",
                  width=18, pady=8, bd=0, cursor="hand2", command=self.show_login).pack(side="left", padx=10)
        tk.Button(btn_box, text="Register as Owner", font=FONTS["body_bold"], bg=COLORS["secondary"], fg="#FFFFFF",
                  width=18, pady=8, bd=0, cursor="hand2", command=self.show_register).pack(side="left", padx=10)

        tk.Button(card, text="Exit Application", font=FONTS["small"], bg=COLORS["bg_card"], fg=COLORS["danger"],
                  bd=0, cursor="hand2", command=self.destroy).pack(pady=(25, 0))

    # =========================================================================
    # 2. OWNER REGISTRATION PAGE
    # =========================================================================
    def show_register(self):
        self.clear_container()
        create_header(self.container, "ParkSlot", "Owner Portal — New Facility Owner Registration")

        main_frame = tk.Frame(self.container, bg=COLORS["bg_main"], pady=20)
        main_frame.pack(expand=True)

        card = tk.Frame(main_frame, bg=COLORS["bg_card"], bd=1, relief="solid", padx=30, pady=25)
        card.pack()

        tk.Label(card, text="Register New Parking Owner", font=FONTS["header"], bg=COLORS["bg_card"], fg=COLORS["text_dark"]).grid(row=0, column=0, columnspan=2, pady=(0, 15))

        fields = [
            ("Full Name:", "entry_name"),
            ("Email Address:", "entry_email"),
            ("Phone Number:", "entry_phone"),
            ("Username:", "entry_username"),
            ("Password:", "entry_pass"),
            ("Confirm Password:", "entry_confirm")
        ]

        self.reg_entries = {}
        for r, (label_text, field_name) in enumerate(fields, start=1):
            tk.Label(card, text=label_text, font=FONTS["body_bold"], bg=COLORS["bg_card"], fg=COLORS["text_dark"]).grid(row=r, column=0, sticky="w", pady=6, padx=(0, 15))
            show_char = "*" if "pass" in field_name or "confirm" in field_name else None
            entry = ttk.Entry(card, width=28, show=show_char)
            entry.grid(row=r, column=1, pady=6)
            self.reg_entries[field_name] = entry

        btn_row = tk.Frame(card, bg=COLORS["bg_card"])
        btn_row.grid(row=7, column=0, columnspan=2, pady=(20, 10))

        def _do_owner_reg():
            fn = self.reg_entries["entry_name"].get().strip()
            em = self.reg_entries["entry_email"].get().strip()
            ph = self.reg_entries["entry_phone"].get().strip()
            un = self.reg_entries["entry_username"].get().strip()
            pw = self.reg_entries["entry_pass"].get()
            cp = self.reg_entries["entry_confirm"].get()

            if not all([fn, em, ph, un, pw, cp]):
                messagebox.showwarning("Error", "All fields are required.")
                return
            if pw != cp:
                messagebox.showerror("Error", "Passwords do not match.")
                return

            conn = get_db_connection()
            cur = conn.cursor()
            try:
                cur.execute("SELECT owner_id FROM owners WHERE username = ? OR email = ?;", (un, em))
                if cur.fetchone():
                    messagebox.showerror("Error", "Username or Email already registered.")
                    return

                cur.execute(
                    """INSERT INTO owners (full_name, email, phone_number, username, password_hash, account_status)
                       VALUES (?, ?, ?, ?, ?, 'Active');""",
                    (fn, em, ph, un, hash_password(pw))
                )
                conn.commit()
                messagebox.showinfo("Success", "Owner registered successfully! Please login.")
                self.show_login()
            except Exception as e:
                messagebox.showerror("Error", str(e))
            finally:
                conn.close()

        tk.Button(btn_row, text="Register", font=FONTS["body_bold"], bg=COLORS["primary"], fg="#FFFFFF",
                  width=12, pady=5, bd=0, cursor="hand2", command=_do_owner_reg).pack(side="left", padx=5)
        tk.Button(btn_row, text="Clear", font=FONTS["body"], bg=COLORS["secondary"], fg="#FFFFFF",
                  width=10, pady=5, bd=0, cursor="hand2", command=lambda: [e.delete(0, tk.END) for e in self.reg_entries.values()]).pack(side="left", padx=5)
        tk.Button(btn_row, text="Back to Login", font=FONTS["body"], bg=COLORS["bg_card"], fg=COLORS["primary"],
                  bd=0, cursor="hand2", command=self.show_login).pack(side="left", padx=5)

    # =========================================================================
    # 3. OWNER LOGIN PAGE
    # =========================================================================
    def show_login(self):
        self.clear_container()
        create_header(self.container, "ParkSlot", "Owner Portal — Authentication")

        main_frame = tk.Frame(self.container, bg=COLORS["bg_main"], pady=40)
        main_frame.pack(expand=True)

        card = tk.Frame(main_frame, bg=COLORS["bg_card"], bd=1, relief="solid", padx=35, pady=30)
        card.pack()

        tk.Label(card, text="Facility Owner Sign In", font=FONTS["header"], bg=COLORS["bg_card"], fg=COLORS["text_dark"]).pack(pady=(0, 20))

        tk.Label(card, text="Username or Email", font=FONTS["body_bold"], bg=COLORS["bg_card"], fg=COLORS["text_dark"]).pack(anchor="w")
        entry_user = ttk.Entry(card, width=32)
        entry_user.pack(pady=(4, 12))
        entry_user.insert(0, "owner1")

        tk.Label(card, text="Password", font=FONTS["body_bold"], bg=COLORS["bg_card"], fg=COLORS["text_dark"]).pack(anchor="w")
        entry_pass = ttk.Entry(card, width=32, show="*")
        entry_pass.pack(pady=(4, 20))
        entry_pass.insert(0, "Owner@123")

        def _login():
            u = entry_user.get().strip()
            p = entry_pass.get()
            if not u or not p:
                messagebox.showwarning("Error", "Please enter both credentials.")
                return

            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                """SELECT owner_id, full_name, email, phone_number, username, password_hash, account_status
                   FROM owners WHERE username = ? OR email = ?;""",
                (u, u)
            )
            row = cur.fetchone()
            conn.close()

            if not row or not verify_password(p, row["password_hash"]):
                messagebox.showerror("Error", "Invalid username or password.")
                return

            if row["account_status"] != "Active":
                messagebox.showerror("Suspended", "Your account is not active.")
                return

            self.current_owner = dict(row)
            self.show_dashboard()

        tk.Button(card, text="Login", font=FONTS["body_bold"], bg=COLORS["primary"], fg="#FFFFFF",
                  width=26, pady=7, bd=0, cursor="hand2", command=_login).pack()

        links_frame = tk.Frame(card, bg=COLORS["bg_card"])
        links_frame.pack(fill="x", pady=(15, 0))

        tk.Button(links_frame, text="Create Owner Account", font=FONTS["small"], bg=COLORS["bg_card"], fg=COLORS["primary"],
                  bd=0, cursor="hand2", command=self.show_register).pack(side="left")
        tk.Button(card, text="← Back to Welcome", font=FONTS["small"], bg=COLORS["bg_card"], fg=COLORS["secondary"],
                  bd=0, cursor="hand2", command=self.show_welcome).pack(pady=(15, 0))

    # =========================================================================
    # 4. OWNER DASHBOARD
    # =========================================================================
    def show_dashboard(self):
        self.clear_container()
        create_header(self.container, "Facility Owner Dashboard", f"Logged in as: {self.current_owner['full_name']}", on_logout=self.logout)

        main_area = tk.Frame(self.container, bg=COLORS["bg_main"], padx=25, pady=20)
        main_area.pack(fill="both", expand=True)

        # Compute Owner specific metrics
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM parking_facilities WHERE owner_id = ?;", (self.current_owner["owner_id"],))
        total_fac = cur.fetchone()[0]

        cur.execute(
            """SELECT COUNT(ps.slot_id) FROM parking_slots ps
               JOIN parking_facilities pf ON ps.facility_id = pf.facility_id
               WHERE pf.owner_id = ?;""",
            (self.current_owner["owner_id"],)
        )
        total_slots = cur.fetchone()[0]

        cur.execute(
            """SELECT COUNT(ps.slot_id) FROM parking_slots ps
               JOIN parking_facilities pf ON ps.facility_id = pf.facility_id
               WHERE pf.owner_id = ? AND ps.current_status = 'Available';""",
            (self.current_owner["owner_id"],)
        )
        avail_slots = cur.fetchone()[0]

        cur.execute(
            """SELECT COUNT(ps.slot_id) FROM parking_slots ps
               JOIN parking_facilities pf ON ps.facility_id = pf.facility_id
               WHERE pf.owner_id = ? AND ps.current_status IN ('Reserved', 'Occupied');""",
            (self.current_owner["owner_id"],)
        )
        booked_slots = cur.fetchone()[0]

        cur.execute(
            """SELECT COUNT(b.booking_id) FROM bookings b
               JOIN parking_slots ps ON b.slot_id = ps.slot_id
               JOIN parking_facilities pf ON ps.facility_id = pf.facility_id
               WHERE pf.owner_id = ?;""",
            (self.current_owner["owner_id"],)
        )
        total_bookings = cur.fetchone()[0]
        conn.close()

        # Stats Cards
        stats_frame = tk.Frame(main_area, bg=COLORS["bg_main"])
        stats_frame.pack(fill="x", pady=(0, 20))

        def make_stat_card(parent, title, val, color):
            box = tk.Frame(parent, bg=COLORS["bg_card"], bd=1, relief="solid", padx=12, pady=10)
            box.pack(side="left", fill="both", expand=True, padx=5)
            tk.Label(box, text=title, font=FONTS["small"], bg=COLORS["bg_card"], fg=COLORS["text_muted"]).pack()
            tk.Label(box, text=str(val), font=FONTS["stat_num"], bg=COLORS["bg_card"], fg=color).pack()

        make_stat_card(stats_frame, "Total Facilities", total_fac, COLORS["primary"])
        make_stat_card(stats_frame, "Total Slots", total_slots, COLORS["secondary"])
        make_stat_card(stats_frame, "Available Slots", avail_slots, COLORS["success"])
        make_stat_card(stats_frame, "Booked / Occupied", booked_slots, COLORS["danger"])
        make_stat_card(stats_frame, "Total Bookings", total_bookings, COLORS["warning"])

        # Menu Grid
        menu_frame = tk.Frame(main_area, bg=COLORS["bg_card"], bd=1, relief="solid", padx=25, pady=20)
        menu_frame.pack(fill="both", expand=True)

        tk.Label(menu_frame, text="Owner Operations & Management", font=FONTS["subtitle"],
                 bg=COLORS["bg_card"], fg=COLORS["text_dark"]).pack(anchor="w", pady=(0, 15))

        btn_grid = tk.Frame(menu_frame, bg=COLORS["bg_card"])
        btn_grid.pack(expand=True)

        actions = [
            ("🏢 Add Parking Facility", "Register new parking premises and timings", self.show_facility_registration),
            ("🅿️ Manage Parking Slots", "Add, edit, or toggle slot statuses", self.show_slot_management),
            ("💰 Set Parking Rates", "Configure hourly tariffs by vehicle type", self.show_rate_management),
            ("📋 View User Bookings", "Monitor active and scheduled reservations", self.show_booking_management),
            ("📊 Parking Records & Fees", "Review historical sessions and revenues", self.show_parking_records),
            ("👤 My Profile", "View and update owner details", self.show_profile)
        ]

        for i, (btn_text, desc, cmd) in enumerate(actions):
            item_box = tk.Frame(btn_grid, bg="#F8FAFC", bd=1, relief="solid", padx=15, pady=12, width=280, height=85)
            item_box.grid(row=i // 3, column=i % 3, padx=10, pady=10)
            item_box.pack_propagate(False)

            tk.Button(item_box, text=btn_text, font=FONTS["body_bold"], bg=COLORS["primary"], fg="#FFFFFF",
                      bd=0, cursor="hand2", command=cmd).pack(fill="x")
            tk.Label(item_box, text=desc, font=FONTS["small"], bg="#F8FAFC", fg=COLORS["text_muted"]).pack(pady=(4, 0))

    def logout(self):
        if messagebox.askyesno("Logout", "Exit Owner account?"):
            self.current_owner = None
            self.show_welcome()

    # =========================================================================
    # 5. MY PROFILE PAGE (OWNER)
    # =========================================================================
    def show_profile(self):
        self.clear_container()
        create_header(self.container, "Owner Profile", f"Owner ID: #{self.current_owner['owner_id']}", on_logout=self.logout)

        main_area = tk.Frame(self.container, bg=COLORS["bg_main"], padx=20, pady=20)
        main_area.pack(expand=True)

        card = tk.Frame(main_area, bg=COLORS["bg_card"], bd=1, relief="solid", padx=30, pady=25)
        card.pack()

        tk.Label(card, text="Facility Owner Profile Details", font=FONTS["subtitle"], bg=COLORS["bg_card"]).grid(row=0, column=0, columnspan=2, pady=(0, 15))

        tk.Label(card, text="Full Name:", font=FONTS["body_bold"], bg=COLORS["bg_card"]).grid(row=1, column=0, sticky="w", pady=6)
        entry_name = ttk.Entry(card, width=28)
        entry_name.grid(row=1, column=1, pady=6)
        entry_name.insert(0, self.current_owner["full_name"])

        tk.Label(card, text="Email Address:", font=FONTS["body_bold"], bg=COLORS["bg_card"]).grid(row=2, column=0, sticky="w", pady=6)
        entry_email = ttk.Entry(card, width=28)
        entry_email.grid(row=2, column=1, pady=6)
        entry_email.insert(0, self.current_owner["email"])

        tk.Label(card, text="Phone Number:", font=FONTS["body_bold"], bg=COLORS["bg_card"]).grid(row=3, column=0, sticky="w", pady=6)
        entry_phone = ttk.Entry(card, width=28)
        entry_phone.grid(row=3, column=1, pady=6)
        entry_phone.insert(0, self.current_owner["phone_number"])

        tk.Label(card, text="Username:", font=FONTS["body_bold"], bg=COLORS["bg_card"]).grid(row=4, column=0, sticky="w", pady=6)
        entry_user = ttk.Entry(card, width=28)
        entry_user.grid(row=4, column=1, pady=6)
        entry_user.insert(0, self.current_owner["username"])
        entry_user.config(state="disabled")

        def _update():
            fn = entry_name.get().strip()
            em = entry_email.get().strip()
            ph = entry_phone.get().strip()
            if not fn or not em or not ph:
                messagebox.showwarning("Error", "All fields are required.")
                return
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("UPDATE owners SET full_name = ?, email = ?, phone_number = ? WHERE owner_id = ?;",
                        (fn, em, ph, self.current_owner["owner_id"]))
            conn.commit()
            conn.close()
            self.current_owner["full_name"] = fn
            self.current_owner["email"] = em
            self.current_owner["phone_number"] = ph
            messagebox.showinfo("Success", "Owner Profile updated!")

        btn_row = tk.Frame(card, bg=COLORS["bg_card"])
        btn_row.grid(row=5, column=0, columnspan=2, pady=(20, 0))

        tk.Button(btn_row, text="Update Profile", font=FONTS["body_bold"], bg=COLORS["primary"], fg="#FFFFFF",
                  pady=5, padx=12, bd=0, cursor="hand2", command=_update).pack(side="left", padx=5)
        tk.Button(btn_row, text="Back to Dashboard", font=FONTS["body"], bg=COLORS["secondary"], fg="#FFFFFF",
                  pady=5, padx=12, bd=0, cursor="hand2", command=self.show_dashboard).pack(side="left", padx=5)

    # =========================================================================
    # 6. PARKING FACILITY REGISTRATION PAGE
    # =========================================================================
    def show_facility_registration(self):
        self.clear_container()
        create_header(self.container, "Register Parking Facility", "Add a new parking premise", on_logout=self.logout)

        main_area = tk.Frame(self.container, bg=COLORS["bg_main"], padx=20, pady=15)
        main_area.pack(fill="both", expand=True)

        card = tk.Frame(main_area, bg=COLORS["bg_card"], bd=1, relief="solid", padx=25, pady=20)
        card.pack(fill="x", pady=(0, 15))

        tk.Label(card, text="Facility Registration Form", font=FONTS["subtitle"], bg=COLORS["bg_card"]).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 10))

        tk.Label(card, text="Facility Name:*", font=FONTS["body_bold"], bg=COLORS["bg_card"]).grid(row=1, column=0, sticky="w", pady=4, padx=5)
        entry_name = ttk.Entry(card, width=22)
        entry_name.grid(row=1, column=1, pady=4, padx=5)

        tk.Label(card, text="Location Address:*", font=FONTS["body_bold"], bg=COLORS["bg_card"]).grid(row=1, column=2, sticky="w", pady=4, padx=5)
        entry_loc = ttk.Entry(card, width=22)
        entry_loc.grid(row=1, column=3, pady=4, padx=5)

        tk.Label(card, text="Contact Number:*", font=FONTS["body_bold"], bg=COLORS["bg_card"]).grid(row=2, column=0, sticky="w", pady=4, padx=5)
        entry_phone = ttk.Entry(card, width=22)
        entry_phone.grid(row=2, column=1, pady=4, padx=5)

        tk.Label(card, text="Total Slots Capacity:", font=FONTS["body_bold"], bg=COLORS["bg_card"]).grid(row=2, column=2, sticky="w", pady=4, padx=5)
        entry_cap = ttk.Entry(card, width=22)
        entry_cap.insert(0, "10")
        entry_cap.grid(row=2, column=3, pady=4, padx=5)

        tk.Label(card, text="Opening Time (HH:MM):", font=FONTS["body_bold"], bg=COLORS["bg_card"]).grid(row=3, column=0, sticky="w", pady=4, padx=5)
        entry_open = ttk.Entry(card, width=22)
        entry_open.insert(0, "06:00")
        entry_open.grid(row=3, column=1, pady=4, padx=5)

        tk.Label(card, text="Closing Time (HH:MM):", font=FONTS["body_bold"], bg=COLORS["bg_card"]).grid(row=3, column=2, sticky="w", pady=4, padx=5)
        entry_close = ttk.Entry(card, width=22)
        entry_close.insert(0, "23:00")
        entry_close.grid(row=3, column=3, pady=4, padx=5)

        # List of existing facilities
        list_card = tk.Frame(main_area, bg=COLORS["bg_card"], bd=1, relief="solid", padx=20, pady=12)
        list_card.pack(fill="both", expand=True)

        tk.Label(list_card, text="Your Registered Facilities", font=FONTS["subtitle"], bg=COLORS["bg_card"]).pack(anchor="w", pady=(0, 6))

        cols = ("id", "name", "loc", "phone", "slots", "hours")
        tree = ttk.Treeview(list_card, columns=cols, show="headings", height=6)
        tree.heading("id", text="ID")
        tree.heading("name", text="Facility Name")
        tree.heading("loc", text="Location")
        tree.heading("phone", text="Contact")
        tree.heading("slots", text="Capacity")
        tree.heading("hours", text="Operating Hours")

        tree.column("id", width=50, anchor="center")
        tree.column("name", width=200)
        tree.column("loc", width=200)
        tree.column("phone", width=120, anchor="center")
        tree.column("slots", width=80, anchor="center")
        tree.column("hours", width=130, anchor="center")
        tree.pack(fill="both", expand=True)

        def load_facs():
            for r in tree.get_children():
                tree.delete(r)
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                """SELECT facility_id, name, location, contact_number, total_slots, (opening_time || ' - ' || closing_time)
                   FROM parking_facilities WHERE owner_id = ? ORDER BY facility_id DESC;""",
                (self.current_owner["owner_id"],)
            )
            for row in cur.fetchall():
                tree.insert("", "end", values=tuple(row))
            conn.close()

        def register_fac():
            fn = entry_name.get().strip()
            loc = entry_loc.get().strip()
            ph = entry_phone.get().strip()
            cap = entry_cap.get().strip() or "0"
            op = entry_open.get().strip()
            cl = entry_close.get().strip()

            if not fn or not loc or not ph:
                messagebox.showerror("Error", "Facility name, location and contact are required.")
                return

            conn = get_db_connection()
            cur = conn.cursor()
            try:
                cur.execute(
                    """INSERT INTO parking_facilities (owner_id, name, location, contact_number, total_slots, opening_time, closing_time)
                       VALUES (?, ?, ?, ?, ?, ?, ?);""",
                    (self.current_owner["owner_id"], fn, loc, ph, int(cap), op, cl)
                )
                conn.commit()
                messagebox.showinfo("Success", f"Facility '{fn}' registered successfully!")
                entry_name.delete(0, tk.END)
                entry_loc.delete(0, tk.END)
                entry_phone.delete(0, tk.END)
                load_facs()
            except Exception as e:
                messagebox.showerror("Error", str(e))
            finally:
                conn.close()

        btn_box = tk.Frame(card, bg=COLORS["bg_card"])
        btn_box.grid(row=4, column=0, columnspan=4, sticky="e", pady=(12, 0))

        tk.Button(btn_box, text="+ Register Facility", font=FONTS["body_bold"], bg=COLORS["primary"], fg="#FFFFFF",
                  bd=0, padx=12, pady=5, cursor="hand2", command=register_fac).pack(side="left", padx=5)
        tk.Button(list_card, text="← Back to Dashboard", font=FONTS["body"], bg=COLORS["secondary"], fg="#FFFFFF",
                  bd=0, padx=12, pady=5, cursor="hand2", command=self.show_dashboard).pack(anchor="e", pady=(8, 0))

        load_facs()

    # =========================================================================
    # 7. PARKING SLOT MANAGEMENT PAGE
    # =========================================================================
    def show_slot_management(self):
        self.clear_container()
        create_header(self.container, "Parking Slot Management", "Add and maintain individual slot spaces", on_logout=self.logout)

        main_area = tk.Frame(self.container, bg=COLORS["bg_main"], padx=20, pady=15)
        main_area.pack(fill="both", expand=True)

        # Facility selector & Slot entry card
        card = tk.Frame(main_area, bg=COLORS["bg_card"], bd=1, relief="solid", padx=20, pady=12)
        card.pack(fill="x", pady=(0, 15))

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT facility_id, name FROM parking_facilities WHERE owner_id = ?;", (self.current_owner["owner_id"],))
        facilities = cur.fetchall()
        conn.close()

        if not facilities:
            messagebox.showwarning("No Facility", "Please register a facility first before creating slots.")
            self.show_facility_registration()
            return

        fac_map = {f["name"]: f["facility_id"] for f in facilities}
        fac_names = list(fac_map.keys())

        tk.Label(card, text="Select Facility:*", font=FONTS["body_bold"], bg=COLORS["bg_card"]).grid(row=0, column=0, sticky="w", padx=5, pady=4)
        combo_fac = ttk.Combobox(card, values=fac_names, state="readonly", width=22)
        combo_fac.current(0)
        combo_fac.grid(row=0, column=1, sticky="w", padx=5, pady=4)

        tk.Label(card, text="Slot Number:*", font=FONTS["body_bold"], bg=COLORS["bg_card"]).grid(row=0, column=2, sticky="w", padx=5, pady=4)
        entry_slot = ttk.Entry(card, width=14)
        entry_slot.grid(row=0, column=3, sticky="w", padx=5, pady=4)

        tk.Label(card, text="Vehicle Type:*", font=FONTS["body_bold"], bg=COLORS["bg_card"]).grid(row=1, column=0, sticky="w", padx=5, pady=4)
        combo_vtype = ttk.Combobox(card, values=["Car", "Bike", "Other"], state="readonly", width=14)
        combo_vtype.current(0)
        combo_vtype.grid(row=1, column=1, sticky="w", padx=5, pady=4)

        tk.Label(card, text="Floor / Zone:", font=FONTS["body_bold"], bg=COLORS["bg_card"]).grid(row=1, column=2, sticky="w", padx=5, pady=4)
        entry_zone = ttk.Entry(card, width=14)
        entry_zone.insert(0, "Ground")
        entry_zone.grid(row=1, column=3, sticky="w", padx=5, pady=4)

        # Slots Table
        table_card = tk.Frame(main_area, bg=COLORS["bg_card"], bd=1, relief="solid", padx=15, pady=12)
        table_card.pack(fill="both", expand=True)

        cols = ("slot_id", "slot_num", "v_type", "zone", "status")
        tree = ttk.Treeview(table_card, columns=cols, show="headings", height=9)
        tree.heading("slot_id", text="Slot ID")
        tree.heading("slot_num", text="Slot Number")
        tree.heading("v_type", text="Supported Vehicle")
        tree.heading("zone", text="Floor / Zone")
        tree.heading("status", text="Current Status")

        tree.column("slot_id", width=70, anchor="center")
        tree.column("slot_num", width=120, anchor="center")
        tree.column("v_type", width=140, anchor="center")
        tree.column("zone", width=140, anchor="center")
        tree.column("status", width=140, anchor="center")
        tree.pack(fill="both", expand=True)

        def load_slots(*args):
            for r in tree.get_children():
                tree.delete(r)
            sel_fac = combo_fac.get()
            if not sel_fac:
                return
            fac_id = fac_map[sel_fac]

            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                """SELECT slot_id, slot_number, vehicle_type, floor_zone, current_status
                   FROM parking_slots WHERE facility_id = ? ORDER BY slot_number ASC;""",
                (fac_id,)
            )
            for row in cur.fetchall():
                tree.insert("", "end", values=tuple(row))
            conn.close()

        combo_fac.bind("<<ComboboxSelected>>", load_slots)

        def add_slot():
            sel_fac = combo_fac.get()
            s_num = entry_slot.get().strip().upper()
            v_type = combo_vtype.get()
            zone = entry_zone.get().strip() or "Ground"

            if not s_num:
                messagebox.showwarning("Error", "Slot number is required (e.g. A01).")
                return

            fac_id = fac_map[sel_fac]
            conn = get_db_connection()
            cur = conn.cursor()
            try:
                cur.execute(
                    """INSERT INTO parking_slots (facility_id, slot_number, vehicle_type, floor_zone, current_status)
                       VALUES (?, ?, ?, ?, 'Available');""",
                    (fac_id, s_num, v_type, zone)
                )
                conn.commit()
                messagebox.showinfo("Success", f"Slot {s_num} created!")
                entry_slot.delete(0, tk.END)
                load_slots()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add slot: {e}")
            finally:
                conn.close()

        def toggle_status():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Select", "Select a slot to toggle active/inactive.")
                return
            s_id = tree.item(sel[0])["values"][0]
            cur_stat = tree.item(sel[0])["values"][4]
            new_stat = "Inactive" if cur_stat == "Available" else "Available"

            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("UPDATE parking_slots SET current_status = ? WHERE slot_id = ?;", (new_stat, s_id))
            conn.commit()
            conn.close()
            load_slots()

        btn_box = tk.Frame(card, bg=COLORS["bg_card"])
        btn_box.grid(row=2, column=0, columnspan=4, sticky="e", pady=(10, 0))
        tk.Button(btn_box, text="+ Add Slot", font=FONTS["body_bold"], bg=COLORS["primary"], fg="#FFFFFF",
                  bd=0, padx=12, pady=4, cursor="hand2", command=add_slot).pack(side="left", padx=5)

        action_row = tk.Frame(table_card, bg=COLORS["bg_card"])
        action_row.pack(fill="x", pady=(10, 0))

        tk.Button(action_row, text="Toggle Active / Inactive", font=FONTS["body"], bg=COLORS["warning"], fg="#FFFFFF",
                  bd=0, padx=10, pady=4, cursor="hand2", command=toggle_status).pack(side="left")
        tk.Button(action_row, text="← Back to Dashboard", font=FONTS["body"], bg=COLORS["secondary"], fg="#FFFFFF",
                  bd=0, padx=10, pady=4, cursor="hand2", command=self.show_dashboard).pack(side="right")

        load_slots()

    # =========================================================================
    # 8. BOOKING MANAGEMENT PAGE (OWNER VIEW)
    # =========================================================================
    def show_booking_management(self):
        self.clear_container()
        create_header(self.container, "Facility Bookings", "Monitor driver reservations across your facilities", on_logout=self.logout)

        main_area = tk.Frame(self.container, bg=COLORS["bg_main"], padx=20, pady=15)
        main_area.pack(fill="both", expand=True)

        card = tk.Frame(main_area, bg=COLORS["bg_card"], bd=1, relief="solid", padx=15, pady=12)
        card.pack(fill="both", expand=True)

        cols = ("b_id", "user_name", "facility", "slot_num", "v_reg", "date", "window", "status")
        tree = ttk.Treeview(card, columns=cols, show="headings", height=11)
        tree.heading("b_id", text="Booking ID")
        tree.heading("user_name", text="Driver Name")
        tree.heading("facility", text="Facility")
        tree.heading("slot_num", text="Slot")
        tree.heading("v_reg", text="Vehicle Number")
        tree.heading("date", text="Date")
        tree.heading("window", text="Time Window")
        tree.heading("status", text="Booking Status")

        tree.column("b_id", width=70, anchor="center")
        tree.column("user_name", width=140)
        tree.column("facility", width=160)
        tree.column("slot_num", width=70, anchor="center")
        tree.column("v_reg", width=110, anchor="center")
        tree.column("date", width=95, anchor="center")
        tree.column("window", width=105, anchor="center")
        tree.column("status", width=95, anchor="center")
        tree.pack(fill="both", expand=True)

        def load_bookings():
            for r in tree.get_children():
                tree.delete(r)
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                """SELECT b.booking_id, u.full_name, pf.name, ps.slot_number, v.registration_number,
                          b.booking_date, (b.start_time || ' - ' || b.end_time) AS win, b.booking_status
                   FROM bookings b
                   JOIN users u ON b.user_id = u.user_id
                   JOIN vehicles v ON b.vehicle_id = v.vehicle_id
                   JOIN parking_slots ps ON b.slot_id = ps.slot_id
                   JOIN parking_facilities pf ON ps.facility_id = pf.facility_id
                   WHERE pf.owner_id = ?
                   ORDER BY b.booking_id DESC;""",
                (self.current_owner["owner_id"],)
            )
            for row in cur.fetchall():
                tree.insert("", "end", values=tuple(row))
            conn.close()

        btn_row = tk.Frame(card, bg=COLORS["bg_card"])
        btn_row.pack(fill="x", pady=(12, 0))

        tk.Button(btn_row, text="🔄 Refresh Bookings", font=FONTS["body"], bg=COLORS["primary"], fg="#FFFFFF",
                  bd=0, padx=12, pady=5, cursor="hand2", command=load_bookings).pack(side="left")
        tk.Button(btn_row, text="← Back to Dashboard", font=FONTS["body"], bg=COLORS["secondary"], fg="#FFFFFF",
                  bd=0, padx=12, pady=5, cursor="hand2", command=self.show_dashboard).pack(side="right")

        load_bookings()

    # =========================================================================
    # 9. PARKING RATE MANAGEMENT PAGE
    # =========================================================================
    def show_rate_management(self):
        self.clear_container()
        create_header(self.container, "Parking Rate Management", "Configure hourly tariffs by vehicle category", on_logout=self.logout)

        main_area = tk.Frame(self.container, bg=COLORS["bg_main"], padx=20, pady=15)
        main_area.pack(fill="both", expand=True)

        # Rate Setter Card
        card = tk.Frame(main_area, bg=COLORS["bg_card"], bd=1, relief="solid", padx=20, pady=15)
        card.pack(fill="x", pady=(0, 15))

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT facility_id, name FROM parking_facilities WHERE owner_id = ?;", (self.current_owner["owner_id"],))
        facs = cur.fetchall()
        conn.close()

        if not facs:
            messagebox.showwarning("No Facility", "Please register a facility first.")
            self.show_facility_registration()
            return

        fac_map = {f["name"]: f["facility_id"] for f in facs}

        tk.Label(card, text="Facility:*", font=FONTS["body_bold"], bg=COLORS["bg_card"]).grid(row=0, column=0, sticky="w", padx=5, pady=6)
        combo_fac = ttk.Combobox(card, values=list(fac_map.keys()), state="readonly", width=22)
        combo_fac.current(0)
        combo_fac.grid(row=0, column=1, sticky="w", padx=5, pady=6)

        tk.Label(card, text="Vehicle Type:*", font=FONTS["body_bold"], bg=COLORS["bg_card"]).grid(row=0, column=2, sticky="w", padx=5, pady=6)
        combo_vt = ttk.Combobox(card, values=["Car", "Bike", "Other"], state="readonly", width=12)
        combo_vt.current(0)
        combo_vt.grid(row=0, column=3, sticky="w", padx=5, pady=6)

        tk.Label(card, text="Rate Per Hour (₹):*", font=FONTS["body_bold"], bg=COLORS["bg_card"]).grid(row=0, column=4, sticky="w", padx=5, pady=6)
        entry_rate = ttk.Entry(card, width=12)
        entry_rate.insert(0, "30.0")
        entry_rate.grid(row=0, column=5, sticky="w", padx=5, pady=6)

        # Rates Table
        table_card = tk.Frame(main_area, bg=COLORS["bg_card"], bd=1, relief="solid", padx=15, pady=12)
        table_card.pack(fill="both", expand=True)

        cols = ("facility", "vtype", "rate", "updated")
        tree = ttk.Treeview(table_card, columns=cols, show="headings", height=7)
        tree.heading("facility", text="Facility Name")
        tree.heading("vtype", text="Vehicle Type")
        tree.heading("rate", text="Rate Per Hour (₹)")
        tree.heading("updated", text="Last Updated")

        tree.column("facility", width=200)
        tree.column("vtype", width=120, anchor="center")
        tree.column("rate", width=120, anchor="center")
        tree.column("updated", width=150, anchor="center")
        tree.pack(fill="both", expand=True)

        def load_rates():
            for r in tree.get_children():
                tree.delete(r)
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                """SELECT pf.name, pr.vehicle_type, pr.rate_per_hour, pr.updated_at
                   FROM parking_rates pr
                   JOIN parking_facilities pf ON pr.facility_id = pf.facility_id
                   WHERE pf.owner_id = ? ORDER BY pf.name;""",
                (self.current_owner["owner_id"],)
            )
            for row in cur.fetchall():
                tree.insert("", "end", values=tuple(row))
            conn.close()

        def set_rate():
            fac_name = combo_fac.get()
            vtype = combo_vt.get()
            try:
                rate_val = float(entry_rate.get().strip())
                if rate_val <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid positive rate.")
                return

            fac_id = fac_map[fac_name]
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                """INSERT INTO parking_rates (facility_id, vehicle_type, rate_per_hour, updated_at)
                   VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                   ON CONFLICT(facility_id, vehicle_type) DO UPDATE SET rate_per_hour = excluded.rate_per_hour, updated_at = CURRENT_TIMESTAMP;""",
                (fac_id, vtype, rate_val)
            )
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", f"Rate for {vtype} updated to ₹{rate_val:.2f}/hr at {fac_name}!")
            load_rates()

        tk.Button(card, text="💾 Save / Update Rate", font=FONTS["body_bold"], bg=COLORS["primary"], fg="#FFFFFF",
                  bd=0, padx=12, pady=4, cursor="hand2", command=set_rate).grid(row=1, column=4, columnspan=2, sticky="e", pady=(10, 0))

        tk.Button(table_card, text="← Back to Dashboard", font=FONTS["body"], bg=COLORS["secondary"], fg="#FFFFFF",
                  bd=0, padx=12, pady=5, cursor="hand2", command=self.show_dashboard).pack(anchor="e", pady=(10, 0))

        load_rates()

    # =========================================================================
    # 10. PARKING RECORDS & REVENUE PAGE
    # =========================================================================
    def show_parking_records(self):
        self.clear_container()
        create_header(self.container, "Parking Records & Revenue", "Audit completed parking sessions & collected fees", on_logout=self.logout)

        main_area = tk.Frame(self.container, bg=COLORS["bg_main"], padx=20, pady=15)
        main_area.pack(fill="both", expand=True)

        card = tk.Frame(main_area, bg=COLORS["bg_card"], bd=1, relief="solid", padx=15, pady=12)
        card.pack(fill="both", expand=True)

        cols = ("b_id", "driver", "vehicle", "slot", "duration", "rate", "fee", "status")
        tree = ttk.Treeview(card, columns=cols, show="headings", height=10)
        tree.heading("b_id", text="Booking ID")
        tree.heading("driver", text="Driver")
        tree.heading("vehicle", text="Vehicle Number")
        tree.heading("slot", text="Slot")
        tree.heading("duration", text="Duration")
        tree.heading("rate", text="Rate/Hr")
        tree.heading("fee", text="Total Fee (₹)")
        tree.heading("status", text="Session Status")

        tree.column("b_id", width=70, anchor="center")
        tree.column("driver", width=140)
        tree.column("vehicle", width=110, anchor="center")
        tree.column("slot", width=70, anchor="center")
        tree.column("duration", width=90, anchor="center")
        tree.column("rate", width=80, anchor="center")
        tree.column("fee", width=90, anchor="center")
        tree.column("status", width=95, anchor="center")
        tree.pack(fill="both", expand=True)

        lbl_total = tk.Label(card, text="Total Revenue Recorded: ₹0.00", font=FONTS["subtitle"], bg=COLORS["bg_card"], fg=COLORS["success"])
        lbl_total.pack(anchor="w", pady=(10, 0))

        def load_records():
            for r in tree.get_children():
                tree.delete(r)
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                """SELECT b.booking_id, u.full_name, v.registration_number, ps.slot_number,
                          COALESCE(fp.duration_hours, 2.0) || ' hrs',
                          '₹' || COALESCE(fp.rate_applied, 30.0),
                          COALESCE(fp.amount, 60.0),
                          b.booking_status
                   FROM bookings b
                   JOIN users u ON b.user_id = u.user_id
                   JOIN vehicles v ON b.vehicle_id = v.vehicle_id
                   JOIN parking_slots ps ON b.slot_id = ps.slot_id
                   JOIN parking_facilities pf ON ps.facility_id = pf.facility_id
                   LEFT JOIN parking_sessions s ON b.booking_id = s.booking_id
                   LEFT JOIN fees_payments fp ON s.session_id = fp.session_id
                   WHERE pf.owner_id = ?;""",
                (self.current_owner["owner_id"],)
            )
            rows = cur.fetchall()
            tot = 0.0
            for row in rows:
                tree.insert("", "end", values=tuple(row))
                if row[6] is not None:
                    tot += float(row[6])
            lbl_total.config(text=f"Total Revenue Recorded for Your Facilities: ₹{tot:.2f}")
            conn.close()

        btn_row = tk.Frame(card, bg=COLORS["bg_card"])
        btn_row.pack(fill="x", pady=(12, 0))

        tk.Button(btn_row, text="🔄 Refresh Records", font=FONTS["body"], bg=COLORS["primary"], fg="#FFFFFF",
                  bd=0, padx=12, pady=5, cursor="hand2", command=load_records).pack(side="left")
        tk.Button(btn_row, text="← Back to Dashboard", font=FONTS["body"], bg=COLORS["secondary"], fg="#FFFFFF",
                  bd=0, padx=12, pady=5, cursor="hand2", command=self.show_dashboard).pack(side="right")

        load_records()

if __name__ == "__main__":
    app = OwnerApp()
    app.mainloop()

