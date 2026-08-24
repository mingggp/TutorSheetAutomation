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
  const out=[];
  for(const lv of PLAN.prio){
    for(const o of idx){
      if(out.length>=quota) break;
      if(o.q.lvl===lv && !out.includes(o)) out.push(o);
    }
    if(out.length>=quota) break;
  }
  // เรียงจากง่ายไปยากภายในพาร์ท (ภายในระดับเดียวกันยังจัดกลุ่มตามแนวโจทย์)
  return out.sort((a,b)=>a.q.lvl-b.q.lvl || a.i-b.i).map(o=>o.q);
}
const half=Math.round(N/2);
const QS=[...pickPart(SUB.parts[0].key,half),...pickPart(SUB.parts[1].key,N-half)];
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

function pic(file,{scale=1}={}){
  const buf=fs.readFileSync(path.join(__dirname,'img',file));
  const w=buf.readUInt32BE(16), h=buf.readUInt32BE(20);
  const s=scale*Math.min(1,MAXIMG/w);
  return new ImageRun({type:"png",data:buf,transformation:{width:Math.round(w*s),height:Math.round(h*s)}});
}
const COLTABS=[2480,4380,6280,8180].map(p=>({type:TabStopType.LEFT,position:p}));

function questionKept(q,i){
  const out=[]; const push=(runs,o)=>out.push([runs,o]);
  const gap = (PMETA[q.part]||{}).gap ?? 460;
  q.stem.split("\n").forEach((ln,k)=>{
    push(k===0?[T(i+".",{bold:true,color:T3}),new TextRun({children:[new Tab()],font:F,size:BODY}),T(ln)]:[T(ln)],
      {before:k===0?gap:60,after:0,line:340,
       indent:{left:IND,hanging:k===0?IND:0},
       tabStops:[{type:TabStopType.LEFT,position:IND}]});
  });
  if(q.img)    push([pic(q.img,{scale:0.80})],{align:AlignmentType.CENTER,before:200,after:100,line:0});
  if(q.optimg) push([pic(q.optimg,{scale:0.92})],{align:AlignmentType.CENTER,before:130,after:120,line:0});
  else if(q.choices.some(c=>c.length>10) || q.choices.join("").length>44){
    q.choices.forEach((c,k)=>push([T(CH[k]+"   ",{bold:true}),T(c)],
      {before:80,after:80,indent:{left:IND+260,hanging:260}}));
  } else {
    const runs=[];
    q.choices.forEach((c,k)=>{
      if(k) runs.push(new TextRun({children:[new Tab()],font:F,size:BODY}));
      runs.push(T(CH[k]+"  ",{bold:true}),T(c));
    });
    push(runs,{before:130,after:60,indent:{left:IND},tabStops:COLTABS});
  }
  return out.map(([runs,o],k)=>P(runs,{...o,keepNext:k<out.length-1}));
}

const kids=[];
kids.push(P([T(SUB.name,{size:64,bold:true,color:SUBC}),
             T("   "+SUB.series+SET+"   ",{size:28,bold:true,color:INK}),
             pic(PLAN.star,{scale:0.62}),
             new TextRun({children:[new Tab()],font:F,size:28}),
             pic("badge.png",{scale:0.62})],
            {after:150,line:0,tabStops:[{type:TabStopType.RIGHT,position:USABLE}]}));
kids.push(P([pic(SUB.flowImg+".png")],{align:AlignmentType.CENTER,before:30,after:120,line:0}));
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
kids.push(P([T("")],{before:520,after:0,line:120,
             border:{bottom:{style:BorderStyle.SINGLE,size:4,color:HAIR,space:2}}}));
kids.push(P([T("End of Exercise",{size:21,color:SOFT})],{before:120,align:AlignmentType.CENTER}));

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
