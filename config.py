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
# OWNER_CHAT_ID supports multiple comma-separated IDs
_OWNER_IDS_RAW = os.getenv("OWNER_CHAT_ID", "")
OWNER_CHAT_IDS = [x.strip() for x in _OWNER_IDS_RAW.split(",") if x.strip()]
OWNER_CHAT_ID = OWNER_CHAT_IDS[0] if OWNER_CHAT_IDS else ""  # Primary owner (backward compat)
HR_CHAT_ID = os.getenv("HR_CHAT_ID", "")
GROUP_CHAT_ID = os.getenv("GROUP_CHAT_ID", "")  # Auto-detected from messages or set manually


def is_owner(user_id):
    """Check if user_id is any of the owner IDs."""
    return str(user_id) in OWNER_CHAT_IDS


def is_admin(user_id):
    """Check if user_id is Owner or HR."""
    uid = str(user_id)
    return uid in OWNER_CHAT_IDS or uid == str(HR_CHAT_ID)

# ─── Excel Configuration ─────────────────────────────────────────────────────
EXCEL_FILE = os.getenv("EXCEL_FILE", "employee_updates.xlsx")

# ─── Google Sheets Configuration ─────────────────────────────────────────────
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID", "")
GOOGLE_CREDS_FILE = os.getenv("GOOGLE_CREDS_FILE", "credentials.json")

# ─── Railway Deployment Support ──────────────────────────────────────────────
GOOGLE_CREDS_JSON = os.getenv("GOOGLE_CREDS_JSON", "")

if GOOGLE_CREDS_JSON and not os.path.exists(GOOGLE_CREDS_FILE):
    try:
        creds_data = json.loads(GOOGLE_CREDS_JSON)
        with open(GOOGLE_CREDS_FILE, "w", encoding="utf-8") as f:
            json.dump(creds_data, f, indent=2)
        logger.info("Created credentials.json from GOOGLE_CREDS_JSON env var")
    except (json.JSONDecodeError, IOError) as e:
        logger.warning(f"Failed to create credentials.json from env var: {e}")

IS_RAILWAY = bool(os.getenv("RAILWAY_ENVIRONMENT", ""))

# ─── Timezone ────────────────────────────────────────────────────────────────
TIMEZONE = os.getenv("TIMEZONE", "Asia/Kolkata")

# ─── Submission Deadline ─────────────────────────────────────────────────────
SUBMISSION_DEADLINE = os.getenv("SUBMISSION_DEADLINE", "11:00")  # 24h format HH:MM

# ─── Data Files ──────────────────────────────────────────────────────────────
STAFF_JSON_FILE = "staff.json"
DAILY_LOG_FILE = "daily_log.json"
LEAVE_LOG_FILE = "leave_log.json"
SETTINGS_FILE = "bot_settings.json"


# ─── Settings (dynamic, saved to file) ───────────────────────────────────────
def load_settings():
    """Load dynamic bot settings from file."""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Error loading {SETTINGS_FILE}: {e}")
    return {}


def save_setting(key, value):
    """Save a dynamic bot setting."""
    settings = load_settings()
    settings[key] = value
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
        return True
    except Exception as e:
        logger.warning(f"Error saving {SETTINGS_FILE}: {e}")
        return False


def get_setting(key, default=None):
    """Get a dynamic bot setting."""
    settings = load_settings()
    return settings.get(key, default)


# ─── Staff Records ───────────────────────────────────────────────────────────
def load_staff_records():
    """Load staff records from staff.json or return defaults."""
    if os.path.exists(STAFF_JSON_FILE):
        try:
            with open(STAFF_JSON_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Error loading {STAFF_JSON_FILE}: {e}")

    return {
        "DEV01": {"name": "Sunny", "dept": "DEVELOPER"},
        "DEV02": {"name": "Piyush", "dept": "DEVELOPER"},
        "DEV03": {"name": "Anand", "dept": "DEVELOPER"},
        "DEV04": {"name": "Adarsh", "dept": "DEVELOPER"},
        "MKT01": {"name": "Bipul", "dept": "MARKETING"},
        "MKT02": {"name": "Finney", "dept": "MARKETING"},
        "MKT03": {"name": "Shivam", "dept": "MARKETING"},
        "MKT04": {"name": "Amar", "dept": "MARKETING"},
        "FIN01": {"name": "Sahil", "dept": "FINANCE"},
        "HR01": {"name": "Shruti", "dept": "HR"},
        "HR02": {"name": "Pooja", "dept": "HR"},
    }


def save_staff_record(emp_id, name, dept):
    """Add or update a staff record."""
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
    """Remove a staff record."""
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



def save_staff_records(records):
    """Save full staff records dict to file."""
    try:
        with open(STAFF_JSON_FILE, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=4)
        return True
    except Exception as e:
        logger.warning(f"Error saving {STAFF_JSON_FILE}: {e}")
        return False


STAFF_RECORDS = load_staff_records()


# ─── Daily Log ───────────────────────────────────────────────────────────────
def load_daily_log():
    """Load daily submission log."""
    if os.path.exists(DAILY_LOG_FILE):
        try:
            with open(DAILY_LOG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Error loading {DAILY_LOG_FILE}: {e}")
    return {}


def save_daily_log(log_data):
    """Save daily submission log."""
    try:
        with open(DAILY_LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(log_data, f, indent=2)
    except Exception as e:
        logger.warning(f"Error saving {DAILY_LOG_FILE}: {e}")


# ─── Leave Log ───────────────────────────────────────────────────────────────
def load_leave_log():
    """Load leave request log."""
    if os.path.exists(LEAVE_LOG_FILE):
        try:
            with open(LEAVE_LOG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Error loading {LEAVE_LOG_FILE}: {e}")
    return {}


def save_leave_log(log_data):
    """Save leave request log."""
    try:
        with open(LEAVE_LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(log_data, f, indent=2)
    except Exception as e:
        logger.warning(f"Error saving {LEAVE_LOG_FILE}: {e}")


def get_deadline():
    """Get the current submission deadline (dynamic or default)."""
    return get_setting("deadline", SUBMISSION_DEADLINE)
