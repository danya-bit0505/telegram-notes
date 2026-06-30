"""
Fetches messages from Telegram bot, classifies as idea/task, saves to separate files.
Usage: python telegram-notes/run.py
"""
import json, re, sys, os, urllib.request
from datetime import datetime

DIR = os.path.dirname(os.path.abspath(__file__))

def load_token():
    env_path = os.path.join(DIR, '.env')
    with open(env_path) as f:
        for line in f:
            if line.startswith('BOT_TOKEN='):
                return line.strip().split('=', 1)[1]
    raise ValueError('.env: BOT_TOKEN not found')

STATE_FILE = os.path.join(DIR, 'state.json')

def load_offset():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f).get('offset', 0)
    return 0

def save_offset(offset):
    with open(STATE_FILE, 'w') as f:
        json.dump({'offset': offset}, f)

def fetch_messages(token, limit=200):
    offset = load_offset()
    url = f'https://api.telegram.org/bot{token}/getUpdates?limit={limit}&offset={offset}'
    with urllib.request.urlopen(url, timeout=10) as r:
        updates = json.loads(r.read()).get('result', [])

    if not updates:
        return []

    # Save offset so these updates won't appear next time
    new_offset = max(upd['update_id'] for upd in updates) + 1
    save_offset(new_offset)

    msgs = []
    for upd in updates:
        msg = upd.get('message') or upd.get('edited_message') or upd.get('channel_post')
        if not msg:
            continue
        text = (msg.get('text') or msg.get('caption', '')).strip()
        if not text or text.startswith('/'):
            continue
        sender = msg.get('from') or {}
        msgs.append({
            'date': datetime.fromtimestamp(msg['date']).strftime('%Y-%m-%d %H:%M'),
            'from': sender.get('username') or sender.get('first_name', 'user'),
            'text': text,
        })
    return msgs

TASK_RE = re.compile(
    r'\b(сделать|задача|нужно|надо|купить|заказать|выполнить|todo|to-do|task|fix|implement|добавить|убрать|исправить|написать|настроить|проверить)\b',
    re.I
)
IDEA_RE = re.compile(
    r'\b(идея|idea|придумал|мысль|concept|вариант|предложение|что если|а вдруг|можно|было бы|хорошо бы|интересно|попробовать)\b',
    re.I
)

STRONG_IDEA_RE = re.compile(r'\b(что если|а что если|а вдруг|было бы|хорошо бы|можно было)\b', re.I)

def classify(text):
    if STRONG_IDEA_RE.search(text):
        return 'idea'
    task_score = len(TASK_RE.findall(text))
    idea_score = len(IDEA_RE.findall(text))
    if task_score == 0 and idea_score == 0:
        if '?' in text:
            return 'idea'
        return 'task'
    return 'task' if task_score >= idea_score else 'idea'

def save_category(name, emoji, msgs):
    if not msgs:
        return
    path = os.path.join(DIR, f'{name}.md')
    new_lines = [f'- `{m["date"]}` {m["text"]}' for m in msgs]
    if not os.path.exists(path):
        header = [f'# {emoji} {name.capitalize()}s', '']
        content = '\n'.join(header + new_lines) + '\n'
    else:
        content = '\n'.join(new_lines) + '\n'
    with open(path, 'a', encoding='utf-8') as f:
        f.write(content)
    return path

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    print('Fetching messages from Telegram...')
    token = load_token()
    msgs = fetch_messages(token)

    if not msgs:
        print('No messages found. Send something to your bot first.')
        return

    print(f'Found {len(msgs)} message(s). Classifying...\n')

    ideas = [m for m in msgs if classify(m['text']) == 'idea']
    tasks = [m for m in msgs if classify(m['text']) == 'task']

    save_category('idea', '💡', ideas)
    save_category('task', '✅', tasks)

    print(f'💡 Ideas  ({len(ideas)}):')
    for m in ideas:
        print(f'  [{m["date"]}] {m["text"]}')

    print(f'\n✅ Tasks  ({len(tasks)}):')
    for m in tasks:
        print(f'  [{m["date"]}] {m["text"]}')

    print(f'\nSaved to:')
    if ideas: print(f'  {os.path.join(DIR, "idea.md")}')
    if tasks:  print(f'  {os.path.join(DIR, "task.md")}')

if __name__ == '__main__':
    main()
