"""
Employee Daily Work Update Telegram Bot
========================================
Parses employee messages in format: EMP_ID Work description
Saves to Excel (local) + Google Sheets, sends notifications to Owner & HR.

Uses python-telegram-bot v21 API (ApplicationBuilder).
"""

import logging
from datetime import datetime, timedelta

import pytz
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters,
)

import config
from excel_handler import save_to_excel, save_to_google_sheets, update_row_in_google_sheets
from commands_employee import mystatus_command, myprofile_command, edit_command, leave_command
from commands_admin import (
    absent_command, late_command, history_command, weeklyreport_command,
    monthly_command, export_command, broadcast_command, deadline_command, sethr_command,
)
from callbacks import allow_callback, edit_callback, leave_callback

# ─── Logging ─────────────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


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
        await bot.send_message(chat_id=int(chat_id), text=message, parse_mode="Markdown")
        logger.info(f"Notification sent to {label}")
    except Exception as e:
        logger.warning(f"Failed to notify {label}: {e}")


# ─── Basic Commands ─────────────────────────────────────────────────────────
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Welcome message."""
    msg = (
        "👋 *Welcome to the Employee Work Update Bot!*\n\n"
        "📝 *Submit your daily update:*\n"
        "`YOUR_ID Your work description`\n\n"
        "📌 *Example:*\n"
        "`DEV01 Fixed the login page and tested it`\n\n"
        "💡 Use /help to see all commands."
    )
    await update.message.reply_text(msg, parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display all commands based on role."""
    user_id = str(update.effective_user.id)
    is_admin = user_id in [str(config.OWNER_CHAT_ID), str(config.HR_CHAT_ID)]

    msg = (
        "📖 *Bot Commands*\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📝 *Submit Update:* `YOUR_ID Work description`\n\n"
        "🔧 *Everyone:*\n"
        "• /start — Welcome message\n"
        "• /help — This menu\n"
        "• /allow `ID` — Request re-submission\n"
        "• /mystatus `ID` — Your weekly status (DM)\n"
        "• /myprofile `ID` — Your profile info (DM)\n"
        "• /edit `ID New text` — Request edit (needs approval)\n"
        "• /leave `ID DD-MM-YYYY Reason` — Request leave\n"
    )

    if is_admin:
        msg += (
            "\n👑 *Admin:*\n"
            "• /staff — List all employees\n"
            "• /addstaff `ID - Name - Dept`\n"
            "• /removestaff `ID`\n"
            "• /report — Today's full status\n"
            "• /absent — Quick absent list\n"
            "• /late — Late submissions\n"
            "• /history `ID` — Employee 7-day history (DM)\n"
            "• /weeklyreport — Weekly grid (DM)\n"
            "• /monthly — Monthly attendance (DM)\n"
            "• /export — Get Excel file / Sheet link (DM)\n"
            "• /broadcast `Text` — Send announcement\n"
            "• /deadline `HH:MM` — Set submission deadline\n"
        )
        if user_id == str(config.OWNER_CHAT_ID):
            msg += "• /sethr `CHAT_ID` — Change HR\n"

    await update.message.reply_text(msg, parse_mode="Markdown")


async def staff_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display registered staff list (Owner/HR only)."""
    user_id = str(update.effective_user.id)
    if user_id not in [str(config.OWNER_CHAT_ID), str(config.HR_CHAT_ID)]:
        await update.message.reply_text("🚫 *Permission Denied*", parse_mode="Markdown")
        return

    if not config.STAFF_RECORDS:
        await update.message.reply_text("📋 No staff records configured.")
        return

    msg = "👥 *Registered Staff*\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
    for emp_id, info in config.STAFF_RECORDS.items():
        msg += f"• `{emp_id}` — {info['name']} ({info['dept']})\n"
    msg += f"\n📊 Total: {len(config.STAFF_RECORDS)} employees"

    await update.message.reply_text(msg, parse_mode="Markdown")


async def addstaff_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add a new staff member (Owner/HR only)."""
    user_id = str(update.effective_user.id)
    if user_id not in [str(config.OWNER_CHAT_ID), str(config.HR_CHAT_ID)]:
        await update.message.reply_text("🚫 *Permission Denied*", parse_mode="Markdown")
        return

    args = " ".join(context.args)
    if not args:
        await update.message.reply_text("❗ *Usage:* `/addstaff ID - Name - Department`", parse_mode="Markdown")
        return

    try:
        parts = [p.strip() for p in args.split("-")]
        if len(parts) != 3:
            raise ValueError
        emp_id, name, dept = parts

        if config.save_staff_record(emp_id, name, dept):
            config.STAFF_RECORDS = config.load_staff_records()
            await update.message.reply_text(
                f"✅ *Staff Added!*\n🆔 `{emp_id.upper()}` | 👤 {name} | 🏢 {dept.upper()}",
                parse_mode="Markdown",
            )
            logger.info(f"Added staff: {emp_id}")
        else:
            await update.message.reply_text("❌ Failed to save.", parse_mode="Markdown")
    except Exception:
        await update.message.reply_text("❗ Use `/addstaff ID - Name - Department`", parse_mode="Markdown")


async def removestaff_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove a staff member (Owner/HR only)."""
    user_id = str(update.effective_user.id)
    if user_id not in [str(config.OWNER_CHAT_ID), str(config.HR_CHAT_ID)]:
        await update.message.reply_text("🚫 *Permission Denied*", parse_mode="Markdown")
        return

    if not context.args:
        await update.message.reply_text("❗ *Usage:* `/removestaff EMP_ID`", parse_mode="Markdown")
        return

    emp_id = context.args[0].upper()
    if emp_id not in config.STAFF_RECORDS:
        await update.message.reply_text(f"❌ `{emp_id}` not found.", parse_mode="Markdown")
        return

    name = config.STAFF_RECORDS[emp_id]["name"]
    if config.remove_staff_record(emp_id):
        config.STAFF_RECORDS = config.load_staff_records()
        await update.message.reply_text(f"✅ *Removed:* `{emp_id}` ({name})", parse_mode="Markdown")
        logger.info(f"Removed staff: {emp_id}")
    else:
        await update.message.reply_text("❌ Failed to remove.", parse_mode="Markdown")


async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Today's full submission status (Owner/HR only)."""
    user_id = str(update.effective_user.id)
    if user_id not in [str(config.OWNER_CHAT_ID), str(config.HR_CHAT_ID)]:
        await update.message.reply_text("🚫 *Permission Denied*", parse_mode="Markdown")
        return

    tz = pytz.timezone(config.TIMEZONE)
    now = datetime.now(tz)
    today_str = now.strftime("%Y-%m-%d")

    if "daily_log" not in context.bot_data:
        context.bot_data["daily_log"] = config.load_daily_log()

    today_log = context.bot_data.get("daily_log", {}).get(today_str, {})
    leave_log = config.load_leave_log()
    today_leaves = leave_log.get(today_str, {})

    submitted, not_submitted, on_leave = [], [], []

    for emp_id, info in config.STAFF_RECORDS.items():
        if emp_id in today_log:
            submitted.append(f"✅ `{emp_id}` — {info['name']}")
        elif emp_id in today_leaves:
            on_leave.append(f"🏖️ `{emp_id}` — {info['name']}")
        else:
            not_submitted.append(f"❌ `{emp_id}` — {info['name']}")

    total = len(config.STAFF_RECORDS)
    done = len(submitted)

    msg = f"📊 *Daily Report — {now.strftime('%d %b %Y')}*\n━━━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"📈 *Progress:* {done}/{total} submitted\n\n"

    if submitted:
        msg += "*✅ Submitted:*\n" + "\n".join(submitted) + "\n\n"
    if on_leave:
        msg += "*🏖️ On Leave:*\n" + "\n".join(on_leave) + "\n\n"
    if not_submitted:
        msg += "*❌ Not Submitted:*\n" + "\n".join(not_submitted)

    await update.message.reply_text(msg, parse_mode="Markdown")


async def allow_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Request re-submission (sends approval to Owner & HR). Max 1 per day."""
    if not context.args:
        await update.message.reply_text("❗ *Usage:* `/allow EMP_ID`", parse_mode="Markdown")
        return

    emp_id = context.args[0].upper()
    requester = update.effective_user
    requester_name = requester.first_name or "Unknown"

    if emp_id not in config.STAFF_RECORDS:
        await update.message.reply_text(f"❌ `{emp_id}` is not registered.", parse_mode="Markdown")
        return

    tz = pytz.timezone(config.TIMEZONE)
    now = datetime.now(tz)
    today_str = now.strftime("%Y-%m-%d")

    if "daily_log" not in context.bot_data:
        context.bot_data["daily_log"] = config.load_daily_log()

    today_log = context.bot_data.get("daily_log", {}).get(today_str, {})
    if emp_id not in today_log:
        await update.message.reply_text(f"ℹ️ `{emp_id}` has not submitted today — no need to allow.", parse_mode="Markdown")
        return

    staff_name = config.STAFF_RECORDS[emp_id]["name"]
    group_name = update.message.chat.title or "Private Chat"
    chat_id = str(update.message.chat.id)

    # ─── Allow Limit: max 1 per day per employee ─────────────────────────
    if "allow_usage" not in context.bot_data:
        context.bot_data["allow_usage"] = {}
    if today_str not in context.bot_data["allow_usage"]:
        context.bot_data["allow_usage"][today_str] = {}

    usage_count = context.bot_data["allow_usage"][today_str].get(emp_id, 0)

    if usage_count >= 1:
        # 2nd+ attempt — send suspicious activity alert to Owner & HR
        alert_msg = (
            f"🚨 *SUSPICIOUS ACTIVITY ALERT*\n━━━━━━━━━━━━━━━━━━━━━━\n"
            f"⚠️ *Employee:* {staff_name} (`{emp_id}`)\n"
            f"📅 *Date:* {now.strftime('%d %b %Y')}\n"
            f"🔁 *Allow Attempts:* {usage_count + 1} (exceeded limit!)\n"
            f"👤 *Requested By:* {requester_name}\n\n"
            f"_This employee has already used their 1 allowed re-submission today. "
            f"Repeated requests may indicate misuse or data manipulation._"
        )

        for admin_id in [config.OWNER_CHAT_ID, config.HR_CHAT_ID]:
            if admin_id:
                try:
                    await context.bot.send_message(
                        chat_id=int(admin_id), text=alert_msg, parse_mode="Markdown",
                    )
                except Exception as e:
                    logger.warning(f"Failed to send alert to {admin_id}: {e}")

        await update.message.reply_text(
            f"🚫 *Request Denied*\n\n`{emp_id}` has already used their 1 re-submission for today. "
            f"Owner & HR have been notified.",
            parse_mode="Markdown",
        )
        logger.warning(f"SUSPICIOUS: {emp_id} attempted /allow #{usage_count + 1} on {today_str}")
        return

    # Track usage (increment AFTER approval is sent)
    context.bot_data["allow_usage"][today_str][emp_id] = usage_count + 1

    approval_msg = (
        f"🔔 *Re-submission Request*\n━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 *By:* {requester_name}\n"
        f"🆔 *Employee:* {staff_name} (`{emp_id}`)\n"
        f"📅 *Date:* {now.strftime('%d %b %Y')}\n"
        f"📍 *Group:* {group_name}\n\nApprove re-submission?"
    )

    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Approve", callback_data=f"allow_approve:{emp_id}:{requester.id}:{chat_id}"),
        InlineKeyboardButton("❌ Reject", callback_data=f"allow_reject:{emp_id}:{requester.id}:{chat_id}"),
    ]])

    for admin_id in [config.OWNER_CHAT_ID, config.HR_CHAT_ID]:
        if admin_id:
            try:
                await context.bot.send_message(
                    chat_id=int(admin_id), text=approval_msg,
                    parse_mode="Markdown", reply_markup=keyboard,
                )
            except Exception as e:
                logger.warning(f"Failed to send to {admin_id}: {e}")

    await update.message.reply_text(f"📨 Request sent to Owner & HR for `{emp_id}`.", parse_mode="Markdown")
    logger.info(f"Allow request for {emp_id} by {requester_name}")


# ─── Main Message Handler ────────────────────────────────────────────────────
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process incoming messages and parse work updates."""
    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()

    # Simple parse: first word = EMP_ID, rest = work
    parts = text.split(None, 1)
    if len(parts) < 2:
        return

    emp_id = parts[0].upper()
    work_update = parts[1].strip()

    # Only process registered IDs
    staff_info = config.STAFF_RECORDS.get(emp_id)
    if not staff_info:
        return

    emp_name = staff_info["name"]
    department = staff_info["dept"]

    tz = pytz.timezone(config.TIMEZONE)
    now = datetime.now(tz)

    user = update.message.from_user
    username = user.username if user.username else user.first_name or "Unknown"
    group_name = update.message.chat.title or ("Private Chat" if update.message.chat.type == "private" else "")

    # ─── Grace Period: 12:00 AM to 1:00 AM → count as yesterday (Late) ────
    if now.hour < 1:
        # Midnight grace period — record for previous day
        record_date = now - timedelta(days=1)
        is_late = True
        grace_note = f"⏰ _Recorded for {record_date.strftime('%d %b')} (late submission)_"
    else:
        record_date = now
        grace_note = ""
        # Normal late check against deadline
        deadline = config.get_deadline()
        try:
            dl_h, dl_m = map(int, deadline.split(":"))
            is_late = now.hour > dl_h or (now.hour == dl_h and now.minute > dl_m)
        except Exception:
            is_late = False

    data = {
        "emp_id": emp_id, "department": department, "emp_name": emp_name,
        "username": username, "date": record_date.strftime("%d-%m-%Y"),
        "day": record_date.strftime("%A"), "time": now.strftime("%I:%M %p"),
        "work_update": work_update, "group_name": group_name,
    }

    logger.info(f"Update: {emp_id} | {department} | {emp_name}")

    # Check daily log
    if "daily_log" not in context.bot_data:
        context.bot_data["daily_log"] = config.load_daily_log()

    log_date_str = record_date.strftime("%Y-%m-%d")
    if log_date_str not in context.bot_data["daily_log"]:
        context.bot_data["daily_log"][log_date_str] = {}

    # Check if this is a re-submission (/allow was used)
    is_resubmission = False
    if emp_id in context.bot_data["daily_log"][log_date_str]:
        # Check if re-submission was approved (daily_log cleared by allow_callback)
        await update.message.reply_text(
            f"❌ *Already Submitted*\n{emp_name} (`{emp_id}`) already submitted for {record_date.strftime('%d %b')}. Use `/allow {emp_id}` to request re-submission.",
            parse_mode="Markdown",
        )
        return

    # Check if employee had a previous submission today that was cleared by /allow
    allow_usage = context.bot_data.get("allow_usage", {}).get(log_date_str, {})
    if emp_id in allow_usage and allow_usage[emp_id] > 0:
        is_resubmission = True

    # Save to Excel & Google Sheets
    save_to_excel(data)
    if is_resubmission:
        # UPDATE existing row instead of creating a new one
        await update_row_in_google_sheets(data)
    else:
        await save_to_google_sheets(data)

    if config.IS_RAILWAY:
        logger.warning("Excel on Railway is ephemeral.")

    # Confirmation
    confirm_msg = f"Thank you, *{emp_name}*! ✅"
    if is_resubmission:
        confirm_msg += "\n📝 _Your previous entry has been updated._"
    if grace_note:
        confirm_msg += f"\n{grace_note}"
    await update.message.reply_text(confirm_msg, parse_mode="Markdown")

    # Notifications
    notification_data = data.copy()
    if is_resubmission:
        notification_data["work_update"] = f"[RE-SUBMIT] {work_update}"
    await send_personal_notification(context.bot, config.OWNER_CHAT_ID, notification_data, "Owner")
    await send_personal_notification(context.bot, config.HR_CHAT_ID, notification_data, "HR")

    # Record with metadata
    context.bot_data["daily_log"][log_date_str][emp_id] = {
        "time": data["time"], "work": work_update, "late": is_late,
    }
    config.save_daily_log(context.bot_data["daily_log"])

    logger.info("Update complete")


# ─── Bot Startup ─────────────────────────────────────────────────────────────
def main():
    """Start the bot."""
    logger.info("=" * 55)
    logger.info("  Employee Work Update Bot — Starting")
    logger.info("=" * 55)

    if not config.BOT_TOKEN:
        logger.error("BOT_TOKEN not set! Add it to .env file.")
        return

    logger.info(f"  Excel: {config.EXCEL_FILE}")
    logger.info(f"  Google Sheets: {'ON' if config.GOOGLE_SHEET_ID else 'OFF'}")
    logger.info(f"  Owner: {'ON' if config.OWNER_CHAT_ID else 'OFF'}")
    logger.info(f"  HR: {'ON' if config.HR_CHAT_ID else 'OFF'}")
    logger.info(f"  Deadline: {config.get_deadline()}")
    logger.info(f"  Staff: {len(config.STAFF_RECORDS)} loaded")
    logger.info("=" * 55)

    app = ApplicationBuilder().token(config.BOT_TOKEN).build()

    # Basic commands
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("staff", staff_command))
    app.add_handler(CommandHandler("addstaff", addstaff_command))
    app.add_handler(CommandHandler("removestaff", removestaff_command))
    app.add_handler(CommandHandler("allow", allow_command))
    app.add_handler(CommandHandler("report", report_command))

    # Employee commands
    app.add_handler(CommandHandler("mystatus", mystatus_command))
    app.add_handler(CommandHandler("myprofile", myprofile_command))
    app.add_handler(CommandHandler("edit", edit_command))
    app.add_handler(CommandHandler("leave", leave_command))

    # Admin commands
    app.add_handler(CommandHandler("absent", absent_command))
    app.add_handler(CommandHandler("late", late_command))
    app.add_handler(CommandHandler("history", history_command))
    app.add_handler(CommandHandler("weeklyreport", weeklyreport_command))
    app.add_handler(CommandHandler("monthly", monthly_command))
    app.add_handler(CommandHandler("export", export_command))
    app.add_handler(CommandHandler("broadcast", broadcast_command))
    app.add_handler(CommandHandler("deadline", deadline_command))
    app.add_handler(CommandHandler("sethr", sethr_command))

    # Callback handlers for buttons
    app.add_handler(CallbackQueryHandler(allow_callback, pattern=r"^allow_"))
    app.add_handler(CallbackQueryHandler(edit_callback, pattern=r"^edit_"))
    app.add_handler(CallbackQueryHandler(leave_callback, pattern=r"^leave_"))

    # Message handler (must be last)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
