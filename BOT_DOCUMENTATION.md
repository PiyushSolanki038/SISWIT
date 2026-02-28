# 🤖 Employee Work Update Bot — Full Documentation

This bot is a simple and fast tool to record your daily work updates into Excel and Google Sheets.

---

## 🏗️ 1. How It Works

The bot listens to messages in the Telegram group. If it sees a **registered Employee ID** followed by a **work description**, it saves the update immediately to Excel and Google Sheets.

> ⚠️ Only messages starting with a **registered Employee ID** are processed. All other messages are silently ignored.

---

## 📝 2. Using the Bot for Updates

To submit your work, enter your message in the following format:

**Format:** `YOUR_ID Your work description`

*   **CORRECT:** `DEV01 Finished the login page`
*   **CORRECT:** `PK042 Started working on database and completed schema design`
*   **INCORRECT:** `DEV01 - Finished the login page` (Do not use the dash symbol `-`)
*   **INCORRECT:** `Hello everyone` (Not a registered ID — will be ignored)

> 💡 Your Employee ID must be registered in the system. Ask admin to use `/addstaff` if you are new.

---

## 🔧 3. Commands

### For Everyone

| Command | Action |
| :--- | :--- |
| **`/start`** | Welcome message with instructions. |
| **`/help`**  | Shows all available commands and format. |
| **`/allow`** | Request re-submission for an employee (e.g., `/allow DEV01`). Sends approval request to Owner & HR. |

### Admin Commands (Owner & HR Only)

| Command | Action |
| :--- | :--- |
| **`/staff`** | Shows the list of registered employees. |
| **`/addstaff`** | Adds a new employee (e.g., `/addstaff ID - Name - Dept`). |
| **`/removestaff`** | Removes an employee (e.g., `/removestaff DEV01`). |
| **`/allow`** | When used by admin, directly approves re-submission (no buttons). |
| **`/report`** | Shows today's submission status — who submitted and who hasn't. |

---

## 🛡️ 4. Duplicate Prevention & Re-submission

To keep the records clean, the bot only allows **one submission per employee per day**.

- If you try to submit a second time, the bot will block it and show an error.
- The daily log **persists across bot restarts** (saved to `daily_log.json`).

### How to Re-submit:
1. **Employee** types `/allow DEV01` in the group
2. **Owner & HR** receive a private message with **✅ Approve** and **❌ Reject** buttons
3. If **approved** → bot notifies the group and the employee can submit again
4. If **rejected** → bot notifies the group that the request was denied

> 💡 **Admin shortcut:** If Owner or HR uses `/allow DEV01` themselves, it's approved instantly — no buttons needed.

## ⚡ 5. Features & Automation

- **Auto-Sync**: Every update is saved to the local Excel file and your Google Sheet in real-time.
- **Non-Blocking**: Google Sheets sync runs in the background — the bot stays responsive.
- **Private Alerts**: The Owner and HR get a private message whenever someone posts an update.
- **Role-Based**: Only approved Owners and HR can use management commands.
- **Daily Report**: Owner/HR can use `/report` to see who has and hasn't submitted today.
- **Persistent Tracking**: Daily submission log survives bot restarts.
- **`.env` Support**: Configuration auto-loads from a `.env` file.
