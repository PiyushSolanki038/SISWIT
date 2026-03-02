# 🤖 Employee Work Update Bot — Full Documentation

A Telegram bot that records daily work updates to Excel & Google Sheets with role-based access control.

---

## 📝 Submit Your Update

**Format:** `YOUR_ID Your work description`

✅ `DEV01 Fixed the login page and deployed to staging`
❌ `Hello everyone` ← ignored (not a registered ID)

> Your Employee ID must be registered. Use `/staff` to check.

---

## 🔧 Commands — Everyone

| Command | Where | What It Does |
|---------|:-----:|-------------|
| `/start` | 💬 Group | Welcome message |
| `/help` | 💬 Group | All commands list |
| `/allow ID` | 📩 Admin DM | Request re-submission (Approve/Reject buttons) |
| `/mystatus ID` | 📩 Your DM | Your 7-day submission status |
| `/myprofile ID` | 📩 Your DM | Your profile & stats |
| `/edit ID New text` | 📩 Admin DM | Request edit (Approve/Reject buttons) |
| `/leave ID DD-MM-YYYY Reason` | 📩 Admin DM | Request leave (Approve/Reject buttons) |

---

## 👑 Commands — Owner & HR Only

| Command | Where | What It Does |
|---------|:-----:|-------------|
| `/staff` | 💬 Group | List all registered employees |
| `/addstaff ID - Name - Dept` | 💬 Group | Add new employee |
| `/removestaff ID` | 💬 Group | Remove employee |
| `/report` | 💬 Group | Today's full status (submitted/absent/leave) |
| `/absent` | 💬 Group | Quick absent-only list |
| `/late` | 💬 Group | Who submitted after deadline |
| `/history ID` | 📩 Your DM | Employee's 7-day history |
| `/weeklyreport` | 📩 Your DM | Full week grid for all employees |
| `/monthly` | 📩 Your DM | Monthly attendance % with progress bars |
| `/export` | 📩 Your DM | Get Excel file + Google Sheet link |
| `/broadcast Text` | 💬 Group | Send announcement |
| `/deadline HH:MM` | 💬 Group | Set/view submission deadline |
| `/sethr CHAT_ID` | 💬 Group | Change HR (Owner only) |

---

## 🛡️ Re-submission & Leave Approval Flow

1. Employee types `/allow DEV01` or `/leave DEV01 05-03-2026 Sick`
2. Owner & HR get a private message with **✅ Approve** / **❌ Reject** buttons
3. On tap → bot notifies the group with the result

---

## 📊 Excel & Google Sheets Structure

| Sheet | Purpose |
|-------|---------|
| `Mar 2026` (monthly) | Daily work entries with Status & On Time columns |
| `Dashboard` | Attendance %, late count, leave count per employee |
| `Leave Register` | All approved leave records |

---

## ⚡ Features

- **Dual storage** — Excel + Google Sheets in real-time
- **Non-blocking** — Google Sheets runs in background thread
- **Role-based** — Employee, Owner, HR permissions
- **Approval flow** — /allow, /edit, /leave with Approve/Reject buttons
- **Persistent tracking** — Daily log survives bot restarts
- **Late detection** — Configurable deadline with /late report
- **Monthly reports** — Visual progress bars per employee
- **`.env` support** — Auto-loads from .env file
