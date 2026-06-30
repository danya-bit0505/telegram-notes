# telegram-notes skill

Claude Code skill `/telegram-notes` — fetches new messages from a Telegram bot, classifies each as **idea** or **task**, and appends them to separate markdown files.

## Setup

Add `BOT_TOKEN` to `.env`:
```
BOT_TOKEN=your-telegram-bot-token
```

## What it does

1. Calls `python run.py`
2. Fetches new messages from the bot via Telegram `getUpdates` API
3. Classifies each message:
   - **idea** — contains idea keywords (`идея`, `мысль`, `concept`) or strong signals (`что если`, `а вдруг`, `было бы`) or ends with `?`
   - **task** — contains task keywords (`сделать`, `нужно`, `купить`, `todo`, `fix`, etc.) or no keywords at all
4. Appends results to `idea.md` and `task.md`
5. Saves `update_id` offset to `state.json` so next run only fetches new messages

## Output

- `idea.md` — 💡 ideas, one per line with timestamp
- `task.md` — ✅ tasks, one per line with timestamp
- `state.json` — tracks last processed update_id (auto-managed, not committed)

## Files

- `run.py` — main script: fetch → classify → save to idea.md / task.md
- `.env` — bot token (not committed)
- `.gitignore` — excludes `.env`, `state.json`
