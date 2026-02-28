"""
Admin commands for the Work Update Bot (Owner & HR only).
Commands: /absent, /late, /history, /weeklyreport, /monthly, /export, /broadcast, /deadline, /sethr
"""

import os
import logging
from datetime import datetime, timedelta

import pytz
from telegram import Update
from telegram.ext import ContextTypes

import config

logger = logging.getLogger(__name__)


def _is_admin(user_id: str) -> bool:
    """Check if the user is Owner or HR."""
    return user_id in [str(config.OWNER_CHAT_ID), str(config.HR_CHAT_ID)]


async def absent_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Quick list of who hasn't submitted today (group reply)."""
    user_id = str(update.effective_user.id)
    if not _is_admin(user_id):
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

    absent = []
    for emp_id, info in config.STAFF_RECORDS.items():
        if emp_id not in today_log and emp_id not in today_leaves:
            absent.append(f"❌ `{emp_id}` — {info['name']} ({info['dept']})")

    if absent:
        msg = f"📋 *Absent Today — {now.strftime('%d %b %Y')}*\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
        msg += "\n".join(absent)
        msg += f"\n\n📊 {len(absent)} employee(s) not submitted"
    else:
        msg = "✅ *All employees have submitted today!*"

    await update.message.reply_text(msg, parse_mode="Markdown")
    logger.info(f"Absent list generated: {len(absent)} missing")


async def late_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show employees who submitted after the deadline (group reply)."""
    user_id = str(update.effective_user.id)
    if not _is_admin(user_id):
        await update.message.reply_text("🚫 *Permission Denied*", parse_mode="Markdown")
        return

    tz = pytz.timezone(config.TIMEZONE)
    now = datetime.now(tz)
    today_str = now.strftime("%Y-%m-%d")
    deadline = config.get_deadline()

    if "daily_log" not in context.bot_data:
        context.bot_data["daily_log"] = config.load_daily_log()

    today_log = context.bot_data.get("daily_log", {}).get(today_str, {})

    try:
        deadline_h, deadline_m = map(int, deadline.split(":"))
    except Exception:
        deadline_h, deadline_m = 11, 0

    late_list = []
    on_time_list = []

    for emp_id, entry in today_log.items():
        if emp_id not in config.STAFF_RECORDS:
            continue
        info = config.STAFF_RECORDS[emp_id]
        sub_time = entry.get("time", "") if isinstance(entry, dict) else ""
        if sub_time:
            try:
                t = datetime.strptime(sub_time, "%I:%M %p")
                if t.hour > deadline_h or (t.hour == deadline_h and t.minute > deadline_m):
                    late_list.append(f"⏰ `{emp_id}` — {info['name']} (at {sub_time})")
                else:
                    on_time_list.append(f"✅ `{emp_id}` — {info['name']} (at {sub_time})")
            except Exception:
                on_time_list.append(f"✅ `{emp_id}` — {info['name']}")
        else:
            on_time_list.append(f"✅ `{emp_id}` — {info['name']}")

    msg = f"⏰ *Late Report — {now.strftime('%d %b %Y')}*\n"
    msg += f"📌 Deadline: {deadline}\n━━━━━━━━━━━━━━━━━━━━━━\n\n"

    if late_list:
        msg += "*❌ Late Submissions:*\n" + "\n".join(late_list) + "\n\n"
    if on_time_list:
        msg += "*✅ On Time:*\n" + "\n".join(on_time_list)
    if not late_list and not on_time_list:
        msg += "No submissions yet today."

    await update.message.reply_text(msg, parse_mode="Markdown")
    logger.info(f"Late report generated: {len(late_list)} late")


async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View last 7 days of an employee's submissions (sent to admin DM)."""
    user_id = str(update.effective_user.id)
    if not _is_admin(user_id):
        await update.message.reply_text("🚫 *Permission Denied*", parse_mode="Markdown")
        return

    if not context.args:
        await update.message.reply_text("❗ *Usage:* `/history EMP_ID`", parse_mode="Markdown")
        return

    emp_id = context.args[0].upper()
    if emp_id not in config.STAFF_RECORDS:
        await update.message.reply_text(f"❌ Employee `{emp_id}` not found.", parse_mode="Markdown")
        return

    staff_info = config.STAFF_RECORDS[emp_id]
    tz = pytz.timezone(config.TIMEZONE)
    now = datetime.now(tz)
    daily_log = config.load_daily_log()
    leave_log = config.load_leave_log()

    msg = f"📜 *History — {staff_info['name']} (`{emp_id}`)*\n"
    msg += f"🏢 {staff_info['dept']}\n━━━━━━━━━━━━━━━━━━━━━━\n\n"

    for i in range(6, -1, -1):
        day = now - timedelta(days=i)
        day_str = day.strftime("%Y-%m-%d")
        day_name = day.strftime("%a %d %b")

        day_log = daily_log.get(day_str, {})
        day_leaves = leave_log.get(day_str, {})

        if emp_id in day_log:
            entry = day_log[emp_id]
            work = entry.get("work", "Submitted") if isinstance(entry, dict) else "Submitted"
            time_str = entry.get("time", "") if isinstance(entry, dict) else ""
            msg += f"✅ {day_name} {time_str}\n   _{work[:60]}_\n"
        elif emp_id in day_leaves:
            msg += f"🏖️ {day_name} — On Leave\n"
        elif day.weekday() >= 5:
            msg += f"🔵 {day_name} — Weekend\n"
        else:
            msg += f"❌ {day_name} — Absent\n"

    try:
        await context.bot.send_message(chat_id=update.effective_user.id, text=msg, parse_mode="Markdown")
        if update.message.chat.type != "private":
            await update.message.reply_text("📩 History sent to your DM!", parse_mode="Markdown")
    except Exception:
        await update.message.reply_text(msg, parse_mode="Markdown")

    logger.info(f"History viewed for {emp_id}")


async def weeklyreport_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Weekly summary for all employees (sent to admin DM)."""
    user_id = str(update.effective_user.id)
    if not _is_admin(user_id):
        await update.message.reply_text("🚫 *Permission Denied*", parse_mode="Markdown")
        return

    tz = pytz.timezone(config.TIMEZONE)
    now = datetime.now(tz)
    daily_log = config.load_daily_log()
    leave_log = config.load_leave_log()

    msg = f"📊 *Weekly Report*\n"
    msg += f"📅 {(now - timedelta(days=6)).strftime('%d %b')} — {now.strftime('%d %b %Y')}\n"
    msg += "━━━━━━━━━━━━━━━━━━━━━━\n\n"

    # Header row with day abbreviations
    days_header = "          "
    for i in range(6, -1, -1):
        day = now - timedelta(days=i)
        days_header += day.strftime("%a") + " "
    msg += f"`{days_header}`\n"

    for emp_id, info in config.STAFF_RECORDS.items():
        row = f"`{emp_id:6s}` "
        submitted = 0
        for i in range(6, -1, -1):
            day = now - timedelta(days=i)
            day_str = day.strftime("%Y-%m-%d")
            day_log = daily_log.get(day_str, {})
            day_leaves = leave_log.get(day_str, {})

            if emp_id in day_log:
                row += " ✅ "
                submitted += 1
            elif emp_id in day_leaves:
                row += " 🏖 "
            elif day.weekday() >= 5:
                row += " 🔵 "
            else:
                row += " ❌ "
        row += f" ({submitted}/7)"
        msg += row + "\n"

    msg += "\n✅=Submitted  ❌=Absent  🏖=Leave  🔵=Weekend"

    try:
        await context.bot.send_message(chat_id=update.effective_user.id, text=msg, parse_mode="Markdown")
        if update.message.chat.type != "private":
            await update.message.reply_text("📩 Weekly report sent to your DM!", parse_mode="Markdown")
    except Exception:
        await update.message.reply_text(msg, parse_mode="Markdown")

    logger.info("Weekly report generated")


async def monthly_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Monthly attendance summary (sent to admin DM)."""
    user_id = str(update.effective_user.id)
    if not _is_admin(user_id):
        await update.message.reply_text("🚫 *Permission Denied*", parse_mode="Markdown")
        return

    tz = pytz.timezone(config.TIMEZONE)
    now = datetime.now(tz)
    daily_log = config.load_daily_log()
    leave_log = config.load_leave_log()

    # Count working days this month (exclude weekends)
    first_day = now.replace(day=1)
    working_days = 0
    current = first_day
    while current <= now:
        if current.weekday() < 5:
            working_days += 1
        current += timedelta(days=1)

    msg = f"📊 *Monthly Report — {now.strftime('%B %Y')}*\n"
    msg += f"📅 Working days so far: {working_days}\n"
    msg += "━━━━━━━━━━━━━━━━━━━━━━\n\n"

    for emp_id, info in config.STAFF_RECORDS.items():
        submitted = 0
        late = 0
        leaves = 0

        current = first_day
        while current <= now:
            day_str = current.strftime("%Y-%m-%d")
            if emp_id in daily_log.get(day_str, {}):
                submitted += 1
                entry = daily_log[day_str][emp_id]
                if isinstance(entry, dict) and entry.get("late"):
                    late += 1
            if emp_id in leave_log.get(day_str, {}):
                leaves += 1
            current += timedelta(days=1)

        pct = round((submitted / working_days) * 100) if working_days > 0 else 0
        pct_bar = "█" * (pct // 10) + "░" * (10 - pct // 10)

        msg += f"*{info['name']}* (`{emp_id}`)\n"
        msg += f"  {pct_bar} {pct}%\n"
        msg += f"  ✅ {submitted} days | ⏰ {late} late | 🏖️ {leaves} leave\n\n"

    try:
        await context.bot.send_message(chat_id=update.effective_user.id, text=msg, parse_mode="Markdown")
        if update.message.chat.type != "private":
            await update.message.reply_text("📩 Monthly report sent to your DM!", parse_mode="Markdown")
    except Exception:
        await update.message.reply_text(msg, parse_mode="Markdown")

    logger.info("Monthly report generated")


async def export_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send the Excel file or Google Sheet link to admin DM."""
    user_id = str(update.effective_user.id)
    if not _is_admin(user_id):
        await update.message.reply_text("🚫 *Permission Denied*", parse_mode="Markdown")
        return

    sent = False

    # Send Excel file
    if os.path.exists(config.EXCEL_FILE):
        try:
            with open(config.EXCEL_FILE, "rb") as f:
                await context.bot.send_document(
                    chat_id=update.effective_user.id,
                    document=f,
                    filename=config.EXCEL_FILE,
                    caption="📊 Employee Updates — Excel File",
                )
            sent = True
        except Exception as e:
            logger.warning(f"Failed to send Excel file: {e}")

    # Send Google Sheet link
    if config.GOOGLE_SHEET_ID:
        link = f"https://docs.google.com/spreadsheets/d/{config.GOOGLE_SHEET_ID}/edit"
        try:
            await context.bot.send_message(
                chat_id=update.effective_user.id,
                text=f"📋 *Google Sheet:*\n[Open Sheet]({link})",
                parse_mode="Markdown",
            )
            sent = True
        except Exception as e:
            logger.warning(f"Failed to send Sheet link: {e}")

    if sent:
        if update.message.chat.type != "private":
            await update.message.reply_text("📩 Export sent to your DM!", parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ No data files found to export.", parse_mode="Markdown")

    logger.info("Export sent")


async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bot sends an announcement message to the group."""
    user_id = str(update.effective_user.id)
    if not _is_admin(user_id):
        await update.message.reply_text("🚫 *Permission Denied*", parse_mode="Markdown")
        return

    if not context.args:
        await update.message.reply_text("❗ *Usage:* `/broadcast Your message here`", parse_mode="Markdown")
        return

    text = " ".join(context.args)
    admin_name = update.effective_user.first_name or "Admin"

    msg = (
        f"📢 *Announcement*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{text}\n\n"
        f"— _{admin_name}_"
    )

    await update.message.reply_text(msg, parse_mode="Markdown")
    logger.info(f"Broadcast by {admin_name}: {text[:50]}")


async def deadline_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set or view the daily submission deadline."""
    user_id = str(update.effective_user.id)
    if not _is_admin(user_id):
        await update.message.reply_text("🚫 *Permission Denied*", parse_mode="Markdown")
        return

    if not context.args:
        current = config.get_deadline()
        await update.message.reply_text(f"⏰ Current deadline: *{current}*\n\nTo change: `/deadline HH:MM`", parse_mode="Markdown")
        return

    new_deadline = context.args[0]
    try:
        h, m = map(int, new_deadline.split(":"))
        if not (0 <= h <= 23 and 0 <= m <= 59):
            raise ValueError
    except Exception:
        await update.message.reply_text("❌ Invalid format. Use `HH:MM` (24h), e.g. `11:00`", parse_mode="Markdown")
        return

    config.save_setting("deadline", new_deadline)

    await update.message.reply_text(
        f"✅ *Deadline Updated!*\n\n"
        f"⏰ New deadline: *{new_deadline}*\n"
        f"Employees submitting after this time will be marked as late.",
        parse_mode="Markdown",
    )
    logger.info(f"Deadline set to {new_deadline}")


async def sethr_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Change HR Chat ID dynamically (Owner only)."""
    user_id = str(update.effective_user.id)

    # Owner only
    if user_id != str(config.OWNER_CHAT_ID):
        await update.message.reply_text("🚫 *Permission Denied:* Only the Owner can change HR.", parse_mode="Markdown")
        return

    if not context.args:
        await update.message.reply_text(
            f"👩‍💼 *Current HR Chat ID:* `{config.HR_CHAT_ID or 'Not set'}`\n\n"
            f"To change: `/sethr CHAT_ID`",
            parse_mode="Markdown",
        )
        return

    new_hr_id = context.args[0]
    config.HR_CHAT_ID = new_hr_id
    config.save_setting("hr_chat_id", new_hr_id)

    await update.message.reply_text(
        f"✅ *HR Updated!*\n\nNew HR Chat ID: `{new_hr_id}`",
        parse_mode="Markdown",
    )
    logger.info(f"HR Chat ID changed to {new_hr_id}")
