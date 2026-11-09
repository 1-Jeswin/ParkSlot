"""
ParkSlot — Main Application Portal Launcher
Allows selecting and launching any of the 3 modules:
1. User (Driver) Module       (run_user.py)
2. Facility Owner Module      (run_owner.py)
3. Master Administrator Module (run_admin.py)
"""
import tkinter as tk
from shared.config import COLORS, FONTS
from shared.database import init_db
from shared.ui_helpers import apply_global_styles
from user_module.app import UserApp
from owner_module.app import OwnerApp
from admin_module.app import AdminApp

class MainLauncher(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ParkSlot — Unified Project Launcher")
        self.geometry("820x540")
        self.resizable(False, False)
        apply_global_styles(self)

        # Ensure database is ready
        init_db()

        # Header Banner
        header = tk.Frame(self, bg=COLORS["header_bg"], padx=20, pady=20)
        header.pack(fill="x")

        tk.Label(
            header,
            text="PARKSLOT",
            font=("Segoe UI", 22, "bold"),
            fg=COLORS["header_text"],
            bg=COLORS["header_bg"]
        ).pack()

        tk.Label(
            header,
            text="Vehicular Parking Space Identification, Allocation & Utilisation Management System",
            font=FONTS["small"],
            fg=COLORS["accent"],
            bg=COLORS["header_bg"]
        ).pack(pady=(4, 0))

        # Main Body
        body = tk.Frame(self, bg=COLORS["bg_main"], padx=30, pady=25)
        body.pack(fill="both", expand=True)

        tk.Label(
            body,
            text="Select a Module to Launch:",
            font=FONTS["subtitle"],
            bg=COLORS["bg_main"],
            fg=COLORS["text_dark"]
        ).pack(anchor="w", pady=(0, 15))

        cards_frame = tk.Frame(body, bg=COLORS["bg_main"])
        cards_frame.pack(fill="both", expand=True)

        # Module 1: User / Driver
        self._create_portal_card(
            cards_frame,
            col=0,
            icon="🚗",
            title="Driver / User Module",
            subtitle="Assigned to: Teammate 1",
            desc="• Find available slots\n• Reserve parking & vehicle\n• Track duration & fee\n• View bookings & cancellations",
            btn_text="Launch Driver Portal",
            btn_color=COLORS["primary"],
            action=self.launch_user
        )

        # Module 2: Owner
        self._create_portal_card(
            cards_frame,
            col=1,
            icon="🏢",
            title="Facility Owner Module",
            subtitle="Assigned to: Teammate 2",
            desc="• Register parking facility\n• Manage slot inventory\n• Set vehicle hourly tariffs\n• View bookings & revenues",
            btn_text="Launch Owner Portal",
            btn_color=COLORS["secondary"],
            action=self.launch_owner
        )

        # Module 3: Admin
        self._create_portal_card(
            cards_frame,
            col=2,
            icon="🛡️",
            title="Administrator Module",
            subtitle="Assigned to: Teammate 3",
            desc="• Central live KPI dashboard\n• Check-in / Check-out\n• Overstay & conflict solver\n• Operational CSV reports",
            btn_text="Launch Admin Console",
            btn_color=COLORS["header_bg"],
            action=self.launch_admin
        )

        # Footer
        footer = tk.Frame(self, bg=COLORS["bg_main"], pady=10)
        footer.pack(fill="x")
        tk.Label(
            footer,
            text="Shared Database: parkslot.db (SQLite) | All modules share real-time state",
            font=FONTS["small"],
            bg=COLORS["bg_main"],
            fg=COLORS["text_muted"]
        ).pack()

    def _create_portal_card(self, parent, col, icon, title, subtitle, desc, btn_text, btn_color, action):
        card = tk.Frame(parent, bg=COLORS["bg_card"], bd=1, relief="solid", padx=16, pady=16)
        card.grid(row=0, column=col, padx=8, pady=5, sticky="nsew")
        parent.grid_columnconfigure(col, weight=1)

        tk.Label(card, text=icon, font=("Segoe UI", 26), bg=COLORS["bg_card"]).pack(pady=(0, 4))
        tk.Label(card, text=title, font=FONTS["body_bold"], bg=COLORS["bg_card"], fg=COLORS["text_dark"]).pack()
        tk.Label(card, text=subtitle, font=FONTS["small"], bg=COLORS["bg_card"], fg=COLORS["accent"]).pack(pady=(0, 8))

        tk.Label(card, text=desc, font=FONTS["small"], bg=COLORS["bg_card"], fg=COLORS["text_muted"], justify="left").pack(anchor="w", pady=(0, 16))

        tk.Button(
            card, text=btn_text, font=FONTS["body_bold"],
            bg=btn_color, fg="#FFFFFF", bd=0, pady=7, cursor="hand2",
            command=action
        ).pack(fill="x", side="bottom")

    def launch_user(self):
        self.withdraw()
        app = UserApp()
        def on_close():
            app.destroy()
            self.deiconify()
        app.protocol("WM_DELETE_WINDOW", on_close)

    def launch_owner(self):
        self.withdraw()
        app = OwnerApp()
        def on_close():
            app.destroy()
            self.deiconify()
        app.protocol("WM_DELETE_WINDOW", on_close)

    def launch_admin(self):
        self.withdraw()
        app = AdminApp()
        def on_close():
            app.destroy()
            self.deiconify()
        app.protocol("WM_DELETE_WINDOW", on_close)

if __name__ == "__main__":
    app = MainLauncher()
    app.mainloop()

