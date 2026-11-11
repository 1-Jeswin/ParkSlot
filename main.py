"""
ParkSlot — Minimalist Artistic Portal Launcher
Professional Parking-Themed Entry UI with Responsive Full-Window Layout
"""
import tkinter as tk
import os
from shared.config import ICON_PNG_PATH
from shared.database import init_db
from shared.ui_helpers import apply_global_styles, center_window
from user_module.app import UserApp
from owner_module.app import OwnerApp
from admin_module.app import AdminApp

class MainLauncher(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ParkSlot")
        self.geometry("760x540")
        self.minsize(520, 440)
        self.resizable(True, True)

        # Parking-Themed Deep Night Palette
        self.THEME = {
            "bg": "#0B132B",           # Deep Midnight Asphalt Navy
            "surface": "#111B38",      # Elevated parking slot card surface
            "border": "#1E2E56",       # Subtle slot bay border
            "border_glow": "#38BDF8",  # Glowing cyan accent line
            "text": "#F8FAFC",         # Crisp white
            "text_muted": "#94A3B8",   # Slate gray
            "driver_hover": "#1D4ED8", # Sapphire Blue
            "owner_hover": "#6D28D9",  # Amethyst Purple
            "admin_hover": "#0284C7"   # Cyan Blue
        }

        self.configure(bg=self.THEME["bg"])
        apply_global_styles(self)
        center_window(self, 760, 540)

        # Ensure database is ready
        init_db()

        self._build_ui()

    def _build_ui(self):
        # Full-window outer container that fills and expands with resizing
        self.main_container = tk.Frame(self, bg=self.THEME["bg"])
        self.main_container.pack(fill="both", expand=True)

        # Centered inner canvas / frame for artistic symmetry
        center_frame = tk.Frame(self.main_container, bg=self.THEME["bg"])
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        # -------------------------------------------------------------
        # 1. ARTISTIC BRANDING (LOGO & NAME)
        # -------------------------------------------------------------
        brand_box = tk.Frame(center_frame, bg=self.THEME["bg"])
        brand_box.pack(pady=(0, 24))

        # Scaled Logo Icon
        if os.path.exists(ICON_PNG_PATH):
            try:
                raw_img = tk.PhotoImage(file=ICON_PNG_PATH)
                self.logo_img = raw_img.subsample(14, 14)  # ~73x73 px refined logo
                logo_lbl = tk.Label(brand_box, image=self.logo_img, bg=self.THEME["bg"], bd=0)
                logo_lbl.pack(pady=(0, 8))
            except Exception:
                pass

        # App Name Typography
        title_lbl = tk.Label(
            brand_box,
            text="PARKSLOT",
            font=("Segoe UI", 24, "bold"),
            fg=self.THEME["text"],
            bg=self.THEME["bg"]
        )
        title_lbl.pack()

        # Minimalist Glowing Parking Bay Line Accent
        bay_line = tk.Frame(brand_box, bg=self.THEME["border_glow"], height=2, width=42)
        bay_line.pack(pady=(6, 0))

        # -------------------------------------------------------------
        # 2. THREE COMPACT, AESTHETIC LOGIN BUTTONS
        # -------------------------------------------------------------
        buttons_box = tk.Frame(center_frame, bg=self.THEME["bg"])
        buttons_box.pack(pady=(10, 0))

        self._create_compact_aesthetic_button(
            parent=buttons_box,
            text="Driver Login",
            hover_bg=self.THEME["driver_hover"],
            command=self.launch_user
        )

        self._create_compact_aesthetic_button(
            parent=buttons_box,
            text="Owner Login",
            hover_bg=self.THEME["owner_hover"],
            command=self.launch_owner
        )

        self._create_compact_aesthetic_button(
            parent=buttons_box,
            text="Admin Login",
            hover_bg=self.THEME["admin_hover"],
            command=self.launch_admin
        )

    def _create_compact_aesthetic_button(self, parent, text, hover_bg, command):
        """Creates a compact, aesthetic pill-style button with subtle glow and borders."""
        btn_wrapper = tk.Frame(parent, bg=self.THEME["bg"], pady=6)
        btn_wrapper.pack()

        btn = tk.Button(
            btn_wrapper,
            text=text,
            font=("Segoe UI", 10, "bold"),
            fg=self.THEME["text"],
            bg=self.THEME["surface"],
            activeforeground="#FFFFFF",
            activebackground=hover_bg,
            relief="flat",
            bd=1,
            highlightthickness=1,
            highlightbackground=self.THEME["border"],
            highlightcolor=self.THEME["border_glow"],
            width=22,
            pady=7,
            cursor="hand2",
            command=command
        )
        btn.pack()

        # Tactile hover effect
        def on_enter(e):
            btn.config(bg=hover_bg, highlightbackground=self.THEME["border_glow"])

        def on_leave(e):
            btn.config(bg=self.THEME["surface"], highlightbackground=self.THEME["border"])

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

    # -----------------------------------------------------------------
    # LAUNCH HANDLERS
    # -----------------------------------------------------------------
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
