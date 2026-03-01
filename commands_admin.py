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
    return config.is_admin(user_id)


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
            else:
                row += " ❌ "
        row += f" ({submitted}/7)"
        msg += row + "\n"

    msg += "\n✅=Submitted  ❌=Absent  🏖=Leave"

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

    # Count all days this month (all days are working — no weekends)
    first_day = now.replace(day=1)
    working_days = 0
    current = first_day
    while current <= now:
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
    if user_id != str(config.OWNER_CHAT_ID) and not config.is_owner(user_id):
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


# ─── Private Chat Commands (Owner & HR) ──────────────────────────────────────

async def announce_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a styled announcement to the group chat (from private chat)."""
    user_id = str(update.effective_user.id)
    if not _is_admin(user_id):
        await update.message.reply_text("🚫 *Permission Denied*", parse_mode="Markdown")
        return

    if not context.args:
        await update.message.reply_text(
            "❗ *Usage:* `/announce Your announcement message here`",
            parse_mode="Markdown",
        )
        return

    group_id = config.GROUP_CHAT_ID
    if not group_id:
        await update.message.reply_text(
            "❌ Group chat ID not set. Send any message in the group first so the bot can detect it, "
            "or set `GROUP_CHAT_ID` in your environment.",
            parse_mode="Markdown",
        )
        return

    text = " ".join(context.args)
    admin_name = update.effective_user.first_name or "Admin"
    role = "👑 Owner" if config.is_owner(user_id) else "👩‍💼 HR"

    announcement = (
        f"📢 *ANNOUNCEMENT*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{text}\n\n"
        f"— _{role}: {admin_name}_\n"
        f"📅 _{datetime.now(pytz.timezone(config.TIMEZONE)).strftime('%d %b %Y, %I:%M %p')}_"
    )

    try:
        await context.bot.send_message(
            chat_id=int(group_id), text=announcement, parse_mode="Markdown",
        )
        await update.message.reply_text("✅ Announcement sent to the group!", parse_mode="Markdown")
        logger.info(f"Announcement by {admin_name}: {text[:50]}")
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to send: {e}", parse_mode="Markdown")
        logger.error(f"Announce failed: {e}")


async def dm_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a private message to a specific employee."""
    user_id = str(update.effective_user.id)
    if not _is_admin(user_id):
        await update.message.reply_text("🚫 *Permission Denied*", parse_mode="Markdown")
        return

    if len(context.args) < 2:
        await update.message.reply_text(
            "❗ *Usage:* `/dm EMP_ID Your message here`\n\n"
            "Example: `/dm DEV01 Please submit your update ASAP`",
            parse_mode="Markdown",
        )
        return

    emp_id = context.args[0].upper()
    message_text = " ".join(context.args[1:])

    if emp_id not in config.STAFF_RECORDS:
        await update.message.reply_text(f"❌ `{emp_id}` is not registered.", parse_mode="Markdown")
        return

    staff_info = config.STAFF_RECORDS[emp_id]
    staff_name = staff_info["name"]
    admin_name = update.effective_user.first_name or "Admin"
    role = "👑 Owner" if config.is_owner(user_id) else "👩‍💼 HR"

    # We need the employee's Telegram chat ID — check if stored
    tg_id = staff_info.get("telegram_id", "")

    if not tg_id:
        await update.message.reply_text(
            f"❌ No Telegram ID stored for `{emp_id}` ({staff_name}).\n\n"
            f"_The employee needs to message the bot first, or use `/announce` to reach the group._",
            parse_mode="Markdown",
        )
        return

    dm_msg = (
        f"📩 *Message from {role}*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{message_text}\n\n"
        f"— _{admin_name}_"
    )

    try:
        await context.bot.send_message(
            chat_id=int(tg_id), text=dm_msg, parse_mode="Markdown",
        )
        await update.message.reply_text(
            f"✅ Message sent to *{staff_name}* (`{emp_id}`)!", parse_mode="Markdown",
        )
        logger.info(f"DM sent to {emp_id} by {admin_name}")
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to send DM: {e}", parse_mode="Markdown")
        logger.error(f"DM failed for {emp_id}: {e}")


async def remind_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send reminders to all employees who haven't submitted today."""
    user_id = str(update.effective_user.id)
    if not _is_admin(user_id):
        await update.message.reply_text("🚫 *Permission Denied*", parse_mode="Markdown")
        return

    group_id = config.GROUP_CHAT_ID
    if not group_id:
        await update.message.reply_text(
            "❌ Group chat ID not set. Send any message in the group first.",
            parse_mode="Markdown",
        )
        return

    tz = pytz.timezone(config.TIMEZONE)
    now = datetime.now(tz)
    today_str = now.strftime("%Y-%m-%d")

    if "daily_log" not in context.bot_data:
        context.bot_data["daily_log"] = config.load_daily_log()

    today_log = context.bot_data.get("daily_log", {}).get(today_str, {})
    leave_log = config.load_leave_log()
    today_leaves = leave_log.get(today_str, {})

    pending = []
    for emp_id, info in config.STAFF_RECORDS.items():
        if emp_id not in today_log and emp_id not in today_leaves:
            pending.append(f"• `{emp_id}` — {info['name']}")

    if not pending:
        await update.message.reply_text(
            "✅ *All employees have submitted today!* No reminders needed.",
            parse_mode="Markdown",
        )
        return

    deadline = config.get_deadline()
    reminder_msg = (
        f"⏰ *REMINDER: Submit Your Work Update!*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📅 *Date:* {now.strftime('%d %b %Y')}\n"
        f"🕐 *Deadline:* {deadline}\n\n"
        f"The following employees have *NOT submitted* yet:\n\n"
        + "\n".join(pending) +
        f"\n\n📝 Please send your update now!\n"
        f"_Format: `YOUR_ID Your work description`_"
    )

    try:
        await context.bot.send_message(
            chat_id=int(group_id), text=reminder_msg, parse_mode="Markdown",
        )
        await update.message.reply_text(
            f"✅ Reminder sent to group! ({len(pending)} employees pending)",
            parse_mode="Markdown",
        )
        logger.info(f"Reminder sent for {len(pending)} employees")
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to send reminder: {e}", parse_mode="Markdown")
        logger.error(f"Remind failed: {e}")


async def warning_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send an official warning to an employee's DM."""
    user_id = str(update.effective_user.id)
    if not _is_admin(user_id):
        await update.message.reply_text("🚫 *Permission Denied*", parse_mode="Markdown")
        return

    if len(context.args) < 2:
        await update.message.reply_text(
            "❗ *Usage:* `/warning EMP_ID Reason for warning`\n\n"
            "Example: `/warning DEV01 Repeated late submissions this week`",
            parse_mode="Markdown",
        )
        return

    emp_id = context.args[0].upper()
    reason = " ".join(context.args[1:])

    if emp_id not in config.STAFF_RECORDS:
        await update.message.reply_text(f"❌ `{emp_id}` is not registered.", parse_mode="Markdown")
        return

    staff_info = config.STAFF_RECORDS[emp_id]
    staff_name = staff_info["name"]
    admin_name = update.effective_user.first_name or "Admin"
    role = "Owner" if config.is_owner(user_id) else "HR"
    tz = pytz.timezone(config.TIMEZONE)
    now = datetime.now(tz)

    tg_id = staff_info.get("telegram_id", "")

    warning_msg = (
        f"⚠️ *OFFICIAL WARNING*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👤 *Employee:* {staff_name} (`{emp_id}`)\n"
        f"📅 *Date:* {now.strftime('%d %b %Y')}\n\n"
        f"📋 *Reason:*\n_{reason}_\n\n"
        f"⚡ Please take this as a formal notice and ensure compliance going forward.\n\n"
        f"— *{role}: {admin_name}*"
    )

    sent_to_employee = False
    if tg_id:
        try:
            await context.bot.send_message(
                chat_id=int(tg_id), text=warning_msg, parse_mode="Markdown",
            )
            sent_to_employee = True
        except Exception as e:
            logger.warning(f"Warning DM failed for {emp_id}: {e}")

    # Also notify the other admin
    for admin_id in config.OWNER_CHAT_IDS + ([config.HR_CHAT_ID] if config.HR_CHAT_ID else []):
        if admin_id and str(admin_id) != user_id:
            try:
                await context.bot.send_message(
                    chat_id=int(admin_id),
                    text=f"📋 *Warning Issued*\n\n{admin_name} ({role}) warned `{emp_id}` ({staff_name})\n\n_Reason: {reason}_",
                    parse_mode="Markdown",
                )
            except Exception:
                pass

    if sent_to_employee:
        await update.message.reply_text(
            f"✅ *Warning sent* to {staff_name} (`{emp_id}`) via DM!\n\n"
            f"📋 Reason: _{reason}_",
            parse_mode="Markdown",
        )
    else:
        await update.message.reply_text(
            f"⚠️ Warning recorded but could *not DM* {staff_name} (`{emp_id}`).\n"
            f"_Employee hasn't started the bot yet._\n\n"
            f"📋 Reason: _{reason}_",
            parse_mode="Markdown",
        )

    logger.info(f"Warning issued to {emp_id} by {admin_name}: {reason[:50]}")
