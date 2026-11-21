# ParkSlot — Parking Space Identification, Allocation & Utilisation Management System

---

## 📁 Project Specification & Blueprint Files

1. **[`PROJECT_SPECIFICATION.md`](file:///c:/Users/Jeswin/OneDrive/Documents/ParkSlot/PROJECT_SPECIFICATION.md)**  
   The authoritative Master Software Requirements Specification (SRS) & Architecture Blueprint.
   - **System Architecture:** Layered Python + Tkinter + SQLite architecture diagram.
   - **Unified Schema:** All 14 relational tables with constraints and foreign keys.
   - **User Module:** Comprehensive breakdown of all 11 user screens, fields, validation, and actions.
   - **Owner Module:** Complete breakdown of all 10 owner screens, facilities, slots, rates, and revenue.
   - **Admin Module:** Complete breakdown of all 13 admin screens, check-in, check-out, overstay scanner, and conflict resolution.
   - **Business Rules:** Overlapping booking formulas, billing algorithms, and state machines.
   - **Implementation Roadmap:** Phased 8-step build order.

2. **[`schema.sql`](file:///c:/Users/Jeswin/OneDrive/Documents/ParkSlot/schema.sql)**  
   Ready-to-execute SQLite DDL script containing:
   - Full table definitions (`admins`, `owners`, `users`, `vehicles`, `parking_facilities`, `parking_rates`, `parking_slots`, `bookings`, `parking_sessions`, `fees_payments`, `overstay_events`, `slot_reallocations`, `waitlist`, `admin_settings`).
   - Query performance indexes.
   - Seed data for default administrator credentials (`admin` / `Admin@123`) and system parameters.

3. **[`PROJECT_PROMPT.md`](file:///c:/Users/Jeswin/OneDrive/Documents/ParkSlot/PROJECT_PROMPT.md)**  
   A plug-and-play prompt template and architectural checklist ready to feed directly into Antigravity AI to start code generation.

---

