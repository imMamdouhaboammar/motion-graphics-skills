from pathlib import Path
import csv,json,math
from html import escape
from rebuild_cards import build as cards
p=Path(__file__).resolve().parents[1]
a={r['asset_id']:r['output_path'] for r in csv.DictReader((p/'assets/asset_manifest.csv').open(encoding='utf-8-sig'))};a['R01']='assets/rebuild/R01_overhead_workspace.png';a['R02']='assets/rebuild/R02_olive_plant.png'
T=[0,2.5,148/30,296/30,13.5,488/30,18.1,671/30,26.3,32.2,1117/30,41.5,1451/30]
htmls={};css=[];j=[]
def image(key,id,x,y,w,h=None,style='',cls='photo'):
 return f'<img id="{id}" class="{cls}" src="{a[key]}" style="left:{x}px;top:{y}px;width:{w}px;'+(f'height:{h}px;' if h else '')+style+'"/>'
def text(s,id,x,y,w,size=90,style='',cls='copy'):
 return f'<div id="{id}" class="{cls}" dir="rtl" style="left:{x}px;top:{y}px;width:{w}px;font-size:{size}px;{style}">{s}</div>'
def world(n,s,style=''):
 htmls[n]=f'<div id="cam{n}" class="camera" style="{style}">{s}</div>'
#01 Camera starts in open sky, descends through ribbon to oversized founder/action.
s=image('A02','r2sky',-190,-800,1460,3000,'object-fit:cover','plate')+image('A01','r2founder',-35,710,960)+text('ناوي تدخل','r2skytype',140,-360,800,98,'color:#f7f2e8;text-shadow:0 4px 14px #453f34aa')
s+='<div id="r2banner" class="r2banner" style="left:-100px;top:440px;width:1280px;height:250px;transform:rotate(-5deg)">'+text('الذكاء الاصطناعي؟','r2btype',90,62,1100,94,'color:#f8f2e7')+'</div>'
s+=text('في شغلك','r2floorcopy',100,1600,800,85,'color:#f7f2e8;text-shadow:0 5px 11px #453f34')
world(1,s)
j.append("tl.fromTo('#cam1',{y:780,scale:1.13},{y:-150,scale:1,duration:1.0,ease:'power3.inOut'},0);tl.from('#r2banner',{x:180,duration:.6,ease:'power3.out'},.55);tl.from('#r2founder',{y:200,scale:.82,duration:.65,ease:'power2.out'},.6);tl.to('#cam1',{scale:1.16,y:-230,duration:.35,ease:'power3.in'},2.15);")
#02 Cutout pressure: hero cropped lower, eight intrusive props, native marks in their physical planes.
s=image('A03','r2manager',40,770,1010)+text('حلو...','r2nice',175,225,730,96,'color:#282423')+text('بس تبدأ<br/>من وين؟','r2where',240,445,640,96,'color:#282423;text-align:right')
props=[('A04','p0',-490,190,1000,18),('A05','p1',610,280,810,-22),('A06','p2',-580,820,1090,22),('A07','p3',570,1080,1050,-18),('A05','p4',-540,1310,840,25),('A04','p5',770,660,950,-22),('A06','p6',650,-120,1050,-20),('A07','p7',-480,-390,1040,22)]
for key,id,x,y,w,r in props:s+=image(key,'r2'+id,x,y,w,style=f'transform:rotate({r}deg)')
s+=text('الردود','r2pressurelabel0',28,620,360,55,'transform:rotate(18deg);color:#282423')+text('المحتوى','r2pressurelabel1',718,1050,300,53,'transform:rotate(-22deg);color:#282423')
world(2,s)
j.append("tl.from('#cam2',{scale:1.12,duration:2.15,ease:'power1.out'},2.5);tl.from('#r2where',{y:50,opacity:0,duration:.18},3.35);tl.from('#r2nice',{opacity:0,duration:.12},2.5);")
for i,(_,id,*_) in enumerate(props):j.append(f"tl.from('#r2{id}',{{x:{-450 if i%2==0 else 450},rotation:{-18 if i%2==0 else 18},duration:.32,ease:'power4.out'}},{2.58+i*.23});")
#03 User revision: eliminate the wooden room entirely. Three tight photographic tool cuts on ivory.
s='<div id="toolreply" class="toolshot">'+image('A05','replyphone',180,430,1250,style='transform:rotate(-17deg)')+image('A20','replyslips',-420,1100,1080,style='transform:rotate(17deg)')+text('ترد على<br/>العملاء','replycopy',95,250,820,112,'color:#292424;text-align:right')+'<div id="replybubble" class="realpaper" dir="rtl" style="left:95px;top:1080px;width:480px;padding:42px;font-family:Thmanyah;font-size:53px;color:#691b24;transform:rotate(7deg)">استفسار جديد<br/>من العميل</div></div>'
s+='<div id="toolcontent" class="toolshot" style="opacity:0">'+image('A25','contentprint',-260,410,1460,style='transform:rotate(-9deg)')+image('A04','contenthand',620,1120,1100,style='transform:rotate(-20deg)')+text('تسوي<br/>محتوى','contentcopy',95,245,820,114,'color:#292424;text-align:right')+'<div id="contentart" class="realpaper" style="left:115px;top:820px;width:720px;height:690px;background:#691b24;transform:rotate(-9deg)">'+image('A30','contentplant',150,225,510)+text('فكرة تتحول<br/>إلى محتوى','contentartcopy',30,35,650,65,'color:#f3e8cd')+'</div></div>'
s+='<div id="toolreport" class="toolshot" style="opacity:0">'+image('A26','reportpage',-120,370,1320,style='transform:rotate(9deg)')+image('A21','reporthands',-340,1250,1750,style='transform:rotate(-7deg)')+text('تطلع<br/>تقارير','reportcopy',95,245,820,114,'color:#292424;text-align:right')+'<div id="reportink" style="position:absolute;left:265px;top:845px;width:610px;height:600px;transform:rotate(9deg)">'+text('قراءة النتائج','reporttitle',0,0,580,63,'color:#691b24')+'<div style="position:absolute;left:20px;top:190px;width:550px;height:210px;border-bottom:6px solid #691b24;display:flex;gap:36px;align-items:end">'+''.join(f'<div class="reportbar" style="width:90px;height:{h}px;background:#691b24"></div>' for h in [65,110,145,190])+'</div><div class="inkrules" style="position:absolute;top:470px"></div></div></div>'
world(3,s)
css.append('.toolshot{position:absolute;inset:0;background:#ede8db;transform-origin:50% 55%}')
j.append("tl.fromTo('#toolreply',{scale:1.1,rotation:3},{scale:1,rotation:0,duration:1.6,ease:'power1.out'},4.933333);tl.from('#replybubble',{x:-480,rotation:-10,duration:.38,ease:'power4.out'},5.3);tl.set(['#toolcontent','#toolreport'],{opacity:0},4.933333);tl.set('#toolreply',{opacity:0},6.533333);tl.set('#toolcontent',{opacity:1},6.533333);tl.fromTo('#toolcontent',{x:100,scale:1.15,rotation:-4},{x:0,scale:1,rotation:0,duration:1.45,ease:'power2.out'},6.533333);tl.from('#contentart',{y:180,rotation:12,duration:.35,ease:'power3.out'},6.65);tl.set('#toolcontent',{opacity:0},8.033333);tl.set('#toolreport',{opacity:1},8.033333);tl.fromTo('#toolreport',{scale:1.15,rotation:4,y:80},{scale:1,rotation:0,y:0,duration:1.8,ease:'power2.out'},8.033333);tl.from('.reportbar',{scaleY:0,transformOrigin:'50% 100%',stagger:.08,duration:.28,ease:'power2.out'},8.25);")
#04 deliberate horizontal body slices, paper shuttles and number occupies supporting right plane.
s=text('٣','body3',480,680,630,680,'color:#691b24;font-family:ThmanyahBlack;text-align:right;line-height:1')
s+=image('A12','bodyfull',-125,330,1000)+image('A12','bodyhead',-125,330,1000,style='clip-path:inset(0 0 72% 0)')
s+=image('A13','bodythobe',-100,680,820,750,'object-fit:fill;clip-path:inset(0 0 35% 0)')+image('A14','bodyjacket',-125,700,810,650,'object-fit:fill;clip-path:inset(0 0 28% 0)')+image('A15','bodypants',110,1190,550,500,'object-fit:fill')
s+=text('فريقك مشغول','bodysmall',575,490,460,70,'text-align:right;color:#292424')+text('ينسخ<br/>ويلصق','bodyaction',595,1330,450,108,'text-align:right;color:#292424')
for i,(x,y,r) in enumerate([(100,1050,-7),(190,1040,8),(380,1130,-5)]):s+=f'<div id="bodyticket{i}" class="realpaper" style="left:{x}px;top:{y}px;width:280px;height:150px;transform:rotate({r}deg)"><div class="inkrules"></div><div class="inkrules short"></div></div>'
world(4,s)
j.append("tl.from('#cam4',{scale:1.035,duration:3.6,ease:'none'},9.866667);tl.from('#body3',{x:200,opacity:0,duration:.2},10.3);tl.set(['#bodythobe','#bodyjacket','#bodypants'],{opacity:0},9.866667);tl.set('#bodythobe',{opacity:1},10.55);tl.set('#bodythobe',{opacity:0},11.13);tl.set('#bodyjacket',{opacity:1},11.13);tl.set('#bodypants',{opacity:1},11.73);tl.set('#bodyhead',{x:35,rotation:-3},10.55);tl.set('#bodyjacket',{x:-20,rotation:3},11.13);tl.from('#bodyaction',{x:120,opacity:0,duration:.18},11.6);tl.from('#bodyticket0',{x:-240,duration:.25},11.6);tl.to('#bodyticket0',{x:400,y:80,rotation:9,duration:.45,ease:'steps(5)'},11.9);tl.to('#bodyticket1',{x:250,y:45,rotation:-9,duration:.4,ease:'steps(5)'},12.35);tl.to('#bodyticket2',{x:-210,y:-40,duration:.4,ease:'steps(5)'},12.85);")
#05 process atlas: long reveal camera, block network instead of simple ladder.
network=[]
for row in range(9):
 for col in range(6):
  x=45+col*170+(row%2)*20;y=360+row*160;rot=[-8,6,2,10][(row+col)%4]
  network.append(f'<rect x="{x}" y="{y}" width="{125+(row%3)*10}" height="{110-(col%3)*15}" rx="3" fill="none" stroke="#cdc6b7" stroke-width="11" transform="rotate({rot} {x} {y})"/>')
route='M220 640 H450 V850 H780 V1080 H500 V1330 H220 V1500 H780'
s='<div id="atlas">'+f'<svg width="1080" height="1920">{"".join(network)}<path d="{route}" fill="none" stroke="#f3eee1" stroke-width="50"/><path id="atlasroute" d="{route}" fill="none" stroke="#691b24" stroke-width="11" stroke-linejoin="round"/></svg>'
for i,(x,y,word) in enumerate([(220,640,'العميل'),(450,850,'المتابعة'),(780,1080,'الأنظمة'),(500,1330,'التسويق'),(780,1500,'القرارات')]):
 s+=f'<div id="atlaspin{i}" class="atlaspin" style="left:{x-23}px;top:{y-62}px">●</div>'+text(word,'atlaslabel'+str(i),x-155,y+8,310,45,'color:#282423;text-shadow:0 3px 3px #ede8db;background:#ede8dbb0')
s+='</div>'+text('نبدأ من<br/>شغلك نفسه','atlasread',130,260,820,111,'color:#292424;text-align:center')
world(5,s)
j.append("tl.from('#atlasread',{y:80,opacity:0,duration:.24},13.5);tl.fromTo('#atlas',{scale:1.8,y:560,x:90},{scale:.78,y:90,x:0,duration:2.55,ease:'power2.inOut'},13.65);tl.from('#atlasroute',{strokeDasharray:2400,strokeDashoffset:2400,duration:2.0,ease:'none'},13.85);")
for i in range(5):j.append(f"tl.from('#atlaspin{i}',{{y:-150,scale:1.6,opacity:0,duration:.2,ease:'power3.out'}},{13.9+i*.42});tl.from('#atlaslabel{i}',{{opacity:0,duration:.1}},{14+i*.42});")
#06 cloned customer cascade with shot change to tangible plant/growing work.
s=text('كيف يوصلك العميل؟','journeycopy',155,315,790,82,'color:#292424')+'<div id="clientcascade">'
for i in range(5):s+=image(['A17','A18','A19','A17','A18'][i],'journey'+str(i),-450+i*275,610+(i%2)*70,750,style=f'transform:rotate({-3+i}deg)')
s+='</div><div id="growthstage">'+image('R02','growthplant',160,645,860,style='filter:url(#cleanAlpha) drop-shadow(16px 20px 10px #34291920)')+text('نفهم مسار<br/>شغلك','growthcopy',95,285,890,96,'color:#292424;text-align:right')+'</div>'
world(6,s)
j.append("tl.from('#journeycopy',{y:60,opacity:0,duration:.16},16.266667);tl.set('#growthstage',{opacity:0},16.266667);tl.to('#clientcascade',{x:-100,duration:1.0,ease:'power2.out'},16.65);tl.set('#clientcascade',{opacity:0},17.45);tl.set('#journeycopy',{opacity:0},17.45);tl.set('#growthstage',{opacity:1},17.45);tl.from('#growthplant',{scaleY:.55,transformOrigin:'50% 95%',duration:.55,ease:'power3.out'},17.45);tl.from('#growthcopy',{y:50,opacity:0,duration:.2},17.6);")
for i in range(5):j.append(f"tl.from('#journey{i}',{{x:250,opacity:0,duration:.2,ease:'power4.out'}},{16.3+i*.1});")
#07 Giant overlapping paperwork acts as a physical bridge into the screen.
s='<svg id="ribbon7" width="1400" height="2200" style="position:absolute;left:-150px;top:-120px"><path id="curl7" d="M-200 1350 C200 1350 1050 900 700 520 C450 250 220 750 550 1100 S1300 1500 1450 740" fill="none" stroke="#691b24" stroke-width="170"/></svg>'
s+=image('A22','contract7',270,970,1110,style='transform:rotate(-14deg)')+image('A20','tickets7',-300,420,1330,style='transform:rotate(13deg)')+image('A16','donor7',-170,360,1380,style='clip-path:inset(0 50% 0 0);transform:rotate(23deg)')+image('A16','receiver7',-20,1100,1380,style='clip-path:inset(0 0 0 50%);transform:rotate(-20deg)')
s+=image('A04','clip7',-330,900,1000,style='transform:rotate(-23deg)')
s+=f'<div id="carried7" class="realpaper" style="left:405px;top:690px;width:460px;height:540px;transform:rotate(12deg)">'+text('متابعة','follow7',35,70,390,72,'text-align:right;color:#282423')+'<div class="inkrules"></div><div class="inkrules short"></div><div class="inkrules"></div><div class="paperstamp">طلب عميل</div></div>'
s+=text('وين تتأخر<br/>المتابعة؟','late7',90,180,910,100,'text-align:right;color:#292424')+text('مهام تاخذ<br/>وقت فريقك','tasks7',290,1430,650,85,'text-align:right;color:#292424')
world(7,s)
j.append("tl.from('#late7',{y:45,opacity:0,duration:.18},18.1);tl.from('#tickets7',{y:-500,rotation:-9,duration:.4,ease:'power3.out'},18.15);tl.from('#donor7',{x:-600,duration:.5,ease:'power3.out'},18.3);tl.from('#receiver7',{x:700,duration:.5,ease:'power3.out'},19.0);tl.from('#carried7',{x:-330,y:-140,rotation:-12,duration:.5,ease:'power3.out'},18.45);tl.to('#carried7',{x:210,y:320,rotation:-18,duration:.6,ease:'power2.inOut'},19.65);tl.to('#donor7',{x:100,y:90,rotation:8,duration:.7},19.5);tl.to('#receiver7',{x:-80,y:-100,rotation:-7,duration:.7},19.5);tl.from('#tasks7',{x:100,opacity:0,duration:.2},19.8);tl.from('#clip7',{x:-500,duration:.5,ease:'power3.out'},20.0);tl.to('#curl7',{attr:{d:'M-200 1230 C400 1560 1200 600 600 400 C300 150 100 880 660 1160 S1400 1580 1450 740'},duration:3.9,ease:'none'},18.1);tl.to('#cam7',{scale:1.08,y:-80,duration:3.8,ease:'none'},18.4);tl.to('#carried7',{scale:3,x:55,y:-260,rotation:0,duration:.32,ease:'power4.in'},22.03);")
#08-10 parallel production module.
b=cards(a)
for n in [8,9,10]:htmls[n]=b['html'+str(n)]
css.append(b['css']);j.append(b['js'])
#11 reset source sparse typography, physical person exits within first beat.
s=text('وقت فريقك','resetone',150,580,780,91,'color:#292424')+text('للقرارات المهمة','resettwo',150,745,780,93,'color:#292424')+image('A31','leadexit',640,1050,700)+text('بدل الشغل المتكرر','resetthree',170,1100,740,61,'color:#292424')
world(11,s)
j.append("tl.from('#resetone',{y:45,opacity:0,duration:.18},37.233333);tl.from('#resettwo',{y:45,opacity:0,duration:.18},38.76);tl.from('#resetthree',{y:40,opacity:0,duration:.18},39.9);tl.to('#leadexit',{x:700,duration:.65,ease:'power2.in'},37.45);")
#12 restrained CTA: meaningful hierarchy without huge headline billboard.
s=text('وين يفيدك<br/>الذكاء الاصطناعي؟','lastquestion',140,650,800,85,'color:#292424')+text('راسلنا بكلمة','lastmsg',165,630,750,78,'color:#292424')+text('ابدأ','lastkeyword',165,790,750,156,'color:#691b24')+text('خلنا نحدد أول خطوة تناسبك','lastline',130,1100,820,55,'color:#292424')
world(12,s)
j.append("tl.from('#lastquestion',{y:40,opacity:0,duration:.2},41.5);tl.set('#lastquestion',{opacity:0},44.64);tl.from('#lastmsg',{y:30,opacity:0,duration:.18},44.64);tl.from('#lastkeyword',{y:20,opacity:0,duration:.2},45.54);tl.from('#lastline',{y:25,opacity:0,duration:.18},46.12);")
basecss='''@font-face{font-family:Thmanyah;src:url(assets/fonts/thmanyahserifdisplay-Regular.woff2);font-weight:400}@font-face{font-family:Thmanyah;src:url(assets/fonts/thmanyahserifdisplay-Bold.woff2);font-weight:700}@font-face{font-family:ThmanyahBlack;src:url(assets/fonts/thmanyahserifdisplay-Black.woff2)}*{box-sizing:border-box}html,body{margin:0;width:100%;height:100%;overflow:hidden;background:#ede8db}#main{position:relative;width:100%;height:100%;overflow:hidden;background:#ede8db}.clip{position:absolute;inset:0;width:1080px;height:1920px;overflow:hidden;background:#ede8db}.camera{position:absolute;inset:0;width:1080px;height:1920px;overflow:visible;background:#ede8db;transform-origin:50% 50%}.photo,.plate{position:absolute;object-fit:contain}.photo{filter:drop-shadow(10px 14px 8px #38281d1a)}.plate{object-fit:cover}.copy{position:absolute;font-family:ThmanyahBlack;font-weight:900;text-align:center;line-height:1.14}.r2banner{position:absolute;background:#691b24;box-shadow:0 20px 18px #171a1730}.realpaper{position:absolute;background:#f3efdf;box-shadow:7px 12px 8px #362c2525;border:1px solid #f9f4e8;overflow:hidden}.inkrules{height:9px;background:#7e736657;width:80%;margin:26px 10%;}.inkrules.short{width:54%}.paperblock{height:100px;width:74%;margin:20px 13%;background:#691b2470}.paperstamp{font-family:Thmanyah;font-size:49px;color:#691b24;border:5px solid #691b24;margin:60px 25px 20px;padding:17px;text-align:center;transform:rotate(-7deg)}.atlaspin{position:absolute;width:47px;height:62px;border-radius:48% 48% 40% 40%;background:#691b24;color:#ede8db;text-align:center;line-height:55px;font-size:45px;box-shadow:8px 12px 8px #39220f33;transform:rotate(-14deg)}#atlas{position:absolute;inset:0;width:1080px;height:1920px;transform-origin:50% 75%}'''
# Six short negative-frame punctuations follow actual reference treatment, not invented sustained dark stage.
for n,times in [(2,[2.5]),(3,[6.533333,8.033333]),(4,[9.866667]),(8,[22.366667])]:
 for t in times:j.append(f"tl.set('#cam{n}',{{filter:'invert(1)'}},{t});tl.set('#cam{n}',{{filter:'invert(0)'}},{t+2/30});")
sections=''.join(f'<section id="s{n}" class="clip" data-start="{T[n-1]}" data-duration="{T[n]-T[n-1]}" data-track-index="{n}">{htmls[n]}</section>' for n in range(1,13))
ready="window.__timelines={};window.__ready=(async()=>{await document.fonts.ready;await Promise.all([...document.images].map(x=>x.decode()));const tl=gsap.timeline({paused:true});"+''.join(j)+"window.__timelines.main=tl;window.seek=t=>{tl.seek(t,false);document.querySelectorAll('.clip').forEach((e,i)=>e.style.display=t>=TIMES[i]&&t<TIMES[i+1]?'block':'none')};return true;})();"
html='<!doctype html><html lang="ar"><head><meta charset="utf-8"><style>'+basecss+''.join(css)+'</style><script src="assets/gsap.min.js"></script></head><body><svg width="0" height="0" style="position:absolute"><filter id="cleanAlpha"><feComponentTransfer><feFuncA type="linear" slope="1.12" intercept="-.1"/></feComponentTransfer></filter></svg><div id="main" data-composition-id="main" data-width="1080" data-height="1920" data-duration="48.36666666666667" data-fps="30">'+sections+'<audio id="voice" src="input/voiceover.wav" data-start="0" data-duration="48.3526667" data-track-index="20"></audio></div><script>const TIMES='+json.dumps(T)+';'+ready+'</script></body></html>'
(p/'index.html').write_text(html)
(p/'build/production.json').write_text(json.dumps({'revision':2,'status':'IN_VISUAL_REVIEW_NOT_APPROVED','segments':[{'id':'A','shots':list(range(1,8)),'engine':'native HyperFrames photographic collage'},{'id':'B','shots':[8,9,10],'engine':'native HyperFrames, independently authored card planes'},{'id':'C','shots':[11,12],'engine':'native HyperFrames sparse reset'}],'source':str(p/'input/reference.mp4'),'voice_immutable':True,'stage_start_frames':[round(t*30) for t in T],'prior_revision':'User rejectedV1; retained as archive. No technicalPASS implies fidelityPASS.'},ensure_ascii=False,indent=2))
