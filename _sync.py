#!/usr/bin/env python3
"""neuroustaz-games ішіндегі 1/ 2/ 3/ 4/ көшірмелерін түпнұсқа сайттардан жаңарту.
Қолдану: python3 _sync.py  (1class, 2class, kobeytu-alemi, bilim-araly реполары қатар тұруы керек)"""
import os, re, sys
ROOT = os.path.dirname(os.path.abspath(__file__))
UP = os.path.dirname(ROOT)
BACK = '<a class="tbtn" id="nuback" href="../" style="position:absolute;left:24px;top:24px;z-index:10;text-decoration:none;color:#1a2a4a;display:inline-flex;align-items:center">⬅ neuroUstaz</a>'
HIDE = "<script>if(new URLSearchParams(location.search).get('l')){document.addEventListener('DOMContentLoaded',()=>{const b=document.getElementById('nuback');b&&b.remove()})}</script>"

def class_site(src, salt_key):
    s = open(src, encoding='utf-8').read()
    a = s.index('<div id="gate">')
    b = s.index('<section id="home"', a)
    s = s[:a] + "<script>window.logout1=()=>{location.href='../'};</script>\n" + s[b:]
    old = '<button class="tbtn" style="position:absolute;left:24px;top:24px;z-index:10" onclick="logout1()">🚪 Шығу</button>'
    assert s.count(old) == 1, src
    s = s.replace(old, BACK)
    s = re.sub(r'<script[^>]*gc\.zgo\.at[^>]*></script>', '', s)  # статистиканы түпнұсқамен араластырмау
    return s.replace('</head>', HIDE + '\n</head>', 1)

def kobeytu(src):
    s = open(src, encoding='utf-8').read()
    s = s.replace('href="https://nurikiitu.github.io/neuroustaz-games/"', 'id="nuback" href="../?g=3"')
    fix = "<script>if(new URLSearchParams(location.search).get('l')){document.addEventListener('DOMContentLoaded',()=>{const b=document.getElementById('nuback');b&&(b.href='../?s=3')})}</script>"
    return s.replace('</head>', fix + '\n</head>', 1)

def bilim(src):
    s = open(src, encoding='utf-8').read()
    assert s.count('<div id="gate">') == 1
    s = s.replace('<div id="gate">', '<div id="gate" class="off">')
    s = s.replace('<button class="btn out" onclick="logout()">🚪 Шығу</button>',
                  '<a class="btn out" id="nuback" href="../" style="text-decoration:none;left:16px;right:auto">⬅ neuroUstaz</a>')
    return s.replace('</head>', HIDE + '\n</head>', 1)

JOBS = {'1': lambda: class_site(f'{UP}/1class/index.html', 'c1'),
        '2': lambda: class_site(f'{UP}/2class/index.html', 'c2'),
        # 'kobeytu': түпнұсқа сайт жабылды — ойынның негізгі нұсқасы осы репода, kobeytu/index.html
        '4': lambda: bilim(f'{UP}/bilim-araly/index.html')}
for d, f in JOBS.items():
    out = f()
    os.makedirs(f'{ROOT}/{d}', exist_ok=True)
    open(f'{ROOT}/{d}/index.html', 'w', encoding='utf-8').write(out)
    print(d, len(out))
