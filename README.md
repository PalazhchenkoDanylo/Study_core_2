<div align="center">

# 📚 Study Core

**A Telegram bot that helps students stay on top of their assignments.**
Track deadlines, get reminders, and never miss a submission again.

<br/>

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![aiogram](https://img.shields.io/badge/aiogram-3.7-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)](https://docs.aiogram.dev)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org)
[![License](https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge)](LICENSE)

</div>

---

## 🧠 What is Study Core?

Study Core is a Telegram bot built specifically for students who want to organize their academic workload without installing yet another app. Everything happens right inside Telegram — add a task, set a deadline, and the bot will remind you at the right time.

The bot is built with **Python** and the **aiogram 3** framework, follows clean **OOP principles**, and stores all data locally in **SQLite** — no external services required.

---

## ✨ Features

<table>
<tr>
<td width="50%">

**📝 Task Management**
- Add tasks with subject, title, description, and deadline
- Edit any task at any time
- Delete with confirmation prompt
- Mark as done — moves to archive

</td>
<td width="50%">

**📋 Views & Filtering**
- All active tasks sorted by deadline
- Upcoming tasks due in 48 hours
- Filter by subject via inline buttons
- Completed tasks archive (last 20)

</td>
</tr>
<tr>
<td width="50%">

**⏰ Smart Reminders**
- ⏰ 1 day before deadline
- 🔔 3 hours before deadline
- 🚨 30 minutes before deadline
- Auto-reset when deadline is edited

</td>
<td width="50%">

**📊 Statistics**
- Active and completed task counts
- Burning deadlines (next 24h)
- Task breakdown by subject

</td>
</tr>
</table>

---

## 🏗 Project Structure

```
study-core/
│
├── bot.py               # DeadlineBot     — entry point, wires all components
├── database.py          # Database        — all SQLite read/write operations
├── handlers.py          # TaskHandlers    — commands, FSM dialogs, callbacks
├── scheduler.py         # TaskScheduler   — background reminder job
├── formatter.py         # Formatter       — date parsing and message rendering
├── keyboard_builder.py  # KeyboardBuilder — reply and inline keyboard factory
├── states.py            # FSM state groups for add/edit flows
│
├── requirements.txt
├── .env.example
└── README.md
```

> Each file contains exactly one class with one responsibility. `bot.py` is the only place that knows about all components — it creates instances and injects dependencies. Swap the database engine, change the scheduler, or redesign the keyboards without touching anything else.

---

## 🧱 Architecture

```
DeadlineBot (bot.py)
│
├── Database (database.py)
│     └── aiosqlite — async SQLite driver
│
├── TaskHandlers (handlers.py)
│     ├── uses → Database
│     ├── uses → Formatter
│     └── uses → KeyboardBuilder
│
├── TaskScheduler (scheduler.py)
│     ├── uses → Database
│     └── uses → Formatter
│
├── Formatter (formatter.py)
│     └── stateless — static methods only, no dependencies
│
└── KeyboardBuilder (keyboard_builder.py)
      └── stateless — static methods only, no dependencies
```

> Dependencies flow in **one direction only**. No circular imports. No global state. No singletons.

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.11+**
- A Telegram bot token from [@BotFather](https://t.me/BotFather)

### Installation

**1. Clone the repository**

```bash
git clone https://github.com/your-username/study-core.git
cd study-core
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Configure environment**

```bash
cp .env.example .env
```

Open `.env` and paste your token:

```env
BOT_TOKEN=123456789:ABCdefGhIjKlmNopQrsTuVwXyz
DB_PATH=deadlines.db
```

> `DB_PATH` is optional — defaults to `deadlines.db` in the project folder.

**4. Run**

```bash
python bot.py
```

```
INFO - ✅ Study Core bot started!
```

Open Telegram, find your bot, and send `/start` 🎉

---

## 🎮 Commands

| Command | Description |
|:--------|:------------|
| `/start` | Show the welcome message and main menu |
| `/add` | Start the add task dialog |
| `/list` | Show all active tasks with action buttons |
| `/upcoming` | Show tasks due in the next 48 hours |
| `/done` | Show the completed tasks archive |
| `/stats` | Show statistics and subject breakdown |
| `/help` | Show available commands and date formats |

> All commands are also available via the **persistent reply keyboard** at the bottom of the chat.

---

## 📅 Supported Date Formats

```
31.12.2025 23:59      →  day.month.year  hour:minute
31.12 23:59           →  day.month       hour:minute  (current year assumed)
2025-12-31 23:59      →  ISO 8601 format
12/31/2025 23:59      →  US month/day/year format
```

---

## ⏰ How Reminders Work

The scheduler runs a background check every **5 minutes** and sends a notification when a task enters one of three windows:

| Time Remaining | Notification |
|:---------------|:-------------|
| 23h – 25h | ⏰ **1 day** until deadline |
| 2h 45m – 3h 15m | 🔔 **3 hours** until deadline |
| 25m – 35m | 🚨 **30 minutes** until deadline |

Each notification is sent **exactly once** per task. Editing the deadline resets all reminder flags automatically.

---

## 🛠 Tech Stack

| Library | Version | Purpose |
|:--------|:-------:|:--------|
| [aiogram](https://docs.aiogram.dev/) | 3.7.0 | Telegram Bot API framework |
| [aiosqlite](https://aiosqlite.omnilib.dev/) | 0.20.0 | Async SQLite database driver |
| [APScheduler](https://apscheduler.readthedocs.io/) | 3.10.4 | Background job scheduler |
| [python-dotenv](https://pypi.org/project/python-dotenv/) | 1.0.1 | Loading config from `.env` |

---

## 📦 Deployment

<details>
<summary><b>Option 1 — screen (quick)</b></summary>

```bash
screen -S study_core
cd /path/to/study-core
python bot.py
# Ctrl+A, then D to detach
```

Reattach later:

```bash
screen -r study_core
```

</details>

<details>
<summary><b>Option 2 — systemd (recommended for VPS)</b></summary>

Create `/etc/systemd/system/study_core.service`:

```ini
[Unit]
Description=Study Core Telegram Bot
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/path/to/study-core
ExecStart=/usr/bin/python3 bot.py
Restart=always
RestartSec=5
EnvironmentFile=/path/to/study-core/.env

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable study_core
sudo systemctl start study_core
```

View live logs:

```bash
journalctl -u study_core -f
```

</details>

---

## 🔮 Roadmap

- [ ] Priority levels — low / medium / high
- [ ] Weekly digest every Monday morning
- [ ] Custom reminder times per task
- [ ] Export tasks to PDF or CSV
- [ ] Shared task lists for study groups

---

## 📄 License

**MIT** — free to use, modify, and distribute.