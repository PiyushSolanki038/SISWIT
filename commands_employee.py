"""
Employee-facing commands for the Work Update Bot.
Commands: /mystatus, /myprofile, /edit, /leave
"""

import logging
from datetime import datetime, timedelta

import pytz
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

import config

logger = logging.getLogger(__name__)


def _find_emp_id_by_telegram(user_id: str) -> str | None:
    """Find an employee ID by matching Telegram user ID from daily_log entries."""
    # Check bot_data for user_id -> emp_id mapping
    return None  # Fallback: use /mystatus EMP_ID


async def mystatus_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show the employee's own submission status for this week (sent to DM)."""
    if not context.args:
        await update.message.reply_text("❗ *Usage:* `/mystatus EMP_ID`", parse_mode="Markdown")
        return

    emp_id = context.args[0].upper()

    if emp_id not in config.STAFF_RECORDS:
        await update.message.reply_text(f"❌ Employee `{emp_id}` is not registered.", parse_mode="Markdown")
        return

    staff_info = config.STAFF_RECORDS[emp_id]
    tz = pytz.timezone(config.TIMEZONE)
    now = datetime.now(tz)

    if "daily_log" not in context.bot_data:
        context.bot_data["daily_log"] = config.load_daily_log()

    # Check last 7 days
    days_status = []
    submitted_count = 0
    for i in range(6, -1, -1):
        day = now - timedelta(days=i)
        day_str = day.strftime("%Y-%m-%d")
        day_name = day.strftime("%a %d %b")
        day_log = context.bot_data.get("daily_log", {}).get(day_str, {})

        if emp_id in day_log:
            days_status.append(f"✅ {day_name} — Submitted")
            submitted_count += 1
        else:
            # Check if it's a weekend
            if day.weekday() >= 5:  # Sat/Sun
                days_status.append(f"🔵 {day_name} — Weekend")
            else:
                days_status.append(f"❌ {day_name} — Not Submitted")

    message = (
        f"📊 *Weekly Status — {staff_info['name']}*\n"
        f"🆔 `{emp_id}` | 🏢 {staff_info['dept']}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
    )
    message += "\n".join(days_status)
    message += f"\n\n📈 *This Week:* {submitted_count}/7 days submitted"

    # Send to DM
    try:
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text=message,
            parse_mode="Markdown",
        )
        if update.message.chat.type != "private":
            await update.message.reply_text("📩 Status sent to your DM!", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(
            f"⚠️ Couldn't send DM. Please start a private chat with the bot first.\n\n{message}",
            parse_mode="Markdown",
        )

    logger.info(f"Status checked for {emp_id}")


async def myprofile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show the employee's profile (sent to DM)."""
    if not context.args:
        await update.message.reply_text("❗ *Usage:* `/myprofile EMP_ID`", parse_mode="Markdown")
        return

    emp_id = context.args[0].upper()

    if emp_id not in config.STAFF_RECORDS:
        await update.message.reply_text(f"❌ Employee `{emp_id}` is not registered.", parse_mode="Markdown")
        return

    staff_info = config.STAFF_RECORDS[emp_id]

    # Count total submissions
    daily_log = config.load_daily_log()
    total_submissions = 0
    for date_str, log in daily_log.items():
        if emp_id in log:
            total_submissions += 1

    # Count leaves
    leave_log = config.load_leave_log()
    total_leaves = 0
    for date_str, leaves in leave_log.items():
        if emp_id in leaves:
            total_leaves += 1

    message = (
        f"👤 *Employee Profile*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 *ID:* `{emp_id}`\n"
        f"👤 *Name:* {staff_info['name']}\n"
        f"🏢 *Department:* {staff_info['dept']}\n"
        f"📊 *Total Submissions:* {total_submissions}\n"
        f"🏖️ *Total Leaves:* {total_leaves}\n"
        f"⏰ *Deadline:* {config.get_deadline()}\n"
    )

    try:
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text=message,
            parse_mode="Markdown",
        )
        if update.message.chat.type != "private":
            await update.message.reply_text("📩 Profile sent to your DM!", parse_mode="Markdown")
    except Exception:
        await update.message.reply_text(message, parse_mode="Markdown")

    logger.info(f"Profile checked for {emp_id}")


async def edit_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Request to edit the last work update (sends approval to Owner & HR)."""
    if len(context.args) < 2:
        await update.message.reply_text("❗ *Usage:* `/edit EMP_ID New work description`", parse_mode="Markdown")
        return

    emp_id = context.args[0].upper()
    new_text = " ".join(context.args[1:])
    requester = update.effective_user
    requester_name = requester.first_name or "Unknown"

    if emp_id not in config.STAFF_RECORDS:
        await update.message.reply_text(f"❌ Employee `{emp_id}` is not registered.", parse_mode="Markdown")
        return

    staff_name = config.STAFF_RECORDS[emp_id]["name"]
    tz = pytz.timezone(config.TIMEZONE)
    now = datetime.now(tz)
    group_name = update.message.chat.title or "Private Chat"
    chat_id = str(update.message.chat.id)

    approval_msg = (
        f"✏️ *Edit Request*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 *Requested by:* {requester_name}\n"
        f"🆔 *Employee:* {staff_name} (`{emp_id}`)\n"
        f"📅 *Date:* {now.strftime('%d %b %Y')}\n"
        f"📝 *New Update:* {new_text}\n"
        f"📍 *Group:* {group_name}\n\n"
        f"Do you approve this edit?"
    )

    # Store the new text temporarily
    if "pending_edits" not in context.bot_data:
        context.bot_data["pending_edits"] = {}
    context.bot_data["pending_edits"][emp_id] = {
        "new_text": new_text,
        "date": now.strftime("%d-%m-%Y"),
    }

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Approve", callback_data=f"edit_approve:{emp_id}:{chat_id}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"edit_reject:{emp_id}:{chat_id}"),
        ]
    ])

    for admin_id in [config.OWNER_CHAT_ID, config.HR_CHAT_ID]:
        if admin_id:
            try:
                await context.bot.send_message(
                    chat_id=int(admin_id), text=approval_msg,
                    parse_mode="Markdown", reply_markup=keyboard,
                )
            except Exception as e:
                logger.warning(f"Failed to send edit request to {admin_id}: {e}")

    await update.message.reply_text(
        f"📨 *Edit Request Sent!*\nYour edit request for `{emp_id}` has been sent to Owner & HR for approval.",
        parse_mode="Markdown",
    )
    logger.info(f"Edit request for {emp_id} by {requester_name}")


async def leave_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Request a leave day (sends approval to Owner & HR).
    Simple format: /leave EMP_ID Reason (defaults to today)
    With date:     /leave EMP_ID tomorrow Reason
                   /leave EMP_ID 05-03-2026 Reason
    """
    if len(context.args) < 2:
        await update.message.reply_text(
            "❗ *Usage:* `/leave EMP_ID Reason`\n\n"
            "📌 *Examples:*\n"
            "• `/leave DEV01 Feeling sick` ← today\n"
            "• `/leave DEV01 tomorrow Doctor appointment`\n"
            "• `/leave DEV01 05-03-2026 Family function`",
            parse_mode="Markdown",
        )
        return

    emp_id = context.args[0].upper()
    requester = update.effective_user
    requester_name = requester.first_name or "Unknown"

    if emp_id not in config.STAFF_RECORDS:
        await update.message.reply_text(f"❌ Employee `{emp_id}` is not registered.", parse_mode="Markdown")
        return

    # Smart date parsing
    tz = pytz.timezone(config.TIMEZONE)
    now = datetime.now(tz)
    second_arg = context.args[1].lower() if len(context.args) > 1 else ""

    if second_arg == "today":
        leave_date = now.strftime("%d-%m-%Y")
        reason = " ".join(context.args[2:]) if len(context.args) > 2 else "Personal"
    elif second_arg == "tomorrow":
        leave_date = (now + timedelta(days=1)).strftime("%d-%m-%Y")
        reason = " ".join(context.args[2:]) if len(context.args) > 2 else "Personal"
    else:
        # Try to parse as date DD-MM-YYYY
        try:
            datetime.strptime(second_arg, "%d-%m-%Y")
            leave_date = second_arg
            reason = " ".join(context.args[2:]) if len(context.args) > 2 else "Personal"
        except ValueError:
            # Not a date — treat everything after EMP_ID as reason, default to today
            leave_date = now.strftime("%d-%m-%Y")
            reason = " ".join(context.args[1:])

    staff_name = config.STAFF_RECORDS[emp_id]["name"]
    dept = config.STAFF_RECORDS[emp_id]["dept"]
    group_name = update.message.chat.title or "Private Chat"
    chat_id = str(update.message.chat.id)
    display_date = datetime.strptime(leave_date, "%d-%m-%Y").strftime("%d %b %Y")

    # Store pending leave
    if "pending_leaves" not in context.bot_data:
        context.bot_data["pending_leaves"] = {}
    context.bot_data["pending_leaves"][f"{emp_id}:{leave_date}"] = {
        "emp_id": emp_id, "name": staff_name, "dept": dept,
        "date": leave_date, "reason": reason,
    }

    approval_msg = (
        f"🏖️ *Leave Request*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 *Requested by:* {requester_name}\n"
        f"🆔 *Employee:* {staff_name} (`{emp_id}`)\n"
        f"🏢 *Department:* {dept}\n"
        f"📅 *Leave Date:* {display_date}\n"
        f"📝 *Reason:* {reason}\n"
        f"📍 *Group:* {group_name}\n\n"
        f"Do you approve this leave?"
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Approve", callback_data=f"leave_approve:{emp_id}:{leave_date}:{chat_id}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"leave_reject:{emp_id}:{leave_date}:{chat_id}"),
        ]
    ])

    for admin_id in [config.OWNER_CHAT_ID, config.HR_CHAT_ID]:
        if admin_id:
            try:
                await context.bot.send_message(
                    chat_id=int(admin_id), text=approval_msg,
                    parse_mode="Markdown", reply_markup=keyboard,
                )
            except Exception as e:
                logger.warning(f"Failed to send leave request to {admin_id}: {e}")

    await update.message.reply_text(
        f"📨 *Leave Request Sent!*\nLeave for `{emp_id}` on *{display_date}* sent to Owner & HR for approval.",
        parse_mode="Markdown",
    )
    logger.info(f"Leave request for {emp_id} on {leave_date} by {requester_name}")
