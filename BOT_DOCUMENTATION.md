# 🤖 Employee Work Update Bot — Complete Command Reference

> **Version:** 2.0 | **Last Updated:** 01 March 2026  
> **Telegram Bot API:** python-telegram-bot v21  
> **Deployment:** Railway + Google Sheets + Excel

---

## 📝 How to Submit Attendance

Just send a message in the group chat:

```
YOUR_ID Your work description here
```

**Example:**
```
DEV01 Fixed the login bug, tested payment flow, updated docs
```

**Bot Response:**
```
Thank you, Piyush! ✅
```

### ⏰ Grace Period (12 AM – 1 AM)
If you submit between **12:00 AM** and **1:00 AM**, it counts as the **previous day** (marked Late):
```
Thank you, Piyush! ✅
⏰ Recorded for 28 Feb (late submission)
```
After **1:00 AM**, submissions count as the new day.

### ❌ Already Submitted
```
❌ Already Submitted
Piyush (DEV02) already submitted for 01 Mar.
Use /allow DEV02 to request re-submission.
```

---

## 🔧 General Commands (Everyone)

### `/start`
Welcome message with quick instructions.
```
👋 Welcome to the Employee Work Update Bot!

📝 Submit your daily update:
YOUR_ID Your work description

📌 Example:
DEV01 Fixed the login page and tested it

💡 Use /help to see all commands.
```

---

### `/help`
Shows all available commands based on your role (Employee vs Admin).

---

### `/allow EMP_ID`
Request to re-submit today's update. Sends approval to Owner & HR.

**Usage:** `/allow DEV02`

**Bot Response:**
```
📨 Request sent to Owner & HR for DEV02.
```

**Owner/HR sees:**
```
🔔 Re-submission Request
━━━━━━━━━━━━━━━━━━━━━━
👤 By: Piyush
🆔 Employee: Piyush (DEV02)
📅 Date: 01 Mar 2026
📍 Group: SISWIT Updates

Approve re-submission?
[✅ Approve] [❌ Reject]
```

> ⚠️ **Limit:** Only **1 re-submission per day** allowed. 2nd attempt triggers a **🚨 Suspicious Activity Alert** to Owner & HR and is **blocked**.

**After re-submission, existing row in Google Sheet is UPDATED (not duplicated).**

---

## 👤 Employee Commands

### `/mystatus`
View your weekly submission status (sent to your DM).

**Usage:** `/mystatus` or `/mystatus DEV02`

```
📊 Your Status — Piyush (DEV02)
🏢 DEVELOPER
━━━━━━━━━━━━━━━━━━━━━━

✅ Mon 24 Feb 09:30 AM
   Fixed login page bug
✅ Tue 25 Feb 10:15 AM
   Updated payment module
❌ Wed 26 Feb — Absent
🏖️ Thu 27 Feb — On Leave
✅ Fri 28 Feb 08:45 AM
   Sprint review & documentation
🔵 Sat 01 Mar — Weekend
🔵 Sun 02 Mar — Weekend

📈 Score: 3/5 (60%)
```

---

### `/myprofile`
View your employee profile (sent to your DM).

**Usage:** `/myprofile` or `/myprofile DEV02`

```
👤 Employee Profile
━━━━━━━━━━━━━━━━━━━━━━
🆔 ID: DEV02
👤 Name: Piyush
🏢 Department: DEVELOPER

📊 This Month:
✅ Submitted: 18 days
⏰ Late: 3 times
🏖️ Leaves: 2 days
📈 Attendance: 90%
```

---

### `/edit EMP_ID New updated text`
Request to edit your last work update. Requires Owner/HR approval.

**Usage:** `/edit DEV02 Fixed login and also updated the dashboard`

```
📨 Edit request sent to Owner & HR for DEV02.
```

---

### `/leave EMP_ID [date] Reason`
Request a leave day. Owner/HR must approve.

**Formats:**
- `/leave DEV02 Not feeling well` → Today
- `/leave DEV02 tomorrow Doctor appointment` → Tomorrow
- `/leave DEV02 05-03-2026 Family function` → Specific date

```
📨 Leave request sent for DEV02.
```

**Owner/HR sees:**
```
🏖️ Leave Request
━━━━━━━━━━━━━━━━━━━━━━
👤 Employee: Piyush (DEV02)
🏢 Department: DEVELOPER
📅 Date: 05-03-2026
📋 Reason: Family function

[✅ Approve] [❌ Reject]
```

**Leave Limit:** 3 free leaves/month. **4th leave onwards** = ₹500 deduction (shown in Excel/Google Sheets only, not in group chat).

---

## 👑 Admin Commands (Owner & HR Only)

### `/staff`
List all registered employees.

```
👥 Registered Staff
━━━━━━━━━━━━━━━━━━━━━━

• DEV01 — Sunny (DEVELOPER)
• DEV02 — Piyush (DEVELOPER)
• DEV03 — Anand (DEVELOPER)
• MKT01 — Bipul (MARKETING)
• FIN01 — Sahil (FINANCE)

📊 Total: 5 employees
```

---

### `/addstaff ID - Name - Department`
Add a new employee.

**Usage:** `/addstaff DEV05 - Rahul - DEVELOPER`

```
✅ Staff Added!
🆔 DEV05 | 👤 Rahul | 🏢 DEVELOPER
```

---

### `/removestaff EMP_ID`
Remove an employee.

**Usage:** `/removestaff DEV05`

```
✅ Removed: DEV05 (Rahul)
```

---

### `/report`
Today's full submission status.

```
📊 Daily Report — 01 Mar 2026
━━━━━━━━━━━━━━━━━━━━━━
📈 Progress: 4/7 submitted

✅ Submitted:
✅ DEV01 — Sunny
✅ DEV02 — Piyush
✅ DEV03 — Anand
✅ MKT01 — Bipul

🏖️ On Leave:
🏖️ FIN01 — Sahil

❌ Not Submitted:
❌ DEV04 — Adarsh
❌ MKT02 — Finney
```

---

### `/absent`
Quick list of who hasn't submitted today.

```
📋 Absent Today — 01 Mar 2026
━━━━━━━━━━━━━━━━━━━━━━

❌ DEV04 — Adarsh (DEVELOPER)
❌ MKT02 — Finney (MARKETING)

📊 2 employee(s) not submitted
```

---

### `/late`
Show employees who submitted after the deadline.

```
⏰ Late Report — 01 Mar 2026
📌 Deadline: 11:00
━━━━━━━━━━━━━━━━━━━━━━

❌ Late Submissions:
⏰ DEV04 — Adarsh (at 02:30 PM)

✅ On Time:
✅ DEV01 — Sunny (at 09:15 AM)
✅ DEV02 — Piyush (at 10:45 AM)
```

---

### `/history EMP_ID`
View an employee's last 7 days (sent to your DM).

**Usage:** `/history DEV02`

```
📜 History — Piyush (DEV02)
🏢 DEVELOPER
━━━━━━━━━━━━━━━━━━━━━━

✅ Mon 24 Feb 09:30 AM
   Fixed login page bug
✅ Tue 25 Feb 10:15 AM
   Updated payment module
❌ Wed 26 Feb — Absent
🏖️ Thu 27 Feb — On Leave
✅ Fri 28 Feb 08:45 AM
   Sprint review
🔵 Sat 01 Mar — Weekend
🔵 Sun 02 Mar — Weekend
```

---

### `/weeklyreport`
Weekly grid showing all employees' status (sent to your DM).

```
📊 Weekly Report
📅 24 Feb — 02 Mar 2026
━━━━━━━━━━━━━━━━━━━━━━

          Mon Tue Wed Thu Fri Sat Sun
DEV01   ✅  ✅  ✅  ✅  ✅  🔵  🔵  (5/7)
DEV02   ✅  ✅  ❌  🏖  ✅  🔵  🔵  (3/7)
MKT01   ✅  ✅  ✅  ✅  ❌  🔵  🔵  (4/7)

✅=Submitted  ❌=Absent  🏖=Leave  🔵=Weekend
```

---

### `/monthly`
Monthly attendance summary with progress bars (sent to your DM).

```
📊 Monthly Report — March 2026
📅 Working days so far: 1
━━━━━━━━━━━━━━━━━━━━━━

Piyush (DEV02)
  ██████████ 100%
  ✅ 1 days | ⏰ 0 late | 🏖️ 0 leave

Sunny (DEV01)
  ██████████ 100%
  ✅ 1 days | ⏰ 0 late | 🏖️ 0 leave
```

---

### `/export`
Get the Excel file and/or Google Sheet link (sent to your DM).

```
📊 Employee Updates — Excel File
[employee_updates.xlsx attached]

📋 Google Sheet:
https://docs.google.com/spreadsheets/d/xxx/edit
```

---

### `/broadcast Your message`
Send an announcement in the current chat.

**Usage:** `/broadcast Tomorrow is a holiday!`

```
📢 Announcement
━━━━━━━━━━━━━━━━━━━━━━

Tomorrow is a holiday!

— Piyush
```

---

### `/deadline HH:MM`
View or change the daily submission deadline.

**View current:** `/deadline`
```
⏰ Current deadline: 11:00

To change: /deadline HH:MM
```

**Change:** `/deadline 10:30`
```
✅ Deadline Updated!

⏰ New deadline: 10:30
Employees submitting after this time will be marked as late.
```

---

### `/sethr CHAT_ID`
Change the HR chat ID (Owner only).

**Usage:** `/sethr 123456789`

```
✅ HR Updated!

New HR Chat ID: 123456789
```

---

## 📢 Private Chat Commands (Owner & HR DM with Bot)

> These commands work from your **private chat** with the bot. They send messages to the **group** or to **individual employees**.

### `/announce Your message`
Send a styled announcement to the group chat from your private chat.

**Usage:** `/announce Tomorrow is a national holiday. No work updates needed.`

**Group sees:**
```
📢 ANNOUNCEMENT
━━━━━━━━━━━━━━━━━━━━━━

Tomorrow is a national holiday. No work updates needed.

— 👑 Owner: Piyush
📅 01 Mar 2026, 03:15 PM
```

**You see:** `✅ Announcement sent to the group!`

---

### `/dm EMP_ID Your message`
Send a private message to a specific employee.

**Usage:** `/dm DEV01 Please submit your update ASAP`

**Employee sees:**
```
📩 Message from 👑 Owner
━━━━━━━━━━━━━━━━━━━━━━

Please submit your update ASAP

— Piyush
```

**You see:** `✅ Message sent to Sunny (DEV01)!`

---

### `/remind`
Send reminders to all employees who haven't submitted today (sent to group).

**Group sees:**
```
⏰ REMINDER: Submit Your Work Update!
━━━━━━━━━━━━━━━━━━━━━━

📅 Date: 01 Mar 2026
🕐 Deadline: 11:00

The following employees have NOT submitted yet:

• DEV04 — Adarsh
• MKT02 — Finney

📝 Please send your update now!
Format: YOUR_ID Your work description
```

**You see:** `✅ Reminder sent to group! (2 employees pending)`

---

### `/warning EMP_ID Reason`
Send an official warning to an employee's DM.

**Usage:** `/warning DEV01 Repeated late submissions this week`

**Employee sees:**
```
⚠️ OFFICIAL WARNING
━━━━━━━━━━━━━━━━━━━━━━

👤 Employee: Sunny (DEV01)
📅 Date: 01 Mar 2026

📋 Reason:
Repeated late submissions this week

⚡ Please take this as a formal notice and
ensure compliance going forward.

— Owner: Piyush
```

**Other admin also gets notified:**
```
📋 Warning Issued

Piyush (Owner) warned DEV01 (Sunny)

Reason: Repeated late submissions this week
```

---

## 📊 Excel & Google Sheets Features

### Monthly Sheets
- Each month gets its own tab: `Mar 2026`, `Apr 2026`, etc.
- Columns: Sr No, Employee ID, Department, Name, Username, Date, Day, Time, Work Update, Group Name, Status, On Time

### Day Separators
When a new day starts, a styled **blue separator row** is inserted:
```
📅 02-03-2026 — Monday
```

### Leave Register Sheet
- Tracks all approved leaves with: Leave #, Employee, Department, Date, Reason, Approved By, Deduction
- 4th leave onwards: **-₹500** deduction (highlighted in red)

### Dashboard Sheet
- Auto-updated summary with total submissions, on-time %, and department breakdown

---

## 🔒 Permission Levels

| Feature | Employee | HR | Owner |
|---------|:--------:|:--:|:-----:|
| Submit update | ✅ | ✅ | ✅ |
| `/mystatus`, `/myprofile` | ✅ | ✅ | ✅ |
| `/edit`, `/leave`, `/allow` | ✅ | ✅ | ✅ |
| `/report`, `/absent`, `/late` | ❌ | ✅ | ✅ |
| `/staff`, `/addstaff`, `/removestaff` | ❌ | ✅ | ✅ |
| `/history`, `/weeklyreport`, `/monthly` | ❌ | ✅ | ✅ |
| `/export`, `/broadcast`, `/deadline` | ❌ | ✅ | ✅ |
| `/announce`, `/dm`, `/remind`, `/warning` | ❌ | ✅ | ✅ |
| `/sethr` | ❌ | ❌ | ✅ |

---

## ⚙️ Environment Variables

| Variable | Required | Description |
|----------|:--------:|-------------|
| `BOT_TOKEN` | ✅ | Telegram bot token from @BotFather |
| `OWNER_CHAT_ID` | ✅ | Owner's Telegram chat ID |
| `HR_CHAT_ID` | ✅ | HR's Telegram chat ID |
| `GOOGLE_SHEET_ID` | ✅ | Google Sheets spreadsheet ID |
| `GOOGLE_CREDS_JSON` | ✅ | Service account JSON credentials (for Railway) |
| `GROUP_CHAT_ID` | 🔄 | Auto-detected from group messages |
| `TIMEZONE` | ❌ | Default: `Asia/Kolkata` |
| `SUBMISSION_DEADLINE` | ❌ | Default: `11:00` (24h format) |
| `EXCEL_FILE` | ❌ | Default: `employee_updates.xlsx` |
| `GOOGLE_CREDS_FILE` | ❌ | Default: `credentials.json` |
