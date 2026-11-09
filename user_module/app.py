import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from shared.config import COLORS, FONTS
from shared.database import get_db_connection, init_db
from shared.security import hash_password, verify_password
from shared.ui_helpers import apply_global_styles, create_header

class UserApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ParkSlot — Driver Portal")
        self.geometry("980x680")
        self.minsize(900, 600)
        apply_global_styles(self)

        self.current_user = None  # Holds logged-in user dict
        self.container = tk.Frame(self, bg=COLORS["bg_main"])
        self.container.pack(fill="both", expand=True)

        init_db()
        self.show_welcome()

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    # =========================================================================
    # 1. WELCOME / HOME PAGE
    # =========================================================================
    def show_welcome(self):
        self.clear_container()
        create_header(self.container, "ParkSlot", "Vehicular Parking Space Identification & Booking")

        body = tk.Frame(self.container, bg=COLORS["bg_main"], pady=40)
        body.pack(expand=True)

        card = tk.Frame(body, bg=COLORS["bg_card"], bd=1, relief="solid", padx=40, pady=30)
        card.pack()

        tk.Label(card, text="Welcome to ParkSlot", font=("Segoe UI", 20, "bold"),
                 bg=COLORS["bg_card"], fg=COLORS["primary"]).pack(pady=(0, 10))
        tk.Label(card, text="Find and reserve hassle-free parking spaces in seconds.\nFast, safe, and transparent billing.",
                 font=FONTS["body"], bg=COLORS["bg_card"], fg=COLORS["text_muted"], justify="center").pack(pady=(0, 25))

        btn_box = tk.Frame(card, bg=COLORS["bg_card"])
        btn_box.pack(pady=10)

        tk.Button(btn_box, text="Driver Login", font=FONTS["body_bold"], bg=COLORS["primary"], fg="#FFFFFF",
                  width=18, pady=8, bd=0, cursor="hand2", command=self.show_login).pack(side="left", padx=10)
        tk.Button(btn_box, text="New Registration", font=FONTS["body_bold"], bg=COLORS["secondary"], fg="#FFFFFF",
                  width=18, pady=8, bd=0, cursor="hand2", command=self.show_register).pack(side="left", padx=10)

        tk.Button(card, text="Exit Application", font=FONTS["small"], bg=COLORS["bg_card"], fg=COLORS["danger"],
                  bd=0, cursor="hand2", command=self.destroy).pack(pady=(25, 0))

    # =========================================================================
    # 2. USER REGISTRATION PAGE
    # =========================================================================
    def show_register(self):
        self.clear_container()
        create_header(self.container, "ParkSlot", "Driver Portal — New User Registration")

        main_frame = tk.Frame(self.container, bg=COLORS["bg_main"], pady=20)
        main_frame.pack(expand=True)

        card = tk.Frame(main_frame, bg=COLORS["bg_card"], bd=1, relief="solid", padx=30, pady=25)
        card.pack()

        tk.Label(card, text="Create Driver Account", font=FONTS["header"], bg=COLORS["bg_card"], fg=COLORS["text_dark"]).grid(row=0, column=0, columnspan=2, pady=(0, 15))

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

        tk.Button(btn_row, text="Register", font=FONTS["body_bold"], bg=COLORS["primary"], fg="#FFFFFF",
                  width=12, pady=5, bd=0, cursor="hand2", command=self._do_register).pack(side="left", padx=5)
        tk.Button(btn_row, text="Clear", font=FONTS["body"], bg=COLORS["secondary"], fg="#FFFFFF",
                  width=10, pady=5, bd=0, cursor="hand2", command=self._clear_reg_fields).pack(side="left", padx=5)
        tk.Button(btn_row, text="Back to Login", font=FONTS["body"], bg=COLORS["bg_card"], fg=COLORS["primary"],
                  bd=0, cursor="hand2", command=self.show_login).pack(side="left", padx=5)

    def _clear_reg_fields(self):
        for entry in self.reg_entries.values():
            entry.delete(0, tk.END)

    def _do_register(self):
        name = self.reg_entries["entry_name"].get().strip()
        email = self.reg_entries["entry_email"].get().strip()
        phone = self.reg_entries["entry_phone"].get().strip()
        username = self.reg_entries["entry_username"].get().strip()
        pwd = self.reg_entries["entry_pass"].get()
        confirm = self.reg_entries["entry_confirm"].get()

        if not all([name, email, phone, username, pwd, confirm]):
            messagebox.showwarning("Validation Error", "All fields are mandatory.")
            return

        if pwd != confirm:
            messagebox.showerror("Error", "Passwords do not match.")
            return

        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("SELECT user_id FROM users WHERE username = ? OR email = ?;", (username, email))
            if cur.fetchone():
                messagebox.showerror("Error", "Username or email is already registered.")
                return

            cur.execute(
                """INSERT INTO users (full_name, email, phone_number, username, password_hash, account_status)
                   VALUES (?, ?, ?, ?, ?, 'Active');""",
                (name, email, phone, username, hash_password(pwd))
            )
            conn.commit()
            messagebox.showinfo("Success", "Account created successfully! Please login.")
            self.show_login()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            conn.close()

    # =========================================================================
    # 3. USER LOGIN PAGE
    # =========================================================================
    def show_login(self):
        self.clear_container()
        create_header(self.container, "ParkSlot", "Driver Portal — Login")

        main_frame = tk.Frame(self.container, bg=COLORS["bg_main"], pady=40)
        main_frame.pack(expand=True)

        card = tk.Frame(main_frame, bg=COLORS["bg_card"], bd=1, relief="solid", padx=35, pady=30)
        card.pack()

        tk.Label(card, text="Driver Sign In", font=FONTS["header"], bg=COLORS["bg_card"], fg=COLORS["text_dark"]).pack(pady=(0, 20))

        tk.Label(card, text="Username or Email", font=FONTS["body_bold"], bg=COLORS["bg_card"], fg=COLORS["text_dark"]).pack(anchor="w")
        self.login_user_entry = ttk.Entry(card, width=32)
        self.login_user_entry.pack(pady=(4, 12))
        self.login_user_entry.insert(0, "indrajith")

        tk.Label(card, text="Password", font=FONTS["body_bold"], bg=COLORS["bg_card"], fg=COLORS["text_dark"]).pack(anchor="w")
        self.login_pass_entry = ttk.Entry(card, width=32, show="*")
        self.login_pass_entry.pack(pady=(4, 20))
        self.login_pass_entry.insert(0, "User@123")

        tk.Button(card, text="Login", font=FONTS["body_bold"], bg=COLORS["primary"], fg="#FFFFFF",
                  width=26, pady=7, bd=0, cursor="hand2", command=self._do_login).pack()

        links_frame = tk.Frame(card, bg=COLORS["bg_card"])
        links_frame.pack(fill="x", pady=(15, 0))

        tk.Button(links_frame, text="Forgot Password?", font=FONTS["small"], bg=COLORS["bg_card"], fg=COLORS["text_muted"],
                  bd=0, cursor="hand2", command=self.show_forgot_password).pack(side="left")
        tk.Button(links_frame, text="Create Account", font=FONTS["small"], bg=COLORS["bg_card"], fg=COLORS["primary"],
                  bd=0, cursor="hand2", command=self.show_register).pack(side="right")

        tk.Button(card, text="← Back to Welcome", font=FONTS["small"], bg=COLORS["bg_card"], fg=COLORS["secondary"],
                  bd=0, cursor="hand2", command=self.show_welcome).pack(pady=(15, 0))

    def _do_login(self):
        user_input = self.login_user_entry.get().strip()
        pwd = self.login_pass_entry.get()

        if not user_input or not pwd:
            messagebox.showwarning("Validation Error", "Please provide both username and password.")
            return

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """SELECT user_id, full_name, email, phone_number, username, password_hash, account_status
               FROM users WHERE username = ? OR email = ?;""",
            (user_input, user_input)
        )
        row = cur.fetchone()
        conn.close()

        if not row:
            messagebox.showerror("Error", "Invalid username or password.")
            return

        if row["account_status"] != "Active":
            messagebox.showerror("Account Suspended", f"Your account status is: {row['account_status']}. Contact Admin.")
            return

        if not verify_password(pwd, row["password_hash"]):
            messagebox.showerror("Error", "Invalid username or password.")
            return

        self.current_user = dict(row)
        self.show_dashboard()

    # =========================================================================
    # 4. FORGOT / RESET PASSWORD PAGE
    # =========================================================================
    def show_forgot_password(self):
        self.clear_container()
        create_header(self.container, "ParkSlot", "Reset Driver Account Password")

        main_frame = tk.Frame(self.container, bg=COLORS["bg_main"], pady=30)
        main_frame.pack(expand=True)

        card = tk.Frame(main_frame, bg=COLORS["bg_card"], bd=1, relief="solid", padx=30, pady=25)
        card.pack()

        tk.Label(card, text="Reset Password", font=FONTS["header"], bg=COLORS["bg_card"], fg=COLORS["text_dark"]).pack(pady=(0, 15))

        tk.Label(card, text="Registered Email Address:", font=FONTS["body_bold"], bg=COLORS["bg_card"], fg=COLORS["text_dark"]).pack(anchor="w")
        email_entry = ttk.Entry(card, width=30)
        email_entry.pack(pady=(4, 10))

        tk.Label(card, text="New Password:", font=FONTS["body_bold"], bg=COLORS["bg_card"], fg=COLORS["text_dark"]).pack(anchor="w")
        new_pass = ttk.Entry(card, width=30, show="*")
        new_pass.pack(pady=(4, 10))

        tk.Label(card, text="Confirm New Password:", font=FONTS["body_bold"], bg=COLORS["bg_card"], fg=COLORS["text_dark"]).pack(anchor="w")
        confirm_pass = ttk.Entry(card, width=30, show="*")
        confirm_pass.pack(pady=(4, 20))

        def _reset():
            em = email_entry.get().strip()
            np = new_pass.get()
            cp = confirm_pass.get()
            if not em or not np or not cp:
                messagebox.showwarning("Validation Error", "All fields are required.")
                return
            if np != cp:
                messagebox.showerror("Error", "Passwords do not match.")
                return

            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT user_id FROM users WHERE email = ?;", (em,))
            if not cur.fetchone():
                conn.close()
                messagebox.showerror("Error", "Email not found.")
                return

            cur.execute("UPDATE users SET password_hash = ? WHERE email = ?;", (hash_password(np), em))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Password updated successfully! Please login.")
            self.show_login()

        btn_row = tk.Frame(card, bg=COLORS["bg_card"])
        btn_row.pack()
        tk.Button(btn_row, text="Reset Password", font=FONTS["body_bold"], bg=COLORS["primary"], fg="#FFFFFF",
                  pady=5, padx=15, bd=0, cursor="hand2", command=_reset).pack(side="left", padx=5)
        tk.Button(btn_row, text="Back to Login", font=FONTS["body"], bg=COLORS["secondary"], fg="#FFFFFF",
                  pady=5, padx=10, bd=0, cursor="hand2", command=self.show_login).pack(side="left", padx=5)

    # =========================================================================
    # 5. USER DASHBOARD
    # =========================================================================
    def show_dashboard(self):
        self.clear_container()
        create_header(self.container, "ParkSlot", f"Welcome, {self.current_user['full_name']}!", on_logout=self.logout)

        main_area = tk.Frame(self.container, bg=COLORS["bg_main"], padx=25, pady=20)
        main_area.pack(fill="both", expand=True)

        # Load live counts
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM vehicles WHERE user_id = ?;", (self.current_user["user_id"],))
        reg_vehicles = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM parking_slots WHERE current_status = 'Available';")
        avail_slots = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM bookings WHERE user_id = ?;", (self.current_user["user_id"],))
        total_bookings = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM bookings WHERE user_id = ? AND booking_status IN ('Confirmed', 'Checked-in');",
                    (self.current_user["user_id"],))
        active_bookings = cur.fetchone()[0]
        conn.close()

        # Metrics Row
        stats_frame = tk.Frame(main_area, bg=COLORS["bg_main"])
        stats_frame.pack(fill="x", pady=(0, 20))

        def make_stat_card(parent, title, val, color):
            box = tk.Frame(parent, bg=COLORS["bg_card"], bd=1, relief="solid", padx=15, pady=12)
            box.pack(side="left", fill="both", expand=True, padx=6)
            tk.Label(box, text=title, font=FONTS["small"], bg=COLORS["bg_card"], fg=COLORS["text_muted"]).pack()
            tk.Label(box, text=str(val), font=FONTS["stat_num"], bg=COLORS["bg_card"], fg=color).pack()

        make_stat_card(stats_frame, "My Registered Vehicles", reg_vehicles, COLORS["primary"])
        make_stat_card(stats_frame, "System Available Slots", avail_slots, COLORS["success"])
        make_stat_card(stats_frame, "My Total Bookings", total_bookings, COLORS["secondary"])
        make_stat_card(stats_frame, "My Active Bookings", active_bookings, COLORS["warning"])

        # Navigation Hub Menu
        menu_frame = tk.Frame(main_area, bg=COLORS["bg_card"], bd=1, relief="solid", padx=30, pady=25)
        menu_frame.pack(fill="both", expand=True)

        tk.Label(menu_frame, text="Quick Actions & Services", font=FONTS["subtitle"],
                 bg=COLORS["bg_card"], fg=COLORS["text_dark"]).pack(anchor="w", pady=(0, 15))

        btn_grid = tk.Frame(menu_frame, bg=COLORS["bg_card"])
        btn_grid.pack(expand=True)

        actions = [
            ("👤 My Profile", "View and update personal details", self.show_profile),
            ("🚗 My Vehicles", "Add, view and manage vehicles", self.show_vehicles),
            ("🅿️ Find Parking", "View available slots and book", self.show_available_slots),
            ("📅 My Bookings", "View reservations and cancellations", self.show_my_bookings),
            ("💳 Fee Details", "View parking rates and charges", self.show_fee_details)
        ]

        for i, (btn_text, desc, cmd) in enumerate(actions):
            item_box = tk.Frame(btn_grid, bg="#F8FAFC", bd=1, relief="solid", padx=15, pady=12, width=280, height=85)
            item_box.grid(row=i // 3, column=i % 3, padx=10, pady=10)
            item_box.pack_propagate(False)

            tk.Button(item_box, text=btn_text, font=FONTS["body_bold"], bg=COLORS["primary"], fg="#FFFFFF",
                      bd=0, cursor="hand2", command=cmd).pack(fill="x")
            tk.Label(item_box, text=desc, font=FONTS["small"], bg="#F8FAFC", fg=COLORS["text_muted"]).pack(pady=(4, 0))

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to log out?"):
            self.current_user = None
            self.show_welcome()

    # =========================================================================
    # 6. MY PROFILE PAGE
    # =========================================================================
    def show_profile(self):
        self.clear_container()
        create_header(self.container, "My Profile", f"Account ID: #{self.current_user['user_id']}", on_logout=self.logout)

        main_area = tk.Frame(self.container, bg=COLORS["bg_main"], padx=20, pady=20)
        main_area.pack(expand=True)

        card = tk.Frame(main_area, bg=COLORS["bg_card"], bd=1, relief="solid", padx=30, pady=25)
        card.pack()

        tk.Label(card, text="Profile Information", font=FONTS["subtitle"], bg=COLORS["bg_card"], fg=COLORS["text_dark"]).grid(row=0, column=0, columnspan=2, pady=(0, 15))

        tk.Label(card, text="Full Name:", font=FONTS["body_bold"], bg=COLORS["bg_card"]).grid(row=1, column=0, sticky="w", pady=6)
        entry_name = ttk.Entry(card, width=28)
        entry_name.grid(row=1, column=1, pady=6)
        entry_name.insert(0, self.current_user["full_name"])

        tk.Label(card, text="Email Address:", font=FONTS["body_bold"], bg=COLORS["bg_card"]).grid(row=2, column=0, sticky="w", pady=6)
        entry_email = ttk.Entry(card, width=28)
        entry_email.grid(row=2, column=1, pady=6)
        entry_email.insert(0, self.current_user["email"])

        tk.Label(card, text="Phone Number:", font=FONTS["body_bold"], bg=COLORS["bg_card"]).grid(row=3, column=0, sticky="w", pady=6)
        entry_phone = ttk.Entry(card, width=28)
        entry_phone.grid(row=3, column=1, pady=6)
        entry_phone.insert(0, self.current_user["phone_number"])

        tk.Label(card, text="Username:", font=FONTS["body_bold"], bg=COLORS["bg_card"]).grid(row=4, column=0, sticky="w", pady=6)
        entry_user = ttk.Entry(card, width=28)
        entry_user.grid(row=4, column=1, pady=6)
        entry_user.insert(0, self.current_user["username"])
        entry_user.config(state="disabled")

        def _update():
            fn = entry_name.get().strip()
            em = entry_email.get().strip()
            ph = entry_phone.get().strip()
            if not fn or not em or not ph:
                messagebox.showwarning("Validation Error", "All fields are required.")
                return
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("UPDATE users SET full_name = ?, email = ?, phone_number = ? WHERE user_id = ?;",
                        (fn, em, ph, self.current_user["user_id"]))
            conn.commit()
            conn.close()
            self.current_user["full_name"] = fn
            self.current_user["email"] = em
            self.current_user["phone_number"] = ph
            messagebox.showinfo("Success", "Profile updated successfully!")

        btn_row = tk.Frame(card, bg=COLORS["bg_card"])
        btn_row.grid(row=5, column=0, columnspan=2, pady=(20, 0))

        tk.Button(btn_row, text="Update Profile", font=FONTS["body_bold"], bg=COLORS["primary"], fg="#FFFFFF",
                  pady=5, padx=12, bd=0, cursor="hand2", command=_update).pack(side="left", padx=5)
        tk.Button(btn_row, text="Back to Dashboard", font=FONTS["body"], bg=COLORS["secondary"], fg="#FFFFFF",
                  pady=5, padx=12, bd=0, cursor="hand2", command=self.show_dashboard).pack(side="left", padx=5)

    # =========================================================================
    # 7. VEHICLE MANAGEMENT PAGE
    # =========================================================================
    def show_vehicles(self):
        self.clear_container()
        create_header(self.container, "My Vehicles", "Register and manage your vehicles", on_logout=self.logout)

        main_area = tk.Frame(self.container, bg=COLORS["bg_main"], padx=20, pady=15)
        main_area.pack(fill="both", expand=True)

        # Form Card (Left / Top)
        form_card = tk.Frame(main_area, bg=COLORS["bg_card"], bd=1, relief="solid", padx=15, pady=12)
        form_card.pack(fill="x", pady=(0, 15))

        tk.Label(form_card, text="Add / Register New Vehicle", font=FONTS["subtitle"],
                 bg=COLORS["bg_card"], fg=COLORS["text_dark"]).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 8))

        tk.Label(form_card, text="Registration No:*", font=FONTS["body_bold"], bg=COLORS["bg_card"]).grid(row=1, column=0, sticky="w", padx=5, pady=4)
        entry_reg = ttk.Entry(form_card, width=16)
        entry_reg.grid(row=1, column=1, sticky="w", padx=5, pady=4)

        tk.Label(form_card, text="Vehicle Type:*", font=FONTS["body_bold"], bg=COLORS["bg_card"]).grid(row=1, column=2, sticky="w", padx=5, pady=4)
        combo_type = ttk.Combobox(form_card, values=["Car", "Bike", "Other"], state="readonly", width=14)
        combo_type.current(0)
        combo_type.grid(row=1, column=3, sticky="w", padx=5, pady=4)

        tk.Label(form_card, text="Model:", font=FONTS["body_bold"], bg=COLORS["bg_card"]).grid(row=2, column=0, sticky="w", padx=5, pady=4)
        entry_model = ttk.Entry(form_card, width=16)
        entry_model.grid(row=2, column=1, sticky="w", padx=5, pady=4)

        tk.Label(form_card, text="Colour:", font=FONTS["body_bold"], bg=COLORS["bg_card"]).grid(row=2, column=2, sticky="w", padx=5, pady=4)
        entry_colour = ttk.Entry(form_card, width=16)
        entry_colour.grid(row=2, column=3, sticky="w", padx=5, pady=4)

        btn_box = tk.Frame(form_card, bg=COLORS["bg_card"])
        btn_box.grid(row=3, column=0, columnspan=4, sticky="e", pady=(10, 0))

        # Table Card (Bottom)
        table_card = tk.Frame(main_area, bg=COLORS["bg_card"], bd=1, relief="solid", padx=15, pady=12)
        table_card.pack(fill="both", expand=True)

        tk.Label(table_card, text="Your Registered Vehicles", font=FONTS["subtitle"],
                 bg=COLORS["bg_card"], fg=COLORS["text_dark"]).pack(anchor="w", pady=(0, 8))

        columns = ("id", "reg", "type", "model", "colour", "created")
        tree = ttk.Treeview(table_card, columns=columns, show="headings", height=8)
        tree.heading("id", text="ID")
        tree.heading("reg", text="Registration Number")
        tree.heading("type", text="Type")
        tree.heading("model", text="Model")
        tree.heading("colour", text="Colour")
        tree.heading("created", text="Added On")

        tree.column("id", width=50, anchor="center")
        tree.column("reg", width=150, anchor="center")
        tree.column("type", width=100, anchor="center")
        tree.column("model", width=140)
        tree.column("colour", width=100)
        tree.column("created", width=150, anchor="center")
        tree.pack(fill="both", expand=True)

        def load_vehicles():
            for row in tree.get_children():
                tree.delete(row)
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT vehicle_id, registration_number, vehicle_type, model, colour, created_at FROM vehicles WHERE user_id = ? ORDER BY vehicle_id DESC;", (self.current_user["user_id"],))
            for r in cur.fetchall():
                tree.insert("", "end", values=tuple(r))
            conn.close()

        def add_vehicle():
            reg = entry_reg.get().strip().upper()
            vtype = combo_type.get()
            model = entry_model.get().strip()
            colour = entry_colour.get().strip()
            if not reg:
                messagebox.showwarning("Error", "Registration number is required.")
                return
            conn = get_db_connection()
            cur = conn.cursor()
            try:
                cur.execute(
                    "INSERT INTO vehicles (user_id, registration_number, vehicle_type, model, colour) VALUES (?, ?, ?, ?, ?);",
                    (self.current_user["user_id"], reg, vtype, model, colour)
                )
                conn.commit()
                messagebox.showinfo("Success", f"Vehicle {reg} registered successfully!")
                entry_reg.delete(0, tk.END)
                entry_model.delete(0, tk.END)
                entry_colour.delete(0, tk.END)
                load_vehicles()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add vehicle: {e}")
            finally:
                conn.close()

        def delete_vehicle():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Select Vehicle", "Please select a vehicle to delete.")
                return
            v_id = tree.item(sel[0])["values"][0]
            v_reg = tree.item(sel[0])["values"][1]
            if messagebox.askyesno("Confirm Delete", f"Delete vehicle {v_reg}?"):
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute("DELETE FROM vehicles WHERE vehicle_id = ? AND user_id = ?;", (v_id, self.current_user["user_id"]))
                conn.commit()
                conn.close()
                load_vehicles()

        tk.Button(btn_box, text="+ Add Vehicle", font=FONTS["body_bold"], bg=COLORS["primary"], fg="#FFFFFF",
                  bd=0, padx=12, pady=4, cursor="hand2", command=add_vehicle).pack(side="left", padx=5)
        tk.Button(table_card, text="🗑 Delete Selected Vehicle", font=FONTS["body"], bg=COLORS["danger"], fg="#FFFFFF",
                  bd=0, padx=10, pady=4, cursor="hand2", command=delete_vehicle).pack(anchor="w", pady=(10, 0))
        tk.Button(table_card, text="← Back to Dashboard", font=FONTS["body"], bg=COLORS["secondary"], fg="#FFFFFF",
                  bd=0, padx=10, pady=4, cursor="hand2", command=self.show_dashboard).pack(anchor="e", pady=(5, 0))

        load_vehicles()

    # =========================================================================
    # 8. AVAILABLE PARKING SLOTS PAGE
    # =========================================================================
    def show_available_slots(self):
        self.clear_container()
        create_header(self.container, "Find Parking", "Browse available facilities & reserve a slot", on_logout=self.logout)

        main_area = tk.Frame(self.container, bg=COLORS["bg_main"], padx=20, pady=15)
        main_area.pack(fill="both", expand=True)

        # Filters Bar
        filter_card = tk.Frame(main_area, bg=COLORS["bg_card"], bd=1, relief="solid", padx=15, pady=10)
        filter_card.pack(fill="x", pady=(0, 12))

        tk.Label(filter_card, text="Location:", font=FONTS["body_bold"], bg=COLORS["bg_card"]).pack(side="left", padx=(0, 4))
        entry_loc = ttk.Entry(filter_card, width=16)
        entry_loc.pack(side="left", padx=4)

        tk.Label(filter_card, text="Vehicle Type:", font=FONTS["body_bold"], bg=COLORS["bg_card"]).pack(side="left", padx=(10, 4))
        combo_vtype = ttk.Combobox(filter_card, values=["All", "Car", "Bike"], state="readonly", width=10)
        combo_vtype.current(0)
        combo_vtype.pack(side="left", padx=4)

        # Table
        table_card = tk.Frame(main_area, bg=COLORS["bg_card"], bd=1, relief="solid", padx=15, pady=12)
        table_card.pack(fill="both", expand=True)

        cols = ("slot_id", "facility", "location", "slot_num", "v_type", "floor", "rate", "status")
        tree = ttk.Treeview(table_card, columns=cols, show="headings", height=10)
        tree.heading("slot_id", text="Slot ID")
        tree.heading("facility", text="Facility Name")
        tree.heading("location", text="Location")
        tree.heading("slot_num", text="Slot Number")
        tree.heading("v_type", text="Type")
        tree.heading("floor", text="Floor / Zone")
        tree.heading("rate", text="Rate/Hr (₹)")
        tree.heading("status", text="Status")

        tree.column("slot_id", width=55, anchor="center")
        tree.column("facility", width=180)
        tree.column("location", width=160)
        tree.column("slot_num", width=90, anchor="center")
        tree.column("v_type", width=75, anchor="center")
        tree.column("floor", width=100)
        tree.column("rate", width=90, anchor="center")
        tree.column("status", width=95, anchor="center")
        tree.pack(fill="both", expand=True)

        def search_slots():
            for r in tree.get_children():
                tree.delete(r)

            loc_filter = entry_loc.get().strip()
            vt_filter = combo_vtype.get()

            query = """
                SELECT ps.slot_id, pf.name, pf.location, ps.slot_number, ps.vehicle_type, ps.floor_zone,
                       COALESCE(pr.rate_per_hour, 30.0) AS rate, ps.current_status, pf.facility_id
                FROM parking_slots ps
                JOIN parking_facilities pf ON ps.facility_id = pf.facility_id
                LEFT JOIN parking_rates pr ON (ps.facility_id = pr.facility_id AND ps.vehicle_type = pr.vehicle_type)
                WHERE ps.current_status != 'Inactive'
            """
            params = []
            if loc_filter:
                query += " AND (pf.location LIKE ? OR pf.name LIKE ?)"
                params.extend([f"%{loc_filter}%", f"%{loc_filter}%"])
            if vt_filter != "All":
                query += " AND ps.vehicle_type = ?"
                params.append(vt_filter)

            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(query, params)
            for row in cur.fetchall():
                tree.insert("", "end", values=tuple(row[:8]))
            conn.close()

        tk.Button(filter_card, text="🔍 Search", font=FONTS["body_bold"], bg=COLORS["primary"], fg="#FFFFFF",
                  bd=0, padx=12, pady=3, cursor="hand2", command=search_slots).pack(side="left", padx=10)
        tk.Button(filter_card, text="Reset", font=FONTS["body"], bg=COLORS["secondary"], fg="#FFFFFF",
                  bd=0, padx=8, pady=3, cursor="hand2", command=lambda: [entry_loc.delete(0, tk.END), combo_vtype.current(0), search_slots()]).pack(side="left")

        btn_row = tk.Frame(table_card, bg=COLORS["bg_card"])
        btn_row.pack(fill="x", pady=(12, 0))

        def book_selected():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Select Slot", "Please select a parking slot to book.")
                return
            item = tree.item(sel[0])["values"]
            slot_status = item[7]
            if slot_status != "Available":
                messagebox.showerror("Unavailable", f"Slot {item[3]} is currently {slot_status}. Please select an Available slot.")
                return
            slot_data = {
                "slot_id": item[0],
                "facility_name": item[1],
                "location": item[2],
                "slot_number": item[3],
                "vehicle_type": item[4],
                "rate": item[6]
            }
            self.show_booking(slot_data)

        tk.Button(btn_row, text="🅿️ Book Selected Slot Now", font=FONTS["body_bold"], bg=COLORS["success"], fg="#FFFFFF",
                  bd=0, padx=14, pady=6, cursor="hand2", command=book_selected).pack(side="left")
        tk.Button(btn_row, text="← Back to Dashboard", font=FONTS["body"], bg=COLORS["secondary"], fg="#FFFFFF",
                  bd=0, padx=12, pady=6, cursor="hand2", command=self.show_dashboard).pack(side="right")

        search_slots()

    # =========================================================================
    # 9. SLOT BOOKING PAGE
    # =========================================================================
    def show_booking(self, slot_data):
        self.clear_container()
        create_header(self.container, "Slot Booking", f"Reserving Slot {slot_data['slot_number']} ({slot_data['facility_name']})", on_logout=self.logout)

        main_area = tk.Frame(self.container, bg=COLORS["bg_main"], padx=20, pady=20)
        main_area.pack(expand=True)

        card = tk.Frame(main_area, bg=COLORS["bg_card"], bd=1, relief="solid", padx=30, pady=20)
        card.pack()

        tk.Label(card, text="Confirm Reservation Details", font=FONTS["subtitle"], bg=COLORS["bg_card"], fg=COLORS["text_dark"]).grid(row=0, column=0, columnspan=2, pady=(0, 15))

        # Facility details
        info_txt = f"Facility: {slot_data['facility_name']} ({slot_data['location']})\nSlot: {slot_data['slot_number']} | Type: {slot_data['vehicle_type']} | Rate: ₹{slot_data['rate']}/hr"
        tk.Label(card, text=info_txt, font=FONTS["body"], bg="#EFF6FF", fg=COLORS["primary"], relief="groove", padx=10, pady=8).grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 15))

        # User's vehicles dropdown
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT vehicle_id, registration_number, vehicle_type FROM vehicles WHERE user_id = ?;", (self.current_user["user_id"],))
        vehicles = cur.fetchall()
        conn.close()

        if not vehicles:
            messagebox.showwarning("No Vehicles Registered", "You need to add a vehicle before booking a slot.")
            self.show_vehicles()
            return

        veh_options = [f"{v['registration_number']} ({v['vehicle_type']})" for v in vehicles]
        veh_map = {f"{v['registration_number']} ({v['vehicle_type']})": v["vehicle_id"] for v in vehicles}

        tk.Label(card, text="Select Registered Vehicle:*", font=FONTS["body_bold"], bg=COLORS["bg_card"]).grid(row=2, column=0, sticky="w", pady=6)
        combo_v = ttk.Combobox(card, values=veh_options, state="readonly", width=25)
        combo_v.current(0)
        combo_v.grid(row=2, column=1, pady=6)

        today_str = datetime.date.today().strftime("%Y-%m-%d")
        tk.Label(card, text="Booking Date (YYYY-MM-DD):*", font=FONTS["body_bold"], bg=COLORS["bg_card"]).grid(row=3, column=0, sticky="w", pady=6)
        entry_date = ttk.Entry(card, width=27)
        entry_date.insert(0, today_str)
        entry_date.grid(row=3, column=1, pady=6)

        now_time = datetime.datetime.now().strftime("%H:%M")
        later_time = (datetime.datetime.now() + datetime.timedelta(hours=2)).strftime("%H:%M")

        tk.Label(card, text="Start Time (HH:MM):*", font=FONTS["body_bold"], bg=COLORS["bg_card"]).grid(row=4, column=0, sticky="w", pady=6)
        entry_start = ttk.Entry(card, width=27)
        entry_start.insert(0, now_time)
        entry_start.grid(row=4, column=1, pady=6)

        tk.Label(card, text="End Time (HH:MM):*", font=FONTS["body_bold"], bg=COLORS["bg_card"]).grid(row=5, column=0, sticky="w", pady=6)
        entry_end = ttk.Entry(card, width=27)
        entry_end.insert(0, later_time)
        entry_end.grid(row=5, column=1, pady=6)

        lbl_est = tk.Label(card, text="Estimated Fee: ₹60.00 (2 Hours)", font=FONTS["body_bold"], bg=COLORS["bg_card"], fg=COLORS["success"])
        lbl_est.grid(row=6, column=0, columnspan=2, pady=10)

        def calc_est(*args):
            try:
                t1 = datetime.datetime.strptime(entry_start.get().strip(), "%H:%M")
                t2 = datetime.datetime.strptime(entry_end.get().strip(), "%H:%M")
                diff = (t2 - t1).total_seconds() / 3600.0
                if diff > 0:
                    hrs = max(1, round(diff, 1))
                    total = hrs * float(slot_data["rate"])
                    lbl_est.config(text=f"Estimated Duration: {hrs:.1f} hrs | Estimated Fee: ₹{total:.2f}")
                else:
                    lbl_est.config(text="End time must be after start time", fg=COLORS["danger"])
            except Exception:
                pass

        entry_start.bind("<KeyRelease>", calc_est)
        entry_end.bind("<KeyRelease>", calc_est)

        def confirm_booking():
            sel_veh = combo_v.get()
            b_date = entry_date.get().strip()
            s_time = entry_start.get().strip()
            e_time = entry_end.get().strip()

            if not b_date or not s_time or not e_time:
                messagebox.showerror("Error", "All date/time fields are required.")
                return

            try:
                t1 = datetime.datetime.strptime(s_time, "%H:%M")
                t2 = datetime.datetime.strptime(e_time, "%H:%M")
                if t2 <= t1:
                    messagebox.showerror("Error", "End time must be strictly after start time.")
                    return
            except ValueError:
                messagebox.showerror("Error", "Invalid time format. Please use HH:MM.")
                return

            veh_id = veh_map[sel_veh]

            conn = get_db_connection()
            cur = conn.cursor()
            try:
                # Check slot collision
                cur.execute(
                    """SELECT COUNT(*) FROM bookings
                       WHERE slot_id = ? AND booking_date = ?
                         AND booking_status IN ('Confirmed', 'Checked-in')
                         AND NOT (end_time <= ? OR start_time >= ?);""",
                    (slot_data["slot_id"], b_date, s_time, e_time)
                )
                if cur.fetchone()[0] > 0:
                    messagebox.showerror("Conflict", "This slot already has a conflicting reservation for this time range.")
                    return

                # Insert booking
                cur.execute(
                    """INSERT INTO bookings (user_id, vehicle_id, slot_id, booking_date, start_time, end_time, booking_status)
                       VALUES (?, ?, ?, ?, ?, ?, 'Confirmed');""",
                    (self.current_user["user_id"], veh_id, slot_data["slot_id"], b_date, s_time, e_time)
                )
                booking_id = cur.lastrowid

                # Update slot to Reserved
                cur.execute("UPDATE parking_slots SET current_status = 'Reserved' WHERE slot_id = ?;", (slot_data["slot_id"],))
                conn.commit()

                messagebox.showinfo(
                    "Booking Confirmed!",
                    f"Reservation Successful!\n\nBooking ID: #{booking_id}\nFacility: {slot_data['facility_name']}\nSlot: {slot_data['slot_number']}\nDate: {b_date} ({s_time} - {e_time})"
                )
                self.show_my_bookings()
            except Exception as e:
                messagebox.showerror("Database Error", str(e))
            finally:
                conn.close()

        btn_row = tk.Frame(card, bg=COLORS["bg_card"])
        btn_row.grid(row=7, column=0, columnspan=2, pady=(15, 0))

        tk.Button(btn_row, text="✓ Confirm Reservation", font=FONTS["body_bold"], bg=COLORS["success"], fg="#FFFFFF",
                  pady=6, padx=15, bd=0, cursor="hand2", command=confirm_booking).pack(side="left", padx=5)
        tk.Button(btn_row, text="Cancel", font=FONTS["body"], bg=COLORS["secondary"], fg="#FFFFFF",
                  pady=6, padx=12, bd=0, cursor="hand2", command=self.show_available_slots).pack(side="left", padx=5)

    # =========================================================================
    # 10. MY BOOKINGS PAGE
    # =========================================================================
    def show_my_bookings(self):
        self.clear_container()
        create_header(self.container, "My Bookings", "View active, upcoming and completed reservations", on_logout=self.logout)

        main_area = tk.Frame(self.container, bg=COLORS["bg_main"], padx=20, pady=15)
        main_area.pack(fill="both", expand=True)

        card = tk.Frame(main_area, bg=COLORS["bg_card"], bd=1, relief="solid", padx=15, pady=12)
        card.pack(fill="both", expand=True)

        cols = ("b_id", "date", "window", "facility", "slot", "vehicle", "status")
        tree = ttk.Treeview(card, columns=cols, show="headings", height=10)
        tree.heading("b_id", text="Booking ID")
        tree.heading("date", text="Date")
        tree.heading("window", text="Time Window")
        tree.heading("facility", text="Facility")
        tree.heading("slot", text="Slot")
        tree.heading("vehicle", text="Vehicle")
        tree.heading("status", text="Status")

        tree.column("b_id", width=80, anchor="center")
        tree.column("date", width=100, anchor="center")
        tree.column("window", width=120, anchor="center")
        tree.column("facility", width=180)
        tree.column("slot", width=80, anchor="center")
        tree.column("vehicle", width=120, anchor="center")
        tree.column("status", width=100, anchor="center")
        tree.pack(fill="both", expand=True)

        def load_bookings():
            for r in tree.get_children():
                tree.delete(r)
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                """SELECT b.booking_id, b.booking_date, (b.start_time || ' - ' || b.end_time) AS win,
                          pf.name, ps.slot_number, v.registration_number, b.booking_status, b.slot_id
                   FROM bookings b
                   JOIN parking_slots ps ON b.slot_id = ps.slot_id
                   JOIN parking_facilities pf ON ps.facility_id = pf.facility_id
                   JOIN vehicles v ON b.vehicle_id = v.vehicle_id
                   WHERE b.user_id = ?
                   ORDER BY b.booking_id DESC;""",
                (self.current_user["user_id"],)
            )
            for row in cur.fetchall():
                tree.insert("", "end", values=tuple(row[:7]))
            conn.close()

        def cancel_booking():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Select Booking", "Please select a booking to cancel.")
                return
            b_id = tree.item(sel[0])["values"][0]
            status = tree.item(sel[0])["values"][6]

            if status != "Confirmed":
                messagebox.showerror("Error", f"Cannot cancel booking with status '{status}'. Only Confirmed bookings can be cancelled.")
                return

            if messagebox.askyesno("Cancel Booking", f"Are you sure you want to cancel booking #{b_id}?"):
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute("SELECT slot_id FROM bookings WHERE booking_id = ?;", (b_id,))
                slot_id = cur.fetchone()[0]

                cur.execute("UPDATE bookings SET booking_status = 'Cancelled', cancellation_reason = 'Cancelled by Driver' WHERE booking_id = ?;", (b_id,))
                cur.execute("UPDATE parking_slots SET current_status = 'Available' WHERE slot_id = ?;", (slot_id,))
                conn.commit()
                conn.close()
                messagebox.showinfo("Cancelled", f"Booking #{b_id} cancelled.")
                load_bookings()

        btn_row = tk.Frame(card, bg=COLORS["bg_card"])
        btn_row.pack(fill="x", pady=(12, 0))

        tk.Button(btn_row, text="❌ Cancel Selected Booking", font=FONTS["body"], bg=COLORS["danger"], fg="#FFFFFF",
                  bd=0, padx=12, pady=5, cursor="hand2", command=cancel_booking).pack(side="left")
        tk.Button(btn_row, text="💳 View Fee Breakdown", font=FONTS["body_bold"], bg=COLORS["primary"], fg="#FFFFFF",
                  bd=0, padx=12, pady=5, cursor="hand2", command=lambda: self.show_fee_details(tree.item(tree.selection()[0])["values"][0] if tree.selection() else None)).pack(side="left", padx=10)
        tk.Button(btn_row, text="← Back to Dashboard", font=FONTS["body"], bg=COLORS["secondary"], fg="#FFFFFF",
                  bd=0, padx=12, pady=5, cursor="hand2", command=self.show_dashboard).pack(side="right")

        load_bookings()

    # =========================================================================
    # 11. FEE DETAILS PAGE
    # =========================================================================
    def show_fee_details(self, selected_booking_id=None):
        self.clear_container()
        create_header(self.container, "Fee Details", "Parking duration and tariff calculation breakdown", on_logout=self.logout)

        main_area = tk.Frame(self.container, bg=COLORS["bg_main"], padx=20, pady=20)
        main_area.pack(expand=True)

        card = tk.Frame(main_area, bg=COLORS["bg_card"], bd=1, relief="solid", padx=30, pady=20)
        card.pack()

        tk.Label(card, text="Select Booking for Billing Breakdown:", font=FONTS["body_bold"], bg=COLORS["bg_card"]).pack(anchor="w", pady=(0, 5))

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """SELECT b.booking_id, b.booking_date, ps.slot_number, pf.name, pr.rate_per_hour
               FROM bookings b
               JOIN parking_slots ps ON b.slot_id = ps.slot_id
               JOIN parking_facilities pf ON ps.facility_id = pf.facility_id
               LEFT JOIN parking_rates pr ON (ps.facility_id = pr.facility_id AND ps.vehicle_type = pr.vehicle_type)
               WHERE b.user_id = ? ORDER BY b.booking_id DESC;""",
            (self.current_user["user_id"],)
        )
        all_b = cur.fetchall()
        conn.close()

        b_map = {f"#{b['booking_id']} - {b['booking_date']} ({b['name']} / {b['slot_number']})": b["booking_id"] for b in all_b}
        combo_b = ttk.Combobox(card, values=list(b_map.keys()), width=45, state="readonly")
        combo_b.pack(pady=(0, 15))

        # Receipt Panel
        receipt = tk.Frame(card, bg="#F8FAFC", bd=1, relief="groove", padx=20, pady=15)
        receipt.pack(fill="x", pady=10)

        lbl_desc = tk.Label(receipt, text="Select a booking above to view fee computation.", font=FONTS["body"], bg="#F8FAFC", justify="left")
        lbl_desc.pack(anchor="w")

        def on_select(*args):
            sel_key = combo_b.get()
            if not sel_key:
                return
            b_id = b_map[sel_key]
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                """SELECT b.booking_id, b.start_time, b.end_time, ps.slot_number, pf.name,
                          COALESCE(pr.rate_per_hour, 30.0) as rate, fp.amount, fp.payment_status
                   FROM bookings b
                   JOIN parking_slots ps ON b.slot_id = ps.slot_id
                   JOIN parking_facilities pf ON ps.facility_id = pf.facility_id
                   LEFT JOIN parking_rates pr ON (ps.facility_id = pr.facility_id AND ps.vehicle_type = pr.vehicle_type)
                   LEFT JOIN parking_sessions s ON b.booking_id = s.booking_id
                   LEFT JOIN fees_payments fp ON s.session_id = fp.session_id
                   WHERE b.booking_id = ?;""",
                (b_id,)
            )
            item = cur.fetchone()
            conn.close()

            if item:
                rate = float(item["rate"])
                # calculate estimated or actual duration
                try:
                    t1 = datetime.datetime.strptime(item["start_time"], "%H:%M")
                    t2 = datetime.datetime.strptime(item["end_time"], "%H:%M")
                    hrs = max(1.0, round((t2 - t1).total_seconds() / 3600.0, 1))
                except Exception:
                    hrs = 2.0
                est_fee = hrs * rate
                status = item["payment_status"] if item["payment_status"] else "Pending (Calculated upon check-out)"
                actual_fee = f"₹{item['amount']:.2f}" if item["amount"] is not None else f"₹{est_fee:.2f} (Estimated)"

                txt = (
                    f"Booking Ref: #{item['booking_id']}\n"
                    f"Facility: {item['name']} | Slot: {item['slot_number']}\n"
                    f"Scheduled Time: {item['start_time']} - {item['end_time']}\n"
                    f"Duration: {hrs:.1f} Hours\n"
                    f"Rate per Hour: ₹{rate:.2f}\n"
                    f"-----------------------------------------\n"
                    f"Total Parking Fee: {actual_fee}\n"
                    f"Payment Status: {status}\n"
                    f"(Calculation: Duration × Rate per Hour)"
                )
                lbl_desc.config(text=txt)

        combo_b.bind("<<ComboboxSelected>>", on_select)

        if b_map:
            combo_b.current(0)
            on_select()

        tk.Button(card, text="← Back to Dashboard", font=FONTS["body"], bg=COLORS["secondary"], fg="#FFFFFF",
                  pady=5, padx=12, bd=0, cursor="hand2", command=self.show_dashboard).pack(pady=(15, 0))

if __name__ == "__main__":
    app = UserApp()
    app.mainloop()

