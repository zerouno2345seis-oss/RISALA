const fs=require('fs');
const {Document,Packer,Paragraph,TextRun,FootnoteReferenceRun,AlignmentType,PageBreak,Footer,PageNumber,LineRuleType}=require('/opt/node22/lib/node_modules/docx');
const AR='Traditional Arabic', LAT='Times New Roman';
// ---- helpers: split Latin segments to Times New Roman
const LATRE=/([A-Za-zÀ-ÿ][A-Za-zÀ-ÿ0-9.,'’\-]*(?:\s+[A-Za-zÀ-ÿ0-9][A-Za-zÀ-ÿ0-9.,'’\-]*)*)/g;
function runs(text,{ar,lat,latSize,bold=false,italics=false,sz=36,lsz=24}){
  const out=[];let last=0,m;
  while((m=LATRE.exec(text))){
    if(m.index>last)out.push(new TextRun({text:text.slice(last,m.index),style:ar,bold,rightToLeft:true,font:AR,size:sz,sizeComplexScript:sz}));
    out.push(new TextRun({text:m[0],style:lat,italics:italics,font:LAT,size:lsz,sizeComplexScript:lsz}));
    last=m.index+m[0].length;
  }
  if(last<text.length)out.push(new TextRun({text:text.slice(last),style:ar,bold,rightToLeft:true,font:AR,size:sz,sizeComplexScript:sz}));
  return out;
}
const fns={};let fid=0;
function fn(text){ // footnote content; **x** = bold title
  fid++;
  const parts=(' '+text).split('**');const ch=[];
  parts.forEach((p,i)=>ch.push(...runs(p,{ar:'FootAr',lat:'FootLat',bold:i%2===1,sz:28,lsz:20})));
  fns[fid]={children:[new Paragraph({style:'FootP',bidirectional:true,alignment:AlignmentType.START,children:ch})]};
  return fid;
}
function P(parts,style='MatnAr'){
  const ch=[];
  for(const p of parts){
    if(typeof p==='string')ch.push(...runs(p,{ar:'BodyAr',lat:'BodyLat'}));
    else if(p.fn)ch.push(new FootnoteReferenceRun(p.fn));
    else if(p.b)ch.push(new TextRun({text:p.b,style:'BodyAr',bold:true,rightToLeft:true,font:AR,size:36,sizeComplexScript:36}));
  }
  return new Paragraph({style,bidirectional:true,alignment:AlignmentType.START,children:ch});
}
function H(t,style){return new Paragraph({style,bidirectional:true,alignment:AlignmentType.START,children:[new TextRun({text:t,rightToLeft:true,font:AR,bold:true,size:36,sizeComplexScript:36})]});}
function ESQ(t){return new Paragraph({style:'QForeign',children:[new TextRun({text:t,style:'BodyLat'})]});}
// ---- content
const LAWNOTE='القانون المدني والتجاري للأمة (Ley 26.994)، ';
const L='http://servicios.infoleg.gob.ar/infolegInternet/anexos/235000-239999/235975/texact.htm';
const body=[];
body.push(H('المطلب الأول: ازدواجية العقد بين المحكمة والمسجد','HSub'));
body.push(H('أولًا: صورة الإشكالية','HMas'));
body.push(P(['يتزوج المسلمون في الأرجنتين بعقدين منفصلين لا يعترف أحدهما بالآخر: عقد مدني يُبرم أمام موظف سجل الحالة المدنية، وعقد شرعي يُبرم في المسجد أو المركز الإسلامي. فالقانون الأرجنتيني لا يرتّب على العقد الشرعي وحده أي أثر مدني، والفقهاء المعاصرون يتحفظون على العقد المدني وحده، لخلوه من الولي، واكتفائه بشاهد غير مسلم، وإغفاله المهر والصيغة الشرعية. فمن اقتصر على العقد الشرعي بقي زواجه بلا وجود قانوني، ومن اقتصر على العقد المدني بقي زواجه موضع نظر شرعي. ويُلاحَظ في الواقع أن بعض المراكز الإسلامية تشترط إبراز محضر الزواج المدني قبل إجراء العقد الشرعي، وأن بعضها يكتفي بالعقد الشرعي.']));
body.push(P(['وتثير هذه الازدواجية ثلاثة أسئلة: ما حكم العقد المدني وحده في الشريعة؟ وما حكم العقد الشرعي غير الموثق مدنيًّا؟ وما أثر كل منهما في القانون، وكيف يُجمع بين العقدين دون تعارض؟']));
body.push(H('ثانيًا: الحكم الشرعي','HMas'));
body.push(P(['اتفق الفقهاء على أن النكاح لا يكون سرًّا، واختلفوا في وسيلة إعلانه وإثباته. فالحنفية',{fn:fn('المرغيناني، **الهداية في شرح بداية المبتدي**، ج1، ص185.')},' والشافعية',{fn:fn('الخطيب الشربيني، **مغني المحتاج إلى معرفة معاني ألفاظ المنهاج**، ج4، ص234.')},' والحنابلة في المشهور',{fn:fn('ابن قدامة، **المغني**، تحقيق التركي، ج9، ص347.')},' يشترطون حضور شاهدين عند العقد. أما الإمام مالك رحمه الله فيكتفي بالإعلان؛ والإشهاد عند المالكية',{fn:fn('الدردير، **الشرح الكبير** (بحاشية الدسوقي)، ج2، ص216، 236–237.')},' مندوب عند العقد، واجب عند الدخول، ويُفسخ نكاح السر المتواصى بكتمانه. وعلة الإشهاد صيانة العقد من الجحود وحفظ النسب، وقد جاء في تعليلها:']));
body.push(P(['«ولأنَّه يتعلَّقُ به حَقُّ غيرِ المُتَعاقِدَيْنِ، وهو الوَلَدُ، فاشْتُرِطتِ الشهادةُ فيه، لئلَّا يَجحَدَه أبُوه».',{fn:fn('ابن قدامة، **المغني**، ج9، ص348.')}]));
body.push(P(['أما التوثيق الكتابي فلم يعدّه المتقدمون ركنًا ولا شرطًا. وقد نبّه شيخ الإسلام ابن تيمية رحمه الله إلى أن الصحابة رضي الله عنهم لم يكونوا يكتبون الصداقات، وأنه قد يقال بوجوب الإشهاد في الأماكن التي يجهل الناس فيها حال بعضهم.',{fn:fn('ابن تيمية، **مجموع الفتاوى**، ج32، ص131، بتصرف.')}]));
body.push(P(['واختلف المعاصرون في العقد الشرعي غير الموثق مدنيًّا بعد اتفاقهم على صحته إذا استوفى أركانه. فمنهم من لا يوجب توثيقه لأن الكتابة ليست ركنًا ولا شرطًا، ومنهم من يوجب التوثيق ويؤثّم تاركه، استنادًا إلى طاعة ولي الأمر ومصلحة حفظ الحقوق وحفظ الأنساب.',{fn:fn('السبيعي، **المسائل الفقهية المستجدة في النكاح مع بيان ما أخذ به القانون الكويتي**، ص162، 164–166، بتصرف.')},' ويحتاج الاستناد إلى طاعة ولي الأمر إلى تكييف إذا كان الحاكم غير مسلم، فيُردّ الوجوب حينئذ إلى حفظ الحقوق وقاعدة أن للوسائل أحكام المقاصد.']));
body.push(P(['أما العقد المدني وحده فيرى بعض المعاصرين أنه لا ينعقد به نكاح شرعًا، لاجتماع مخالفات فيه: خلوّه من الولي، واكتفائه بشاهد غير مسلم، وخلوّه من المهر، وعدم اشتماله على إيجاب وقبول شرعيين؛ وأن التوثيق المدني لا صلة له بصحة العقد، فمن احتاج إليه أجرى بعده عقدًا بصيغة شرعية.',{fn:fn('يسري إبراهيم، **فقه النوازل للأقليات المسلمة**، ج2، ص991–992، 998، بتصرف.')},' ويرى آخرون أن العقد المدني إذا تحقق إشهاره وخلا من موانع الزواج ترتبت عليه آثار الزواج للشبهة، مع وجوب إعادته في الإطار الإسلامي.',{fn:fn('قرارات المؤتمر السنوي الثاني لمجمع فقهاء الشريعة بأمريكا، كوبنهاغن، 22–25 يونيو 2004م، المحور السادس. https://www.amjaonline.org/declaration-articles/decisions-and-recommendations-of-amjas-second-annual-convention-denmark-ar')}]));
body.push(H('ثالثًا: الحكم القانوني الأرجنتيني','HMas'));
body.push(P(['تشترط المادة 406 من القانون المدني والتجاري',{fn:fn(LAWNOTE+'المادة 406. '+L)},' لوجود الزواج رضا الزوجين معبَّرًا عنه بشخصيهما أمام السلطة المختصة بإبرامه، وتنص على أن:']));
body.push(ESQ('«El acto que carece de este requisito no produce efectos civiles.»'));
body.push(P(['أي أن «التصرف الذي يخلو من هذا الشرط لا يرتّب آثارًا مدنية». وقد عدّ الشرّاح فقد هذا الشرط سببًا لانعدام التصرف (inexistencia) لا لبطلانه، فلا زواج إذا أُعطي الرضا أمام سلطة دينية فقط.',{fn:fn('Herrera, Caramelo, Picasso (dirs.), **Código Civil y Comercial de la Nación Comentado**, t. II, Buenos Aires, Infojus, 2015, pp. 13–14، بتصرف.')}]));
body.push(P(['وتشترط المادة 418 أن يُعقد الزواج علنًا بحضور شاهدين، وأربعة إن عُقد خارج مكتب السجل.',{fn:fn(LAWNOTE+'المادة 418. '+L)},' ولا يُقيَّد في دفاتر الزواج إلا ما عُقد أمام السلطة المختصة أو أمر بقيده قاضٍ.',{fn:fn('Ley 26.413 de Registro del Estado Civil y Capacidad de las Personas، المادتان 1 و51.')},' وحيازة الحالة الزوجية (posesión de estado) وحدها لا تكفي لإثبات الزواج.',{fn:fn(LAWNOTE+'المادة 423.')}]));
body.push(P(['وأقرب نظام قانوني يستوعب من اقتصر على العقد الشرعي هو الاتحاد المعيشي (unión convivencial)،',{fn:fn(LAWNOTE+'المادتان 509 و510.')},' ويُشترط له استمرار المساكنة سنتين وانتفاء مانع الرابطة الزوجية. وأثره محدود: فالأموال المكتسبة تبقى في ذمة من اكتسبها ما لم يوجد اتفاق،',{fn:fn(LAWNOTE+'المادة 528.')},' ولا يرث إلا الزوج لا الشريك في هذا الاتحاد،',{fn:fn(LAWNOTE+'المادة 2424.')},' ولا يثبت للباقي منهما إلا حق السكنى سنتين.',{fn:fn(LAWNOTE+'المادة 527.')},' ولم تقف الدراسة فيما اطّلعت عليه من الأحكام على حكم أرجنتيني في أثر العقد الشرعي وحده.']));
body.push(H('رابعًا: المقارنة والحلول','HMas'));
body.push(P(['يتفق الفقه والقانون على أن الزواج لا يكون سرًّا، وأن علة ذلك صيانة العقد من الجحود وحفظ النسب. ويفترقان في ثلاثة مواضع: الأول أن القانون يجعل حضور الموظف العام شرط وجود للزواج، بينما لا يجعل الفقه التوثيق شرط صحة، فالعقد الشرعي صحيح في الشريعة لا وجود له في القانون. والثاني أن العقد المدني وحده صحيح في القانون، مختلف فيه في الشريعة بين من يمنع انعقاده ومن يرتب عليه آثار الشبهة. والثالث أن القانون لا يشترط في الشاهدين الإسلام، بخلاف المذاهب الأربعة في نكاح المسلمة.']));
body.push(P(['ويمكن الجمع بين العقدين بأربع وسائل، يُفصَّل القول فيها في الفصل الخامس: أولاها العقد المزدوج في مجلس واحد، لأن المادة 418 تجيز عقد الزواج المدني خارج المكتب بأربعة شهود دون اشتراط تعذر الحضور،',{fn:fn('Herrera, Caramelo, Picasso (dirs.), **Código Civil y Comercial de la Nación Comentado**, t. II, Buenos Aires, Infojus, 2015, p. 25.')},' فيحضر الموظف إلى المسجد ويُجرى العقدان معًا، مع اختيار شاهدين مسلمين وإجراء الإيجاب والقبول الشرعيين بحضور الولي. وثانيتها تقديم العقد المدني وإجراء العقد الشرعي عقبه مباشرة. وثالثتها حماية من اقتصرت على العقد الشرعي باتفاق مكتوب في الأموال والسكن ووصية في حدود ما يجيزه القانون. ورابعتها بروتوكول موحد تلتزمه المراكز الإسلامية.']));
// ---- appendix
body.push(new Paragraph({children:[new PageBreak()]}));
body.push(H('ملحق للمراجعة (ليس من المتن)','HSub'));
const notes=[
'قرار معلّق: في العقد المدني وحده، هل يُعتمد في الرسالة قول من لا يصححه أم قرار المجمع (شبهة مع وجوب الإعادة)؟ عُرض القولان بلا ترجيح.',
'الملاحظة الميدانية في المقدمة (اشتراط بعض المراكز محضر الزواج المدني) من خبرة الباحث، ولا حاشية لها بحسب قاعدة عدم الاستشهاد بأعماله.',
'بيانات الطبعات (الهداية، مغني المحتاج، المغني، الشرح الكبير، مجموع الفتاوى، السبيعي، يسري إبراهيم) تُذكر في ثبت المصادر آخر الرسالة، ولم تُطابق صفحات المغني على طبعة دار عالم الكتب 1997 بعد.',
'الحاشية 9: نص قرار المجمع (2004) منقول من تقرير المشروع ولم يُطابق على صفحة القرار ولا على PDF؛ يحتاج مطابقة قبل الطباعة.',
'الحاشية 7 (السبيعي): لم تُنقل حاشية الصفحة 162 بحروفها، وموضع حاشية القول الثاني بين ص164 وص165 غير محسوم.',
'الحاشيتان 11 و19: ترجمة نصوص الشرّاح أولية. والحواشي 14 و16 و18 (المواد 423 و528 و527): لم تُنقل نصوصها بعد إلى المرجع الموحد للنصوص القانونية. والحاشية 12: عدم اشتراط دين الشاهدين في المادة 418 مستنتج من سكوت النص.',
'الحاشية 19: لوائح سجل بوينس آيرس في إجراء الزواج المدني داخل دور العبادة لم يُتحقق منها.',
'حُذف من المتن ما لم يُقرأ نصه: حكم محكمة فوز دو إيغواسو (البرازيل)، وحكم Akhter v Khan (إنجلترا 2020)، ونسبة قرار المؤتمر السادس (2009).',
'الروابط في حاشيتي القانون والمجمع إبقاءٌ لتوجيه المشرف في الإحالة إلى المصدر الرسمي؛ ويُعدَّل إن رأيتَ غير ذلك.'
];
notes.forEach(t=>body.push(P(['• '+t])));
// ---- styles
const sty={default:{document:{run:{font:AR,size:36,sizeComplexScript:36,rightToLeft:true,language:{value:'ar-SA',bidirectional:'ar-SA',eastAsia:'ar-SA'}}}},paragraphStyles:[
 {id:'MatnAr',name:'متن عربي 18',basedOn:'Normal',quickFormat:true,run:{font:AR,size:36,sizeComplexScript:36,color:'000000'},paragraph:{alignment:AlignmentType.START,bidirectional:true,spacing:{line:240,lineRule:LineRuleType.AUTO,after:60}}},
 {id:'HMain',name:'عنوان رئيسي عربي Bold',basedOn:'MatnAr',run:{bold:true,size:40,sizeComplexScript:40},paragraph:{spacing:{before:120,after:120},keepNext:true}},
 {id:'HSub',name:'عنوان فرعي عربي Bold',basedOn:'MatnAr',run:{bold:true,size:36,sizeComplexScript:36},paragraph:{spacing:{before:120,after:60},keepNext:true}},
 {id:'HMas',name:'عنوان مسألة عربي Bold',basedOn:'MatnAr',run:{bold:true,size:36,sizeComplexScript:36},paragraph:{spacing:{before:120,after:120},keepNext:true}},
 {id:'FootP',name:'حاشية عربية 14',basedOn:'MatnAr',run:{size:28,sizeComplexScript:28},paragraph:{spacing:{after:0}}},
 {id:'QForeign',name:'اقتباس أجنبي',basedOn:'Normal',run:{font:LAT,size:24},paragraph:{alignment:AlignmentType.LEFT,bidirectional:false,spacing:{line:240,after:60}}}
],characterStyles:[
 {id:'BodyAr',name:'متن عربي (حرف)',run:{font:AR,size:36,sizeComplexScript:36,color:'000000',rightToLeft:true}},
 {id:'BodyLat',name:'مصطلح أجنبي في المتن Times 12',run:{language:{value:'es-AR'},font:LAT,size:24,sizeComplexScript:24,color:'000000'}},
 {id:'FootAr',name:'حاشية عربية (حرف)',run:{font:AR,size:28,sizeComplexScript:28,rightToLeft:true}},
 {id:'FootLat',name:'مصطلح أجنبي في الحاشية Times 10',run:{language:{value:'es-AR'},font:LAT,size:20,sizeComplexScript:20}},
 {id:'FootnoteReference',name:'رقم الحاشية في المتن مرتفع',basedOn:'DefaultParagraphFont',run:{superScript:true,font:AR,size:28,sizeComplexScript:28}}
]};

const cm=x=>Math.round(x*567);
const doc=new Document({styles:sty,footnotes:fns,sections:[{
 properties:{page:{size:{width:11906,height:16838},margin:{top:cm(2.5),bottom:cm(3),left:cm(1.5),right:cm(3.5),footer:cm(1.2)}}},
 footers:{default:new Footer({children:[new Paragraph({alignment:AlignmentType.CENTER,children:[new TextRun({children:[PageNumber.CURRENT],font:AR,size:28})]})]})},
 children:body}]});
Packer.toBuffer(doc).then(b=>{fs.mkdirSync(process.argv[2],{recursive:true});fs.writeFileSync(process.argv[2]+'/'+process.argv[3],b);console.log('ok');});
