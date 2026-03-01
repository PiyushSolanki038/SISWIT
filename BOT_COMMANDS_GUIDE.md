# 🤖 Work Update Bot — Commands Guide

---

## 📝 How to Submit Attendance
Just type in the group chat:
```
YOUR_ID Your work description
```
**Examples:**
- `DEV01 Fixed the login page and tested it`
- `MKT03 Created social media posts for campaign`
- `HR01 Processed employee onboarding today`

### ⏰ Attendance Deadline
- **Before 1:00 PM** → Recorded for **previous day** (✅ On Time)
- **After 1:00 PM** → Recorded for **current day** (✅ On Time)

---

## 👥 Registered Employees

| ID | Name | Department |
|:---|:---|:---|
| DEV01 | Sunny | DEVELOPER |
| DEV02 | Piyush | DEVELOPER |
| DEV03 | Anand | DEVELOPER |
| DEV04 | Adarsh | DEVELOPER |
| MKT01 | Bipul | MARKETING |
| MKT02 | Finney | MARKETING |
| MKT03 | Shivam | MARKETING |
| MKT04 | Amar | MARKETING |
| FIN01 | Sahil | FINANCE |
| HR01 | Shruti | HR |
| HR02 | Pooja | HR |

---

## 📋 General Commands
*Available to everyone.*

| Command | Usage | What It Does |
|:---|:---|:---|
| `/start` | `/start` | Welcome message + how to submit |
| `/help` | `/help` | Shows all available commands |
| `/staff` | `/staff` | Lists all registered employees |
| `/report` | `/report` | Today's attendance summary |

---

## 👤 Employee Commands

| Command | Usage | What It Does |
|:---|:---|:---|
| `/mystatus` | `/mystatus DEV01` | Your 7-day attendance history → **DM** |
| `/myprofile` | `/myprofile DEV01` | Your profile + total submissions → **DM** |
| `/edit` | `/edit DEV01 New text` | Request to edit your last update (needs approval) |
| `/leave` | `/leave DEV01 Sick` | Request leave (needs approval) |

**Leave examples:**
- `/leave DEV01 Feeling sick` → today
- `/leave DEV01 tomorrow Doctor visit`
- `/leave DEV01 05-03-2026 Family function`

---

## 🛠️ Admin Commands — Group Chat
*Owner & HR only.*

| Command | Usage | What It Does |
|:---|:---|:---|
| `/absent` | `/absent` | Lists who hasn't submitted today |
| `/late` | `/late` | Lists late submissions |
| `/addstaff` | `/addstaff ID Name Dept` | Register new employee |
| `/removestaff` | `/removestaff ID` | Remove employee |
| `/allow` | `/allow DEV01` | Allow re-submission (1 time only) |
| `/deadline` | `/deadline 13:00` | Set submission deadline |
| `/sethr` | `/sethr CHAT_ID` | Change HR (Owner only) |
| `/broadcast` | `/broadcast Message` | Send announcement in group |

---

## 📊 Admin Reports — Sent to DM
*Large reports go to your private DM to keep group clean.*

| Command | Usage | What It Does |
|:---|:---|:---|
| `/history` | `/history DEV01` | 7-day detailed history of any employee |
| `/weeklyreport` | `/weeklyreport` | Visual grid ✅/❌ for all employees |
| `/monthly` | `/monthly` | Monthly stats with progress bars |
| `/export` | `/export` | Get Excel file + Google Sheets link |

---

## 🔐 Private Chat Commands — DM the Bot
*Owner & HR only. Send these in your private chat with the bot.*

| Command | Usage | What It Does |
|:---|:---|:---|
| `/announce` | `/announce Tomorrow holiday` | Sends 📢 announcement to group |
| `/dm` | `/dm DEV01 Submit ASAP` | Private message to an employee |
| `/remind` | `/remind` | Remind all who haven't submitted |
| `/warning` | `/warning DEV01 Late 3x` | Send ⚠️ official warning to employee |

---

## � Approval Rules

| Who Requests | Approval Goes To |
|:---|:---|
| Regular Employee | Both Owner & HR |
| HR (Shruti/Pooja) | **Owner only** |
| Owner | **HR only** |

---

## 💡 Tips
1. **All 7 days** are working days (no weekends)
2. **DM the bot first** — tap Start in private chat so it can send you messages
3. **Data is saved** to Excel file + Google Sheets automatically
4. **Group Chat ID** is auto-detected when anyone sends a message
