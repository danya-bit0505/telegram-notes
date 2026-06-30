Fetch messages from the Telegram bot, classify each as idea or task, save to separate files.

Steps:
1. Run `python run.py` from the telegram-notes directory
2. Show the user the results:
   - 💡 Ideas list
   - ✅ Tasks list
3. Mention saved files: `idea.md` and `task.md`
4. If no messages: ask user to send something to the bot first
5. If network error: suggest enabling VPN (Telegram API may be blocked)
6. If token error: check BOT_TOKEN in `.env`

How classification works:
- Task keywords: сделать, нужно, надо, купить, todo, fix, добавить, исправить, etc.
- Idea keywords: идея, мысль, что если, можно было бы, concept, etc.
- Phrases like "что если" / "а вдруг" always → idea (strong signal)
- Messages with "?" default to idea; everything else defaults to task
- Messages starting with "/" (bot commands) are ignored

Output files (append-only, never overwritten):
- `idea.md` — all ideas, one per line with timestamp
- `task.md` — all tasks, one per line with timestamp

State:
- `state.json` — stores the last processed update_id offset so reruns only fetch new messages
