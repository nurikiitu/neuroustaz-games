#!/usr/bin/env python3
"""neuroustaz-games (1–4 сынып хабы) көшірмелерін түпнұсқа сайттардан жаңарту + хабтың өз қорғанысы.
Қолдану: python3 _sync.py   (1class, 2class, 3class, bilim-araly реполары қатар тұруы керек)
Хабтың кодтары: _codes.json  ({"КОД": {"n": "Аты-жөні", "x": 1?, "d": 4?, "e": ms?}})
Бір кодпен хабтың барлық бөліміне кіреді (salt 'nuhub:', sessionStorage 'hub_ok')."""
import os, re, json, hashlib
ROOT = os.path.dirname(os.path.abspath(__file__))
UP = os.path.dirname(ROOT)
SALT = 'nuhub:'
KEY = 'hub_ok'

def codes():
    raw = json.load(open(f'{ROOT}/_codes.json', encoding='utf-8'))
    out = {}
    for k, v in raw.items():
        k = k.strip().upper()
        h = hashlib.sha256((SALT + k).encode()).hexdigest()
        ent = {'n': v['n'], 'u': v.get('u', ''), 'k': k}
        for f in ('e', 'x', 'd'):
            if f in v: ent[f] = v[f]
        out[h] = ent
    return out

def cjs(C):
    def val(v):
        return json.dumps(v, ensure_ascii=False) if isinstance(v, str) else str(v)
    items = []
    for h, e in C.items():
        items.append("'%s':{%s}" % (h, ','.join(f"{k}:{val(v)}" for k, v in e.items())))
    return 'const C={' + ','.join(items) + '};'

BACK = '<a class="tbtn" id="nuback" href="../" style="position:absolute;left:24px;top:24px;z-index:10;text-decoration:none;color:#1a2a4a;display:inline-flex;align-items:center">⬅ neuroUstaz</a>'
OUT = ('<button class="tbtn" style="position:fixed;right:16px;top:16px;z-index:60" '
       'onclick="try{sessionStorage.removeItem(\'hub_ok\')}catch(e){};location.reload()">🚪 Шығу</button>')

def protect(s, salt, key, pre, C):
    """Түпнұсқа сайттың қорғанысын хабқа бейімдеу: өз salt-ы, өз сессия кілті, өз Firestore/GoatCounter белгісі, өз кодтары."""
    assert s.count(f"'{salt}'") == 1, salt
    s = s.replace(f"'{salt}'", f"'{SALT}'")
    s = s.replace(f"'{key}'", f"'{KEY}'")
    s = s.replace(f"'{pre}-kod-'", "'hub-kod-'").replace(f"'{pre}-'", "'hub-'")
    m = re.search(r"const C=\{'[0-9a-f]{64}':\{.*?\}\};", s, re.S)
    assert m, 'C not found'
    s = s[:m.start()] + cjs(C) + s[m.end():]
    s = re.sub(r'neuroUstaz · [0-9]-сынып</h2>', 'neuroUstaz · 1–4 сынып</h2>', s)
    return s

def class_copy(src, salt, key, pre, grade, C):
    s = open(src, encoding='utf-8').read()
    s = protect(s, salt, key, pre, C)
    old = '<button class="tbtn" style="position:absolute;left:24px;top:24px;z-index:10" onclick="logout1()">🚪 Шығу</button>'
    if old in s: s = s.replace(old, BACK)
    s = s.replace("c.href='kobeytu/'", "c.href='../kobeytu/'").replace("c.href='bilim/'", "c.href='../4/'")
    s = re.sub(r"b\.href=G\.n\+'/'", "b.href='../'+G.n+'/'", s)
    # бірден өз сыныбын ашу
    return s.replace('</body>', f"<script>try{{if(!new URLSearchParams(location.search).get('home'))openGrade({grade})}}catch(e){{}}</script>\n</body>", 1)

def hub_index(C):
    s = open(f'{UP}/3class/index.html', encoding='utf-8').read()
    s = protect(s, 'class3:', 'c3_ok', '3class', C)
    s = s.replace('<title>neuroUstaz · 3-сынып</title>', '<title>neuroUstaz · Ойындар</title>', 1)
    a = "const QP=new URLSearchParams(location.search);"
    i = s.index(a); j = s.index('</script>', i)
    s = s[:i] + a + """
const LOCK=(()=>{const q=QP.get('s')||location.hash.replace('#','');const n=+q;return GRADES.some(g=>g.n===n)?n:null})();
if(LOCK&&LOCK!==3)location.replace(LOCK+'/?l=1');
else if(LOCK===3){openGrade(3);$('#gradebar button').style.visibility='hidden';window.showGrades=()=>openGrade(3)}
else if(QP.get('g')==='3')openGrade(3);
""" + s[j:]
    return s.replace('</body>', OUT + '\n</body>', 1)

def bilim(C):
    s = open(f'{UP}/bilim-araly/index.html', encoding='utf-8').read()
    s = protect(s, 'bilimaraly:', 'ba_ok', '4class', C)
    s = s.replace('<button class="btn out" onclick="logout()">🚪 Шығу</button>',
                  '<a class="btn out" id="nuback" href="../" style="text-decoration:none;left:16px;right:auto">⬅ neuroUstaz</a>')
    return s

def kobeytu(C):
    p = f'{ROOT}/kobeytu/index.html'
    s = open(p, encoding='utf-8').read()
    hs = json.dumps(list(C.keys()))
    s = re.sub(r"/\*HUB\*/const HUBH=\[[^\]]*\];", "", s)
    a = "(function(){const H=["
    assert s.count(a) == 1
    s = s.replace(a, f"/*HUB*/const HUBH={hs};" + a)
    b = "if(H.includes(ok))g.style.display='none';"
    if b in s:
        s = s.replace(b, "let hb=null;try{hb=sessionStorage.getItem('hub_ok')}catch(e){}if(H.includes(ok)||HUBH.includes(hb))g.style.display='none';")
    return s

if __name__ == '__main__':
    C = codes()
    JOBS = {'1/index.html': lambda: class_copy(f'{UP}/1class/index.html', 'class1:', 'c1_ok', '1class', 1, C),
            '2/index.html': lambda: class_copy(f'{UP}/2class/index.html', 'class2:', 'c2_ok', '2class', 2, C),
            '3/index.html': lambda: class_copy(f'{UP}/3class/index.html', 'class3:', 'c3_ok', '3class', 3, C),
            '4/index.html': lambda: bilim(C),
            'bilim/index.html': lambda: bilim(C),
            'index.html': lambda: hub_index(C),
            'kobeytu/index.html': lambda: kobeytu(C)}
    for path, f in JOBS.items():
        s = f()
        open(f'{ROOT}/{path}', 'w', encoding='utf-8').write(s)
        print('ok', path, len(s))
