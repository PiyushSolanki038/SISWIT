"""
Configuration for Employee Work Update Telegram Bot.
Reads from .env file first, then environment variables, falls back to defaults.
Supports Railway deployment via GOOGLE_CREDS_JSON env var.
"""

import os
import json
import logging

# Load .env file if it exists (must be before any os.getenv calls)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, skip silently

logger = logging.getLogger(__name__)

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
        logger.info("Created service_account.json from GOOGLE_CREDS_JSON env var")
    except (json.JSONDecodeError, IOError) as e:
        logger.warning(f"Failed to create service_account.json from env var: {e}")

# Detect Railway environment
IS_RAILWAY = bool(os.getenv("RAILWAY_ENVIRONMENT", ""))

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
            logger.warning(f"Error loading {STAFF_JSON_FILE}: {e}")
    
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
        logger.warning(f"Error saving {STAFF_JSON_FILE}: {e}")
        return False

def remove_staff_record(emp_id):
    """Remove a staff record from staff.json."""
    records = load_staff_records()
    emp_id = emp_id.upper()
    if emp_id not in records:
        return False
    del records[emp_id]
    try:
        with open(STAFF_JSON_FILE, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=4)
        return True
    except Exception as e:
        logger.warning(f"Error saving {STAFF_JSON_FILE}: {e}")
        return False

# Load records on startup
STAFF_RECORDS = load_staff_records()

# ─── Daily Log Persistence ───────────────────────────────────────────────────
DAILY_LOG_FILE = "daily_log.json"

def load_daily_log():
    """Load daily submission log from daily_log.json."""
    if os.path.exists(DAILY_LOG_FILE):
        try:
            with open(DAILY_LOG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Error loading {DAILY_LOG_FILE}: {e}")
    return {}

def save_daily_log(log_data):
    """Save daily submission log to daily_log.json."""
    try:
        with open(DAILY_LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(log_data, f, indent=2)
    except Exception as e:
        logger.warning(f"Error saving {DAILY_LOG_FILE}: {e}")
