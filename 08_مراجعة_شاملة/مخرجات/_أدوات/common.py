# -*- coding: utf-8 -*-
"""أدوات مشتركة: المسارات، وتحويل الرموز التقنية إلى عناوين كاملة (تعليمة الباحث: لا رموز في ما يقرؤه)."""
import re, json, os

ROOT = '/home/user/risala/08_مراجعة_شاملة'
OUT = os.path.join(ROOT, 'مخرجات')
TOOLS = os.path.join(OUT, '_أدوات')
HAND = os.path.join(TOOLS, 'بيانات_يدوية')
OUTLINE = '/home/user/risala/04_خطة_الإشكاليات/المخطط_المقترح_للرسالة_والإشكاليات_الموسعة.md'
DATA_JSON = os.path.join(OUT, 'data.json')

GROUPS = {
    'خ': 'إشكاليات الخطبة', 'ز': 'إشكاليات الزواج', 'ط': 'إشكاليات الطلاق والفرقة',
    'ن': 'إشكاليات النسب', 'ح': 'إشكاليات الحضانة', 'ف': 'إشكاليات النفقة والحقوق المالية',
}
GROUP_SIZE = {'خ': 6, 'ز': 9, 'ط': 7, 'ن': 5, 'ح': 5, 'ف': 5}

ISSUE_TITLES = {}   # code -> full title
CASE_NAMES = {}     # ق-NN / ن-NN / إ-NN -> descriptor
MAJMA_NAMES = {
    'م-01': 'قرار مجمع الفقه الإسلامي الدولي (مذكور عند الزحيلي)',
    'م-02': 'قرار مجمع الفقه الإسلامي الدولي (جواب السؤالين الثالث والرابع)',
    'م-03': 'قرار مجمع الفقه الإسلامي الدولي رقم 52 (3/6) في اشتراط الإشهاد في النكاح',
    'م-04': 'قرار مجمع الفقه الإسلامي الدولي في التحكيم',
    'م-15': 'قرار مجمع فقهاء الشريعة بأمريكا 2004 في الاعتداد بالإجراءات القانونية',
}
DEFAULT_MAJMA = 'قرار مجمعي في سجل المجامع المشترك'
DEFAULT_QARAR = 'حكم في سجل الأحكام المشترك'

LET = 'ء-ؿف-ي'
ISSUE_RE = re.compile(r'(?<![' + LET + r'A-Za-z0-9])(و?)([خزطنحف])(\d)(?:\s*[–\-]\s*([خزطنحف])?(\d))?(?!\d)')
ID_RE = re.compile(r'(?<![' + LET + r'])(و?)([قمنإ])-(\d{2})(?!\d)')


def short(s, n=70):
    s = s.strip()
    return s if len(s) <= n else s[:n].rstrip() + '…'


def _issue_repl(m):
    pre, L, a, L2, b = m.group(1), m.group(2), int(m.group(3)), m.group(4), m.group(5)
    if L not in GROUPS:
        return m.group(0)
    def t(i):
        return ISSUE_TITLES.get(f'{L}{i}', m.group(0))
    if b is None:
        return f'{pre}«{t(a)}»' if f'{L}{a}' in ISSUE_TITLES else m.group(0)
    b = int(b)
    if L2 and L2 != L:
        return m.group(0)
    if a == 1 and b == GROUP_SIZE[L]:
        return f'{pre}{GROUPS[L]}'
    ids = list(range(a, b + 1))
    if len(ids) <= 3:
        return pre + '، '.join(f'«{t(i)}»' for i in ids)
    return f'{pre}«{t(a)}» إلى «{t(b)}»'


def _id_repl(m):
    pre, L, n = m.group(1), m.group(2), m.group(3)
    key = f'{L}-{n}'
    if L == 'م':
        d = MAJMA_NAMES.get(key, DEFAULT_MAJMA)
    elif L == 'ق':
        d = CASE_NAMES.get(key, DEFAULT_QARAR)
    else:
        d = CASE_NAMES.get(key, 'حكم من تقرير القاضي')
    return f'{pre}«{short(d, 80)}»'


def humanize(s):
    if not isinstance(s, str):
        return s
    s = ISSUE_RE.sub(_issue_repl, s)
    s = ID_RE.sub(_id_repl, s)
    return s


SKIP_KEYS = {'id', 'tid', 'tech', 'code', 'issue_ids', 'case_ids', 'agent_no', 'ref'}


def clean(o, key=None):
    if key in SKIP_KEYS:
        return o
    if isinstance(o, str):
        return humanize(o)
    if isinstance(o, list):
        return [clean(x, key) for x in o]
    if isinstance(o, dict):
        return {k: clean(v, k) for k, v in o.items()}
    return o


CODE_LEFT = re.compile(r'(?<![' + LET + r'A-Za-z0-9])[خزطنحف]\d(?!\d)|(?<![' + LET + r'])[قمنإ]-\d{2}(?!\d)')


def find_codes(s):
    return CODE_LEFT.findall(s or '')


def load_json(p):
    with open(p, encoding='utf-8') as f:
        return json.load(f)
