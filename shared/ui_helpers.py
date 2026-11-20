import tkinter as tk
from tkinter import ttk, messagebox
import os
from shared.config import COLORS, FONTS, ICON_PNG_PATH, ICON_ICO_PATH

def set_window_icon(window):
    """Applies the official ParkSlot application icon to any Tkinter window."""
    try:
        if os.path.exists(ICON_ICO_PATH):
            window.iconbitmap(ICON_ICO_PATH)
        if os.path.exists(ICON_PNG_PATH):
            icon_img = tk.PhotoImage(file=ICON_PNG_PATH)
            window.iconphoto(True, icon_img)
            window._app_icon_ref = icon_img
    except Exception:
        pass

def apply_global_styles(root):
    """Applies modern ttk styles and window icon across the application."""
    set_window_icon(root)
    root.configure(bg=COLORS["bg_main"])
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except Exception:
        pass

    # Frame styles
    style.configure("Main.TFrame", background=COLORS["bg_main"])
    style.configure("Card.TFrame", background=COLORS["bg_card"], relief="solid", borderwidth=1)

    # Label styles
    style.configure("Title.TLabel", background=COLORS["header_bg"], foreground=COLORS["header_text"], font=FONTS["title"])
    style.configure("SubTitle.TLabel", background=COLORS["header_bg"], foreground=COLORS["accent"], font=FONTS["subtitle"])
    style.configure("CardTitle.TLabel", background=COLORS["bg_card"], foreground=COLORS["text_dark"], font=FONTS["subtitle"])
    style.configure("CardBody.TLabel", background=COLORS["bg_card"], foreground=COLORS["text_dark"], font=FONTS["body"])
    style.configure("Muted.TLabel", background=COLORS["bg_card"], foreground=COLORS["text_muted"], font=FONTS["small"])

    # Button styles
    style.configure("Primary.TButton", font=FONTS["body_bold"], background=COLORS["primary"], foreground="#FFFFFF")
    style.map("Primary.TButton", background=[("active", COLORS["primary_hover"])])

    style.configure("Success.TButton", font=FONTS["body_bold"], background=COLORS["success"], foreground="#FFFFFF")
    style.configure("Danger.TButton", font=FONTS["body_bold"], background=COLORS["danger"], foreground="#FFFFFF")
    style.configure("Secondary.TButton", font=FONTS["body"], background=COLORS["secondary"], foreground="#FFFFFF")

    # Entry and Combobox
    style.configure("TEntry", padding=5, font=FONTS["body"], fieldbackground=COLORS["bg_card"], foreground=COLORS["text_dark"])
    style.configure("TCombobox", padding=5, font=FONTS["body"], fieldbackground=COLORS["bg_card"], foreground=COLORS["text_dark"])

    # Treeview styles (matching dark parking theme)
    style.configure("Treeview.Heading", font=FONTS["body_bold"], background=COLORS["surface_hi"], foreground=COLORS["accent"])
    style.configure("Treeview", font=FONTS["body"], rowheight=26, background=COLORS["bg_card"], fieldbackground=COLORS["bg_card"], foreground=COLORS["text_dark"])
    style.map("Treeview", background=[("selected", COLORS["accent"])], foreground=[("selected", "#0B132B")])

def center_window(window, width: int, height: int):
    """Centers a Tkinter window on the primary display."""
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = max(0, int((screen_width - width) / 2))
    y = max(0, int((screen_height - height) / 2))
    window.geometry(f"{width}x{height}+{x}+{y}")

def create_header(parent, title_text: str, subtitle_text: str = "", on_logout=None):
    """Creates a consistent polished dark parking-themed top navigation banner."""
    header = tk.Frame(parent, bg=COLORS["header_bg"], height=58, padx=20, pady=10)
    header.pack(fill="x", side="top")

    text_frame = tk.Frame(header, bg=COLORS["header_bg"])
    text_frame.pack(side="left", fill="y")

    title = tk.Label(text_frame, text=title_text, font=FONTS["title"], fg=COLORS["header_text"], bg=COLORS["header_bg"])
    title.pack(anchor="w")

    if subtitle_text:
        sub = tk.Label(text_frame, text=subtitle_text, font=FONTS["small"], fg=COLORS["text_muted"], bg=COLORS["header_bg"])
        sub.pack(anchor="w")

    if on_logout:
        btn_logout = tk.Button(
            header, text="Logout", font=FONTS["body_bold"],
            bg=COLORS["danger"], fg="#FFFFFF", activebackground="#B91C1C",
            activeforeground="#FFFFFF", bd=0, padx=14, pady=5, cursor="hand2",
            command=on_logout
        )
        btn_logout.pack(side="right", pady=5)

    # Cyan glowing strip beneath header
    accent_strip = tk.Frame(parent, bg=COLORS["accent"], height=2)
    accent_strip.pack(fill="x", side="top")

    return header

def create_card(parent, padx=15, pady=15):
    """Creates a card frame with border and elevated dark background."""
    card = tk.Frame(parent, bg=COLORS["bg_card"], bd=1, relief="solid", highlightthickness=1,
                    highlightbackground=COLORS["border"])
    card.pack(fill="both", expand=True, padx=padx, pady=pady)
    return card

