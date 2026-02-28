"""
Callback handlers for inline keyboard buttons.
Handles: allow approve/reject, edit approve/reject, leave approve/reject.
"""

import logging
from datetime import datetime

import pytz
from telegram import Update
from telegram.ext import ContextTypes

import config
from excel_handler import save_leave_to_excel, count_monthly_leaves

logger = logging.getLogger(__name__)


async def allow_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Approve/Reject for /allow re-submission requests."""
    query = update.callback_query
    await query.answer()

    admin_id = str(query.from_user.id)
    admin_name = query.from_user.first_name or "Admin"

    if admin_id not in [str(config.OWNER_CHAT_ID), str(config.HR_CHAT_ID)]:
        await query.edit_message_text("🚫 You are not authorized.")
        return

    parts = query.data.split(":")
    if len(parts) != 4:
        await query.edit_message_text("❌ Invalid request data.")
        return

    action, emp_id, requester_id, group_chat_id = parts
    staff_name = config.STAFF_RECORDS.get(emp_id, {}).get("name", emp_id)

    if action == "allow_approve":
        now = datetime.now(pytz.timezone(config.TIMEZONE))
        today_str = now.strftime("%Y-%m-%d")

        if "daily_log" not in context.bot_data:
            context.bot_data["daily_log"] = config.load_daily_log()

        if today_str in context.bot_data.get("daily_log", {}) and emp_id in context.bot_data["daily_log"][today_str]:
            del context.bot_data["daily_log"][today_str][emp_id]
            config.save_daily_log(context.bot_data["daily_log"])

        await query.edit_message_text(
            f"✅ *Approved* by {admin_name}\n\nEmployee `{emp_id}` ({staff_name}) can now re-submit today.",
            parse_mode="Markdown",
        )

        try:
            await context.bot.send_message(
                chat_id=int(group_chat_id),
                text=f"✅ *Re-submission Approved!*\n\n`{emp_id}` ({staff_name}) — approved by {admin_name}. You can submit again.",
                parse_mode="Markdown",
            )
        except Exception as e:
            logger.warning(f"Failed to notify group: {e}")

        logger.info(f"Re-submission approved for {emp_id} by {admin_name}")

    elif action == "allow_reject":
        await query.edit_message_text(
            f"❌ *Rejected* by {admin_name}\n\nRe-submission for `{emp_id}` ({staff_name}) was denied.",
            parse_mode="Markdown",
        )
        try:
            await context.bot.send_message(
                chat_id=int(group_chat_id),
                text=f"❌ *Re-submission Denied*\n\n`{emp_id}` ({staff_name}) — denied by {admin_name}.",
                parse_mode="Markdown",
            )
        except Exception as e:
            logger.warning(f"Failed to notify group: {e}")

        logger.info(f"Re-submission rejected for {emp_id} by {admin_name}")


async def edit_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Approve/Reject for /edit requests."""
    query = update.callback_query
    await query.answer()

    admin_id = str(query.from_user.id)
    admin_name = query.from_user.first_name or "Admin"

    if admin_id not in [str(config.OWNER_CHAT_ID), str(config.HR_CHAT_ID)]:
        await query.edit_message_text("🚫 You are not authorized.")
        return

    parts = query.data.split(":")
    if len(parts) != 3:
        await query.edit_message_text("❌ Invalid request data.")
        return

    action, emp_id, group_chat_id = parts
    staff_name = config.STAFF_RECORDS.get(emp_id, {}).get("name", emp_id)

    if action == "edit_approve":
        # Get pending edit text
        pending = context.bot_data.get("pending_edits", {}).get(emp_id, {})
        new_text = pending.get("new_text", "N/A")

        await query.edit_message_text(
            f"✅ *Edit Approved* by {admin_name}\n\n"
            f"Employee `{emp_id}` ({staff_name})\n"
            f"📝 New update: _{new_text}_",
            parse_mode="Markdown",
        )

        try:
            await context.bot.send_message(
                chat_id=int(group_chat_id),
                text=f"✅ *Edit Approved!*\n\n`{emp_id}` ({staff_name}) — your edit was approved by {admin_name}.",
                parse_mode="Markdown",
            )
        except Exception as e:
            logger.warning(f"Failed to notify group: {e}")

        # Clean up pending
        if emp_id in context.bot_data.get("pending_edits", {}):
            del context.bot_data["pending_edits"][emp_id]

        logger.info(f"Edit approved for {emp_id} by {admin_name}")

    elif action == "edit_reject":
        await query.edit_message_text(
            f"❌ *Edit Rejected* by {admin_name}\n\nEdit for `{emp_id}` ({staff_name}) was denied.",
            parse_mode="Markdown",
        )
        try:
            await context.bot.send_message(
                chat_id=int(group_chat_id),
                text=f"❌ *Edit Denied*\n\n`{emp_id}` ({staff_name}) — edit denied by {admin_name}.",
                parse_mode="Markdown",
            )
        except Exception as e:
            logger.warning(f"Failed to notify group: {e}")

        if emp_id in context.bot_data.get("pending_edits", {}):
            del context.bot_data["pending_edits"][emp_id]

        logger.info(f"Edit rejected for {emp_id} by {admin_name}")


async def leave_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Approve/Reject for /leave requests."""
    query = update.callback_query
    await query.answer()

    admin_id = str(query.from_user.id)
    admin_name = query.from_user.first_name or "Admin"

    if admin_id not in [str(config.OWNER_CHAT_ID), str(config.HR_CHAT_ID)]:
        await query.edit_message_text("🚫 You are not authorized.")
        return

    parts = query.data.split(":")
    if len(parts) != 4:
        await query.edit_message_text("❌ Invalid request data.")
        return

    action, emp_id, leave_date, group_chat_id = parts
    staff_name = config.STAFF_RECORDS.get(emp_id, {}).get("name", emp_id)
    dept = config.STAFF_RECORDS.get(emp_id, {}).get("dept", "UNKNOWN")

    if action == "leave_approve":
        # Save to leave log
        leave_log = config.load_leave_log()
        # Convert DD-MM-YYYY to YYYY-MM-DD for log key
        try:
            date_obj = datetime.strptime(leave_date, "%d-%m-%Y")
            log_key = date_obj.strftime("%Y-%m-%d")
        except Exception:
            log_key = leave_date

        if log_key not in leave_log:
            leave_log[log_key] = {}

        pending = context.bot_data.get("pending_leaves", {}).get(f"{emp_id}:{leave_date}", {})
        reason = pending.get("reason", "N/A")

        leave_log[log_key][emp_id] = {"approved_by": admin_name, "reason": reason}
        config.save_leave_log(leave_log)

        # Count monthly leaves (including this one)
        leave_count = count_monthly_leaves(emp_id, leave_date)

        # Save to Excel Leave Register (with deduction if > 3)
        save_leave_to_excel(emp_id, staff_name, dept, leave_date, reason, admin_name, leave_count)

        # Admin message — shows deduction info privately
        admin_msg = (
            f"✅ *Leave Approved* by {admin_name}\n\n"
            f"🆔 `{emp_id}` ({staff_name})\n"
            f"📅 {leave_date}\n"
            f"📊 Leave #{leave_count} this month"
        )
        if leave_count > 3:
            deduction = (leave_count - 3) * 500
            admin_msg += f"\n\n⚠️ *Extra leave!* Salary deduction: *-₹{deduction}*"
            admin_msg += f"\n_(3 free leaves exceeded, ₹500 per extra leave)_"

        await query.edit_message_text(admin_msg, parse_mode="Markdown")

        # Group message — simple, NO deduction info shown
        try:
            await context.bot.send_message(
                chat_id=int(group_chat_id),
                text=f"✅ *Leave Approved!*\n\n`{emp_id}` ({staff_name}) — leave on `{leave_date}` approved by {admin_name}.",
                parse_mode="Markdown",
            )
        except Exception as e:
            logger.warning(f"Failed to notify group: {e}")

        # Clean up
        key = f"{emp_id}:{leave_date}"
        if key in context.bot_data.get("pending_leaves", {}):
            del context.bot_data["pending_leaves"][key]

        logger.info(f"Leave #{leave_count} approved for {emp_id} on {leave_date} by {admin_name}")

    elif action == "leave_reject":
        await query.edit_message_text(
            f"❌ *Leave Rejected* by {admin_name}\n\n"
            f"Leave for `{emp_id}` ({staff_name}) on `{leave_date}` was denied.",
            parse_mode="Markdown",
        )
        try:
            await context.bot.send_message(
                chat_id=int(group_chat_id),
                text=f"❌ *Leave Denied*\n\n`{emp_id}` ({staff_name}) — leave on `{leave_date}` denied by {admin_name}.",
                parse_mode="Markdown",
            )
        except Exception as e:
            logger.warning(f"Failed to notify group: {e}")

        key = f"{emp_id}:{leave_date}"
        if key in context.bot_data.get("pending_leaves", {}):
            del context.bot_data["pending_leaves"][key]

        logger.info(f"Leave rejected for {emp_id} on {leave_date} by {admin_name}")
