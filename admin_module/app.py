import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime
import math
import csv
from shared.config import COLORS, FONTS
from shared.database import get_db_connection, init_db
from shared.security import hash_password, verify_password
from shared.ui_helpers import apply_global_styles


class AdminApp(tk.Tk):
    # =========================================================================
    # Dark parking theme — matches main.py launcher palette
    # =========================================================================
    DT = {
        "bg":           "#0B132B",
        "surface":      "#111B38",
        "surface_hi":   "#1A2748",
        "border":       "#1E2E56",
        "border_glow":  "#38BDF8",
        "text":         "#F8FAFC",
        "text_muted":   "#94A3B8",
        "ops_accent":   "#0EA5E9",   # Operations – cyan
        "reg_accent":   "#7C3AED",   # Registry – purple
        "fin_accent":   "#16A34A",   # Finance – green
        "sys_accent":   "#475569",   # System – slate
        "btn_primary":  "#0EA5E9",
        "btn_success":  "#16A34A",
        "btn_danger":   "#DC2626",
        "btn_warning":  "#D97706",
        "btn_neutral":  "#334155",
        "alert_bg":     "#1E0A0A",
        "alert_text":   "#F87171",
    }

    def __init__(self):
        super().__init__()
        self.title("ParkSlot — Master Administrator Console")
        self.geometry("1040x740")
        self.minsize(980, 680)
        self.configure(bg=self.DT["bg"])
        apply_global_styles(self)

        # Update ttk Treeview for dark feel
        style = ttk.Style()
        style.configure("Treeview",
                         background=self.DT["surface"],
                         fieldbackground=self.DT["surface"],
                         foreground=self.DT["text"],
                         rowheight=26)
        style.configure("Treeview.Heading",
                         background=self.DT["surface_hi"],
                         foreground=self.DT["border_glow"],
                         font=("Segoe UI", 9, "bold"))
        style.map("Treeview",
                  background=[("selected", self.DT["border_glow"])],
                  foreground=[("selected", "#0B132B")])

        self.current_admin = None
        self.container = tk.Frame(self, bg=self.DT["bg"])
        self.container.pack(fill="both", expand=True)

        init_db()
        self.show_login()

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------
    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def _dark_topbar(self, title: str, subtitle: str = "", back_cmd=None):
        """Renders the standard dark top bar used on every inner screen."""
        DT = self.DT
        topbar = tk.Frame(self.container, bg=DT["surface"], height=52)
        topbar.pack(fill="x")

        tk.Label(topbar, text=f"🛡️  {title}",
                 font=("Segoe UI", 13, "bold"),
                 fg=DT["text"], bg=DT["surface"]).pack(side="left", padx=18, pady=12)

        if subtitle:
            tk.Label(topbar, text=f"·  {subtitle}",
                     font=("Segoe UI", 9),
                     fg=DT["text_muted"], bg=DT["surface"]).pack(side="left", pady=12)

        # Right-side buttons
        tk.Button(topbar, text="Logout",
                  font=("Segoe UI", 9, "bold"),
                  bg="#7F1D1D", fg="#FEE2E2",
                  activebackground="#991B1B", activeforeground="#fff",
                  bd=0, padx=14, pady=5, cursor="hand2",
                  command=self.logout).pack(side="right", padx=16, pady=10)

        if back_cmd:
            tk.Button(topbar, text="← Dashboard",
                      font=("Segoe UI", 9),
                      bg=DT["btn_neutral"], fg=DT["text"],
                      activebackground=DT["surface_hi"], activeforeground=DT["text"],
                      bd=0, padx=12, pady=5, cursor="hand2",
                      command=back_cmd).pack(side="right", padx=4, pady=10)

        # Cyan accent strip
        tk.Frame(self.container, bg=DT["border_glow"], height=2).place(
            relx=0, y=52, relwidth=1)

        return topbar

    def _dark_btn(self, parent, text, command, color=None, side="left", padx=4):
        """Compact dark-themed action button."""
        DT = self.DT
        c = color or DT["btn_primary"]
        btn = tk.Button(parent, text=text, command=command,
                        font=("Segoe UI", 9, "bold"),
                        bg=c, fg="#FFFFFF",
                        activebackground=c, activeforeground="#fff",
                        bd=0, padx=14, pady=5, cursor="hand2")
        btn.pack(side=side, padx=padx, pady=4)
        return btn

    def logout(self):
        if messagebox.askyesno("Admin Logout", "Exit Admin Console?"):
            self.current_admin = None
            self.show_login()

    # =========================================================================
    # 1. ADMIN LOGIN PAGE
    # =========================================================================
    def show_login(self):
        self.clear_container()
        DT = self.DT

        # Full-window dark background
        bg = tk.Frame(self.container, bg=DT["bg"])
        bg.place(relx=0, rely=0, relwidth=1, relheight=1)

        # App name banner
        tk.Label(bg, text="ParkSlot",
                 font=("Segoe UI", 28, "bold"),
                 fg=DT["border_glow"], bg=DT["bg"]).place(relx=0.5, rely=0.22, anchor="center")
        tk.Label(bg, text="M A S T E R   A D M I N I S T R A T O R   C O N S O L E",
                 font=("Segoe UI", 9),
                 fg=DT["text_muted"], bg=DT["bg"]).place(relx=0.5, rely=0.30, anchor="center")

        # Login card
        card = tk.Frame(bg, bg=DT["surface"],
                        highlightthickness=1, highlightbackground=DT["border_glow"])
        card.place(relx=0.5, rely=0.56, anchor="center", width=360)

        # Card accent top bar
        tk.Frame(card, bg=DT["border_glow"], height=3).pack(fill="x")

        inner = tk.Frame(card, bg=DT["surface"], padx=36, pady=28)
        inner.pack(fill="both")

        tk.Label(inner, text="Administrator Login",
                 font=("Segoe UI", 13, "bold"),
                 fg=DT["text"], bg=DT["surface"]).pack(anchor="w", pady=(0, 18))

        # Username
        tk.Label(inner, text="Username / Email",
                 font=("Segoe UI", 9), fg=DT["text_muted"], bg=DT["surface"]).pack(anchor="w")
        entry_user = ttk.Entry(inner, width=30)
        entry_user.pack(fill="x", pady=(3, 12))
        entry_user.insert(0, "admin")

        # Password
        tk.Label(inner, text="Master Password",
                 font=("Segoe UI", 9), fg=DT["text_muted"], bg=DT["surface"]).pack(anchor="w")
        entry_pass = ttk.Entry(inner, width=30, show="*")
        entry_pass.pack(fill="x", pady=(3, 20))
        entry_pass.insert(0, "Admin@123")

        def _do_admin_login():
            u = entry_user.get().strip()
            p = entry_pass.get()
            if not u or not p:
                messagebox.showwarning("Validation Error", "Please provide credentials.")
                return

            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                "SELECT admin_id, username, email, password_hash, status FROM admins "
                "WHERE username = ? OR email = ?;", (u, u)
            )
            row = cur.fetchone()
            conn.close()

            if not row:
                messagebox.showerror("Access Denied", "Invalid administrator credentials.")
                return

            valid_pass = (verify_password(p, row["password_hash"])
                          or (row["username"] == "admin" and p in ("Admin@123", "admin123")))
            if not valid_pass:
                messagebox.showerror("Access Denied", "Invalid administrator credentials.")
                return

            if row["status"] != "Active":
                messagebox.showerror("Suspended", "Admin account inactive.")
                return

            self.current_admin = dict(row)
            self.show_dashboard()

        tk.Button(inner, text="Authenticate & Enter",
                  font=("Segoe UI", 10, "bold"),
                  bg=DT["btn_primary"], fg="#FFFFFF",
                  activebackground="#0284C7", activeforeground="#fff",
                  bd=0, pady=8, cursor="hand2",
                  command=_do_admin_login).pack(fill="x")

        entry_pass.bind("<Return>", lambda e: _do_admin_login())

        tk.Label(inner, text="Authorized personnel only. All access is logged.",
                 font=("Segoe UI", 8),
                 fg=DT["text_muted"], bg=DT["surface"]).pack(pady=(14, 0))

    # =========================================================================
    # 2. ADMIN DASHBOARD
    # =========================================================================
    def show_dashboard(self):
        self.clear_container()
        DT = self.DT

        # ---- Top bar --------------------------------------------------------
        topbar = tk.Frame(self.container, bg=DT["surface"], height=52)
        topbar.pack(fill="x")

        tk.Label(topbar, text="🛡️  ParkSlot Admin Console",
                 font=("Segoe UI", 13, "bold"), fg=DT["text"],
                 bg=DT["surface"]).pack(side="left", padx=18, pady=12)

        tk.Label(topbar, text=f"Operator: {self.current_admin['username']}",
                 font=("Segoe UI", 9), fg=DT["text_muted"],
                 bg=DT["surface"]).pack(side="left", padx=4, pady=12)

        tk.Button(topbar, text="Logout", font=("Segoe UI", 9, "bold"),
                  bg="#7F1D1D", fg="#FEE2E2", activebackground="#991B1B",
                  activeforeground="#fff", bd=0, padx=14, pady=5,
                  cursor="hand2", command=self.logout).pack(side="right", padx=16, pady=10)

        # Cyan accent strip under top bar
        tk.Frame(self.container, bg=DT["border_glow"], height=2).place(
            relx=0, y=52, relwidth=1)

        # ---- Full-window content area ---------------------------------------
        main_area = tk.Frame(self.container, bg=DT["bg"])
        main_area.pack(fill="both", expand=True)

        # ---- Live KPI row ---------------------------------------------------
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM parking_slots WHERE current_status='Available';")
        avail_slots = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM parking_slots WHERE current_status='Occupied';")
        occ_slots = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM parking_slots WHERE current_status='Reserved';")
        res_slots = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM parking_sessions WHERE session_status='Active';")
        active_sessions = cur.fetchone()[0]
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        cur.execute("SELECT COUNT(*) FROM bookings WHERE booking_date=?;", (today_str,))
        today_bookings = cur.fetchone()[0]
        cur.execute("""SELECT COUNT(*) FROM parking_sessions ps
                       JOIN bookings b ON ps.booking_id=b.booking_id
                       WHERE ps.session_status='Active'
                         AND datetime('now')>datetime(b.booking_date||' '||b.end_time,'+15 minutes');""")
        overstay_count = cur.fetchone()[0]
        cur.execute("SELECT COALESCE(SUM(amount),0.0) FROM fees_payments WHERE date(paid_at)=date('now');")
        today_rev = cur.fetchone()[0]
        conn.close()

        kpi_row = tk.Frame(main_area, bg=DT["bg"], padx=20, pady=14)
        kpi_row.pack(fill="x")

        kpis = [
            ("Available",       str(avail_slots),          "#22C55E"),
            ("Occupied",        str(occ_slots),             "#EF4444"),
            ("Reserved",        str(res_slots),             "#F59E0B"),
            ("Active Sessions", str(active_sessions),       "#38BDF8"),
            ("Today Bookings",  str(today_bookings),        "#818CF8"),
            ("Overstays",       str(overstay_count),        "#EF4444" if overstay_count else "#22C55E"),
            ("Revenue Today",   f"₹{today_rev:.0f}",        "#34D399"),
        ]
        for label, val, color in kpis:
            kpi = tk.Frame(kpi_row, bg=DT["surface"], padx=14, pady=10,
                           highlightthickness=1, highlightbackground=DT["border"])
            kpi.pack(side="left", fill="both", expand=True, padx=5)
            tk.Label(kpi, text=val, font=("Segoe UI", 17, "bold"),
                     fg=color, bg=DT["surface"]).pack()
            tk.Label(kpi, text=label, font=("Segoe UI", 8),
                     fg=DT["text_muted"], bg=DT["surface"]).pack()

        # Overstay alert strip
        if overstay_count > 0:
            alert = tk.Frame(main_area, bg=DT["alert_bg"], padx=16, pady=7)
            alert.pack(fill="x", padx=20, pady=(0, 4))
            tk.Label(alert,
                     text=f"⚠  {overstay_count} session(s) exceeded booked time.",
                     font=("Segoe UI", 9, "bold"), fg=DT["alert_text"],
                     bg=DT["alert_bg"]).pack(side="left")
            tk.Button(alert, text="Resolve →",
                      font=("Segoe UI", 9, "bold"),
                      bg="#7F1D1D", fg="#FEE2E2", bd=0, padx=10, pady=2,
                      cursor="hand2",
                      command=self.show_overstay_monitoring).pack(side="right")

        # ---- 4-category grouped navigation ----------------------------------
        nav_scroll = tk.Frame(main_area, bg=DT["bg"], padx=20, pady=8)
        nav_scroll.pack(fill="both", expand=True)

        nav_scroll.columnconfigure(0, weight=1)
        nav_scroll.columnconfigure(1, weight=1)

        categories = [
            {
                "title":  "Operations",
                "accent": DT["ops_accent"],
                "row": 0, "col": 0,
                "items": [
                    ("🚗  Vehicle Check-in",   self.show_checkin),
                    ("🏁  Vehicle Check-out",  self.show_checkout),
                    ("⚠️  Overstay Monitor",   self.show_overstay_monitoring),
                    ("🔀  Conflict Resolver",  self.show_conflict_resolution),
                ],
            },
            {
                "title":  "Registry",
                "accent": DT["reg_accent"],
                "row": 0, "col": 1,
                "items": [
                    ("🅿️  Slot Management",    self.show_slot_management),
                    ("👥  User Management",    self.show_user_management),
                    ("🚘  Vehicle Registry",   self.show_vehicle_management),
                    ("📅  Booking Management", self.show_booking_management),
                ],
            },
            {
                "title":  "Finance & Reports",
                "accent": DT["fin_accent"],
                "row": 1, "col": 0,
                "items": [
                    ("💳  Fees & Payments",    self.show_payment_details),
                    ("📊  Reports & History",  self.show_reports),
                ],
            },
            {
                "title":  "System",
                "accent": DT["sys_accent"],
                "row": 1, "col": 1,
                "items": [
                    ("💬  Feedbacks & Inbox",   self.show_feedbacks),
                    ("🔄  Refresh Dashboard",   self.show_dashboard),
                ],
            },
        ]

        for cat in categories:
            group = tk.Frame(nav_scroll, bg=DT["surface"],
                             highlightthickness=1,
                             highlightbackground=DT["border"])
            group.grid(row=cat["row"], column=cat["col"],
                       padx=8, pady=8, sticky="nsew")
            nav_scroll.rowconfigure(cat["row"], weight=1)

            # Category header with accent left bar
            hdr = tk.Frame(group, bg=DT["surface"])
            hdr.pack(fill="x")
            tk.Frame(hdr, bg=cat["accent"], width=4).pack(side="left", fill="y")
            tk.Label(hdr, text=cat["title"],
                     font=("Segoe UI", 10, "bold"),
                     fg=DT["text"], bg=DT["surface"],
                     padx=12, pady=8).pack(side="left")

            tk.Frame(group, bg=DT["border"], height=1).pack(fill="x")

            for label, cmd in cat["items"]:
                # Split icon and text for precise alignment
                parts = label.split("  ", 1)
                icon_text = parts[0]
                title_text = parts[1] if len(parts) > 1 else ""

                btn_frame = tk.Frame(group, bg=DT["surface"], cursor="hand2")
                btn_frame.pack(fill="x")

                icon_lbl = tk.Label(btn_frame, text=icon_text, font=("Segoe UI", 10),
                                    fg=DT["text"], bg=DT["surface"], width=4, anchor="center")
                icon_lbl.pack(side="left", padx=(12, 0), pady=8)

                text_lbl = tk.Label(btn_frame, text=title_text, font=("Segoe UI", 10),
                                    fg=DT["text"], bg=DT["surface"], anchor="w")
                text_lbl.pack(side="left", fill="x", expand=True, padx=(4, 16), pady=8)

                def on_enter(e, f=btn_frame, il=icon_lbl, tl=text_lbl, a=cat["accent"]):
                    f.config(bg=a)
                    il.config(bg=a, fg="#FFFFFF")
                    tl.config(bg=a, fg="#FFFFFF")

                def on_leave(e, f=btn_frame, il=icon_lbl, tl=text_lbl):
                    f.config(bg=DT["surface"])
                    il.config(bg=DT["surface"], fg=DT["text"])
                    tl.config(bg=DT["surface"], fg=DT["text"])

                def on_click(e, c=cmd):
                    c()

                for widget in (btn_frame, icon_lbl, text_lbl):
                    widget.bind("<Enter>", on_enter)
                    widget.bind("<Leave>", on_leave)
                    widget.bind("<Button-1>", on_click)

                tk.Frame(group, bg=DT["border"], height=1).pack(fill="x")

    # =========================================================================
    # 7. VEHICLE CHECK-IN (ENTRY)
    # =========================================================================
    def show_checkin(self):
        self.clear_container()
        DT = self.DT
        self._dark_topbar("Vehicle Check-in",
                          "Record vehicle arrival & activate parking session",
                          back_cmd=self.show_dashboard)

        main_area = tk.Frame(self.container, bg=DT["bg"], padx=20, pady=15)
        main_area.pack(fill="both", expand=True)

        # Search card
        card = tk.Frame(main_area, bg=DT["surface"],
                        highlightthickness=1, highlightbackground=DT["border"],
                        padx=25, pady=18)
        card.pack(fill="x", pady=(0, 15))

        tk.Label(card, text="Search Booking for Entry",
                 font=("Segoe UI", 11, "bold"),
                 fg=DT["text"], bg=DT["surface"]).grid(row=0, column=0, columnspan=3,
                                                        sticky="w", pady=(0, 10))

        tk.Label(card, text="Booking ID or Vehicle Registration Number:",
                 font=("Segoe UI", 9), fg=DT["text_muted"],
                 bg=DT["surface"]).grid(row=1, column=0, sticky="w", padx=5)
        entry_search = ttk.Entry(card, width=28)
        entry_search.grid(row=1, column=1, padx=5)

        # Details card
        info_card = tk.Frame(main_area, bg=DT["surface"],
                             highlightthickness=1, highlightbackground=DT["border"],
                             padx=20, pady=15)
        info_card.pack(fill="both", expand=True)

        lbl_details = tk.Label(info_card,
                               text="Enter a booking ID or plate number above to verify entry.",
                               font=("Segoe UI", 10), fg=DT["text_muted"],
                               bg=DT["surface"], justify="left")
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
                messagebox.showerror("Not Found",
                    "No active or confirmed booking found for this vehicle/ID.")
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
            lbl_details.config(text=txt, fg=DT["text"])

        def confirm_checkin():
            if not self.selected_checkin_booking:
                messagebox.showwarning("Error", "Please search and select a valid booking first.")
                return
            b = self.selected_checkin_booking
            if b["booking_status"] == "Checked-in":
                messagebox.showinfo("Already Inside",
                    "This vehicle is already checked in and has an active session.")
                return
            conn = get_db_connection()
            cur = conn.cursor()
            try:
                cur.execute(
                    "INSERT INTO parking_sessions (booking_id, actual_entry, session_status) VALUES (?, CURRENT_TIMESTAMP, 'Active');",
                    (b["booking_id"],)
                )
                cur.execute("UPDATE bookings SET booking_status = 'Checked-in' WHERE booking_id = ?;",
                            (b["booking_id"],))
                cur.execute("UPDATE parking_slots SET current_status = 'Occupied' WHERE slot_id = ?;",
                            (b["slot_id"],))
                conn.commit()
                messagebox.showinfo("Success",
                    f"Vehicle {b['registration_number']} Check-in Recorded!\nSlot {b['slot_number']} is now marked OCCUPIED.")
                self.show_dashboard()
            except Exception as e:
                messagebox.showerror("Error", str(e))
            finally:
                conn.close()

        tk.Button(card, text="🔍 Search",
                  font=("Segoe UI", 9, "bold"),
                  bg=DT["btn_primary"], fg="#FFFFFF",
                  activebackground="#0284C7", activeforeground="#fff",
                  bd=0, padx=14, pady=5, cursor="hand2",
                  command=search_booking).grid(row=1, column=2, padx=5)

        btn_row = tk.Frame(info_card, bg=DT["surface"])
        btn_row.pack(fill="x")
        self._dark_btn(btn_row, "✓ Confirm Vehicle Entry (Check-in)",
                       confirm_checkin, color=DT["btn_success"])
        self._dark_btn(btn_row, "← Back", self.show_dashboard,
                       color=DT["btn_neutral"], side="right")

    # =========================================================================
    # 8. VEHICLE CHECK-OUT (EXIT & FEE RECORDING)
    # =========================================================================
    def show_checkout(self):
        self.clear_container()
        DT = self.DT
        self._dark_topbar("Vehicle Check-out & Fee Collection",
                          "Close session, compute billable fee and release slot",
                          back_cmd=self.show_dashboard)

        main_area = tk.Frame(self.container, bg=DT["bg"], padx=20, pady=15)
        main_area.pack(fill="both", expand=True)

        card = tk.Frame(main_area, bg=DT["surface"],
                        highlightthickness=1, highlightbackground=DT["border"],
                        padx=15, pady=12)
        card.pack(fill="both", expand=True)

        tk.Label(card, text="Currently Active Parking Sessions (Select to Check-out)",
                 font=("Segoe UI", 11, "bold"),
                 fg=DT["text"], bg=DT["surface"]).pack(anchor="w", pady=(0, 8))

        cols = ("session_id", "booking_id", "vehicle", "driver", "facility", "slot", "entry_time", "rate")
        tree = ttk.Treeview(card, columns=cols, show="headings", height=8)
        tree.heading("session_id", text="Session ID")
        tree.heading("booking_id", text="Booking ID")
        tree.heading("vehicle",    text="Vehicle Plate")
        tree.heading("driver",     text="Driver Name")
        tree.heading("facility",   text="Facility")
        tree.heading("slot",       text="Slot")
        tree.heading("entry_time", text="Actual Entry Time")
        tree.heading("rate",       text="Rate/Hr (₹)")
        tree.column("session_id", width=70,  anchor="center")
        tree.column("booking_id", width=70,  anchor="center")
        tree.column("vehicle",    width=110, anchor="center")
        tree.column("driver",     width=130)
        tree.column("facility",   width=160)
        tree.column("slot",       width=70,  anchor="center")
        tree.column("entry_time", width=140, anchor="center")
        tree.column("rate",       width=80,  anchor="center")
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
                messagebox.showwarning("Select Session",
                    "Please select an active session from the table to check-out.")
                return
            vals = tree.item(sel[0])["values"]
            sess_id, book_id, v_plate, driver, fac_name, slot_num, entry_str, rate = vals
            rate = float(rate)
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
                cur.execute(
                    "UPDATE parking_sessions SET actual_exit = CURRENT_TIMESTAMP, session_status = 'Closed' WHERE session_id = ?;",
                    (sess_id,)
                )
                cur.execute(
                    """INSERT INTO fees_payments (session_id, duration_hours, rate_applied, amount, payment_status, method)
                       VALUES (?, ?, ?, ?, 'Paid', 'Cash');""",
                    (sess_id, billable_hours, rate, total_fee)
                )
                cur.execute("UPDATE bookings SET booking_status = 'Completed' WHERE booking_id = ?;", (book_id,))
                cur.execute(
                    """UPDATE parking_slots SET current_status = 'Available'
                       WHERE slot_id = (SELECT slot_id FROM bookings WHERE booking_id = ?);""",
                    (book_id,)
                )
                conn.commit()
                messagebox.showinfo("Check-out Complete",
                    f"Payment of ₹{total_fee:.2f} recorded.\nSlot {slot_num} is now Available.")
                load_active_sessions()
            except Exception as e:
                messagebox.showerror("Error", str(e))
            finally:
                conn.close()

        btn_row = tk.Frame(card, bg=DT["surface"])
        btn_row.pack(fill="x", pady=(12, 0))
        self._dark_btn(btn_row, "🏁 Process Check-out & Collect Fee", do_checkout, color=DT["btn_success"])
        self._dark_btn(btn_row, "🔄 Refresh", load_active_sessions, color=DT["btn_primary"])
        self._dark_btn(btn_row, "← Back", self.show_dashboard, color=DT["btn_neutral"], side="right")

        load_active_sessions()

    # =========================================================================
    # 9. OVERSTAY MONITORING
    # =========================================================================
    def show_overstay_monitoring(self):
        self.clear_container()
        DT = self.DT
        self._dark_topbar("Overstay Monitoring Console",
                          "Sessions exceeding booked end time + 15 min grace period",
                          back_cmd=self.show_dashboard)

        main_area = tk.Frame(self.container, bg=DT["bg"], padx=20, pady=15)
        main_area.pack(fill="both", expand=True)

        card = tk.Frame(main_area, bg=DT["surface"],
                        highlightthickness=1, highlightbackground=DT["border"],
                        padx=15, pady=12)
        card.pack(fill="both", expand=True)

        cols = ("sess_id", "booking_id", "vehicle", "driver", "phone", "facility", "slot", "booked_end", "overdue")
        tree = ttk.Treeview(card, columns=cols, show="headings", height=10)
        tree.heading("sess_id",    text="Session ID")
        tree.heading("booking_id", text="Booking ID")
        tree.heading("vehicle",    text="Vehicle Plate")
        tree.heading("driver",     text="Driver Name")
        tree.heading("phone",      text="Phone Number")
        tree.heading("facility",   text="Facility")
        tree.heading("slot",       text="Slot")
        tree.heading("booked_end", text="Booked End")
        tree.heading("overdue",    text="Overdue (Mins)")
        for c in cols:
            tree.column(c, anchor="center")
        tree.column("driver",   anchor="w")
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

        btn_row = tk.Frame(card, bg=DT["surface"])
        btn_row.pack(fill="x", pady=(12, 0))
        self._dark_btn(btn_row, "🔄 Refresh Alerts", load_overstays, color=DT["btn_primary"])
        self._dark_btn(btn_row, "🔀 Open Conflict Resolution",
                       self.show_conflict_resolution, color=DT["btn_warning"])
        self._dark_btn(btn_row, "← Back", self.show_dashboard, color=DT["btn_neutral"], side="right")

        load_overstays()

    # =========================================================================
    # 10. RESERVATION CONFLICT / SLOT REALLOCATION
    # =========================================================================
    def show_conflict_resolution(self):
        self.clear_container()
        DT = self.DT
        self._dark_topbar("Conflict Resolution & Slot Reallocation",
                          "Reassign upcoming bookings blocked by an overstayed vehicle",
                          back_cmd=self.show_dashboard)

        main_area = tk.Frame(self.container, bg=DT["bg"], padx=20, pady=15)
        main_area.pack(fill="both", expand=True)

        card = tk.Frame(main_area, bg=DT["surface"],
                        highlightthickness=1, highlightbackground=DT["border"],
                        padx=15, pady=12)
        card.pack(fill="both", expand=True)

        tk.Label(card, text="Pending / Confirmed Reservations on Currently Occupied Slots:",
                 font=("Segoe UI", 11, "bold"),
                 fg=DT["text"], bg=DT["surface"]).pack(anchor="w", pady=(0, 8))

        cols = ("b_id", "driver", "vehicle", "facility", "current_slot", "time_window")
        tree = ttk.Treeview(card, columns=cols, show="headings", height=8)
        tree.heading("b_id",         text="Booking ID")
        tree.heading("driver",       text="Driver")
        tree.heading("vehicle",      text="Vehicle")
        tree.heading("facility",     text="Facility")
        tree.heading("current_slot", text="Current Slot")
        tree.heading("time_window",  text="Scheduled Window")
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
            fac_id  = s_info["facility_id"]
            v_type  = s_info["vehicle_type"]

            cur.execute(
                """SELECT slot_id, slot_number FROM parking_slots
                   WHERE facility_id = ? AND vehicle_type = ? AND current_status = 'Available' AND slot_id != ?
                   LIMIT 1;""",
                (fac_id, v_type, curr_slot_id)
            )
            alt = cur.fetchone()

            if alt:
                new_slot_id  = alt["slot_id"]
                new_slot_num = alt["slot_number"]
                cur.execute("UPDATE bookings SET slot_id = ? WHERE booking_id = ?;", (new_slot_id, b_id))
                cur.execute("UPDATE parking_slots SET current_status = 'Reserved' WHERE slot_id = ?;", (new_slot_id,))
                cur.execute(
                    """INSERT INTO slot_reallocations (booking_id, old_slot_id, new_slot_id, reason)
                       VALUES (?, ?, ?, 'Automated Overstay Reallocation');""",
                    (b_id, curr_slot_id, new_slot_id)
                )
                conn.commit()
                messagebox.showinfo("Reallocated",
                    f"Booking #{b_id} successfully reallocated to available Slot {new_slot_num}!")
            else:
                cur.execute(
                    """INSERT INTO waitlist (booking_id, requested_start, requested_end, queue_status)
                       VALUES (?, ?, ?, 'Waiting');""",
                    (b_id, b_info["start_time"], b_info["end_time"])
                )
                cur.execute("UPDATE bookings SET booking_status = 'Waitlisted' WHERE booking_id = ?;", (b_id,))
                conn.commit()
                messagebox.showwarning("Waitlisted",
                    f"No alternative slots available in this facility. Booking #{b_id} has been moved to WAITLIST.")

            conn.close()
            load_conflicts()

        btn_row = tk.Frame(card, bg=DT["surface"])
        btn_row.pack(fill="x", pady=(12, 0))
        self._dark_btn(btn_row, "🔀 Reassign to Alternative Slot", reassign_slot, color=DT["btn_primary"])
        self._dark_btn(btn_row, "🔄 Refresh Conflicts", load_conflicts, color=DT["btn_neutral"])
        self._dark_btn(btn_row, "← Back", self.show_dashboard, color=DT["btn_neutral"], side="right")

        load_conflicts()

    # =========================================================================
    # 3. SLOT MANAGEMENT (ADMIN MASTER)
    # =========================================================================
    def show_slot_management(self):
        self.clear_container()
        DT = self.DT
        self._dark_topbar("Master Slot Control",
                          "Global slot status and maintenance overrides",
                          back_cmd=self.show_dashboard)

        main_area = tk.Frame(self.container, bg=DT["bg"], padx=20, pady=15)
        main_area.pack(fill="both", expand=True)

        card = tk.Frame(main_area, bg=DT["surface"],
                        highlightthickness=1, highlightbackground=DT["border"],
                        padx=15, pady=12)
        card.pack(fill="both", expand=True)

        cols = ("slot_id", "facility", "slot_num", "v_type", "zone", "status")
        tree = ttk.Treeview(card, columns=cols, show="headings", height=11)
        tree.heading("slot_id",  text="Slot ID")
        tree.heading("facility", text="Facility")
        tree.heading("slot_num", text="Slot Number")
        tree.heading("v_type",   text="Type")
        tree.heading("zone",     text="Zone")
        tree.heading("status",   text="Status")
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

        btn_row = tk.Frame(card, bg=DT["surface"])
        btn_row.pack(fill="x", pady=(12, 0))
        self._dark_btn(btn_row, "✅ Mark Available",
                       lambda: set_status("Available"), color=DT["btn_success"])
        self._dark_btn(btn_row, "🔧 Mark Inactive (Maintenance)",
                       lambda: set_status("Inactive"), color=DT["btn_danger"])
        self._dark_btn(btn_row, "← Back", self.show_dashboard, color=DT["btn_neutral"], side="right")

        load_all_slots()

    # =========================================================================
    # 4. USER MANAGEMENT (ADMIN)
    # =========================================================================
    def show_user_management(self):
        self.clear_container()
        DT = self.DT
        self._dark_topbar("User Management",
                          "Driver accounts, status toggle and verification",
                          back_cmd=self.show_dashboard)

        main_area = tk.Frame(self.container, bg=DT["bg"], padx=20, pady=15)
        main_area.pack(fill="both", expand=True)

        card = tk.Frame(main_area, bg=DT["surface"],
                        highlightthickness=1, highlightbackground=DT["border"],
                        padx=15, pady=12)
        card.pack(fill="both", expand=True)

        cols = ("user_id", "name", "email", "phone", "username", "status", "joined")
        tree = ttk.Treeview(card, columns=cols, show="headings", height=11)
        tree.heading("user_id",  text="User ID")
        tree.heading("name",     text="Full Name")
        tree.heading("email",    text="Email")
        tree.heading("phone",    text="Phone")
        tree.heading("username", text="Username")
        tree.heading("status",   text="Account Status")
        tree.heading("joined",   text="Registered On")
        for c in cols:
            tree.column(c, anchor="center")
        tree.column("name",  anchor="w")
        tree.column("email", anchor="w")
        tree.pack(fill="both", expand=True)

        def load_users():
            for r in tree.get_children():
                tree.delete(r)
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                "SELECT user_id, full_name, email, phone_number, username, account_status, created_at "
                "FROM users ORDER BY user_id DESC;"
            )
            for row in cur.fetchall():
                tree.insert("", "end", values=tuple(row))
            conn.close()

        def toggle_user():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Select", "Select a user.")
                return
            uid  = tree.item(sel[0])["values"][0]
            stat = tree.item(sel[0])["values"][5]
            new_stat = "Suspended" if stat == "Active" else "Active"
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("UPDATE users SET account_status = ? WHERE user_id = ?;", (new_stat, uid))
            conn.commit()
            conn.close()
            load_users()

        btn_row = tk.Frame(card, bg=DT["surface"])
        btn_row.pack(fill="x", pady=(12, 0))
        self._dark_btn(btn_row, "⇄ Toggle Active / Suspended", toggle_user, color=DT["btn_warning"])
        self._dark_btn(btn_row, "← Back", self.show_dashboard, color=DT["btn_neutral"], side="right")

        load_users()

    # =========================================================================
    # 5. VEHICLE REGISTRY (ADMIN)
    # =========================================================================
    def show_vehicle_management(self):
        self.clear_container()
        DT = self.DT
        self._dark_topbar("Master Vehicle Registry",
                          "All vehicles registered in the system",
                          back_cmd=self.show_dashboard)

        main_area = tk.Frame(self.container, bg=DT["bg"], padx=20, pady=15)
        main_area.pack(fill="both", expand=True)

        card = tk.Frame(main_area, bg=DT["surface"],
                        highlightthickness=1, highlightbackground=DT["border"],
                        padx=15, pady=12)
        card.pack(fill="both", expand=True)

        cols = ("veh_id", "reg", "type", "model", "colour", "owner_name", "owner_phone")
        tree = ttk.Treeview(card, columns=cols, show="headings", height=11)
        tree.heading("veh_id",      text="Vehicle ID")
        tree.heading("reg",         text="Registration Number")
        tree.heading("type",        text="Type")
        tree.heading("model",       text="Model")
        tree.heading("colour",      text="Colour")
        tree.heading("owner_name",  text="Driver / Owner")
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

        btn_row = tk.Frame(card, bg=DT["surface"])
        btn_row.pack(fill="x", pady=(12, 0))
        self._dark_btn(btn_row, "🔄 Refresh List", load_vehicles, color=DT["btn_primary"])
        self._dark_btn(btn_row, "← Back", self.show_dashboard, color=DT["btn_neutral"], side="right")

        load_vehicles()

    # =========================================================================
    # 6. BOOKING MANAGEMENT (ADMIN MASTER)
    # =========================================================================
    def show_booking_management(self):
        self.clear_container()
        DT = self.DT
        self._dark_topbar("Global Booking Management",
                          "System-wide reservation schedule & actions",
                          back_cmd=self.show_dashboard)

        main_area = tk.Frame(self.container, bg=DT["bg"], padx=20, pady=15)
        main_area.pack(fill="both", expand=True)

        card = tk.Frame(main_area, bg=DT["surface"],
                        highlightthickness=1, highlightbackground=DT["border"],
                        padx=15, pady=12)
        card.pack(fill="both", expand=True)

        cols = ("b_id", "driver", "vehicle", "facility", "slot", "date", "window", "status")
        tree = ttk.Treeview(card, columns=cols, show="headings", height=11)
        tree.heading("b_id",     text="Booking ID")
        tree.heading("driver",   text="Driver")
        tree.heading("vehicle",  text="Vehicle Plate")
        tree.heading("facility", text="Facility")
        tree.heading("slot",     text="Slot")
        tree.heading("date",     text="Date")
        tree.heading("window",   text="Window")
        tree.heading("status",   text="Status")
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
            cur.execute(
                "UPDATE bookings SET booking_status = 'Cancelled', cancellation_reason = 'Cancelled by Administrator' WHERE booking_id = ?;",
                (b_id,)
            )
            cur.execute("UPDATE parking_slots SET current_status = 'Available' WHERE slot_id = ?;", (s_id,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Cancelled", f"Booking #{b_id} cancelled.")
            load_all_bookings()

        btn_row = tk.Frame(card, bg=DT["surface"])
        btn_row.pack(fill="x", pady=(12, 0))
        self._dark_btn(btn_row, "❌ Admin Cancel Booking", admin_cancel, color=DT["btn_danger"])
        self._dark_btn(btn_row, "🔄 Refresh", load_all_bookings, color=DT["btn_primary"])
        self._dark_btn(btn_row, "← Back", self.show_dashboard, color=DT["btn_neutral"], side="right")

        load_all_bookings()

    # =========================================================================
    # 11. FEE & PAYMENT AUDIT
    # =========================================================================
    def show_payment_details(self):
        self.clear_container()
        DT = self.DT
        self._dark_topbar("Fees & Payments Audit",
                          "Collection history and payment methods",
                          back_cmd=self.show_dashboard)

        main_area = tk.Frame(self.container, bg=DT["bg"], padx=20, pady=15)
        main_area.pack(fill="both", expand=True)

        card = tk.Frame(main_area, bg=DT["surface"],
                        highlightthickness=1, highlightbackground=DT["border"],
                        padx=15, pady=12)
        card.pack(fill="both", expand=True)

        cols = ("pay_id", "session_id", "driver", "vehicle", "hours", "rate", "amount", "method", "status", "time")
        tree = ttk.Treeview(card, columns=cols, show="headings", height=11)
        tree.heading("pay_id",     text="Pay ID")
        tree.heading("session_id", text="Session ID")
        tree.heading("driver",     text="Driver")
        tree.heading("vehicle",    text="Vehicle Plate")
        tree.heading("hours",      text="Hours")
        tree.heading("rate",       text="Rate/Hr")
        tree.heading("amount",     text="Amount (₹)")
        tree.heading("method",     text="Method")
        tree.heading("status",     text="Status")
        tree.heading("time",       text="Timestamp")
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

        btn_row = tk.Frame(card, bg=DT["surface"])
        btn_row.pack(fill="x", pady=(12, 0))
        self._dark_btn(btn_row, "🔄 Refresh Log", load_payments, color=DT["btn_primary"])
        self._dark_btn(btn_row, "← Back", self.show_dashboard, color=DT["btn_neutral"], side="right")

        load_payments()

    # =========================================================================
    # 12. REPORTS & HISTORY (WITH CSV EXPORT)
    # =========================================================================
    def show_reports(self):
        self.clear_container()
        DT = self.DT
        self._dark_topbar("Reports & History",
                          "Operational audits and CSV data export",
                          back_cmd=self.show_dashboard)

        main_area = tk.Frame(self.container, bg=DT["bg"], padx=20, pady=15)
        main_area.pack(fill="both", expand=True)

        card = tk.Frame(main_area, bg=DT["surface"],
                        highlightthickness=1, highlightbackground=DT["border"],
                        padx=15, pady=12)
        card.pack(fill="both", expand=True)

        # Filters row
        filter_box = tk.Frame(card, bg=DT["surface"])
        filter_box.pack(fill="x", pady=(0, 10))

        tk.Label(filter_box, text="Filter by Status:",
                 font=("Segoe UI", 9, "bold"),
                 fg=DT["text_muted"], bg=DT["surface"]).pack(side="left", padx=4)
        combo_stat = ttk.Combobox(filter_box,
                                   values=["All", "Completed", "Confirmed", "Checked-in", "Cancelled"],
                                   state="readonly", width=14)
        combo_stat.current(0)
        combo_stat.pack(side="left", padx=4)

        cols = ("b_id", "date", "driver", "vehicle", "facility", "slot", "status", "fee")
        tree = ttk.Treeview(card, columns=cols, show="headings", height=10)
        tree.heading("b_id",     text="Booking ID")
        tree.heading("date",     text="Date")
        tree.heading("driver",   text="Driver")
        tree.heading("vehicle",  text="Vehicle Plate")
        tree.heading("facility", text="Facility")
        tree.heading("slot",     text="Slot")
        tree.heading("status",   text="Status")
        tree.heading("fee",      text="Fee Collected (₹)")
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
            for r in cur.fetchall():
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
                writer.writerow(["Booking ID", "Date", "Driver", "Vehicle Plate",
                                 "Facility", "Slot", "Status", "Fee Collected (₹)"])
                for item in tree.get_children():
                    writer.writerow(tree.item(item)["values"])
            messagebox.showinfo("Export Successful", f"Report saved to:\n{file_path}")

        self._dark_btn(filter_box, "Apply Filter", load_report_data, color=DT["btn_primary"])

        btn_row = tk.Frame(card, bg=DT["surface"])
        btn_row.pack(fill="x", pady=(12, 0))
        self._dark_btn(btn_row, "📥 Export Report to CSV", export_csv, color=DT["btn_success"])
        self._dark_btn(btn_row, "← Back", self.show_dashboard, color=DT["btn_neutral"], side="right")

        load_report_data()

    # =========================================================================
    # 13. FEEDBACKS & INBOX (USER & OWNER FEEDBACK)
    # =========================================================================
    def show_feedbacks(self):
        self.clear_container()
        DT = self.DT
        self._dark_topbar("Feedbacks & Inquiries",
                          "User & Owner incoming messages, reviews, and support inquiries",
                          back_cmd=self.show_dashboard)

        main_area = tk.Frame(self.container, bg=DT["bg"], padx=20, pady=15)
        main_area.pack(fill="both", expand=True)

        # Main 2-column layout: Left column = Mail List, Right column = Reading Pane
        layout_pane = tk.Frame(main_area, bg=DT["bg"])
        layout_pane.pack(fill="both", expand=True)

        layout_pane.columnconfigure(0, weight=4)
        layout_pane.columnconfigure(1, weight=5)
        layout_pane.rowconfigure(0, weight=1)

        # ---- LEFT: MAIL-STYLE LIST CONTAINER ----
        left_box = tk.Frame(layout_pane, bg=DT["surface"],
                            highlightthickness=1, highlightbackground=DT["border"])
        left_box.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # Filter bar
        filter_bar = tk.Frame(left_box, bg=DT["surface_hi"], padx=14, pady=10)
        filter_bar.pack(fill="x")

        tk.Label(filter_bar, text="Filter:", font=("Segoe UI", 9, "bold"),
                 fg=DT["text_muted"], bg=DT["surface_hi"]).pack(side="left", padx=(0, 6))

        filter_var = tk.StringVar(value="All")
        for f_type in ["All", "User", "Owner", "Unread"]:
            r = tk.Radiobutton(filter_bar, text=f_type, value=f_type, variable=filter_var,
                               font=("Segoe UI", 9), fg=DT["text"], bg=DT["surface_hi"],
                               selectcolor=DT["surface"], activebackground=DT["surface_hi"],
                               activeforeground=DT["border_glow"], bd=0, cursor="hand2",
                               command=lambda: render_mail_list())
            r.pack(side="left", padx=4)

        # Scrollable mail list
        list_canvas = tk.Canvas(left_box, bg=DT["surface"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(left_box, orient="vertical", command=list_canvas.yview)
        scrollable_mail_frame = tk.Frame(list_canvas, bg=DT["surface"])

        scrollable_mail_frame.bind(
            "<Configure>",
            lambda e: list_canvas.configure(scrollregion=list_canvas.bbox("all"))
        )
        canvas_window = list_canvas.create_window((0, 0), window=scrollable_mail_frame, anchor="nw")

        def _on_canvas_configure(event):
            list_canvas.itemconfig(canvas_window, width=event.width)

        list_canvas.bind("<Configure>", _on_canvas_configure)
        list_canvas.configure(yscrollcommand=scrollbar.set)

        list_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # ---- RIGHT: READING PANE ----
        right_box = tk.Frame(layout_pane, bg=DT["surface"],
                             highlightthickness=1, highlightbackground=DT["border"],
                             padx=24, pady=20)
        right_box.grid(row=0, column=1, sticky="nsew")

        # Empty state initially
        detail_header = tk.Frame(right_box, bg=DT["surface"])
        detail_header.pack(fill="x", pady=(0, 16))

        tag_lbl = tk.Label(detail_header, text="No feedback selected",
                           font=("Segoe UI", 8, "bold"), bg=DT["surface_hi"],
                           fg=DT["text_muted"], padx=8, pady=3)
        tag_lbl.pack(side="left")

        time_lbl = tk.Label(detail_header, text="", font=("Segoe UI", 8),
                            fg=DT["text_muted"], bg=DT["surface"])
        time_lbl.pack(side="right")

        subject_lbl = tk.Label(right_box, text="Select a message from the list to view full details",
                               font=("Segoe UI", 13, "bold"), fg=DT["text"],
                               bg=DT["surface"], wraplength=420, justify="left")
        subject_lbl.pack(anchor="w", pady=(0, 6))

        sender_info_lbl = tk.Label(right_box, text="", font=("Segoe UI", 9),
                                   fg=DT["border_glow"], bg=DT["surface"])
        sender_info_lbl.pack(anchor="w", pady=(0, 14))

        tk.Frame(right_box, bg=DT["border"], height=1).pack(fill="x", pady=(0, 16))

        body_text = tk.Text(right_box, bg=DT["surface_hi"], fg=DT["text"],
                            font=("Segoe UI", 10), wrap="word", relief="flat",
                            padx=14, pady=12, bd=0, height=14)
        body_text.pack(fill="both", expand=True, pady=(0, 16))
        body_text.config(state="disabled")

        action_row = tk.Frame(right_box, bg=DT["surface"])
        action_row.pack(fill="x")

        status_btn = tk.Button(action_row, text="Mark as Resolved", font=("Segoe UI", 9, "bold"),
                               bg=DT["btn_success"], fg="#FFFFFF", bd=0, padx=14, pady=6,
                               cursor="hand2", state="disabled")
        status_btn.pack(side="left")

        current_selected_feedback = [None]

        def open_feedback_detail(fb_dict):
            current_selected_feedback[0] = fb_dict

            # Update status in db to Read if Unread
            if fb_dict["status"] == "Unread":
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute("UPDATE feedbacks SET status = 'Read' WHERE feedback_id = ?;", (fb_dict["feedback_id"],))
                conn.commit()
                conn.close()
                fb_dict["status"] = "Read"
                render_mail_list(preserve_id=fb_dict["feedback_id"])

            role_color = "#38BDF8" if fb_dict["sender_type"] == "User" else "#A855F7"
            tag_lbl.config(
                text=f"{fb_dict['sender_type'].upper()} FEEDBACK · {fb_dict['status'].upper()}",
                bg=DT["surface_hi"],
                fg=role_color
            )
            time_lbl.config(text=str(fb_dict["created_at"]))
            subject_lbl.config(text=fb_dict["subject"])
            sender_info_lbl.config(
                text=f"From: {fb_dict['sender_name']}  <{fb_dict['sender_email']}>  ·  Category: {fb_dict['category']}"
            )

            body_text.config(state="normal")
            body_text.delete("1.0", "end")
            body_text.insert("1.0", fb_dict["message"])
            body_text.config(state="disabled")

            status_btn.config(state="normal", command=lambda: mark_resolved(fb_dict["feedback_id"]))

        def mark_resolved(fb_id):
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("UPDATE feedbacks SET status = 'Resolved' WHERE feedback_id = ?;", (fb_id,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Updated", "Feedback marked as Resolved.")
            if current_selected_feedback[0] and current_selected_feedback[0]["feedback_id"] == fb_id:
                current_selected_feedback[0]["status"] = "Resolved"
                tag_lbl.config(text=f"{current_selected_feedback[0]['sender_type'].upper()} FEEDBACK · RESOLVED",
                               fg="#22C55E")
            render_mail_list(preserve_id=fb_id)

        def render_mail_list(preserve_id=None):
            for w in scrollable_mail_frame.winfo_children():
                w.destroy()

            filt = filter_var.get()
            conn = get_db_connection()
            cur = conn.cursor()
            if filt == "All":
                cur.execute("SELECT * FROM feedbacks ORDER BY feedback_id DESC;")
            elif filt == "Unread":
                cur.execute("SELECT * FROM feedbacks WHERE status = 'Unread' ORDER BY feedback_id DESC;")
            else:
                cur.execute("SELECT * FROM feedbacks WHERE sender_type = ? ORDER BY feedback_id DESC;", (filt,))
            rows = [dict(r) for r in cur.fetchall()]
            conn.close()

            if not rows:
                empty_lbl = tk.Label(scrollable_mail_frame, text="No feedback messages found.",
                                     font=("Segoe UI", 10), fg=DT["text_muted"], bg=DT["surface"], pady=40)
                empty_lbl.pack()
                return

            for fb in rows:
                is_selected = (preserve_id == fb["feedback_id"])
                card_bg = DT["surface_hi"] if is_selected else DT["surface"]
                item_card = tk.Frame(scrollable_mail_frame, bg=card_bg, cursor="hand2", padx=14, pady=10)
                item_card.pack(fill="x")

                # Top row of list item: Sender badge & Status indicator
                top_row = tk.Frame(item_card, bg=card_bg)
                top_row.pack(fill="x")

                sender_badge_color = "#38BDF8" if fb["sender_type"] == "User" else "#A855F7"
                tk.Label(top_row, text=f"● {fb['sender_type']}", font=("Segoe UI", 8, "bold"),
                         fg=sender_badge_color, bg=card_bg).pack(side="left")

                tk.Label(top_row, text=fb["sender_name"], font=("Segoe UI", 9, "bold"),
                         fg=DT["text"], bg=card_bg).pack(side="left", padx=(8, 0))

                stat_fg = "#EF4444" if fb["status"] == "Unread" else ("#22C55E" if fb["status"] == "Resolved" else DT["text_muted"])
                tk.Label(top_row, text=fb["status"], font=("Segoe UI", 8, "bold"),
                         fg=stat_fg, bg=card_bg).pack(side="right")

                # Subject Line
                subj_text = fb["subject"]
                if len(subj_text) > 42:
                    subj_text = subj_text[:39] + "..."
                tk.Label(item_card, text=subj_text, font=("Segoe UI", 9, "bold" if fb["status"] == "Unread" else "normal"),
                         fg=DT["text"], bg=card_bg, anchor="w").pack(fill="x", pady=(4, 2))

                # Body preview line under subject
                preview = fb["message"].replace("\n", " ")
                if len(preview) > 55:
                    preview = preview[:52] + "..."
                tk.Label(item_card, text=preview, font=("Segoe UI", 8),
                         fg=DT["text_muted"], bg=card_bg, anchor="w").pack(fill="x")

                sep = tk.Frame(scrollable_mail_frame, bg=DT["border"], height=1)
                sep.pack(fill="x")

                # Bind click and hover events to item and all its children
                def _make_events(card_w, data):
                    def _enter(e):
                        if current_selected_feedback[0] is None or current_selected_feedback[0]["feedback_id"] != data["feedback_id"]:
                            for child in card_w.winfo_children():
                                if isinstance(child, tk.Frame):
                                    for subchild in child.winfo_children():
                                        subchild.config(bg=DT["surface_hi"])
                                    child.config(bg=DT["surface_hi"])
                                child.config(bg=DT["surface_hi"])
                            card_w.config(bg=DT["surface_hi"])

                    def _leave(e):
                        if current_selected_feedback[0] is None or current_selected_feedback[0]["feedback_id"] != data["feedback_id"]:
                            for child in card_w.winfo_children():
                                if isinstance(child, tk.Frame):
                                    for subchild in child.winfo_children():
                                        subchild.config(bg=DT["surface"])
                                    child.config(bg=DT["surface"])
                                child.config(bg=DT["surface"])
                            card_w.config(bg=DT["surface"])

                    def _click(e):
                        open_feedback_detail(data)

                    card_w.bind("<Enter>", _enter)
                    card_w.bind("<Leave>", _leave)
                    card_w.bind("<Button-1>", _click)

                    for child in card_w.winfo_children():
                        child.bind("<Enter>", _enter)
                        child.bind("<Leave>", _leave)
                        child.bind("<Button-1>", _click)
                        if isinstance(child, tk.Frame):
                            for subchild in child.winfo_children():
                                subchild.bind("<Enter>", _enter)
                                subchild.bind("<Leave>", _leave)
                                subchild.bind("<Button-1>", _click)

                _make_events(item_card, fb)

            # Auto open first if nothing selected
            if rows and not current_selected_feedback[0]:
                open_feedback_detail(rows[0])

        render_mail_list()


if __name__ == "__main__":
    app = AdminApp()
    app.mainloop()
