import tkinter as tk
from tkinter import ttk, messagebox
from shared.config import COLORS, FONTS

def apply_global_styles(root):
    """Applies modern ttk styles across the entire application."""
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
    style.configure("TEntry", padding=5, font=FONTS["body"])
    style.configure("TCombobox", padding=5, font=FONTS["body"])

    # Treeview styles
    style.configure("Treeview.Heading", font=FONTS["body_bold"], background=COLORS["header_bg"], foreground=COLORS["header_text"])
    style.configure("Treeview", font=FONTS["body"], rowheight=26, background="#FFFFFF", fieldbackground="#FFFFFF")
    style.map("Treeview", background=[("selected", COLORS["primary"])], foreground=[("selected", "#FFFFFF")])

def create_header(parent, title_text: str, subtitle_text: str = "", on_logout=None):
    """Creates a consistent top navigation banner."""
    header = tk.Frame(parent, bg=COLORS["header_bg"], height=70, padx=20, pady=10)
    header.pack(fill="x", side="top")

    text_frame = tk.Frame(header, bg=COLORS["header_bg"])
    text_frame.pack(side="left", fill="y")

    title = tk.Label(text_frame, text=title_text, font=FONTS["title"], fg=COLORS["header_text"], bg=COLORS["header_bg"])
    title.pack(anchor="w")

    if subtitle_text:
        sub = tk.Label(text_frame, text=subtitle_text, font=FONTS["small"], fg=COLORS["accent"], bg=COLORS["header_bg"])
        sub.pack(anchor="w")

    if on_logout:
        btn_logout = tk.Button(
            header, text="Logout", font=FONTS["body_bold"],
            bg=COLORS["danger"], fg="#FFFFFF", activebackground="#B91C1C",
            activeforeground="#FFFFFF", bd=0, padx=14, pady=5, cursor="hand2",
            command=on_logout
        )
        btn_logout.pack(side="right", pady=5)

    return header

def create_card(parent, padx=15, pady=15):
    """Creates a card frame with border and white background."""
    card = tk.Frame(parent, bg=COLORS["bg_card"], bd=1, relief="solid", highlightthickness=0)
    card.pack(fill="both", expand=True, padx=padx, pady=pady)
    return card

