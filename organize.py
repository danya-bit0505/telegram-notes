"""
Reads JSON from fetch.py stdout and writes organized notes.md
Usage: python fetch.py | python organize.py
"""
import json, sys, re
from collections import defaultdict
from datetime import datetime

CATEGORIES = {
    'todo':     r'\b(todo|сделать|задача|task|нужно|надо)\b',
    'idea':     r'\b(idea|идея|придумал|мысль|concept)\b',
    'link':     r'https?://',
    'reminder': r'\b(напомни|remind|не забыть|важно|deadline|дедлайн)\b',
}

def categorize(text):
    t = text.lower()
    for cat, pattern in CATEGORIES.items():
        if re.search(pattern, t, re.I):
            return cat
    return 'note'

def hashtags(text):
    return re.findall(r'#\w+', text)

def build_notes(msgs):
    by_date = defaultdict(lambda: defaultdict(list))
    for m in msgs:
        day = m['date'][:10]
        cat = categorize(m['text'])
        by_date[day][cat].append(m)

    cat_icons = {'todo': '✅', 'idea': '💡', 'link': '🔗', 'reminder': '⏰', 'note': '📝'}
    lines = ['# Telegram Notes', f'_Updated: {datetime.now().strftime("%Y-%m-%d %H:%M")}_', '']

    # Summary
    total = len(msgs)
    counts = defaultdict(int)
    for m in msgs:
        counts[categorize(m['text'])] += 1
    lines += ['## Summary', '']
    lines += [f'- Total messages: {total}']
    for cat, icon in cat_icons.items():
        if counts[cat]:
            lines.append(f'- {icon} {cat.capitalize()}: {counts[cat]}')
    lines.append('')

    # By date
    lines.append('## Notes by Date')
    for day in sorted(by_date.keys(), reverse=True):
        lines += ['', f'### {day}', '']
        for cat in ['todo', 'reminder', 'idea', 'link', 'note']:
            if cat not in by_date[day]:
                continue
            icon = cat_icons[cat]
            lines.append(f'**{icon} {cat.capitalize()}**')
            for m in by_date[day][cat]:
                time = m['date'][11:]
                tags = ' '.join(hashtags(m['text']))
                tag_str = f' `{tags}`' if tags else ''
                lines.append(f'- `{time}` {m["text"]}{tag_str}')
            lines.append('')

    # All tags index
    all_tags = defaultdict(list)
    for m in msgs:
        for tag in hashtags(m['text']):
            all_tags[tag].append(m)
    if all_tags:
        lines += ['## Tag Index', '']
        for tag in sorted(all_tags):
            lines.append(f'**{tag}** ({len(all_tags[tag])})')
            for m in all_tags[tag]:
                lines.append(f'- `{m["date"]}` {m["text"][:80]}')
        lines.append('')

    return '\n'.join(lines)

if __name__ == '__main__':
    msgs = json.loads(sys.stdin.read())
    if not msgs:
        print('No messages found.')
        sys.exit(0)
    notes = build_notes(msgs)
    out = 'telegram-notes/notes.md'
    with open(out, 'w', encoding='utf-8') as f:
        f.write(notes)
    print(notes)
    print(f'\nSaved to {out}')
