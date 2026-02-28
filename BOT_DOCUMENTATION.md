# 🤖 Employee Work Update Bot — Full Documentation

This bot is a simple and fast tool to record your daily work updates into Excel and Google Sheets.

---

## 🏗️ 1. How It Works

The bot listens to any message in the Telegram group. If it sees your **Employee ID** followed by your **Work**, it saves it immediately.

---

## 📝 2. Using the Bot for Updates

To submit your work, enter your message in the following format:

**Format:** `YOUR_ID Your work description`

*   **CORRECT:** `DEV01 Finished the login page`
*   **CORRECT:** `PK042 Started working on database`
*   **INCORRECT:** `DEV01 - Finished the login page` (Do not use the dash symbol `-`)

---

## � 3. Admin Commands (Owner & HR Only)

| Command | Action |
| :--- | :--- |
| **`/staff`** | Shows the list of registered employees and instructions. |
| **`/addstaff`**| Adds a new employee to the system (e.g., `/addstaff ID - Name - Dept`). |

---

## � 4. Features & Automation

- **Auto-Sync**: Every update is saved to the local Excel file and your Google Sheet in real-time.
- **Private Alerts**: The Owner and HR get a private message whenever someone posts an update.
- **Role-Based**: Only approved Owners and HR can use management commands.
