#!/usr/bin/env python3
import re
from pathlib import Path

root = Path(__file__).resolve().parent.parent / '-ShortyTables'
pattern = re.compile(r"\sstyle=\"[^\"]*\"")
changed = []
for p in sorted(root.glob('*')):
    if p.is_file() and p.suffix.lower() in ['.html', '.txt', '.json']:
        text = p.read_text(encoding='utf-8')
        new = pattern.sub('', text)
        if new != text:
            p.write_text(new, encoding='utf-8')
            changed.append(str(p.relative_to(Path.cwd())))

if changed:
    print('Updated files:')
    for f in changed:
        print(f)
else:
    print('No inline styles found.')
