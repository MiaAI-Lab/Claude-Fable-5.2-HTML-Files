"""Build the static gallery from the numbered HTML and prompt files."""
from pathlib import Path
import html
import re

ROOT = Path(__file__).resolve().parent.parent


def studies():
    result = []
    for page in sorted(ROOT.glob('[0-9][0-9][0-9]-*.html')):
        source = page.with_suffix('.txt')
        text = source.read_text(encoding='utf-8')
        fields = re.split(r'^(TITLE|PROMPT|DESCRIPTION|VISUAL TECHNIQUES)\s*\n', text, flags=re.M)
        sections = dict(zip(fields[1::2], (value.strip() for value in fields[2::2])))
        for key in ('TITLE', 'PROMPT', 'DESCRIPTION'):
            if not sections.get(key):
                raise ValueError(f'{source.name}: missing {key}')
        result.append(dict(file=page.name, stem=page.stem, number=page.name[:3],
                           title=sections['TITLE'], prompt=sections['PROMPT'],
                           description=sections['DESCRIPTION'], source=source.name))
    if not result:
        raise ValueError('No studies found')
    return result


def build():
    items = studies()
    cards = []
    esc = html.escape
    for item in items:
        f, title, num = esc(item['file']), esc(item['title']), item['number']
        cards.append(f'''<article class="card" id="study-{num}">
  <a class="thumb" href="{f}" target="_blank" rel="noopener" aria-label="Open {title}">
    <img src="thumbs/{esc(item['stem'])}.jpg" alt="{title} screenshot" width="1440" height="1000" loading="lazy" decoding="async">
    <span class="preview-missing" hidden>Screenshot will appear after the gallery is published.<br><span>Open {title} ↗</span></span>
  </a>
  <div class="card-top">
    <span class="num">{num}</span>
    <div class="main"><h2><a href="{f}" target="_blank" rel="noopener">{title}</a></h2>
    <p class="desc">{esc(item['description'])}</p></div>
    <div class="actions"><a class="btn btn-open" href="{f}" target="_blank" rel="noopener" aria-label="Open {title}">↗ Open</a>
    <button class="btn btn-prompt" type="button" aria-expanded="false" aria-controls="prompt-{num}">☰ Prompt</button></div>
  </div>
  <div class="prompt-panel" id="prompt-{num}" hidden><h3>Original prompt</h3>
    <div class="prompt-text">{esc(item['prompt'])}</div>
    <a class="file-name" href="{esc(item['source'])}" target="_blank" rel="noopener">{esc(item['source'])}</a>
  </div>
</article>''')
    template = (ROOT / 'scripts/gallery-template.html').read_text(encoding='utf-8')
    output = template.replace('<!-- CARDS -->', '\n'.join(cards)).replace('{{COUNT}}', str(len(items)))
    (ROOT / 'index.html').write_text(output, encoding='utf-8')
    print(f'Built index.html with {len(items)} studies and complete original prompts.')


if __name__ == '__main__':
    build()
