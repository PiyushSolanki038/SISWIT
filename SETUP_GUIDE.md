# 🤖 Employee Work Update Bot — Setup Guide

Complete step-by-step guide to get your bot running locally and on Railway.

---

## Step 1: Create Your Telegram Bot

1. Open Telegram and search for **@BotFather**
2. Send `/newbot`
3. Enter a **name** (e.g., `Work Update Bot`)
4. Enter a **username** ending in `bot` (e.g., `mycompany_updates_bot`)
5. BotFather gives you a **token** like `7123456789:AAH...` — copy it, you'll need it

---

## Step 2: Get Chat IDs for Owner & HR

1. Open Telegram and search for **@userinfobot**
2. Send `/start` — it will reply with your **Chat ID** (a number like `923456789`)
3. Ask your HR person to do the same and share their Chat ID with you
4. These are your **OWNER_CHAT_ID** and **HR_CHAT_ID**

---

## Step 3: Add Bot to Your Telegram Group

1. Open your Telegram group
2. Tap on the group name → **Add Members**
3. Search for your bot's username and add it
4. Go to group settings → **Administrators** → **Add Administrator**
5. Select your bot and give it **Send Messages** permission
6. Save

> ⚠️ The bot **must be an admin** in the group to read all messages.

---

## Step 4: Run Locally (Windows/Mac/Linux)

### 4.1 Install Python
- Download Python 3.10+ from [python.org](https://python.org)
- During install, ✅ check **"Add Python to PATH"**

### 4.2 Install Dependencies
Open terminal/command prompt in the project folder and run:
```bash
pip install -r requirements.txt
```

### 4.3 Set Your Configuration
Open `config.py` and replace the defaults:
```python
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"    # ← Paste token from BotFather
OWNER_CHAT_ID = "923456789"          # ← Your Chat ID
HR_CHAT_ID = "987654321"             # ← HR's Chat ID
```

Or use environment variables (recommended):
```bash
# Windows (Command Prompt)
set BOT_TOKEN=7123456789:AAH...
set OWNER_CHAT_ID=923456789
set HR_CHAT_ID=987654321

# Windows (PowerShell)
$env:BOT_TOKEN="7123456789:AAH..."
$env:OWNER_CHAT_ID="923456789"
$env:HR_CHAT_ID="987654321"

# Linux/Mac
export BOT_TOKEN="7123456789:AAH..."
export OWNER_CHAT_ID="923456789"
export HR_CHAT_ID="987654321"
```

### 4.4 Run the Bot
```bash
python bot.py
```

You should see:
```
  🤖 Employee Work Update Bot
  📋 Format: EMP_ID - DEPT - Work description
  🟢 Bot is running... Press Ctrl+C to stop
```

### 4.5 Test It
Go to your Telegram group and send:
```
PK042 - SALES - Aaj maine 3 client calls ki aur 2 deals close ki
```

The bot will:
- ✅ Reply in the group with confirmation
- 📊 Save to `employee_updates.xlsx`
- 📩 Send notifications to Owner & HR

---

## Step 5: Google Sheets Setup (Optional)

### 5.1 Create a Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **Select a Project** → **New Project**
3. Name it (e.g., `Work Bot`) → **Create**

### 5.2 Enable APIs
1. Go to **APIs & Services** → **Library**
2. Search and enable:
   - **Google Sheets API**
   - **Google Drive API**

### 5.3 Create Service Account
1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **Service Account**
3. Name it (e.g., `work-bot-service`) → **Create and Continue**
4. Skip the optional steps → **Done**
5. Click on the service account you just created
6. Go to **Keys** tab → **Add Key** → **Create New Key** → **JSON**
7. A `.json` file downloads — rename it to `service_account.json`
8. Place it in the same folder as `bot.py`

### 5.4 Create and Share Google Sheet
1. Go to [Google Sheets](https://sheets.google.com) → **Create new spreadsheet**
2. Name it (e.g., `Employee Updates`)
3. Copy the **Sheet ID** from the URL:
   ```
   https://docs.google.com/spreadsheets/d/SHEET_ID_IS_HERE/edit
   ```
4. Click **Share** → paste the service account email (found in `service_account.json` under `client_email`) → **Editor** → **Share**

### 5.5 Configure Sheet ID
In `config.py`, set:
```python
GOOGLE_SHEET_ID = "your_sheet_id_here"
```

Or as env variable:
```bash
set GOOGLE_SHEET_ID=your_sheet_id_here
```

---

## Step 6: Deploy on Railway (Free Hosting)

### 6.1 Push to GitHub
1. Create a **GitHub repository**
2. Push all project files to it:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
   git push -u origin main
   ```

> ⚠️ Do NOT push `service_account.json` to GitHub! Add it to `.gitignore`.

### 6.2 Deploy on Railway
1. Go to [railway.app](https://railway.app/) → Sign in with GitHub
2. Click **New Project** → **Deploy from GitHub Repo**
3. Select your repository
4. Railway will detect the `Procfile` automatically

### 6.3 Set Environment Variables
Go to your Railway project → **Variables** tab → Add these:

| Variable | Value |
|----------|-------|
| `BOT_TOKEN` | Your bot token from BotFather |
| `OWNER_CHAT_ID` | Your Chat ID |
| `HR_CHAT_ID` | HR's Chat ID |
| `GOOGLE_SHEET_ID` | Your Google Sheet ID (or leave empty) |
| `GOOGLE_CREDS_JSON` | Full contents of `service_account.json` |

> 💡 For `GOOGLE_CREDS_JSON`, open `service_account.json`, copy **all** the text, and paste it as the value. The bot will automatically create the file on Railway.

### 6.4 Deploy
Click **Deploy** — Railway will install dependencies and start the bot!

---

## 📋 Message Format Reference

Employees send updates in this format:
```
EMPLOYEE_ID - DEPARTMENT - Work description here
```

**Examples:**
```
PK042 - SALES - Aaj maine 3 client calls ki aur 2 deals close ki
EMP001 - IT - Fixed server issues and deployed new update
HR003 - HR - Conducted 5 interviews for developer position
MKT007 - MARKETING - Created social media campaign for product launch
```

**Rules:**
- Employee ID can be letters + numbers (e.g., PK042, EMP001, A1)
- Department can be letters + numbers + spaces (e.g., SALES, IT SUPPORT)
- Separated by ` - ` (space-dash-space)
- Work description is everything after the second dash
- All other messages are silently ignored

---

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| Bot doesn't respond | Make sure bot is admin in the group |
| Excel not saving | Check file permissions in the folder |
| Google Sheets error | Verify Sheet ID and service account sharing |
| Notifications not received | Double-check Chat IDs with @userinfobot |
| Bot token error | Re-copy token from @BotFather |
| Railway deployment fails | Check logs in Railway dashboard |

---

## 📁 Project Files

```
telegram/
├── bot.py              # Main bot logic
├── config.py           # Configuration (env vars + defaults)
├── requirements.txt    # Python dependencies
├── Procfile            # Railway deployment config
├── SETUP_GUIDE.md      # This file
└── service_account.json # Google credentials (not in git)
```
