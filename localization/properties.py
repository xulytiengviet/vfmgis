"""Java Properties reader/writer; preserve escaped keys and continuation lines."""
import re

def unescape(value):
    def convert(m):
        token = m.group(1)
        if token.startswith('u'):
            return chr(int(token[1:], 16))
        return {'n': '\n', 'r': '\r', 't': '\t', 'f': '\f'}.get(token, token)
    return re.sub(r'\\(u[0-9a-fA-F]{4}|.)', convert, value)

def loads(data):
    if isinstance(data, bytes):
        data = data.decode('iso-8859-1')
    result, pending = {}, ''
    for raw in data.splitlines():
        line = pending + raw.lstrip(' \t\f')
        if (len(line) - len(line.rstrip('\\'))) % 2:
            pending = line[:-1]
            continue
        pending = ''
        if not line or line[0] in '#!':
            continue
        match = re.match(r'((?:\\.|[^=:\s])*)\s*(?:[=:]\s*)?(.*)$', line)
        if match:
            result[unescape(match[1])] = unescape(match[2])
    if pending:
        raise ValueError('Unterminated properties continuation')
    return result

def escape(value, key=False):
    out = ''
    for i, ch in enumerate(value):
        if ch == '\\': out += '\\\\'
        elif ch == '\n': out += '\\n'
        elif ch == '\r': out += '\\r'
        elif ch == '\t': out += '\\t'
        elif ord(ch) > 126 or ord(ch) < 32: out += '\\u%04x' % ord(ch)
        elif (key and ch in ' =:#!') or (i == 0 and ch == ' '): out += '\\' + ch
        else: out += ch
    return out

def dumps(values):
    return ('# VFMGIS Vietnamese localization; GPL-3.0-or-later\n' + '\n'.join(escape(k, True) + '=' + escape(v) for k, v in sorted(values.items())) + '\n').encode('ascii')
