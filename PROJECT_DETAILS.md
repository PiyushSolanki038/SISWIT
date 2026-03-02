# 🏗️ SISWIT Attendance System — Technical & Functional Documentation

This document provides a comprehensive overview of the **SISWIT Employee Attendance Bot**, covering its architecture, core logic, data structures, and feature set.

---

## 📅 1. Project Overview
The SISWIT Attendance Bot is a professional automation tool designed to track employee daily work updates via Telegram. It captures submissions in real-time and synchronizes them with both **local Excel files** and **Google Sheets** for permanent, cloud-accessible record-keeping.

---

## 🛠️ 2. Technology Stack
- **Language**: Python 3.10+
- **Framework**: `python-telegram-bot` (v21.x ApplicationBuilder)
- **Data Handling**: 
    - `openpyxl`: Local Excel file generation and formatting.
    - `gspread`: Google Sheets API integration.
    - `JSON`: Local persistence for logs (`daily_log.json`, `staff.json`).
- **Timezone Management**: `pytz` (configured for `Asia/Kolkata`).
- **Cloud Deployment**: Compatible with Railway, Heroku, and local servers.

---

## 📐 3. System Architecture
The bot operates on a "Listener-Processor-Writer" pattern:
1.  **Listener**: Monitors a dedicated Telegram group for messages starting with registered Employee IDs.
2.  **Processor**: Validates the ID, determines the attendance date based on cutoff logic, and checks punctuality against the deadline.
3.  **Writer**: Simultaneously updates the local `employee_updates.xlsx` and calls a background thread to sync with Google Sheets.

---

## ⚖️ 4. Core Business Logic

### ⏰ Attendance Date (1:00 PM Cutoff)
To handle night shifts or early morning submissions, the bot uses a "Submission Date" logic:
- **Submitted BEFORE 1:00 PM**: Marked for the **Previous Day**.
- **Submitted AFTER 1:00 PM**: Marked for the **Current Day**.

### ⚡ Punctuality (11:00 AM Deadline)
Punctuality is determined by the submission time:
- **Before 11:00 AM**: Marked as `✅ YES` (On Time).
- **After 11:00 AM**: Marked as `❌ LATE`.

### 🍃 Leave Management
The system tracks monthly leaves automatically:
- **Free Leaves**: Each employee gets **3 free leaves** per month.
- **Extra Leaves**: Starting from the **4th leave**, a deduction of **₹500 per leave** is calculated.
- **Approval Flow**: Employee requests via `/leave`, and both Owner and HR receive buttons to **Approve** or **Reject**.

---

## 📊 5. Data Structures

### Attendance Sheet (12-Column Professional Layout)
Both Excel and Google Sheets follow this strict structure:
1.  **S.No.** — Auto-incrementing serial number.
2.  **Date** — The calculated attendance date (DD-MM-YYYY).
3.  **Day** — Day of the week.
4.  **Employee Name** — From `staff.json`.
5.  **Emp ID** — Unique employee identifier.
6.  **Department** — department name.
7.  **Submit Time** — Exact time of submission (e.g., 2:30 PM).
8.  **Punctuality** — `YES` or `❌ LATE`.
9.  **Work Report** — The actual description provided by the employee.
10. **Source** — Fixed as `SISWIT`.
11. **Telegram User** — Username of the sender.
12. **Revision** — `Original` or `📝 Edited`.

### Leave Register (10-Column Layout)
1. **Sr No** | 2. **Emp ID** | 3. **Name** | 4. **Dept** | 5. **Date** | 6. **Reason** | 7. **Approved By** | 8. **Status** | 9. **Leave #** | 10. **Deduction**

---

## 🔐 6. Role-Based Access Control (RBAC)

- **Owner**: Full access to all commands, staff management, and financial reports.
- **HR**: Similar to Owner, but cannot change the HR Chat ID.
- **Employee**: Can submit updates, view their own status/profile, and request leaves/edits.

---

## 🚀 7. Key Features
- **Real-time Google Sync**: Uses `asyncio.to_thread` to ensure the bot doesn't lag while writing to the cloud.
- **Header Auto-Repair**: Automatically fixes Google Sheet headers if they are modified or outdated.
- **Visual Reports**: `/monthly` and `/weeklyreport` generate text-based progress bars and status grids.
- **Atomic Operations**: Uses `SHEET_LOCK` to prevent data corruption during simultaneous writes.
- **Revision Tracking**: If an admin approves an edit, the entry is updated and marked as "Edited".

---

## 📂 8. File Manifest
- `bot.py`: Entry point and command handlers.
- `config.py`: Central configuration, date logic, and staff records.
- `excel_handler.py`: Core logic for Excel and Google Sheets operations.
- `callbacks.py`: Logic for interactive button clicks (Approvals).
- `commands_admin.py`: Privileged commands for Owners/HR.
- `commands_employee.py`: Commands for regular staff.
- `staff.json`: Persistent registry of all employees.
- `leave_log.json`: Record of monthly leave counts and approvals.
