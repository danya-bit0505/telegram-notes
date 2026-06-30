import json, re, sys, os, tempfile, urllib.request
from datetime import datetime

DIR = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(DIR, 'state.json')

def load_token():
 env = os.path.join(DIR, '.env')
 with open(env) as f:
  for line in f:
   if line.startswith('BOT_TOKEN='):
    return line.strip().split('=',1)[1]
 raise ValueError('BOT_TOKEN not found in .env')

def save_category(name, emoji, msgs):
 if not msgs: return
 path = os.path.join(DIR, f'{name}.md')
 lines = [f'- `{m["date"]}` {m["text"]}' for m in msgs]
 if not os.path.exists(path):
  lines = [f'# {emoji} {name.capitalize()}s', ''] + lines
 with open(path, 'a', encoding='utf-8') as f:
  f.write('\n'.join(lines) + '\n')

def load_offset():
 if os.path.exists(STATE):
  with open(STATE) as f: return json.load(f).get('offset', 0)
 return 0

def save_offset(v):
 with open(STATE, 'w') as f: json.dump({'offset': v}, f)

def ensure_whisper():
 try:
  import whisper; return whisper
 except ImportError:
  import subprocess
  print('Installing openai-whisper...')
  subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'openai-whisper'])
  import whisper; return whisper

_model = None
def transcribe(token, file_id):
 global _model
 url = f'https://api.telegram.org/bot{token}/getFile?file_id={file_id}'
 with urllib.request.urlopen(url, timeout=10) as r:
  fp = json.loads(r.read())['result']['file_path']
 dl = f'https://api.telegram.org/file/bot{token}/{fp}'
 with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as tmp:
  tmp_path = tmp.name
 try:
  urllib.request.urlretrieve(dl, tmp_path)
  if _model is None:
   print('Loading Whisper model...')
   _model = ensure_whisper().load_model('base')
  return _model.transcribe(tmp_path)['text'].strip()
 finally:
  os.unlink(tmp_path)

def fetch_messages(token):
 url = f'https://api.telegram.org/bot{token}/getUpdates?limit=200&offset={load_offset()}'
 with urllib.request.urlopen(url, timeout=10) as r:
  updates = json.loads(r.read()).get('result', [])
 if not updates: return []
 save_offset(max(u['update_id'] for u in updates) + 1)
 msgs = []
 for u in updates:
  msg = u.get('message') or u.get('edited_message') or u.get('channel_post')
  if not msg: continue
  voice = msg.get('voice')
  if voice:
   try:
    text = transcribe(token, voice['file_id'])
    label = f'🎤 {text}'
   except Exception as e:
    print(f'Voice transcription failed: {e}'); continue
  else:
   text = (msg.get('text') or msg.get('caption','')).strip()
   if not text or text.startswith('/'): continue
   label = text
  s = msg.get('from') or {}
  msgs.append({'date': datetime.fromtimestamp(msg['date']).strftime('%Y-%m-%d %H:%M'),
               'text': label, 'from': s.get('username') or s.get('first_name','user')})
 return msgs

TASK = re.compile(r'\b(сделать|задача|нужно|надо|купить|заказать|todo|task|fix|добавить|исправить|написать|проверить)\b', re.I)
IDEA = re.compile(r'\b(идея|idea|мысль|concept|вариант|предложение|попробовать|интересно)\b', re.I)
STRONG = re.compile(r'\b(что если|а вдруг|было бы|хорошо бы|можно было)\b', re.I)

def classify(text):
 if STRONG.search(text): return 'idea'
 t, i = len(TASK.findall(text)), len(IDEA.findall(text))
 if t == 0 and i == 0: return 'idea' if '?' in text else 'task'
 return 'task' if t >= i else 'idea'

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
 print(f'💡 Ideas ({len(ideas)}):')
 for m in ideas: print(f'  [{m["date"]}] {m["text"]}')
 print(f'\n✅ Tasks ({len(tasks)}):')
 for m in tasks: print(f'  [{m["date"]}] {m["text"]}')
 print('\nSaved to: idea.md, task.md')

if __name__ == '__main__':
 main()
