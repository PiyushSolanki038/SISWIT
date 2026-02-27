"""
Configuration for Employee Work Update Telegram Bot.
Reads from environment variables first, falls back to hardcoded defaults.
Supports Railway deployment via GOOGLE_CREDS_JSON env var.
"""

import os
import json

# ─── Telegram Bot Configuration ───────────────────────────────────────────────
# ─── Telegram Bot Configuration ───────────────────────────────────────────────
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Chat IDs for personal notifications (get from @userinfobot on Telegram)
OWNER_CHAT_ID = os.getenv("OWNER_CHAT_ID", "")
HR_CHAT_ID = os.getenv("HR_CHAT_ID", "")

# ─── Excel Configuration ─────────────────────────────────────────────────────
EXCEL_FILE = os.getenv("EXCEL_FILE", "employee_updates.xlsx")

# ─── Google Sheets Configuration ─────────────────────────────────────────────
# Leave empty string "" to skip Google Sheets silently
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID", "")
GOOGLE_CREDS_FILE = os.getenv("GOOGLE_CREDS_FILE", "credentials.json")

# ─── Railway Deployment Support ──────────────────────────────────────────────
# If GOOGLE_CREDS_JSON env var is set (full JSON string), write it to file
GOOGLE_CREDS_JSON = os.getenv("GOOGLE_CREDS_JSON", "")

if GOOGLE_CREDS_JSON and not os.path.exists(GOOGLE_CREDS_FILE):
    try:
        creds_data = json.loads(GOOGLE_CREDS_JSON)
        with open(GOOGLE_CREDS_FILE, "w", encoding="utf-8") as f:
            json.dump(creds_data, f, indent=2)
        print("✅ Created service_account.json from GOOGLE_CREDS_JSON env var")
    except (json.JSONDecodeError, IOError) as e:
        print(f"⚠️ Failed to create service_account.json from env var: {e}")

# ─── Timezone ────────────────────────────────────────────────────────────────
TIMEZONE = os.getenv("TIMEZONE", "Asia/Kolkata")

# ─── Staff Mapping (ID -> Name, Department) ──────────────────────────────
# Staff records are stored in staff.json for persistence.
STAFF_JSON_FILE = "staff.json"

def load_staff_records():
    """Load staff records from staff.json or return defaults."""
    if os.path.exists(STAFF_JSON_FILE):
        try:
            with open(STAFF_JSON_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Error loading {STAFF_JSON_FILE}: {e}")
    
    # Defaults if file doesn't exist
    return {
        "DEV01": {"name": "Sunny", "dept": "DEVELOPER"},
        "DEV02": {"name": "Piyush", "dept": "DEVELOPER"},
        "DEV03": {"name": "Anand", "dept": "DEVELOPER"},
        "DEV04": {"name": "Adarsh", "dept": "DEVELOPER"},
        "MKT01": {"name": "Bipul", "dept": "MARKETING"},
        "MKT02": {"name": "Finney", "dept": "MARKETING"},
        "FIN01":  {"name": "Sahil", "dept": "FINANCE"},
    }

def save_staff_record(emp_id, name, dept):
    """Add or update a staff record and save to staff.json."""
    records = load_staff_records()
    records[emp_id.upper()] = {"name": name, "dept": dept.upper()}
    try:
        with open(STAFF_JSON_FILE, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=4)
        return True
    except Exception as e:
        print(f"⚠️ Error saving {STAFF_JSON_FILE}: {e}")
        return False

# Load records on startup
STAFF_RECORDS = load_staff_records()
