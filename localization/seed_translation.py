"""One-off public-string draft translation. Never used by the installed app.

Output remains explicitly machine-draft until reviewed. No credentials, geometry,
project files or user data are sent. Only upstream public UI resource strings.
"""
import concurrent.futures
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from catalog import collect

TOKEN = re.compile(r'\{[^{}]*\}|%(?:\d+\$)?[-+#0 .\d]*[a-zA-Z]|https?://\S+|<[^>]*>')

def placeholders(s):
    return sorted(TOKEN.findall(s))

def request(lines):
    query = '\n'.join(lines)
    url = 'https://translate.googleapis.com/translate_a/single?' + urllib.parse.urlencode({'client': 'gtx', 'sl': 'auto', 'tl': 'vi', 'dt': 't', 'q': query})
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=40) as r:
        data = json.load(r)
    return ''.join(x[0] or '' for x in data[0]).split('\n')

def translate(group):
    masks = []
    protected = []
    for source in group:
        tokens = []
        def mask(m):
            tokens.append(m[0])
            return 'ZXQ%04dQXZ' % (len(tokens) - 1)
        protected.append(TOKEN.sub(mask, source).replace('\n', ' ZXQLINEQXZ '))
        masks.append(tokens)
    last = None
    for attempt in range(4):
        try:
            output = request(protected)
            if len(output) != len(group):
                if len(group) > 1:
                    half = len(group) // 2
                    return {**translate(group[:half]), **translate(group[half:])}
                raise ValueError('Line count changed')
            result = {}
            for source, target, tokens in zip(group, output, masks):
                for i, token in enumerate(tokens):
                    target = re.sub(r'ZXQ\s*%04d\s*QXZ' % i, lambda m: token, target, flags=re.I)
                target = re.sub(r'\s*ZXQLINEQXZ\s*', '\n', target, flags=re.I)
                if placeholders(source) != placeholders(target):
                    raise ValueError('Placeholder mismatch: ' + source)
                result[source] = target
            return result
        except Exception as e:
            last = str(e)
            time.sleep(min(2 ** attempt, 8))
    if len(group) > 1:
        half = len(group) // 2
        return {**translate(group[:half]), **translate(group[half:])}
    print('UNTRANSLATED', repr(group[0]), last, flush=True)
    return {}

def main():
    bundles = collect(sys.argv[1])
    target = Path(sys.argv[2]); target.parent.mkdir(parents=True, exist_ok=True)
    values = sorted(set(v for b in bundles.values() for v in b.values()))
    translated = json.loads(target.read_text(encoding='utf-8')) if target.exists() else {}
    groups, group, size = [], [], 0
    for value in values:
        if value in translated: continue
        if not re.search(r'[A-Za-zÀ-ÿ]', value):
            translated[value] = value
            continue
        if size + len(value) > 1400 and group:
            groups.append(group); group, size = [], 0
        group.append(value); size += len(value) + 1
    if group: groups.append(group)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for i, result in enumerate(pool.map(translate, groups)):
            translated.update(result)
            target.write_text(json.dumps(translated, ensure_ascii=False, indent=2, sort_keys=True), encoding='utf-8')
            if i % 10 == 0: print(i, '/', len(groups), 'batches;', len(translated), '/', len(values), flush=True)
    missing = [v for v in values if v not in translated]
    target.with_suffix('.missing.json').write_text(json.dumps(missing, ensure_ascii=False, indent=2), encoding='utf-8')
    print('Draft:', len(translated), 'Missing:', len(missing))

if __name__ == '__main__': main()
