# -*- coding: utf-8 -*-
"""يولّد صفحة HTML واحدة مستقلة (بلا اعتماد خارجي) من data.json."""
import json, os
from common import DATA_JSON, OUT, load_json

D = load_json(DATA_JSON)

TEMPLATE = r'''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>خريطة الرسالة التفاعلية</title>
<style>
:root{--bg:#f6f4ef;--panel:#ffffff;--ink:#1d2a30;--mute:#5b6b72;--line:#d9d5ca;--brand:#1f4e5f;--brand2:#2f7a8a;--link:#0b5cad;
--g:#d4efdc;--gt:#14532d;--y:#fdf0c2;--yt:#6b4e00;--o:#fbd9c4;--ot:#7c3a12;--r:#fcd0d0;--rt:#7f1d1d;--n:#e6e6e6;--nt:#444;--b:#d8e8f7;--bt:#0b3a66}
:root[data-theme="dark"]{--bg:#12181b;--panel:#1b2428;--ink:#e6ecee;--mute:#9fb0b6;--line:#33434a;--brand:#5ec0d4;--brand2:#3d9aae;--link:#7cc0ff;
--g:#1d4a2e;--gt:#bdf0cc;--y:#4d4210;--yt:#ffe9a0;--o:#5a3318;--ot:#ffd3b3;--r:#5a2020;--rt:#ffc9c9;--n:#333c40;--nt:#d0d6d8;--b:#1f3a55;--bt:#c5e1fb}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#12181b;--panel:#1b2428;--ink:#e6ecee;--mute:#9fb0b6;--line:#33434a;--brand:#5ec0d4;--brand2:#3d9aae;--link:#7cc0ff;
--g:#1d4a2e;--gt:#bdf0cc;--y:#4d4210;--yt:#ffe9a0;--o:#5a3318;--ot:#ffd3b3;--r:#5a2020;--rt:#ffc9c9;--n:#333c40;--nt:#d0d6d8;--b:#1f3a55;--bt:#c5e1fb}}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--ink);font-family:"Segoe UI",Tahoma,"Noto Naskh Arabic","Noto Sans Arabic",Arial,sans-serif;line-height:1.75;font-size:16px}
a{color:var(--link);word-break:break-all}
header{position:sticky;top:0;z-index:20;background:var(--brand);color:#fff;padding:10px 16px;display:flex;flex-wrap:wrap;gap:10px;align-items:center}
:root[data-theme="dark"] header{color:#0b1114}
header h1{font-size:1.05rem;margin:0;flex:1 1 260px;line-height:1.4}
header input,header select,header button{font:inherit;font-size:.9rem;padding:6px 10px;border-radius:8px;border:1px solid var(--line);background:var(--panel);color:var(--ink)}
header input{flex:1 1 220px;min-width:140px}
header button{cursor:pointer}
nav.tabs{display:flex;gap:4px;overflow-x:auto;padding:8px 16px 0;background:var(--bg);border-bottom:1px solid var(--line);position:sticky;top:var(--hh,58px);z-index:15}
nav.tabs button{font:inherit;font-size:.92rem;border:1px solid var(--line);border-bottom:none;background:var(--panel);color:var(--mute);padding:8px 14px;border-radius:10px 10px 0 0;cursor:pointer;white-space:nowrap}
nav.tabs button.on{background:var(--brand);color:#fff;border-color:var(--brand)}
:root[data-theme="dark"] nav.tabs button.on{color:#0b1114}
main{padding:14px 16px 60px;max-width:1500px;margin:0 auto}
.layout{display:grid;grid-template-columns:330px 1fr;gap:16px;align-items:start}
.tree{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:10px;position:sticky;top:calc(var(--hh,58px) + 52px);max-height:calc(100vh - 140px);overflow:auto;font-size:.9rem}
.tree details{margin:2px 0}
.tree summary{cursor:pointer;padding:4px 6px;border-radius:6px;font-weight:600}
.tree summary:hover,.tree a.leaf:hover{background:var(--n)}
.tree details details{margin-right:12px}
.tree a.leaf{display:flex;gap:6px;align-items:flex-start;padding:3px 6px;margin-right:12px;border-radius:6px;color:var(--ink);text-decoration:none;word-break:normal}
.tree a.sel,.tree summary.sel{background:var(--b);color:var(--bt)}
.dot{flex:0 0 10px;width:10px;height:10px;border-radius:50%;margin-top:8px;display:inline-block;background:var(--n)}
.l4{background:#2e9d57}.l3{background:#e0b11d}.l2{background:#e8803a}.l1{background:#d64545}.l0{background:#9aa5a9}
.card{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:14px 16px;margin:0 0 14px;scroll-margin-top:150px}
.card h3{margin:0 0 6px;font-size:1.05rem;line-height:1.55}
.crumb{color:var(--mute);font-size:.82rem;margin-bottom:4px}
.badges{display:flex;flex-wrap:wrap;gap:6px;margin:6px 0 10px}
.badge{display:inline-block;padding:1px 10px;border-radius:999px;font-size:.8rem;border:1px solid transparent;background:var(--n);color:var(--nt)}
.b4{background:var(--g);color:var(--gt)}.b3{background:var(--y);color:var(--yt)}.b2{background:var(--o);color:var(--ot)}.b1{background:var(--r);color:var(--rt)}.b0{background:var(--n);color:var(--nt)}
.v-good{background:var(--g);color:var(--gt)}.v-warn{background:var(--y);color:var(--yt)}.v-bad{background:var(--r);color:var(--rt)}.v-info{background:var(--b);color:var(--bt)}
.sec{margin:10px 0 0}
.sec h4{margin:0 0 3px;font-size:.88rem;color:var(--brand2)}
.sec ul{margin:0;padding:0 18px 0 0}
.sec li{margin:2px 0}
.sec p{margin:0}
.chip{display:inline-block;margin:2px 0 2px 6px;padding:1px 10px;border-radius:8px;background:var(--b);color:var(--bt);font-size:.82rem;cursor:pointer;border:none;font-family:inherit}
.muted{color:var(--mute)}
.scroller{overflow-x:auto;border:1px solid var(--line);border-radius:12px;background:var(--panel)}
table{border-collapse:collapse;width:100%;font-size:.88rem}
th,td{padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top;text-align:right}
th{background:var(--brand);color:#fff;position:sticky;top:0;white-space:nowrap}
:root[data-theme="dark"] th{color:#0b1114}
td.w{min-width:260px}
.tools{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 12px;align-items:center}
.tools select,.tools input{font:inherit;padding:6px 10px;border-radius:8px;border:1px solid var(--line);background:var(--panel);color:var(--ink)}
.count{color:var(--mute);font-size:.88rem}
.drawer-btn{display:none}
.team{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:12px}
.hide{display:none!important}
.legend{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 12px;font-size:.85rem}
@media (max-width:900px){
 .layout{grid-template-columns:1fr}
 .tree{position:fixed;inset:0 0 0 auto;width:min(88vw,380px);z-index:40;max-height:none;border-radius:0;transform:translateX(110%);transition:transform .2s}
 .tree.open{transform:none}
 .drawer-btn{display:inline-block}
 main{padding:10px 12px 60px}
 header{padding:8px 12px}nav.tabs{padding:8px 12px 0}
}
</style>
</head>
<body>
<header id="hd">
 <h1>خريطة الرسالة: أحكام الأسرة للأقليات المسلمة في الغرب بين الفقه والقانون – الأرجنتين نموذجًا</h1>
 <input id="q" type="search" placeholder="ابحث في كل شيء: عنوان، مادة، مصدر، حكم…" aria-label="بحث">
 <select id="fm" aria-label="درجة النضج"><option value="">كل درجات النضج</option><option>جاهزة</option><option>متقدمة</option><option>متوسطة</option><option>تحتاج</option><option>أولية</option><option>ضعيفة</option><option>غير مقيّم</option></select>
 <select id="fv" aria-label="حالة التوثيق"><option value="">كل حالات التوثيق</option><option value="جزئي">موثق جزئيًا</option><option value="موثق نص">موثق نصًّا</option><option value="يحتاج">يحتاج تحققًا</option><option value="منقول">منقول أو غير محقق</option><option value="غير موثق">غير موثق</option></select>
 <select id="fs" aria-label="الأولوية"><option value="">★ و ○</option><option value="★">★ مفصل</option><option value="○">○ مختصر</option></select>
 <button id="th" type="button" aria-label="تبديل الوضع">الوضع الداكن/الفاتح</button>
 <button id="db" class="drawer-btn" type="button">الشجرة</button>
</header>
<nav class="tabs" id="tabs"></nav>
<main id="main"></main>
<script id="data" type="application/json">__DATA__</script>
<script>
const D = JSON.parse(document.getElementById('data').textContent);
const $ = (s, r=document) => r.querySelector(s);
const esc = s => String(s==null?'':s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const linkify = s => esc(s).replace(/(https?:\/\/[^\s)»،؛<]+)/g, u => '<a href="'+u+'" target="_blank" rel="noopener">'+u+'</a>');
const NOLINK = 'بلا رابط [يحتاج تحققًا]';
const state = {tab:'map', node:'ch1', q:'', fm:'', fv:'', fs:''};
const TABS = [['map','الخريطة'],['new','الإشكاليات الجديدة'],['cases','الأحكام'],['errors','سجل الأخطاء'],['plan','خطة الرفع'],['sources','المصادر'],['fiqh','فقه الأقليات والرسائل'],['team','الفريق']];
function sk(k){try{return localStorage.getItem(k)}catch(e){return null}}
function sv(k,v){try{localStorage.setItem(k,v)}catch(e){}}
// ---------- ثيم
(function(){const t=sk('theme'); if(t) document.documentElement.setAttribute('data-theme',t);})();
$('#th').onclick=()=>{const cur=document.documentElement.getAttribute('data-theme')||(matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light'); const nx=cur==='dark'?'light':'dark'; document.documentElement.setAttribute('data-theme',nx); sv('theme',nx);};
// ---------- أدوات
function matClass(it){return 'b'+it.maturity_level}
function verClass(v){v=v||''; if(v.includes('يحتاج')) return 'v-warn'; if(v.includes('غير موثق')||v.includes('غير مصنَّف')) return 'v-bad'; if(v.includes('موثق نص')||v.includes('مطابق')) return 'v-good'; if(v.includes('جزئيًا')) return 'v-info'; return ''}
function list(arr){return arr&&arr.length?'<ul>'+arr.map(x=>'<li>'+linkify(x)+'</li>').join('')+'</ul>':''}
function block(t,html){return html?'<div class="sec"><h4>'+t+'</h4>'+html+'</div>':''}
function linkList(arr){return arr&&arr.length?'<ul>'+arr.map(f=>'<li>'+esc(f.t)+' — '+(f.u&&f.u.startsWith('http')?'<a href="'+esc(f.u)+'" target="_blank" rel="noopener">رابط</a>':'<span class="muted">'+NOLINK+'</span>')+'</li>').join('')+'</ul>':''}
function itemText(it){return JSON.stringify(it)}
const ALL = [];
let KI=0; D.chapters.forEach(c=>c.sections.forEach(s=>s.items.forEach(it=>{it.k='k'+(KI++); ALL.push({c,s,it,txt:itemText(it)});})));
function passes(o){
  const it=o.it;
  if(state.fm && !(it.maturity||'').startsWith(state.fm)) return false;
  if(state.fv){const v=it.verify||''; if(state.fv==='جزئي'){ if(!v.includes('جزئيًا')) return false;} else if(state.fv==='موثق نص'){ if(!v.includes('موثق نص')) return false;} else if(state.fv==='يحتاج'){ if(!v.includes('يحتاج')) return false;} else if(state.fv==='منقول'){ if(!(v.includes('منقول')||v.includes('غير محقق'))) return false;} else if(state.fv==='غير موثق'){ if(!v.includes('غير موثق')) return false;}}
  if(state.fs && it.star!==state.fs) return false;
  if(state.q && !o.txt.includes(state.q)) return false;
  return true;
}
function inNode(o){const n=state.node; if(n==='all') return true; if(n.startsWith('item:')) return o.it.k===n.slice(5); if(n.startsWith('sec:')) return o.s.id===n.slice(4); return o.c.id===n;}
// ---------- بطاقة
function card(o){
  const it=o.it, c=o.c, s=o.s;
  const cases = (it.cases||[]).map(x=>esc(x.name)+' <span class="muted">['+esc(x.level)+']</span>'+(x.urls&&x.urls[0]?' — <a href="'+esc(x.urls[0])+'" target="_blank" rel="noopener">رابط</a>':'')).map(x=>'<li>'+x+'</li>').join('');
  const news = (it.new_issues||[]).map(n=>'<button class="chip" data-new="'+esc(n.title)+'">'+esc(n.title)+' ('+esc(n.star)+')</button>').join('');
  const adds = list(it.additions);
  return '<article class="card" id="i-'+it.k+'">'
   +'<div class="crumb">'+esc(c.title)+(s.title?' ← '+esc(s.title):'')+'</div>'
   +'<h3>'+esc(it.title)+'</h3>'
   +'<div class="badges">'+(it.star?'<span class="badge">'+esc(it.star)+(it.star==='★'?' مفصل':' مختصر')+'</span>':'')
   +'<span class="badge '+matClass(it)+'" title="'+esc(it.maturity_basis)+'">النضج: '+esc(it.maturity)+(it.maturity_score?' ('+esc(it.maturity_score)+')':'')+'</span>'
   +'<span class="badge '+verClass(it.verify)+'">التوثيق: '+esc(it.verify)+'</span>'
   +(it.size?'<span class="badge">'+esc(it.size)+'</span>':'')+'</div>'
   +block('الموجود', it.exists?'<p>'+linkify(it.exists)+'</p>'+(it.witness?'<p class="muted">الشاهد في المخطط: '+esc(it.witness)+'</p>':''):'')
   +block('الإشكالات والثغرات', list(it.issues)+(it.missing?'<p><b>ما ينقص:</b> '+linkify(it.missing)+'</p>':''))
   +block('المقترح إضافته', adds+(news?'<p>إشكاليات جديدة مقترحة: '+news+'</p>':''))
   +block('الأحكام القضائية المرتبطة', cases?'<ul>'+cases+'</ul>':'')
   +block('المصادر الفقهية المتحققة', linkList(it.fiqh))
   +block('المواد القانونية', list(it.laws))
   +block('مصادر وروابط', linkList(it.sources))
   +(it.scores?block('درجات النضج (من 5)','<p>الواقع '+it.scores.real+' · الفقه '+it.scores.fiqh+' · القانون '+it.scores.law+' · القضاء '+it.scores.case+' · المقارنة '+it.scores.comp+'</p>'):'')
   +'<p class="muted" style="font-size:.8rem;margin:8px 0 0">أساس درجة النضج: '+esc(it.maturity_basis)+'</p>'
   +'</article>';
}
// ---------- شجرة
function treeHTML(){
  let h='<a class="leaf" href="#" data-node="all"><b>عرض كل البنود</b></a>';
  D.chapters.forEach(c=>{
    h+='<details open><summary data-node="'+c.id+'">'+esc(c.title)+'</summary>';
    c.sections.forEach(s=>{
      const its=s.items;
      if(s.title){h+='<details open><summary data-node="sec:'+s.id+'">'+esc(s.title)+'</summary>';}
      its.forEach(it=>{h+='<a class="leaf" href="#i-'+it.k+'" data-node="item:'+it.k+'"><span class="dot l'+it.maturity_level+'"></span><span>'+esc(it.title)+'</span></a>';});
      if(s.title) h+='</details>';
    });
    h+='</details>';
  });
  return h;
}
function renderMap(){
  const cnt={};
  const rows=ALL.filter(o=>inNode(o)&&passes(o));
  const total=ALL.filter(passes).length;
  $('#main').innerHTML='<div class="legend"><span class="badge b4">جاهزة/متقدمة</span><span class="badge b3">تحتاج/متوسطة</span><span class="badge b2">أولية</span><span class="badge b1">ضعيفة</span><span class="badge b0">غير مقيّم</span><span class="count">'+rows.length+' بندًا معروضًا من '+ALL.length+(total!==ALL.length?' (بعد الفلترة: '+total+')':'')+'</span></div>'
   +'<div class="layout"><aside class="tree" id="tree">'+treeHTML()+'</aside><section id="cards">'+(rows.map(card).join('')||'<p class="muted">لا نتائج مطابقة.</p>')+'</section></div>';
  const tr=$('#tree');
  tr.onclick=e=>{const a=e.target.closest('[data-node]'); if(!a) return; const n=a.getAttribute('data-node'); if(a.tagName==='A'&&a.classList.contains('leaf')&&n.startsWith('item:')){state.node=n; e.preventDefault(); renderCards(); $('#tree').classList.remove('open'); window.scrollTo({top:$('#cards').offsetTop-130}); return;}
    if(a.tagName==='SUMMARY'){state.node=n; setTimeout(renderCards,0); } else {e.preventDefault(); state.node=n; renderCards();} };
  bindChips();
}
function renderCards(){
  const rows=ALL.filter(o=>inNode(o)&&passes(o));
  $('#cards').innerHTML=rows.map(card).join('')||'<p class="muted">لا نتائج مطابقة.</p>';
  const lg=$('.count'); if(lg) lg.textContent=rows.length+' بندًا معروضًا من '+ALL.length;
  document.querySelectorAll('#tree .sel').forEach(x=>x.classList.remove('sel'));
  const sel=document.querySelector('#tree [data-node="'+state.node+'"]'); if(sel) sel.classList.add('sel');
  bindChips();
}
function bindChips(){document.querySelectorAll('[data-new]').forEach(b=>b.onclick=()=>{state.tab='new'; state.q=b.getAttribute('data-new'); $('#q').value=state.q; render();});}
// ---------- جداول عامة
function table(heads, rows, opts){
  return '<div class="scroller"><table><thead><tr>'+heads.map(h=>'<th>'+esc(h)+'</th>').join('')+'</tr></thead><tbody>'+rows.join('')+'</tbody></table></div>';
}
const hit = (s) => !state.q || s.includes(state.q);
function renderNew(){
  const rows=D.new_issues.filter(n=>hit(JSON.stringify(n))).map(n=>'<tr><td>'+n.n+'</td><td>'+esc(n.star)+'</td><td class="w"><b>'+esc(n.title)+'</b><br><span class="muted">'+esc(n.scenario)+'</span></td><td class="w">'+esc(n.place)+'</td><td class="w">'+linkify(n.article)+'</td><td class="w">'+linkify(n.fiqh)+'</td><td>'+esc(n.witness)+'</td><td>'+esc(n.importance)+'</td><td><span class="badge '+verClass(n.verify)+'">'+esc(n.verify)+'</span></td></tr>');
  $('#main').innerHTML='<p class="count">'+rows.length+' من '+D.new_issues.length+' إشكالية جديدة (من المستكشف)</p>'+table(['#','الأولوية','الإشكالية والسيناريو','الموضع المقترح','المادة القانونية','الفقه','الشاهد','الأهمية','التوثيق'],rows);
}
function renderCases(){
  const ex=D.cases_extra.filter(c=>hit(JSON.stringify(c))).map(c=>'<tr><td class="w"><b>'+esc(c.name)+'</b></td><td>'+esc(c.kind)+'</td><td>'+esc(c.date)+'</td><td class="w">'+esc(c.category)+'<br><span class="muted">'+esc(c.summary.slice(0,420))+'</span></td><td><span class="badge v-warn">'+esc(c.level)+'</span></td><td>'+(c.urls.length?c.urls.map(u=>'<a href="'+esc(u)+'" target="_blank" rel="noopener">رابط</a>').join('<br>'):'<span class="muted">'+NOLINK+'</span>')+'</td></tr>');
  const old=D.cases_old.filter(c=>hit(JSON.stringify(c))).map(c=>'<tr><td class="w"><b>'+esc(c.name)+'</b></td><td>'+esc(c.court)+'</td><td>'+esc(c.date)+'</td><td class="w">'+esc(c.topic)+'</td><td><span class="badge '+(c.level.includes('نص كامل')?'v-good':'v-warn')+'">'+esc(c.level)+'</span></td><td>'+(c.url?'<a href="'+esc(c.url)+'" target="_blank" rel="noopener">رابط</a>':'<span class="muted">'+NOLINK+'</span>')+'</td></tr>');
  $('#main').innerHTML='<h2>أحكام السجل المشترك ('+old.length+')</h2>'+table(['الحكم','المحكمة','التاريخ','الموضوع','مستوى التحقق','الرابط'],old)
   +'<h2>أحكام إضافية من القاضي ('+ex.length+')</h2><p class="muted">كلها ملخصات ثانوية: لم يُقرأ نص أي حكم منها، ولا يُستشهد بها في المتن قبل التحقق.</p>'+table(['الحكم','النوع','التاريخ','الموضوع والملخص','مستوى التحقق','الرابط'],ex)
   +'<h2>فجوات قضائية موثقة</h2>'+list(D.case_gaps);
}
function renderErrors(){
  const sev=state.sev||'', ag=state.ag||'';
  const rows=D.errors.filter(e=>(!sev||e.severity===sev)&&(!ag||e.agent===ag)&&hit(JSON.stringify(e)));
  const order={'حرجة':0,'عالية':1,'متوسطة':2,'منخفضة':3}; rows.sort((a,b)=>order[a.severity]-order[b.severity]);
  const cls={'حرجة':'b1','عالية':'b2','متوسطة':'b3','منخفضة':'b4'};
  const agents=[...new Set(D.errors.map(e=>e.agent))];
  $('#main').innerHTML='<div class="tools"><select id="sv"><option value="">كل درجات الخطورة</option>'+['حرجة','عالية','متوسطة','منخفضة'].map(x=>'<option'+(sev===x?' selected':'')+'>'+x+'</option>').join('')+'</select><select id="sa"><option value="">كل الوكلاء</option>'+agents.map(x=>'<option'+(ag===x?' selected':'')+'>'+x+'</option>').join('')+'</select><span class="count">'+rows.length+' من '+D.errors.length+'</span></div>'
   +table(['الموضع','الوصف','الخطورة','الوكيل','التوصية','الحالة'],rows.map(e=>'<tr><td class="w">'+esc(e.position)+'</td><td class="w">'+linkify(e.desc)+'</td><td><span class="badge '+cls[e.severity]+'">'+esc(e.severity)+'</span></td><td>'+esc(e.agent)+'</td><td class="w">'+esc(e.rec)+'</td><td>'+esc(e.status)+'</td></tr>'))
   +'<h2>بنود «يحتاج تحققًا» المجمّعة</h2>'+D.needs_check.map(n=>'<details><summary><b>'+esc(n.agent)+'</b> ('+n.items.length+')</summary>'+list(n.items.filter(x=>hit(x)))+'</details>').join('');
  $('#sv').onchange=e=>{state.sev=e.target.value;renderErrors()}; $('#sa').onchange=e=>{state.ag=e.target.value;renderErrors()};
}
function renderPlan(){
  const cls={'عالية':'b1','متوسطة':'b3','منخفضة':'b4'};
  const st=D.plan_stages.filter(s=>hit(JSON.stringify(s))).map(s=>'<tr><td>'+esc(s.stage)+'</td><td>'+esc(s.level)+'</td><td class="w">'+esc(s.task)+'</td><td><span class="badge '+cls[s.priority]+'">'+esc(s.priority)+'</span></td><td>'+esc(s.duration)+'</td><td class="w">'+esc(s.criterion)+'</td><td>'+esc(s.agent)+'</td></tr>');
  const tk=D.plan_tasks.filter(s=>hit(JSON.stringify(s))).map(s=>'<tr><td class="w">'+esc(s.task)+'</td><td>'+esc(s.stage)+'</td><td><span class="badge '+cls[s.priority]+'">'+esc(s.priority)+'</span></td><td>'+esc(s.duration)+'</td><td class="w">'+esc(s.criterion)+'</td><td>'+esc(s.agent)+'</td></tr>');
  $('#main').innerHTML='<h2>مراحل الرفع (المحرر)</h2><p class="muted">الجدول الزمني الإجمالي نحو 22–26 أسبوعًا [رأي المحرر].</p>'+table(['المرحلة','المستوى','المهمة','الأولوية','المدة','معيار القبول','الوكيل'],st)
   +'<h2>مهام من تقارير الوكلاء</h2>'+table(['المهمة','المرحلة','الأولوية','المدة','معيار القبول','الوكيل'],tk);
}
function renderSources(){
  const sel=state.sf||'';
  const rows=D.sources.filter(s=>(!sel||(sel==='nolink'?!s.url:!!s.url))&&hit(JSON.stringify(s)));
  $('#main').innerHTML='<div class="tools"><select id="sf"><option value="">كل المصادر</option><option value="link"'+(sel==='link'?' selected':'')+'>بروابط</option><option value="nolink"'+(sel==='nolink'?' selected':'')+'>بلا رابط</option></select><span class="count">'+rows.length+' من '+D.sources.length+'</span></div>'
   +table(['المصدر أو سياقه','النوع','الرابط','مستوى التحقق','الوكيل'],rows.map(s=>'<tr><td class="w">'+esc(s.name)+'</td><td>'+esc(s.kind)+'</td><td class="w">'+(s.url?'<a href="'+esc(s.url)+'" target="_blank" rel="noopener">'+esc(s.url.length>70?s.url.slice(0,70)+'…':s.url)+'</a>':'<span class="muted">'+NOLINK+'</span>')+'</td><td>'+esc(s.level)+'</td><td>'+esc(s.agents.join('، '))+'</td></tr>'));
  $('#sf').onchange=e=>{state.sf=e.target.value;renderSources()};
}
function renderFiqh(){
  let h='<h2>مراجع فقه الأقليات (المؤسس)</h2>'+table(['المرجع','الحالة','ما تحقق'],D.minority_refs.filter(r=>hit(r.join(' '))).map(r=>'<tr><td class="w">'+esc(r[0])+'</td><td>'+esc(r[1])+'</td><td class="w">'+linkify(r[2])+'</td></tr>'));
  h+='<h2>القواعد الفقهية المتحققة (المنهجي)</h2>';
  h+=D.rules?table(['القاعدة','صيغتها','المرجع في الشاملة','تطبيقها'],D.rules.filter(r=>hit(r.join(' '))).map(r=>'<tr><td>'+esc(r[0])+'</td><td class="w">'+esc(r[1])+'</td><td class="w">'+esc(r[2])+'</td><td class="w">'+esc(r[3])+'</td></tr>')):'<p class="muted">ينتظر تقرير المنهجي (13).</p>';
  h+='<h2>رسائل جامعية مشابهة (المنهجي)</h2>';
  h+=D.theses?table(['#','الرسالة','الدرجة والجامعة','الرابط','الاطلاع'],D.theses.filter(r=>hit(r.join(' '))).map(r=>'<tr><td>'+esc(r[0])+'</td><td class="w">'+esc(r[1])+'</td><td class="w">'+esc(r[2])+'</td><td class="w">'+linkify(r[3])+'</td><td>'+esc(r[4])+'</td></tr>')):'<p class="muted">ينتظر تقرير المنهجي (13).</p>';
  h+='<h2>مصفوفة التحديات والمقترحات (الفصل الخامس)</h2>'+table(['#','التحدي','مصدره','المقترح','الجهة','الجدوى القانونية','الدليل'],D.matrix.filter(r=>hit(r.join(' '))).map(r=>'<tr>'+r.map(c=>'<td class="w">'+esc(c)+'</td>').join('')+'</tr>'));
  $('#main').innerHTML=h;
}
function renderTeam(){
  $('#main').innerHTML='<div class="team">'+D.team.map(t=>'<div class="card"><h3>'+esc(t.name)+'</h3><p>'+esc(t.role)+'</p>'+(t.file?'<p class="muted" style="font-size:.8rem">'+esc(t.file)+'</p>':'')+'</div>').join('')+'</div>'
   +'<p class="muted">'+esc(D.meta.note)+' تاريخ التوليد: '+esc(D.meta.generated)+'.</p>';
}
function render(){
  document.querySelectorAll('#tabs button').forEach(b=>b.classList.toggle('on',b.dataset.t===state.tab));
  ({map:renderMap,new:renderNew,cases:renderCases,errors:renderErrors,plan:renderPlan,sources:renderSources,fiqh:renderFiqh,team:renderTeam})[state.tab]();
  if(state.tab==='map'){const sel=document.querySelector('#tree [data-node="'+state.node+'"]'); if(sel) sel.classList.add('sel');}
}
$('#tabs').innerHTML=TABS.map(t=>'<button type="button" data-t="'+t[0]+'">'+t[1]+'</button>').join('');
$('#tabs').onclick=e=>{const b=e.target.closest('button'); if(!b) return; state.tab=b.dataset.t; render(); window.scrollTo(0,0);};
$('#q').oninput=e=>{state.q=e.target.value.trim(); render();};
['fm','fv','fs'].forEach(id=>$('#'+id).onchange=e=>{state[id]=e.target.value; state.tab='map'; if(id!=='fs'||true) render();});
$('#db').onclick=()=>{const t=$('#tree'); if(t) t.classList.toggle('open');};
function fixHeader(){document.documentElement.style.setProperty('--hh',$('#hd').offsetHeight+'px');}
addEventListener('resize',fixHeader); fixHeader();
state.node='all';
render();
</script>
</body>
</html>
'''


def main():
    blob = json.dumps(D, ensure_ascii=False).replace('</', '<\\/')
    html = TEMPLATE.replace('__DATA__', blob)
    p = os.path.join(OUT, 'خريطة_الرسالة_التفاعلية.html')
    with open(p, 'w', encoding='utf-8') as f:
        f.write(html)
    print('saved', p, len(html) // 1024, 'KB')


if __name__ == '__main__':
    main()
