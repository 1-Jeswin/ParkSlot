import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = os.path.join(BASE_DIR, "parkslot.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")

# Modern Professional Color Palette
COLORS = {
    "bg_main": "#F1F5F9",          # Light Slate background
    "bg_card": "#FFFFFF",          # Pure white card background
    "primary": "#2563EB",          # Primary Blue
    "primary_hover": "#1D4ED8",    # Darker Blue
    "secondary": "#475569",        # Slate Gray
    "accent": "#0EA5E9",           # Sky Blue
    "success": "#16A34A",          # Green
    "danger": "#DC2626",           # Red
    "warning": "#D97706",          # Amber
    "text_dark": "#0F172A",        # Dark text
    "text_muted": "#64748B",       # Muted text
    "border": "#CBD5E1",           # Border gray
    "header_bg": "#1E293B",        # Dark Slate header
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

