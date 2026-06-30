import json, urllib.request, os
from datetime import datetime

def load_token():
    env = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    with open(env) as f:
        for line in f:
            if line.startswith('BOT_TOKEN='):
                return line.strip().split('=', 1)[1]
    raise ValueError('.env: BOT_TOKEN not found')

def fetch(token, limit=200):
    url = f'https://api.telegram.org/bot{token}/getUpdates?limit={limit}'
    with urllib.request.urlopen(url, timeout=10) as r:
        return json.loads(r.read()).get('result', [])

def extract(updates):
    msgs = []
    for upd in updates:
        msg = upd.get('message') or upd.get('edited_message') or upd.get('channel_post')
        if not msg:
            continue
        text = msg.get('text') or msg.get('caption', '')
        if not text.strip():
            continue
        sender = msg.get('from') or {}
        msgs.append({
            'date': datetime.fromtimestamp(msg['date']).strftime('%Y-%m-%d %H:%M'),
            'from': sender.get('username') or sender.get('first_name', 'bot'),
            'text': text.strip(),
        })
    return msgs

if __name__ == '__main__':
    token = load_token()
    msgs = extract(fetch(token))
    print(json.dumps(msgs, ensure_ascii=False, indent=2))
