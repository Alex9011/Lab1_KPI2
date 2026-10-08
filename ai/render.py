"""Render this project's Mermaid ER subset to SVG, using only Python stdlib.

Cardinality labels use 1 and 0..*; the declarative source remains Mermaid.
Usage from project root: python ai/render.py
"""
from pathlib import Path
import re
from html import escape

root = Path(__file__).resolve().parents[1]
text = (root / 'diagram.mmd').read_text(encoding='utf-8')
entities = {}
for name, block in re.findall(r'^    (\w+) \{\n(.*?)^    \}', text, re.M | re.S):
    attrs = []
    for line in block.strip().splitlines():
        m = re.fullmatch(r'\s*(\w+)\s+(\w+)(?:\s+(PK|FK|UK))?(?:\s+"([^"]*)")?\s*', line)
        if not m:
            raise ValueError('Unsupported attribute: ' + line)
        attrs.append(m.groups(default=''))
    entities[name] = attrs
relations = re.findall(r'^    (\w+) ([|o}{.]+) (\w+) : (\w+)$', text, re.M)
layout = {'Author': (40, 90, 350), 'Book': (590, 90, 410),
          'Copy': (1200, 90, 550), 'Member': (40, 610, 530), 'Loan': (950, 520, 800)}
assert set(entities) == set(layout), 'Layout supports the five project entities.'
assert len(relations) == 4
h = lambda name: 48 + 46 * len(entities[name])
svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="900" viewBox="0 0 1800 900">',
       '<title>ER-модель бібліотеки</title>',
       '<desc>Сутності, атрибути та кардинальності автоматично прочитано з diagram.mmd.</desc>',
       '<style>text{font-family:Arial,DejaVu Sans,sans-serif;fill:#152b40} .edge{stroke:#486477;stroke-width:2;stroke-dasharray:6 4;fill:none} .field{font-size:16px} .small{font-size:14px} .card{font-size:18px;font-weight:bold}</style>',
       '<rect width="1800" height="900" fill="#fff"/>']
def label(x,y,s,cls='field',anchor='start'):
    svg.append(f'<text x="{x}" y="{y}" class="{cls}" text-anchor="{anchor}">{escape(s)}</text>')
routes = {
 ('Book', 'Author'): ((590,170), (390,170), 'авторство'),
 ('Book', 'Copy'): ((1000,170), (1200,170), 'примірники'),
 ('Member', 'Loan'): ((570,710), (950,710), 'видачі'),
 ('Copy', 'Loan'): ((1470,90+h('Copy')), (1470,520), 'історія видач'),
}
card = {'||': '1', '}o': '0..*', 'o{': '0..*'}
for a, notation, b, name in relations:
    (x1,y1),(x2,y2),caption = routes[(a,b)]
    left,right=notation.split('..')
    c1,c2=card[left],card[right]
    svg.append(f'<path class="edge" d="M{x1} {y1} L{x2} {y2}"/>')
    if y1==y2:
        d=1 if x2>x1 else -1
        label(x1+d*30,y1+25,c1,'card','middle')
        label(x2-d*30,y2+25,c2,'card','middle')
        label((x1+x2)/2,y1-16,caption,'small','middle')
    else:
        label(x1+14,y1+28,c1,'card')
        label(x2+14,y2-15,c2,'card')
        label(x1+14,(y1+y2)/2,caption,'field')
for name, attrs in entities.items():
    x,y,w=layout[name]; height=h(name)
    svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{height}" rx="5" fill="#f7fafc" stroke="#345a73" stroke-width="2"/>')
    svg.append(f'<path d="M{x} {y+48}H{x+w}" stroke="#345a73"/>')
    label(x+16,y+31,name,'card')
    # Fixed schema columns; remaining width contains optional descriptions.
    for i,(typ,field,key,comment) in enumerate(attrs):
        yy=y+48+i*46
        if i:
            svg.append(f'<path d="M{x} {yy}H{x+w}" stroke="#cedae2"/>')
        label(x+12,yy+29,typ,'small')
        label(x+98,yy+29,field)
        label(x+272,yy+29,key,'small')
        if comment:
            # Keep metadata readable within the wider entity boxes.
            if w<500:
                label(x+w-12,y+30,comment,'small','end')
            else:
                label(x+315,yy+29,comment,'small')
svg.append('</svg>')
(root / 'diagram.svg').write_text('\n'.join(svg),encoding='utf-8')
print('SVG generated from diagram.mmd: 5 entities, 17 attributes, 4 relationships.')
