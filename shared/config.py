import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = os.path.join(BASE_DIR, "parkslot.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
ICON_PNG_PATH = os.path.join(ASSETS_DIR, "icon.png")
ICON_ICO_PATH = os.path.join(ASSETS_DIR, "icon.ico")

# Unified Professional Dark Parking-Themed Color Palette
COLORS = {
    "bg_main": "#0B132B",          # Deep Midnight Asphalt Navy
    "bg_card": "#111B38",          # Elevated parking slot card surface
    "surface": "#111B38",          # Elevated surface
    "surface_hi": "#1A2748",       # High surface / Hover state
    "primary": "#0EA5E9",          # Sky Blue / Cyan accent
    "primary_hover": "#0284C7",    # Darker Cyan Blue
    "secondary": "#334155",        # Slate Gray
    "accent": "#38BDF8",           # Glowing cyan accent line
    "border_glow": "#38BDF8",      # Glowing cyan border accent
    "success": "#16A34A",          # Forest Green
    "danger": "#DC2626",           # Crimson Red
    "warning": "#D97706",          # Amber
    "text_dark": "#F8FAFC",        # Crisp white text
    "text_light": "#F8FAFC",       # Crisp white text
    "text_muted": "#94A3B8",       # Slate gray
    "border": "#1E2E56",           # Subtle slot bay border
    "header_bg": "#111B38",        # Dark surface header
    "header_text": "#F8FAFC"       # Light header text
}

# Fonts
FONTS = {
    "title": ("Segoe UI", 16, "bold"),
    "subtitle": ("Segoe UI", 12, "bold"),
    "header": ("Segoe UI", 14, "bold"),
    "body": ("Segoe UI", 10),
    "body_bold": ("Segoe UI", 10, "bold"),
    "small": ("Segoe UI", 9),
    "stat_num": ("Segoe UI", 20, "bold")
}

