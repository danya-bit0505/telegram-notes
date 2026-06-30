# telegram-notes

Claude Code skill that fetches messages from a Telegram bot, classifies them as ideas or tasks, and saves results to separate markdown files.

## Usage

```
/telegram-notes
```

## Setup

1. Create a Telegram bot via [@BotFather](https://t.me/BotFather) and get your token
2. Create a `.env` file in this directory:
   ```
   BOT_TOKEN=your-telegram-bot-token
   ```
3. Install dependencies: none (uses Python standard library only)
4. Send messages to your bot in Telegram
5. Run `/telegram-notes` in Claude Code

## How it works

- Fetches up to 200 new messages from the bot via Telegram `getUpdates` API
- Classifies each message as **idea** or **task** using keyword scoring:
  - Strong idea signals: `что если`, `а вдруг`, `было бы`, `можно было`
  - Task keywords: `сделать`, `нужно`, `купить`, `todo`, `fix`, `добавить`, etc.
  - Idea keywords: `идея`, `мысль`, `concept`, `предложение`, etc.
  - Messages with `?` default to idea; everything else defaults to task
- Saves results to `idea.md` and `task.md` (append-only)
- Tracks processed messages in `state.json` via `update_id` offset — reruns only fetch new messages

## Output files

| File | Contents |
|---|---|
| `idea.md` | 💡 Ideas, one per line with timestamp |
| `task.md` | ✅ Tasks, one per line with timestamp |
| `state.json` | Last processed update_id (auto-managed) |

## Files

| File | Purpose |
|---|---|
| `run.py` | Main script: fetch, classify, save |
| `.env` | Bot token (not committed) |
| `state.json` | Offset state (not committed) |
| `.gitignore` | Excludes `.env`, `state.json`, output files |
