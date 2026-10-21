# -*- coding: utf-8 -*-
"""يقرأ تقارير md (01..13) والمخطط المعتمد، ويدمجها مع البيانات اليدوية، ويولّد data.json.
الرموز التقنية (خ1، ز1، ق-04، ن-01 ...) تبقى في حقول المعرّف فقط، وتُحوَّل في كل نص مقروء إلى العنوان الكامل."""
import re, glob, os, json, datetime
from common import *

REPORTS = sorted(glob.glob(os.path.join(ROOT, '[0-9][0-9]_*.md')))
REP = {os.path.basename(p)[:2]: p for p in REPORTS}


def read(p):
    with open(p, encoding='utf-8') as f:
        return f.read()


def strip_md(s):
    return re.sub(r'\*\*|`', '', s).strip()


def tokens(text):
    """رموز الإشكاليات الواردة في نص (مع توسيع المدى)."""
    out = []
    for m in ISSUE_RE.finditer(text or ''):
        L, a, L2, b = m.group(2), int(m.group(3)), m.group(4), m.group(5)
        if L not in GROUPS:
            continue
        if b is None:
            out.append(f'{L}{a}')
        else:
            out += [f'{L}{i}' for i in range(a, int(b) + 1)]
    seen = []
    for t in out:
        if t not in seen:
            seen.append(t)
    return seen


# ------------------------------------------------------------------ المخطط المعتمد
def parse_outline():
    lines = read(OUTLINE).split('\n')
    start = next(i for i, l in enumerate(lines) if l.startswith('## رابعًا'))
    end = next(i for i, l in enumerate(lines) if l.startswith('## خامسًا'))
    seg = lines[start:end]
    chapters = []
    cur = None
    for l in seg:
        m = re.match(r'^### (.+)$', l)
        if m:
            cur = {'title': m.group(1).strip(), 'raw': []}
            chapters.append(cur)
            continue
        if cur is not None:
            cur['raw'].append(l)
    keys = ['ch1', 'ch2', 'ch3', 'ch4', 'ch5', 'conc', 'app']
    assert len(chapters) == 7, [c['title'] for c in chapters]
    outl = []
    for key, ch in zip(keys, chapters):
        raw = [l for l in ch['raw'] if l.strip() and not l.startswith('>') and not l.startswith('---')]
        sectioned = any(re.match(r'^- \*\*المبحث', l) for l in raw)
        c = {'id': key, 'title': ch['title'], 'sections': []}
        if not sectioned:
            sec = {'id': f'{key}-0', 'title': '', 'items': []}
            c['sections'].append(sec)
            n = 0
            for l in raw:
                if re.match(r'^- ', l):
                    n += 1
                    t = strip_md(l[2:])
                    sec['items'].append({'id': f'{key}-0-{n}', 'title': t, 'star': '', 'code': '', 'details': []})
                elif re.match(r'^\s+- ', l) and sec['items']:
                    sec['items'][-1]['details'].append(strip_md(l.strip()[2:]))
        else:
            sec = None
            si = 0
            for l in raw:
                if re.match(r'^- \*\*المبحث', l):
                    si += 1
                    sec = {'id': f'{key}-{si}', 'title': strip_md(l[2:]), 'items': []}
                    c['sections'].append(sec)
                    j = 0
                elif re.match(r'^- ', l) and sec is not None:
                    # بند على مستوى الفصل (خلاصة الفصل)
                    t = strip_md(l[2:])
                    last = {'id': f'{key}-end', 'title': t, 'star': '', 'code': '', 'details': []}
                    c.setdefault('end', last)
                elif re.match(r'^\s+- ', l) and sec is not None:
                    t = strip_md(l.strip()[2:])
                    if t.startswith('تمهيد'):
                        sec['items'].append({'id': f'{key}-{si}-0', 'title': t, 'star': '', 'code': '', 'details': []})
                    else:
                        j += 1
                        m = re.search(r'\(([خزطنحف]\d)\)\s*([★○])?\s*(\*\(.*?\)\*)?\s*$', t)
                        code, star = '', ''
                        if m:
                            code, star = m.group(1), (m.group(2) or '')
                            t = t[:m.start()].rstrip()
                            tail = re.sub(r'[*]', '', m.group(3) or '')
                        else:
                            tail = ''
                        sec['items'].append({'id': code or f'{key}-{si}-{j}', 'title': (t + ' ' + tail).strip(), 'base': t, 'star': star, 'code': code, 'details': []})
        outl.append(c)
        if 'end' in c:
            c['sections'][-1]['items'].append(c.pop('end'))
    return outl


def issue_title_map(outl):
    for c in outl:
        for s in c['sections']:
            for it in s['items']:
                if it['code']:
                    t = re.sub(r'^المطلب [^:]+:\s*', '', it.get('base', it['title'])).rstrip('.')
                    ISSUE_TITLES[it['code']] = t


def parse_outline_tables():
    """جداول القائمة الموسعة: السند القانوني والشاهد والتوصية."""
    out = {}
    for l in read(OUTLINE).split('\n'):
        if re.match(r'^\|\s*[خزطنحف]\d\s*\|', l):
            cells = [c.strip() for c in l.strip().strip('|').split('|')]
            out[cells[0]] = {'title': cells[1], 'law': strip_md(cells[2]), 'witness': strip_md(cells[3]), 'rec': cells[4]}
    return out


# ------------------------------------------------------------------ الموازن والناسب
def parse_muwazin():
    res = {}
    for l in read(REP['04']).split('\n'):
        m = re.match(r'^\|\s*([خزطنحف]\d)\s+(.+?)\s*([★○])\s*\|\s*([\d.]+)k\s*\|\s*(\S+)\s*\|\s*(.+?)\s*\|\s*$', l)
        if m:
            res[m.group(1)] = {'size': m.group(4), 'label': m.group(5), 'missing': m.group(6)}
    assert len(res) == 22, len(res)
    return res


def parse_nasib():
    txt = read(REP['05']).split('\n')
    scores, missing = {}, {}
    for l in txt:
        m = re.match(r'^\|\s*([نحف]\d)\s+(.+?)\s*\|\s*(\d)\s*\|\s*(\d)\s*\|\s*(\d)\s*\|\s*(\d)\s*\|\s*(\d)\s*\|\s*(.+?)\s*\|\s*$', l)
        if m:
            verdict = strip_md(m.group(8))
            mm = re.match(r'(\S+)(?: دنيا)?.*?\(([\d.]+)\)', verdict)
            scores[m.group(1)] = {'real': int(m.group(3)), 'fiqh': int(m.group(4)), 'law': int(m.group(5)),
                                  'case': int(m.group(6)), 'comp': int(m.group(7)), 'verdict': verdict,
                                  'label': mm.group(1) if mm else verdict, 'score': mm.group(2) if mm else ''}
        m2 = re.match(r'^- \*\*([نحف]\d):\*\*\s*(.+)$', l)
        if m2:
            missing[m2.group(1)] = m2.group(2)
    assert len(scores) == 15 and len(missing) == 15, (len(scores), len(missing))
    return scores, missing


LEVEL = {'جاهزة': 4, 'متقدمة': 4, 'تحتاج': 3, 'متوسطة': 3, 'أولية': 2, 'ضعيفة': 1, 'غير': 0}


def level_of(label):
    for k, v in LEVEL.items():
        if label.startswith(k):
            return v
    return 0


# ------------------------------------------------------------------ المستكشف
def parse_mustakshif():
    lines = read(REP['11']).split('\n')
    items = []
    cur = None
    for l in lines:
        m = re.match(r'^### ([★○]) (\d+)\. (.+)$', l)
        if m:
            cur = {'n': int(m.group(2)), 'star': m.group(1), 'title': strip_md(m.group(3)), 'f': {}, 'lines': []}
            items.append(cur)
            continue
        if l.startswith('## ') or l.startswith('---'):
            if l.startswith('## '):
                cur = None
            continue
        if cur is not None:
            m2 = re.match(r'^- \*\*(.+?):\*\*\s*(.*)$', l)
            if m2:
                k, v = m2.group(1), m2.group(2)
                mi = re.search(r'\*\*(الأهمية|الصلة):\*\*\s*(.*)$', v)
                if mi:
                    cur['f'][mi.group(1)] = mi.group(2)
                    v = v[:mi.start()].strip()
                cur['f'][k] = v
            elif l.strip():
                cur['lines'].append(l.strip())
    out = []
    for it in items:
        f = it['f']
        urls = re.findall(r'https?://[^\s)»،؛]+', ' '.join(f.values()))
        urls = [u.rstrip('.,*') for u in urls]
        loc = f.get('الموضع', '')
        out.append({
            'n': it['n'], 'star': it['star'], 'title': it['title'],
            'scenario': strip_md(f.get('سيناريو', '')), 'place': strip_md(loc),
            'article': strip_md(f.get('المادة', '') or f.get('القانون', '')),
            'fiqh': strip_md(f.get('الفقه', '')), 'witness': strip_md(f.get('الشاهد', '') or f.get('الصلة', '')),
            'importance': strip_md(f.get('الأهمية', '')), 'proposal': strip_md(f.get('الحل المقترح للبحث', '')),
            'urls': urls, 'issue_ids': tokens(loc),
            'verify': 'يحتاج تحققًا' if ('يحتاج تحققًا' in ' '.join(f.values())) else 'نص مطابق/منقول بحسب التقرير',
        })
    assert len(out) == 48, len(out)
    return out


# ------------------------------------------------------------------ القاضي
def parse_qadi():
    lines = read(REP['12']).split('\n')
    cases, gaps, social = [], [], []
    cat, cat_ids, cur = '', [], None
    mode = ''
    for l in lines:
        if l.startswith('## '):
            mode = 'b' if l.startswith('## ب.') else 'j' if l.startswith('## ج.') else 'd' if l.startswith('## د.') else ''
            cur = None
            continue
        m = re.match(r'^### (?:\d+\) )?(.+)$', l)
        if m and mode == 'b':
            cat_ids = tokens(m.group(1))
            cat = re.sub(r'\s*\([^)]*\)\s*$', '', m.group(1)).strip()
            cur = None
            continue
        if mode == 'b':
            m = re.match(r'^\*\*([نإ]-\d\d)\.\s*(.*?)\*\*(.*)$', l)
            if m:
                cur = {'id': m.group(1), 'head': m.group(2).strip(), 'tags': m.group(3), 'body': [], 'cat': cat, 'cat_ids': cat_ids}
                cases.append(cur)
                continue
            m = re.match(r'^\*\*([نإ]-\d\d)\.\s*(.*?)\*\*\s*(.*)$', l)
            if cur is not None and l.strip():
                cur['body'].append(l.strip())
        elif mode == 'j':
            m = re.match(r'^(\d+)\. (.+)$', l)
            if m:
                gaps.append(strip_md(m.group(2)))
        elif mode == 'd':
            m = re.match(r'^(\d+)\. (.+)$', l)
            if m:
                social.append(strip_md(m.group(2)))
    out = []
    for c in cases:
        body = ' '.join(c['body'])
        full = c['head'] + ' ' + c['tags'] + ' ' + body
        urls = [u.rstrip('.,*') for u in re.findall(r'https?://[^\s)»،؛]+', full)]
        tags = re.findall(r'\[([^\]]+)\]', c['tags'] + ' ' + (body if len(body) < 400 else ''))
        t = ' '.join(re.findall(r'\[([^\]]+)\]', c['tags']))
        if 'ث-رسمي' in t:
            level = 'ملخص من موقع قضائي رسمي أو مستودع نيابة (النص الكامل غير مقروء)'
        elif 'ث-ملخص' in t:
            level = 'ملخص ثانوي في نتيجة بحث (النص الكامل غير مقروء)'
        elif 'إداري' in t:
            level = 'قرار إداري أو لائحة (ليس حكمًا)'
        elif 'تاريخي' in t:
            level = 'ملخص ثانوي، حكم تاريخي (النص غير مقروء)'
        elif 'إجرائي' in t:
            level = 'مرجع إجرائي ثانوي'
        else:
            level = 'غير مصنَّف في التقرير (النص الكامل غير مقروء)'
        need = 'يحتاج تحققًا' in (c['tags'] + body)
        m = re.search(r'الإشكالية[^:]*:\s*(.+?)(?:\.|$)', body)
        ids = tokens(m.group(0)) if m else []
        ids = ids or c['cat_ids']
        head = re.sub(r'\s*\((?:[^()]*)\)\s*\.?$', '', c['head']).strip().rstrip('.،')
        dm = re.search(r'(\d{1,2}/\d{1,2}/\d{4}|\b(?:19|20)\d{2}\b)', c['head'] + ' ' + body)
        fm = re.search(r'Fallos\s+[\d:]+', c['head'] + ' ' + body)
        is_gap = c['head'].startswith('لا حكم')
        rec = {
            'id': c['id'], 'name': c['head'].rstrip('.'), 'short': head, 'category': c['cat'],
            'kind': 'إداري' if c['id'].startswith('إ') else ('فجوة' if is_gap else 'قضائي'),
            'summary': body.replace('الرابط:', 'الرابط:').split('الرابط:')[0].strip(),
            'date': dm.group(1) if dm else 'غير مبيّن في التقرير', 'fallos': fm.group(0) if fm else '',
            'level': level, 'need_check': need, 'urls': urls, 'issue_ids': ids,
            'pending': ' ؛ '.join(x for x in re.findall(r'\[يحتاج تحققًا[^\]]*\]', c['tags'] + ' ' + body)),
        }
        out.append(rec)
        CASE_NAMES[c['id']] = short(rec['short'], 90)
    return out, gaps, social


# ------------------------------------------------------------------ جداول عامة
def md_tables(path):
    """يعيد قائمة جداول: كل جدول (عنوان أقرب، صفوف الخلايا)."""
    res, cur, head = [], None, ''
    for l in read(path).split('\n'):
        if l.startswith('#'):
            head = l.lstrip('# ').strip()
        if l.startswith('|'):
            cells = [strip_md(c) for c in l.strip().strip('|').split('|')]
            if all(re.fullmatch(r':?-{2,}:?', c) for c in cells):
                continue
            if cur is None:
                cur = {'head': head, 'rows': []}
                res.append(cur)
            cur['rows'].append(cells)
        else:
            cur = None
    return res


def parse_plan():
    stages = []
    level = ''
    for l in read(REP['09']).split('\n'):
        m = re.match(r'^### المستوى (\d): (.+)$', l)
        if m:
            level = m.group(2).strip()
        m = re.match(r'^\|\s*م(\d+)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*$', l)
        if m:
            stages.append({'stage': int(m.group(1)), 'level': level, 'task': strip_md(m.group(2)),
                           'duration': strip_md(m.group(3)), 'criterion': strip_md(m.group(4)),
                           'priority': {'أساسي (يمنع الرد أو الإعادة)': 'عالية', 'مهم': 'متوسطة', 'تحسيني': 'منخفضة'}.get(level, level)})
    assert len(stages) == 11, len(stages)
    return stages


def parse_needs_check():
    out = []
    for no, p in REP.items():
        txt = read(p).split('\n')
        start = None
        for i, l in enumerate(txt):
            if l.startswith('#') and 'يحتاج تحققًا' in l and ('قائمة' in l or '(هـ)' in l or 'خامسًا' in l):
                start = i + 1
                break
        if start is None:
            continue
        items = []
        for l in txt[start:]:
            if l.startswith('## ') or (l.startswith('# ')):
                break
            m = re.match(r'^(?:\d+\.|-)\s+(.+)$', l.strip())
            if m:
                items.append(strip_md(m.group(1)))
            elif l.strip() and no == '11' and '·' in l:
                items += [x.strip() for x in strip_md(l).split('·') if x.strip()]
        if items:
            out.append({'agent_no': no, 'items': items})
    return out


def parse_matrix():
    t = md_tables(REP['06'])
    mat = next(x for x in t if x['rows'][0][0] == '#')
    annex = next(x for x in t if x['rows'][0][0] == 'القسم')
    return mat['rows'][1:], annex['rows'][1:]


def parse_theses():
    if '13' not in REP:
        return None, None
    t = md_tables(REP['13'])
    th = next((x for x in t if x['rows'][0][:2] == ['#', 'الرسالة']), None)
    rules = next((x for x in t if x['rows'][0][0] == 'القاعدة'), None)
    return (th['rows'][1:] if th else None), (rules['rows'][1:] if rules else None)


URL_RE = re.compile(r'(?:https?://|(?<![\w/.])shamela\.ws/)[^\s)»،؛\]|]+')
DEFAULT_LEVEL = {
    '01': 'منقول عن ملخص بحث (يحتاج تحققًا)', '02': 'من فهرس مجلة أو نتيجة بحث، النص غير مقروء',
    '03': 'مقروء بحسب التقرير', '04': 'بحسب التقرير', '05': 'بحسب التقرير', '06': 'ثانوي: نتيجة بحث لم تُقرأ كاملة',
    '07': 'مطابق في الشاملة (ترقيم المطبوع كما تعرضه الشاملة ما لم يُذكر خلافه)', '08': 'مطابق/مذكور في تقرير القانوني',
    '09': 'مذكور في تقرير المحرر', '10': 'مذكور في تقرير المدقق',
    '11': 'مقتطف من الشاملة أو مصدر ثانوي بحسب وسم التقرير', '12': 'ملخص ثانوي في نتيجة بحث (النص غير مقروء)',
    '13': 'ملخص بحث لم يُفتح (إلا ما وُسم بقراءة في الشاملة)',
}


def harvest_urls(team):
    names = {t[0]: t[1] for t in team}
    seen = {}
    for no, p in REP.items():
        for l in read(p).split('\n'):
            for m in URL_RE.finditer(l):
                u = m.group(0).rstrip('.,*:;')
                if u.startswith('shamela.ws'):
                    u = 'https://' + u
                ctx = URL_RE.sub('', l)
                ctx = re.sub(r'^[\s|\-\d.*]+', '', strip_md(ctx))
                ctx = re.sub(r'[|]+', ' ', ctx)
                ctx = re.sub(r'\(\s*\)', '', ctx)
                ctx = re.sub(r'(\s*[؛،;]\s*){2,}', ' ؛ ', ctx)
                ctx = re.sub(r'\s*[؛،;:]\s*(?=[.)]|$)', '', ctx)
                ctx = short(re.sub(r'\s+', ' ', ctx).strip(' ؛،:.'), 140)
                if '[يحتاج تحققًا' in l:
                    lv = 'يحتاج تحققًا'
                elif '[ث-ملخص]' in l:
                    lv = 'ملخص ثانوي لم يُقرأ نصه'
                elif '[ث-رسمي]' in l:
                    lv = 'ملخص من موقع قضائي رسمي (النص غير مقروء)'
                elif '[نص' in l:
                    lv = 'نص مقروء/مطابق بحسب التقرير'
                elif '[منقول' in l:
                    lv = 'منقول دون مطابقة على الأصل'
                else:
                    lv = DEFAULT_LEVEL[no]
                if u in seen:
                    if names[no] not in seen[u]['agents']:
                        seen[u]['agents'].append(names[no])
                    continue
                seen[u] = {'name': ctx, 'url': u, 'level': lv, 'agents': [names[no]]}
    return list(seen.values())


def kind_of_url(u):
    if 'shamela.ws' in u or 'aljam3' in u:
        return 'مصدر فقهي (الشاملة/الجامع)'
    if 'saij' in u or 'infoleg' in u or 'boletinoficial' in u or 'argentina.gob' in u:
        return 'نص قانوني أو حكم أرجنتيني'
    if any(x in u for x in ['diariojudicial', 'abogados.com', 'microjuris', 'pagina12', 'lagaceta', 'tiempoar', 'diariodecuyo', 'noticiasnqn', 'a24', 'hoydia']):
        return 'خبر أو تعليق قضائي ثانوي'
    if any(x in u for x in ['repositor', 'dspace', 'eprints', 'wrap.', 'ehu.es', 'toubkal', 'thesescanada', 'escholarship', 'dialnet', 'uca.edu', 'doi.org', 'academia', 'research-information']):
        return 'دراسة أو رسالة جامعية'
    return 'مصدر ثانوي/مقارن'


# ------------------------------------------------------------------ التجميع
def build():
    team = load_json(os.path.join(HAND, 'فريق_وأحكام_ومهام_ومصادر.json'))
    outl = parse_outline()
    issue_title_map(outl)
    otab = parse_outline_tables()
    muw = parse_muwazin()
    nas, nas_missing = parse_nasib()
    new_issues = parse_mustakshif()
    cases_x, gaps, social = parse_qadi()
    for c in team['old_cases']:
        CASE_NAMES[c['id']] = c['name']
    stages = parse_plan()
    needs = parse_needs_check()
    matrix, annex = parse_matrix()
    theses, rules = parse_theses()
    urls = harvest_urls(team['team'])

    hand = {}
    for f in ['بنود_ف1_ف2_ف5_خاتمة_ملاحق.json', 'بنود_ف3.json', 'بنود_ف4.json']:
        hand.update(load_json(os.path.join(HAND, f)))
    errors_raw = load_json(os.path.join(HAND, 'سجل_الأخطاء.json'))
    agent_name = {t[0]: t[1] for t in team['team']}

    # ربط الإشكاليات الجديدة والأحكام بالبنود
    by_issue_new, by_issue_case = {}, {}
    for n in new_issues:
        for i in n['issue_ids']:
            by_issue_new.setdefault(i, []).append(n)
    case_rows = []
    for c in cases_x:
        for i in c['issue_ids']:
            by_issue_case.setdefault(i, []).append({'name': c['short'], 'level': c['level'], 'urls': c['urls'][:1], 'src': 'القاضي'})
    for c in team['old_cases']:
        for i in c['issues']:
            by_issue_case.setdefault(i, []).append({'name': c['name'], 'level': c['level'], 'urls': [c['url']] if c['url'] else [], 'src': 'السجل المشترك'})

    chapters = []
    for c in outl:
        ch = {'id': c['id'], 'title': c['title'], 'sections': []}
        for s in c['sections']:
            sec = {'id': s['id'], 'title': s['title'], 'items': []}
            for it in s['items']:
                h = hand.get(it['id'], {})
                code = it['code']
                m_label, m_score, size, missing = h.get('maturity', 'غير مقيّم'), '', '', ''
                basis = h.get('basis', 'لا حكم في التقارير')
                scores = None
                if code in muw:
                    m_label, size, missing = muw[code]['label'], muw[code]['size'] + ' ألف كلمة تقريبًا', muw[code]['missing']
                    basis = 'جدول النضج في تقرير الموازن'
                elif code in nas:
                    m_label, m_score, scores = nas[code]['label'], nas[code]['score'], nas[code]
                    missing = nas_missing[code]
                    basis = 'جدول النضج في تقرير الناسب'
                issues = list(h.get('issues', []))
                laws = list(h.get('laws', []))
                if code in otab:
                    laws.insert(0, 'السند القانوني في المخطط: ' + otab[code]['law'])
                    wit = otab[code]['witness']
                else:
                    wit = ''
                item = {
                    'id': it['id'], 'code': code, 'title': it['title'], 'star': it['star'],
                    'outline_details': it['details'], 'witness': wit,
                    'maturity': m_label, 'maturity_level': level_of(m_label), 'maturity_score': m_score,
                    'maturity_basis': basis, 'size': size, 'scores': scores,
                    'exists': h.get('exists', ''), 'issues': issues, 'missing': missing,
                    'additions': list(h.get('additions', [])),
                    'cases': by_issue_case.get(code, []),
                    'new_issues': [{'n': n['n'], 'title': n['title'], 'star': n['star']} for n in by_issue_new.get(code, [])],
                    'fiqh': h.get('fiqh', []), 'laws': laws,
                    'sources': [x for x in h.get('sources', [])],
                    'verify': h.get('verify', 'غير مصنَّف'),
                }
                sec['items'].append(item)
            ch['sections'].append(sec)
        chapters.append(ch)

    errors = []
    for e in errors_raw:
        errors.append({'agent': agent_name[e[0]], 'agent_no': e[0], 'position': e[1], 'severity': e[2], 'desc': e[3],
                       'rec': e[4], 'status': 'مفتوح — يحتاج تحققًا' if 'يحتاج تحققًا' in e[3] + e[4] else 'مفتوح'})

    stage_by = {s['stage']: s for s in stages}
    plan_stages = [{'stage': 'المرحلة %d' % s['stage'], 'level': s['level'], 'priority': s['priority'], 'task': s['task'],
                    'duration': s['duration'], 'criterion': s['criterion'], 'agent': 'المحرر', 'n': s['stage']} for s in stages]
    plan_tasks = []
    for t in team['tasks']:
        st = stage_by.get(int(t[1]))
        plan_tasks.append({'task': t[0], 'stage': 'المرحلة %s' % t[1], 'priority': t[2], 'agent': t[3],
                           'report': agent_name.get(t[4], t[4]),
                           'duration': st['duration'] if st else '', 'criterion': st['criterion'] if st else ''})

    src = []
    for s in team['sources_manual']:
        src.append({'name': s[0], 'kind': s[1], 'url': s[2], 'level': s[3], 'agents': [agent_name.get(s[4], s[4])]})
    known = {x['url'] for x in src if x['url']}
    for u in urls:
        if u['url'] in known:
            continue
        src.append({'name': u['name'], 'kind': kind_of_url(u['url']), 'url': u['url'], 'level': u['level'], 'agents': u['agents']})
    for s in src:
        if not s['url']:
            s['level'] = s['level'] if 'يحتاج تحققًا' in s['level'] else s['level']

    # مصادر بنود الخريطة (الفقهية وغيرها) تُضاف إلى سجل المصادر مع المطلب المرتبط
    by_url = {x['url']: x for x in src if x['url']}
    for c in chapters:
        for sec in c['sections']:
            for it in sec['items']:
                for f in it['fiqh'] + it['sources']:
                    if f['u'] and f['u'] in by_url:
                        by_url[f['u']].setdefault('related', [])
                        if it['title'] not in by_url[f['u']]['related']:
                            by_url[f['u']]['related'].append(it['title'])
                    else:
                        e = {'name': f['t'], 'kind': 'مصدر فقهي (الشاملة/الجامع)' if f in it['fiqh'] else 'مصدر مذكور في بند الخريطة',
                             'url': f['u'] if f['u'].startswith('http') else '', 'level': it['verify'], 'agents': ['من بنود الخريطة'], 'related': [it['title']]}
                        src.append(e)
                        if e['url']:
                            by_url[e['url']] = e
    for x in src:
        x.setdefault('related', [])
    mrefs = []
    for t in md_tables(REP['03']):
        if t['rows'][0][0] == 'المرجع':
            mrefs = t['rows'][1:]
    if theses:
        theses = [[r[0], r[1], r[2], r[3], 'قُرئ نصه في الشاملة' if 'ق' in r[4] and 'م' not in r[4] else 'من ملخص بحث أو فهرس، النص غير مقروء'] for r in theses]
    data = {
        'meta': {'title': 'خريطة الرسالة: أحكام الأسرة للأقليات المسلمة في الغرب بين الفقه والقانون – الأرجنتين نموذجًا',
                 'generated': datetime.date.today().isoformat(),
                 'reports': [os.path.basename(p) for p in REPORTS],
                 'has_report13': '13' in REP,
                 'note': 'مستخرجة من تقارير فريق المراجعة دون إضافة محتوى؛ كل بند معه مصدره أو «بلا رابط [يحتاج تحققًا]».'},
        'chapters': chapters,
        'new_issues': new_issues,
        'cases_extra': cases_x, 'cases_old': team['old_cases'], 'case_gaps': gaps, 'social_issues': social,
        'errors': errors, 'needs_check': [{'agent': agent_name[n['agent_no']], 'agent_no': n['agent_no'], 'items': n['items']} for n in needs],
        'sources': src, 'plan_stages': plan_stages, 'plan_tasks': plan_tasks,
        'team': [{'no': t[0], 'name': t[1], 'role': t[2], 'file': next((os.path.basename(p) for p in REPORTS if os.path.basename(p).startswith(t[0])), '')} for t in team['team']],
        'matrix': matrix, 'annex1': annex,
        'theses': theses, 'rules': rules, 'minority_refs': mrefs,
        'nasib_scores': [{'code': k, **v} for k, v in nas.items()],
    }
    data = clean(data)
    return data


def main():
    data = build()
    with open(DATA_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    # تقرير الرموز المتبقية في النصوص المقروءة
    left = []

    def walk(o, key=None, path=''):
        if key in SKIP_KEYS:
            return
        if isinstance(o, str):
            c = find_codes(o)
            if c:
                left.append((path, c, o[:80]))
        elif isinstance(o, list):
            for i, x in enumerate(o):
                walk(x, key, path)
        elif isinstance(o, dict):
            for k, v in o.items():
                walk(v, k, path + '/' + k)
    walk(data)
    print('data.json written; رموز متبقية:', len(left))
    for x in left[:15]:
        print(x)


if __name__ == '__main__':
    main()
