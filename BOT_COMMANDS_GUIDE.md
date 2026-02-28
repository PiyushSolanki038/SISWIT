# 🤖 Work Update Bot — Commands Guide

This guide provides a comprehensive list of all commands available in the Work Update Bot, categorized by user role and access level.

---

## 📋 General Commands
*Available to everyone in the group chat.*

| Command | Usage | Description |
|:---|:---|:---|
| `/start` | `/start` | Displays the welcome message and basic instructions. |
| `/help` | `/help` | Shows this help guide and a list of all available commands. |
| `/staff` | `/staff` | Shows a list of all registered employees and their departments. |
| `/report` | `/report` | Shows a quick summary of today's attendance status. |

---

## 👤 Employee Commands
*Used by employees to manage their own updates and profile.*

| Command | Usage | Description |
|:---|:---|:---|
| `/mystatus` | `/mystatus EMP_ID` | Sends your weekly submission history to your **Private DM**. |
| `/myprofile` | `/myprofile EMP_ID` | Sends your full profile (total days, leaves, etc.) to your **Private DM**. |
| `/edit` | `/edit EMP_ID New Text` | Sends a request to Owner/HR to edit your last submission. |
| `/leave` | `/leave EMP_ID [Date] Reason` | Requests leave approval. Date can be `today`, `tomorrow`, or `DD-MM-YYYY`. |

---

## 🛠️ Admin Commands (Group Chat)
*Accessible only to the **Owner** and **HR**. Can be used in the group chat.*

| Command | Usage | Description |
|:---|:---|:---|
| `/absent` | `/absent` | Lists all employees who have not submitted their update today. |
| `/late` | `/late` | Lists employees who submitted after the official deadline. |
| `/addstaff` | `/addstaff ID Name Dept` | Registers a new employee into the system. |
| `/removestaff`| `/removestaff ID` | Removes an employee from the system. |
| `/deadline` | `/deadline HH:MM` | Sets the daily submission deadline (e.g., `/deadline 11:30`). |
| `/sethr` | `/sethr CHAT_ID` | (Owner Only) Sets or updates the HR administrator's Chat ID. |
| `/allow` | `/allow EMP_ID` | Allows an employee to re-submit their attendance for today. |

---

## 📊 Admin Reports (Sent to Private DM)
*These commands process large amounts of data and send the results to the admin's DM to keep the group chat clean.*

| Command | Usage | Description |
|:---|:---|:---|
| `/history` | `/history EMP_ID` | Shows the last 7 days of detailed history for a specific employee. |
| `/weeklyreport`| `/weeklyreport` | Sends a visual grid (✅/❌) of everyone's performance for the week. |
| `/monthly` | `/monthly` | Sends a monthly summary with performance bars and leave counts. |
| `/export` | `/export` | Sends the latest **Excel file** and the **Google Sheets link**. |

---

## 🔐 Private Chat Special Commands (Owner & HR Only)
*These commands work **only when sent privately** to the bot. They allow admins to manage the team and communicate effectively.*

| Command | Usage | Description |
|:---|:---|:---|
| `/announce` | `/announce Message` | Sends a professionally styled 📢 announcement to the group chat. |
| `/dm` | `/dm EMP_ID Message` | Sends a private message from the admin to the employee's DM. |
| `/remind` | `/remind` | Scans for pending submissions and sends a group-wide reminder. |
| `/warning` | `/warning EMP_ID Reason`| Sends a formal ⚠️ **OFFICIAL WARNING** to an employee's DM. |

---

## 💡 Pro Tips

1. **Format:** Always use your employee ID (e.g., `DEV01`) for commands that require it.
2. **Privacy:** The bot sends reports to your DM. Make sure you have **started a chat** with the bot privately for this to work.
3. **Deadlines:** Submissions after the deadline are automatically marked as `⏰ Late` in Excel and Google Sheets.
4. **Auto-Save:** Every update is instantly saved to both the local Excel file and the cloud Google Sheet.
