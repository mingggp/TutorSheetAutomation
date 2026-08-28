const {Document,Packer,Paragraph,TextRun,ImageRun,Tab,TabStopType,BorderStyle,
       AlignmentType,PageBreak,Footer,PageNumber,LineRuleType}=require('docx');
const fs=require('fs'), path=require('path');

const BANK=JSON.parse(fs.readFileSync(path.join(__dirname,'questions.json'),'utf8'));

// ---------- ค่าที่สั่งได้จากบรรทัดคำสั่ง ----------
const argv=process.argv.slice(2);
const arg=(k,d)=>{const i=argv.indexOf('--'+k);return i<0?d:argv[i+1];};
const MIX = arg('mix','std');              // easy | std | hard
const N   = parseInt(arg('n','50'),10);
const SET = arg('set','1');
const OUTF= arg('out','out.docx');

// ของที่ต่างกันระหว่างวิชาอยู่ใน subjects.json ไฟล์เดียว เพิ่มวิชาใหม่ไม่ต้องแตะไฟล์นี้
const KEY = argv.includes('--key');          // ฉบับครู มีเฉลย
const CAP = parseInt(arg('cap','2'),10);     // แนวเดียวกันได้ไม่เกินกี่ข้อต่อชีท (กติกาข้อ 5)
const SUBJ= arg('subject','tpat3');
const SUB = JSON.parse(fs.readFileSync(path.join(__dirname,'subjects.json'),'utf8'))[SUBJ];
if(!SUB||!SUB.parts){console.error('ไม่รู้จักวิชา "'+SUBJ+'" — ดูรายชื่อคีย์ใน subjects.json');process.exit(1);}
const PMETA=Object.fromEntries(SUB.parts.map(p=>[p.key,p]));

const PLAN={
  easy:{prio:[1,2,3], star:'star1.png'},
  std :{prio:[2,1,3], star:'star2.png'},
  hard:{prio:[3,2,1], star:'star3.png'},
}[MIX];
if(!PLAN){console.error('mix ต้องเป็น easy | std | hard');process.exit(1);}

function pickPart(part,quota){
  const idx=BANK.map((q,i)=>({q,i})).filter(o=>o.q.part===part);
  const out=[], seen=new Set(), n={};
  // เก็บทีละรอบ ค่อย ๆ ผ่อนเพดานจำนวนข้อต่อแนว
  // รอบแรกจำกัดแนวละ CAP ข้อตามกติกาข้อ 5 ถ้าคลังไม่พอค่อยผ่อนทีละขั้น
  // ผลคือชีทได้หลายแนวก่อนเสมอ แทนที่จะกวาดจากหัวคลังจนแนวแรกล้น
  for(let cap=CAP; cap<=quota && out.length<quota; cap++){
    for(const lv of PLAN.prio){
      for(const o of idx){
        if(out.length>=quota) break;
        if(o.q.lvl!==lv || seen.has(o.i)) continue;
        const a=o.q.arche;
        if((n[a]||0)>=cap) continue;
        out.push(o); seen.add(o.i); n[a]=(n[a]||0)+1;
      }
      if(out.length>=quota) break;
    }
  }
  // เรียงจากง่ายไปยากภายในพาร์ท (ภายในระดับเดียวกันยังจัดกลุ่มตามแนวโจทย์)
  return out.sort((a,b)=>a.q.lvl-b.q.lvl || a.i-b.i).map(o=>o.q);
}
// แบ่งโควตาให้ทุกพาร์ทเท่า ๆ กัน เศษที่เหลือตกกับพาร์ทต้น ๆ
// (TPAT3 มี 2 พาร์ท · TGAT2 มี 3 ท่อน · วิชาต่อไปอาจไม่เท่านี้)
const NP=SUB.parts.length;
const quota=SUB.parts.map((_,i)=>Math.floor(N/NP)+(i<N%NP?1:0));
const QS=SUB.parts.flatMap((p,i)=>pickPart(p.key,quota[i]));
const cnt=[1,2,3].map(lv=>QS.filter(q=>q.lvl===lv).length);

// ---------- สไตล์ ----------
const F="Sarabun";
const SUBC=SUB.color, T1="00D5C9", T3="28A1AB";
const INK="1F2528", MID="5B6669", SOFT="9AA5A8", HAIR="D3DADC";
const CH=SUB.optionLabels||["ก.","ข.","ค.","ง.","จ."], BODY=27, USABLE=9638, MAXIMG=600, IND=580;

const T=(t,o={})=>new TextRun({text:t,font:F,size:o.size||BODY,bold:o.bold,color:o.color||INK});
const P=(runs,o={})=>new Paragraph({
  spacing:{before:o.before||0,after:o.after||0,
           ...(o.line===0?{}:{line:o.line||300,lineRule:LineRuleType.AUTO})},
  alignment:o.align,indent:o.indent,keepNext:o.keepNext,keepLines:true,
  border:o.border,tabStops:o.tabStops,
  children:Array.isArray(runs)?runs:[T(runs,o)]});

// hi = ไฟล์นี้ถูกเก็บที่ความละเอียดกี่เท่าของขนาดที่จะแสดง (ดู draw._save)
// รูปเล็กอย่างโลโก้กับดาวเก็บ 3 เท่าเพื่อให้คมตอนพิมพ์ ต้องหารกลับตอนวาง
function pic(file,{scale=1,hi=1}={}){
  const buf=fs.readFileSync(path.join(__dirname,'img',file));
  const w=buf.readUInt32BE(16), h=buf.readUInt32BE(20);
  const s=scale*Math.min(1,MAXIMG/(w/hi))/hi;
  return new ImageRun({type:"png",data:buf,transformation:{width:Math.round(w*s),height:Math.round(h*s)}});
}
const COLTABS=[2480,4380,6280,8180].map(p=>({type:TabStopType.LEFT,position:p}));

function questionKept(q,i){
  const out=[]; const push=(runs,o)=>out.push([runs,o]);
  const gap = (PMETA[q.part]||{}).gap ?? 460;
  // **ข้อความ** ในโจทย์ = ตัวหนา ใช้เน้นคำปฏิเสธอย่าง "ไม่ใช่" กับ "เป็นไปไม่ได้"
  // ซึ่งเด็กอ่านข้ามบ่อยที่สุด ถ้าไม่รองรับ ดอกจันจะพิมพ์ออกมาในชีทจริง
  const segs = ln => ln.split("**").map((t,j)=>[t, j%2===1]).filter(([t])=>t!=="");
  q.stem.split(/\r?\n/).forEach((ln,k)=>{
    const runs = k===0
      ? [T(i+".",{bold:true,color:T3}),new TextRun({children:[new Tab()],font:F,size:BODY})]
      : [];
    segs(ln).forEach(([t,b])=>runs.push(T(t,{bold:b||undefined})));
    push(runs,
      {before:k===0?gap:60,after:0,line:340,
       indent:{left:IND,hanging:k===0?IND:0},
       tabStops:[{type:TabStopType.LEFT,position:IND}]});
  });
  if(q.img)    push([pic(q.img,{scale:0.80})],{align:AlignmentType.CENTER,before:200,after:100,line:0});
  if(q.optimg){
    push([pic(q.optimg,{scale:0.92})],{align:AlignmentType.CENTER,before:130,after:40,line:0});
    // ตัวเลือกเป็นรูป ระบายสีในตัวเลือกไม่ได้ ต้องพิมพ์เฉลยกำกับใต้แถบรูปแทน
    // ไม่งั้นครูต้องพลิกไปดูตารางท้ายเล่มถึงครึ่งชีท (21 จาก 50 ข้อเป็นแบบนี้)
    if(KEY) push([T("เฉลย  ",{size:22,color:MID}),
                  T(CH[q.ansIdx],{size:30,bold:true,color:SUBC})],
                 {align:AlignmentType.CENTER,before:0,after:110});
    else push([T("")],{after:80,line:0});
  }
  else if(q.choices.some(c=>c.length>10) || q.choices.join("").length>44){
    q.choices.forEach((c,k)=>{
      const hit = KEY && k===q.ansIdx;
      push([T(CH[k]+"   ",{bold:true,color:hit?SUBC:undefined}),
            T(c,{bold:hit||undefined,color:hit?SUBC:undefined})],
        {before:80,after:80,indent:{left:IND+260,hanging:260}});
    });
  } else {
    const runs=[];
    q.choices.forEach((c,k)=>{
      if(k) runs.push(new TextRun({children:[new Tab()],font:F,size:BODY}));
      const hit = KEY && k===q.ansIdx;
      runs.push(T(CH[k]+"  ",{bold:true,color:hit?SUBC:undefined}),
                T(c,{bold:hit||undefined,color:hit?SUBC:undefined}));
    });
    push(runs,{before:130,after:60,indent:{left:IND},tabStops:COLTABS});
  }
  return out.map(([runs,o],k)=>P(runs,{...o,keepNext:k<out.length-1}));
}

const kids=[];
kids.push(P([T(SUB.name,{size:64,bold:true,color:SUBC}),
             T("   "+SUB.series+SET+(KEY?"  ·  ฉบับครู":"")+"   ",{size:28,bold:true,color:INK}),
             pic(PLAN.star,{scale:0.62,hi:3}),
             new TextRun({children:[new Tab()],font:F,size:28}),
             pic("badge.png",{scale:0.62,hi:3})],
            {after:150,line:0,tabStops:[{type:TabStopType.RIGHT,position:USABLE}]}));
kids.push(P([pic(SUB.flowImg+".png",{hi:3})],{align:AlignmentType.CENTER,before:30,after:120,line:0}));
kids.push(P([T("")],{after:60,border:{bottom:{style:BorderStyle.SINGLE,size:8,color:T1,space:6}},line:200}));

let part=null;
QS.forEach((q,idx)=>{
  if(q.part!==part){
    part=q.part;
    const isP1=part===SUB.parts[0].key;
    if(!isP1) kids.push(new Paragraph({children:[new PageBreak()]}));
    kids.push(P([T(part,{size:34,bold:true,color:SUBC}),
                 T("   ·   "+((PMETA[part]||{}).label||""),{size:31,bold:true})],
                {before:isP1?280:0,after:30,keepNext:true}));
    kids.push(P([T("")],
                {after:180,keepNext:true,line:120,
                 border:{bottom:{style:BorderStyle.SINGLE,size:6,color:"00C8B5",space:5}}}));
  }
  questionKept(q,idx+1).forEach(x=>kids.push(x));
});
if(KEY){
  // ตารางเฉลยรวมท้ายเล่ม — จำเป็นเพราะข้อที่ตัวเลือกเป็นรูป ระบายในตัวข้อไม่ได้
  kids.push(new Paragraph({children:[new PageBreak()]}));
  kids.push(P([T("เฉลยรวม",{size:40,bold:true,color:SUBC})],{after:60}));
  kids.push(P([T(QS.length+" ข้อ   ·   ระบายสีในตัวข้อแล้วเฉพาะข้อที่ตัวเลือกเป็นตัวหนังสือ",
                 {size:22,color:MID})],{after:220}));
  const KTAB=[900,1800,2700,3600,4500,5400,6300,7200,8100].map(x=>({type:TabStopType.LEFT,position:x}));
  for(let r=0;r<QS.length;r+=10){
    const runs=[];
    QS.slice(r,r+10).forEach((q,k)=>{
      if(k) runs.push(new TextRun({children:[new Tab()],font:F,size:BODY}));
      runs.push(T((r+k+1)+". ",{size:23,color:MID}),
                T(CH[q.ansIdx].replace(/[.)]/,""),{size:26,bold:true,color:T3}));
    });
    kids.push(P(runs,{before:60,after:60,tabStops:KTAB}));
  }
}
// เส้นกับข้อความอยู่บรรทัดเดียวกัน — ใช้ em dash เพราะ Sarabun ไม่มีอักขระ box-drawing
const DASH = "—".repeat(13);
kids.push(P([T(DASH+"  ",{size:21,color:HAIR}),
             T("End of Exercise",{size:21,color:SOFT}),
             T("  "+DASH,{size:21,color:HAIR})],
            {before:560,align:AlignmentType.CENTER}));

const doc=new Document({
  styles:{default:{document:{run:{font:F,size:BODY,color:INK}}},
          paragraphStyles:[{id:"FootLine",name:"FootLine",basedOn:"Normal",
            run:{font:F,size:14,color:"BCC5C7"}}]},
  sections:[{
    properties:{page:{margin:{top:1134,bottom:1000,left:1134,right:1134}}},
    footers:{default:new Footer({children:[
      new Paragraph({style:"FootLine",
        tabStops:[{type:TabStopType.RIGHT,position:USABLE}],
        border:{top:{style:BorderStyle.SINGLE,size:4,color:HAIR,space:6}},
        children:[new TextRun({text:"mingsmileyface",font:F,size:17,color:SOFT}),
                  new TextRun({children:[new Tab()],font:F,size:14}),
                  new TextRun({children:[PageNumber.CURRENT],font:F,size:14,color:"BCC5C7"})]})
    ]})},
    children:kids}]
});
Packer.toBuffer(doc).then(b=>{fs.writeFileSync(path.join(__dirname,OUTF),b);
  console.log(OUTF,'|',MIX,'| ข้อ',QS.length,'| ง่าย',cnt[0],'ปานกลาง',cnt[1],'ยาก',cnt[2]);});
