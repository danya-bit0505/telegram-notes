Fetch new messages from the Telegram bot (text and voice), classify each as idea or task, save to separate files.

Steps:
1. Run `python run.py` from the telegram-notes directory
2. If openai-whisper is not installed and there are voice messages, the script installs it automatically
3. Show the user the results:
   - 💡 Ideas list (text or 🎤 voice transcript)
   - ✅ Tasks list (text or 🎤 voice transcript)
4. Mention saved files: `idea.md` and `task.md`

If errors occur:
- No messages: ask user to send something to the bot first
- Voice transcription fails: check that ffmpeg is installed (`winget install ffmpeg`)
- Network error: suggest enabling VPN (Telegram API may be blocked)
- Token error: check BOT_TOKEN in `.env`

How it works:
- Text messages: classified directly by keyword scoring
- Voice messages: downloaded as .ogg, transcribed locally with Whisper (base model), then classified
- Strong idea signals: `что если`, `а вдруг`, `было бы` → always idea
- Task keywords: сделать, нужно, купить, todo, fix, добавить, etc.
- Idea keywords: идея, мысль, concept, вариант, etc.
- Messages with `?` and no keywords → idea; everything else → task
- Voice transcripts are prefixed with 🎤 in output files
- Processed update_id saved to `state.json` — reruns only fetch new messages
