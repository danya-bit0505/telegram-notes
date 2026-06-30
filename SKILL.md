# telegram-notes skill

Claude Code skill `/telegram-notes` — fetches new messages from a Telegram bot, classifies each as **idea** or **task**, and appends them to separate markdown files. Supports both text and voice messages.

## Setup

Add `BOT_TOKEN` to `.env`:
```
BOT_TOKEN=your-telegram-bot-token
```

Whisper is installed automatically on first voice message. Requires `ffmpeg` in PATH for audio decoding:
- Windows: `winget install ffmpeg`
- Mac: `brew install ffmpeg`

## What it does

1. Calls `python run.py`
2. Fetches new messages via Telegram `getUpdates` API (offset tracked in `state.json`)
3. For **text messages**: classifies directly
4. For **voice messages**: downloads `.ogg` file, transcribes with local Whisper (`base` model), then classifies the transcript
5. Classification rules:
   - **idea** — strong signals (`что если`, `а вдруг`, `было бы`) or idea keywords (`идея`, `мысль`, `concept`) or ends with `?`
   - **task** — task keywords (`сделать`, `нужно`, `купить`, `todo`, `fix`) or no keywords
6. Appends results to `idea.md` and `task.md`

## Output

- `idea.md` — 💡 ideas (text or 🎤 voice transcript)
- `task.md` — ✅ tasks (text or 🎤 voice transcript)
- `state.json` — last processed update_id (auto-managed, not committed)

## Files

- `run.py` — fetch → transcribe (if voice) → classify → save
- `.env` — bot token (not committed)
- `.gitignore` — excludes `.env`, `state.json`
