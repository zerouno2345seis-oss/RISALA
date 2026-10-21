# -*- coding: utf-8 -*-
"""تشغيل الخط كاملًا: استخراج -> xlsx -> html."""
import subprocess, sys, os
here = os.path.dirname(os.path.abspath(__file__))
for s in ('extract.py', 'build_xlsx.py', 'build_html.py'):
    subprocess.check_call([sys.executable, os.path.join(here, s)], cwd=here)
