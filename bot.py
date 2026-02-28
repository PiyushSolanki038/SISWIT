"""
Employee Daily Work Update Telegram Bot
========================================
Parses employee messages in format: EMP_ID - DEPT - Work description
Saves to Excel (local) + Google Sheets, sends notifications to Owner & HR.

Uses python-telegram-bot v21 API (ApplicationBuilder).
"""

import re
import os
import logging
from datetime import datetime

import pytz
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

import config

# ─── Logging ─────────────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ─── Regex Pattern ───────────────────────────────────────────────────────────
# Matches: EMP_ID Work description
# EMP_ID: alphanumeric (e.g., PK01, DEV01)
# Work: everything after the first space
UPDATE_PATTERN = re.compile(
    r"^([A-Za-z0-9]+)\s+(.+)$",
    re.DOTALL,
)


# ─── Excel Functions ─────────────────────────────────────────────────────────
def save_to_excel(data: dict) -> bool:
    """Save the update to a professionally formatted Excel file."""
    try:
        from openpyxl import Workbook, load_workbook
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

        headers = [
            "Sr No", "Employee ID", "Department", "Employee Name",
            "Telegram Username", "Date", "Day", "Time",
            "Work Update", "Group Name",
        ]

        file_path = config.EXCEL_FILE

        if os.path.exists(file_path):
            wb = load_workbook(file_path)
            ws = wb.active
            next_row = ws.max_row + 1
            sr_no = next_row - 1  # subtract header row
        else:
            wb = Workbook()
            ws = wb.active
            ws.title = "Employee Updates"

            # ── Header styling ──
            header_fill = PatternFill(start_color="1B3A5C", end_color="1B3A5C", fill_type="solid")
            header_font = Font(name="Arial", bold=True, color="FFFFFF", size=11)
            header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            thin_border = Border(
                left=Side(style="thin", color="B0B0B0"),
                right=Side(style="thin", color="B0B0B0"),
                top=Side(style="thin", color="B0B0B0"),
                bottom=Side(style="thin", color="B0B0B0"),
            )

            for col_idx, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col_idx, value=header)
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = header_alignment
                cell.border = thin_border

            # Column widths
            col_widths = [8, 15, 15, 20, 20, 14, 12, 10, 50, 25]
            for i, width in enumerate(col_widths, 1):
                ws.column_dimensions[chr(64 + i)].width = width

            # Freeze header row
            ws.freeze_panes = "A2"

            # Auto-filter
            ws.auto_filter.ref = f"A1:J1"

            next_row = 2
            sr_no = 1

        # ── Write data row ──
        row_data = [
            sr_no,
            data["emp_id"],
            data["department"],
            data["emp_name"],
            data["username"],
            data["date"],
            data["day"],
            data["time"],
            data["work_update"],
            data["group_name"],
        ]

        # Alternating row colors
        if sr_no % 2 == 0:
            row_fill = PatternFill(start_color="E8F0FE", end_color="E8F0FE", fill_type="solid")
        else:
            row_fill = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")

        data_font = Font(name="Arial", size=10)
        data_alignment = Alignment(vertical="center", wrap_text=True)
        thin_border = Border(
            left=Side(style="thin", color="D0D0D0"),
            right=Side(style="thin", color="D0D0D0"),
            top=Side(style="thin", color="D0D0D0"),
            bottom=Side(style="thin", color="D0D0D0"),
        )

        for col_idx, value in enumerate(row_data, 1):
            cell = ws.cell(row=next_row, column=col_idx, value=value)
            cell.fill = row_fill
            cell.font = data_font
            cell.alignment = data_alignment
            cell.border = thin_border

        # Center-align Sr No, Date, Day, Time columns
        for col in [1, 6, 7, 8]:
            ws.cell(row=next_row, column=col).alignment = Alignment(
                horizontal="center", vertical="center"
            )

        wb.save(file_path)
        print(f"📊 Excel: Saved update #{sr_no} to {file_path}")
        return True

    except Exception as e:
        print(f"❌ Excel Error: {e}")
        logger.error(f"Excel save failed: {e}", exc_info=True)
        return False


# ─── Google Sheets Functions ─────────────────────────────────────────────────
def save_to_google_sheets(data: dict) -> bool:
    """Save the update to Google Sheets using a service account."""
    if not config.GOOGLE_SHEET_ID:
        # Silently skip if no Sheet ID configured
        return False

    try:
        import gspread
        from google.oauth2.service_account import Credentials

        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]

        creds = Credentials.from_service_account_file(config.GOOGLE_CREDS_FILE, scopes=scopes)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(config.GOOGLE_SHEET_ID).sheet1

        # Check if headers exist
        existing = sheet.get_all_values()
        headers = [
            "Sr No", "Employee ID", "Department", "Employee Name",
            "Telegram Username", "Date", "Day", "Time",
            "Work Update", "Group Name",
        ]

        if not existing:
            sheet.append_row(headers)
            sr_no = 1
        else:
            sr_no = len(existing)  # rows minus header = count, +1 for new = len

        row = [
            sr_no,
            data["emp_id"],
            data["department"],
            data["emp_name"],
            data["username"],
            data["date"],
            data["day"],
            data["time"],
            data["work_update"],
            data["group_name"],
        ]

        sheet.append_row(row)
        print(f"📋 Google Sheets: Saved update #{sr_no}")
        return True

    except Exception as e:
        print(f"❌ Google Sheets Error: {e}")
        logger.error(f"Google Sheets save failed: {e}", exc_info=True)
        return False


# ─── Notification Functions ──────────────────────────────────────────────────
async def send_personal_notification(bot, chat_id: str, data: dict, label: str):
    """Send a personal notification to Owner or HR."""
    if not chat_id:
        return

    try:
        message = (
            f"📬 *New Work Update Received*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 *Employee:* {data['emp_name']} (`{data['emp_id']}`)\n"
            f"🏢 *Department:* {data['department']}\n"
            f"💬 *Telegram:* @{data['username']}\n"
            f"📅 *Date:* {data['date']} ({data['day']})\n"
            f"🕐 *Time:* {data['time']}\n"
            f"📝 *Update:*\n{data['work_update']}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📍 *Group:* {data['group_name']}"
        )
        await bot.send_message(
            chat_id=int(chat_id),
            text=message,
            parse_mode="Markdown",
        )
        print(f"📩 Notification sent to {label} (Chat ID: {chat_id})")

    except Exception as e:
        print(f"⚠️ Failed to notify {label}: {e}")
        logger.error(f"Notification to {label} failed: {e}", exc_info=True)


# ─── Command Handlers ────────────────────────────────────────────────────────
async def staff_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display the list of registered staff members and instructions (Owner/HR only)."""
    user_id = str(update.effective_user.id)
    
    # Check if user is Owner or HR
    if user_id not in [config.OWNER_CHAT_ID, config.HR_CHAT_ID]:
        await update.message.reply_text("🚫 *Permission Denied:* Only the Owner and HR can use this command.", parse_mode="Markdown")
        print(f"🛑 Unauthorized attempt by {user_id} to access /staff")
        return

    if not config.STAFF_RECORDS:
        await update.message.reply_text("📋 No staff records configured in `config.py`.")
        return

    message = "👥 *Registered Staff & Attendance Format*\n"
    message += "━━━━━━━━━━━━━━━━━━━━━━\n"
    message += "Use the following ID and Department for your daily updates:\n\n"
    
    for emp_id, info in config.STAFF_RECORDS.items():
        message += f"• `{emp_id}` — {info['name']} ({info['dept']})\n"
    
    message += "\n📝 *Update Format:*\n"
    message += "`ID - Work description`"
    
    await update.message.reply_text(message, parse_mode="Markdown")
    print("💬 Staff list shared in group")


async def addstaff_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Dynamically add a new staff member (Owner/HR only)."""
    user_id = str(update.effective_user.id)
    
    # Check if user is Owner or HR
    if user_id not in [config.OWNER_CHAT_ID, config.HR_CHAT_ID]:
        await update.message.reply_text("🚫 *Permission Denied:* Only the Owner and HR can add staff.", parse_mode="Markdown")
        return

    # Expected: /addstaff ID - Name - Dept
    args = " ".join(context.args)
    if not args:
        await update.message.reply_text("❗ *Usage:* `/addstaff ID - Name - Department`", parse_mode="Markdown")
        return

    try:
        # Simple split by dash
        parts = [p.strip() for p in args.split("-")]
        if len(parts) != 3:
            raise ValueError("Invalid format")
        
        emp_id, name, dept = parts
        
        # Save to file
        success = config.save_staff_record(emp_id, name, dept)
        
        if success:
            # Refresh in-memory records
            config.STAFF_RECORDS = config.load_staff_records()
            await update.message.reply_text(
                f"✅ *Staff Added Successfully!*\n\n"
                f"🆔 *ID:* `{emp_id.upper()}`\n"
                f"👤 *Name:* {name}\n"
                f"🏢 *Dept:* {dept.upper()}",
                parse_mode="Markdown"
            )
            print(f"👤 Added new staff: {emp_id} - {name}")
        else:
            await update.message.reply_text("❌ *Error:* Failed to save staff record.")

    except Exception:
        await update.message.reply_text("❗ *Format error:* Use `/addstaff ID - Name - Department`", parse_mode="Markdown")


# ─── Main Message Handler ────────────────────────────────────────────────────
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process incoming group messages and parse work updates."""
    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()
    match = UPDATE_PATTERN.match(text)

    if not match:
        # Silently ignore messages that don't match the format
        return

    # ── Parse the message ──
    emp_id = match.group(1).strip().upper()
    work_update = match.group(2).strip()

    # Timezone-aware datetime
    tz = pytz.timezone(config.TIMEZONE)
    now = datetime.now(tz)

    # Build data dict
    user = update.message.from_user
    username = user.username if user.username else user.first_name or "Unknown"
    
    # Check if ID exists in records
    staff_info = config.STAFF_RECORDS.get(emp_id)
    if staff_info:
        emp_name = staff_info['name']
        department = staff_info['dept']
    else:
        # If ID not registered, we can't get department automatically
        # For simplicity, we'll mark it as Unknown or ignore it
        # But to be safe, let's allow "ID - DEPT - WORK" by checking if work_update contains a dash
        if " - " in work_update:
            sub_parts = work_update.split(" - ", 1)
            department = sub_parts[0].strip().upper()
            work_update = sub_parts[1].strip()
            emp_name = user.first_name or "Unknown"
        else:
            department = "UNKNOWN"
            emp_name = user.first_name or "Unknown"

    group_name = ""
    if update.message.chat.title:
        group_name = update.message.chat.title
    elif update.message.chat.type == "private":
        group_name = "Private Chat"

    data = {
        "emp_id": emp_id,
        "department": department,
        "emp_name": emp_name,
        "username": username,
        "date": now.strftime("%d-%m-%Y"),
        "day": now.strftime("%A"),
        "time": now.strftime("%I:%M %p"),
        "work_update": work_update,
        "group_name": group_name,
    }

    print(f"\n{'='*50}")
    print(f"📥 New Update Received!")
    print(f"   👤 {emp_id} | {department} | {emp_name}")
    print(f"   📝 {work_update[:80]}...")
    print(f"{'='*50}")

    # ── Save to Excel ──
    excel_saved = save_to_excel(data)

    # ── Save to Google Sheets ──
    sheets_saved = save_to_google_sheets(data)

    # ── Build confirmation message ──
    saved_to = []
    if excel_saved:
        saved_to.append("📊 Excel")
    if sheets_saved:
        saved_to.append("📋 Google Sheets")

    saved_str = " • ".join(saved_to) if saved_to else "⚠️ No storage saved"

    confirmation = f"Thank you, *{data['emp_name']}*! ✅"

    # ── Send group confirmation ──
    try:
        await update.message.reply_text(confirmation, parse_mode="Markdown")
        print("💬 Group confirmation sent")
    except Exception as e:
        print(f"⚠️ Failed to send group confirmation: {e}")

    # ── Send personal notifications ──
    await send_personal_notification(context.bot, config.OWNER_CHAT_ID, data, "Owner")
    await send_personal_notification(context.bot, config.HR_CHAT_ID, data, "HR")

    print("✅ Update processing complete!\n")


# ─── Bot Startup ─────────────────────────────────────────────────────────────
def main():
    """Start the bot."""
    print("\n" + "=" * 55)
    print("  🤖 Employee Work Update Bot")
    print("  📋 Format: EMP_ID - DEPT - Work description")
    print("=" * 55)

    # Validate config
    if config.BOT_TOKEN == "YOUR_BOT_TOKEN_HERE" or not config.BOT_TOKEN:
        print("❌ ERROR: Set your BOT_TOKEN in config.py or as env variable!")
        return

    print(f"  📊 Excel file: {config.EXCEL_FILE}")
    print(f"  📋 Google Sheets: {'Configured' if config.GOOGLE_SHEET_ID else 'Disabled'}")
    print(f"  👤 Owner notifications: {'ON' if config.OWNER_CHAT_ID else 'OFF'}")
    print(f"  👩‍💼 HR notifications: {'ON' if config.HR_CHAT_ID else 'OFF'}")
    print(f"  🌍 Timezone: {config.TIMEZONE}")
    print("=" * 55)
    print("  🟢 Bot is running... Press Ctrl+C to stop\n")

    # Build and run the application (v21 API)
    app = ApplicationBuilder().token(config.BOT_TOKEN).build()

    # Add command handlers
    app.add_handler(CommandHandler("staff", staff_command))
    app.add_handler(CommandHandler("addstaff", addstaff_command))

    # Handle all text messages (groups + private)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start polling
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
