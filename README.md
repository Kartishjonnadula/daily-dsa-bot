# Daily DSA

A lightweight Discord bot that delivers two globally shared DSA problems every day to registered Discord users.

The goal is to create a simple **LeetCode Daily-style experience inside Discord**, using a continuously maintained problem list.

## Features

- 🧠 Two DSA problems every day
- 🌍 One global problem pair for everyone
- 🔄 Global problem rotation with no repeats within a rotation
- 👤 Users register themselves in a Discord channel
- 📢 Registered users are mentioned when daily problems are posted
- 📺 Multiple users can register in the same channel
- 🔀 Users can move their registration to another channel
- ❌ Users can unregister at any time
- 💾 SQLite persistence for registrations and rotation history
- 📝 `problems.json` is the source of truth for problem data
- ➕ New problem IDs automatically become available
- 📅 Daily delivery at 12:00 PM IST

## Commands

| Command | Description |
|---|---|
| `/register` | Register yourself for daily problems in the current channel |
| `/unregister` | Stop receiving daily problems in the current server |
| `/problems` | Show today's two globally selected problems |
| `/rotation` | Show current rotation status |
| `/status` | Show registered user count |
| `/ping` | Check whether the bot is online |

## How It Works

### Registration

When a user runs `/register`, the bot stores:

```text
user_id
guild_id
channel_id
```

The user is then mentioned in that channel when the daily problems are posted.

If the same user registers again in another channel in the same server, their channel is updated.

### Global Problems

Problems are **not selected per user or per channel**.

Every registered channel receives exactly the same two problems.

```text
#dsa
@Alice @Bob
    ↓
Two Sum
3Sum

#leetcode
@Charlie
    ↓
Two Sum
3Sum
```

The pair is selected once globally and reused everywhere.

### Rotation

Problems use a stable ID, preferably the LeetCode problem slug:

```json
{
  "id": "two-sum",
  "title": "Two Sum",
  "difficulty": "Easy",
  "category": "Arrays & Hashing",
  "url": "https://leetcode.com/problems/two-sum/"
}
```

The database records problem IDs already used in the current rotation.

With 150 problems:

```text
150 problems
    ↓
2 problems/day
    ↓
75 days
    ↓
Rotation complete
    ↓
New rotation starts
```

Rotation history is preserved in SQLite.

### Updating Problems

`neet_code/problems.json` is the source of truth.

You can add new problems at any time. Newly added IDs are automatically considered unused in the current rotation.

Removing a problem from `problems.json` does not delete historical rotation records.

## Project Structure

```text
Daily DSA/
│
├── bot.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── LICENSE
│
└── neet_code/
    ├── __init__.py
    ├── database.py
    ├── problems.py
    ├── problems.json
    ├── rotation.py
    └── scheduler.py
```

## Requirements

- Python 3.13+
- A Discord application/bot
- A Discord server where the bot can view and send messages

## Local Setup

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd Daily-DSA
```

### 2. Create a virtual environment

Windows:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure the Discord token

Copy `.env.example` to `.env`:

```env
DISCORD_TOKEN=your_discord_bot_token
```

**Never commit `.env` to GitHub.**

### 5. Start the bot

```bash
python bot.py
```

## Discord Permissions

The bot needs enough permissions to:

- View registered channels
- Send messages
- Mention registered users

## Database

The bot uses SQLite:

```text
neet_code/neetcode.db
```

This file is generated automatically and should not be committed to Git.

### `registrations`

Stores notification registrations:

```text
user_id
guild_id
channel_id
registered_at
```

### `rotations`

Stores rotation history:

```text
id
started_at
completed_at
```

### `rotation_problems`

Stores problem IDs used in each rotation:

```text
rotation_id
problem_id
used_at
```

### `daily_problems`

Stores the exact pair selected for each date. This guarantees `/problems` and the scheduled message use the same pair.

## Deployment

The bot can run on a small Python/Pterodactyl-style hosting instance.

Start command:

```bash
python bot.py
```

Required environment variable:

```text
DISCORD_TOKEN
```

Do not upload `.env` or `neet_code/neetcode.db`.

## Security

Never commit:

- Discord bot tokens
- `.env`
- Database files
- Hosting credentials
- API keys

If a Discord bot token is exposed, regenerate it immediately in the Discord Developer Portal.

## Development

For local testing, the scheduler can temporarily be changed to run shortly after startup.

Restore the production schedule of **12:00 PM IST** before deployment.

## License

This project is licensed under the MIT License.

## Disclaimer

Daily DSA is an independent community project and is not affiliated with LeetCode or NeetCode.
