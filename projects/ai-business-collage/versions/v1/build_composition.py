from pathlib import Path
import csv,json
p=Path(__file__).resolve().parents[1]
assets={r['asset_id']:r['output_path'] for r in csv.DictReader((p/'assets/asset_manifest.csv').open(encoding='utf-8-sig'))}
starts=[0,2.5,4.93,9.87,13.5,16.27,18.1,22.37,26.3,32.2,37.23,41.5,1451/30]
starts=[round(t*30)/30 for t in starts]
parts=[]
def img(a,id,x,y,w,h=None,cls='photo',extra=''):
 return f'<img id="{id}" class="{cls}" src="{assets[a]}" style="left:{x}px;top:{y}px;width:{w}px;'+(f'height:{h}px;' if h else '')+f'{extra}"/>'
def txt(t,id,x,y,w=900,size=90,cls='type',extra=''):
 return f'<div id="{id}" class="{cls}" dir="rtl" style="left:{x}px;top:{y}px;width:{w}px;font-size:{size}px;{extra}">{t}</div>'
def scene(n,s):
 parts.append(f'<section id="s{n}" class="clip" data-start="{starts[n-1]}" data-duration="{starts[n]-starts[n-1]}" data-track-index="{n}"><div class="world" id="w{n}">{s}</div></section>')
scene(1,img('A02','sky',0,-350,1080,2400,'plate')+img('A01','founder',290,770,650)+txt('ناوي تدخل','open1',90,270,900,100)+txt('الذكاء الاصطناعي؟','open2',80,480,920,98)+txt('في شغلك','ribbon',-40,1410,1160,100,'ribbon'))
scene(2,txt('حلو...','nice',80,240,920,118)+txt('بس تبدأ من وين؟','where',80,420,920,92)+img('A03','manager',220,710,640)+img('A04','cliphand',-140,670,560)+img('A05','phonehand',660,760,570)+img('A06','screenhand',-220,1160,630)+img('A07','folderhand',640,1250,650))
s=img('A08','desk',-350,-150,4000,2400,'plate')
for i,a in enumerate(['A09','A10','A11']):
 x=i*1100;s+=img(a,'over'+str(i),x,440,1000)+txt(['الردود','المحتوى','التقارير'][i],'tool'+str(i),x+80,230,850,120)+txt(['أداة','وأداة','وثالثة'][i],'toolsmall'+str(i),x+100,1500,800,64)
scene(3,s)
s=txt('٣','three',-70,200,1220,850)+img('A12','worker',235,650,610)+img('A13','garment1',290,790,530)+img('A14','garment2',285,790,540)+img('A15','garment3',305,1170,500)+img('A16','transfer',-100,1040,1200,extra='clip-path:inset(0 50% 0 0);')+img('A16','receiver',-100,1040,1200,extra='clip-path:inset(0 0 0 50%);')+txt('','handoffcard',400,1190,260,50,'strip',extra='height:150px;transform:rotate(-8deg);')+txt('ينسخ','copy',75,365,440,112)+txt('ويلصق','paste',565,1420,440,112)
scene(4,s)
s=txt('نبدأ من شغلك نفسه','maptitle',90,220,900,85)
s+='<div id="map" style="position:absolute;left:0;top:0;width:1080px;height:1920px"><svg width="1080" height="1920"><g fill="none" stroke="#c6baa7" stroke-width="2" opacity=".5"><path d="M-50 450 Q420 300 1040 510 T1150 1000 M-50 500 Q420 350 1040 560 T1150 1050 M-50 550 Q420 400 1040 610 T1150 1100 M0 1600 Q420 1450 1080 1650 M0 1640 Q420 1490 1080 1690"/></g><g fill="#ded5c4"><path d="M430 610h190v130H430z M490 900h220v130H490z M80 890h130v240H80z M820 1050h140v240H820z M390 1490h280v200H390z"/></g><path d="M240 570 H780 V830 H340 V1120 H750 V1410 H270" fill="none" stroke="#c7baa5" stroke-width="70"/><path id="route" d="M240 570 H780 V830 H340 V1120 H750 V1410 H270" fill="none" stroke="#691b24" stroke-width="18" stroke-linejoin="round"/></svg>'
for i,(x,y,t) in enumerate([(240,570,'العميل'),(780,830,'المتابعة'),(340,1120,'الأنظمة'),(750,1410,'التسويق'),(270,1410,'القرارات')]):
 s+=f'<div class="pin" id="pin{i}" style="left:{x-30}px;top:{y-30}px"></div>'+txt(t,'pinlabel'+str(i),x-180,y+60,360,52)
s+='</div>';scene(5,s)
s=txt('كيف يوصلك العميل؟','arrival',80,260,920,96)
for i,a in enumerate(['A17','A18','A19','A17']):
 s+=img(a,'client'+str(i),-30+i*380,710,430)+txt(['استفسار','تواصل','طلب','متابعة'][i],'clientlabel'+str(i),i*380+30,1430,350,52,'strip')
scene(6,s)
scene(7,txt('وين تتأخر المتابعة؟','late',80,230,920,90)+img('A22','folders',470,900,650)+img('A20','slips',120,650,860)+img('A21','sort',-80,810,1200)+txt('مهام كل يوم','daily',80,1430,920,90)+txt('طلب','slip1',220,750,300,50,'strip')+txt('متابعة','slip2',530,840,350,50,'strip'))
s=txt('نربط الأنظمة','connecttitle',80,240,920,100)+img('A23','monitor',-30,590,1140)+img('A24','phone',30,1180,400)
s+='<svg id="connections" width="1080" height="1920" style="position:absolute"><path id="wire" d="M260 1390 V1170 H570 V920 H870" fill="none" stroke="#691b24" stroke-width="15"/></svg><div id="dashboard" class="screen" style="left:175px;top:720px;width:730px;height:410px"><div class="screenhead">مسار العمل</div><div class="rows"><span>العملاء</span><span>الطلبات</span><span>المتابعة</span></div><div class="bar"></div><div class="bar" style="width:65%"></div><div class="bar" style="width:80%"></div></div>'
scene(8,s)
s=txt('مساعد يعمل مع فريقك','assistant',80,230,920,83)
s+='<div id="fieldmask" style="position:absolute;left:0;top:500px;width:1080px;height:1420px;overflow:hidden"><div id="field" style="position:absolute;left:-580px;top:150px;width:2400px;height:2400px;transform:perspective(2400px) rotateX(15deg) rotateZ(-17deg)">'
for i in range(9):
 x=(i%3)*730;y=(i//3)*680
 s+=f'<div class="card" id="card{i}" style="left:{x}px;top:{y}px;width:610px;height:560px">'+img(['A25','A26','A27'][i%3],'cardphoto'+str(i),25,65,550,380,'cardphoto')+txt(['يرد','يرتب','يتابع'][i%3],'cardlabel'+str(i),25,410,550,70)+'</div>'
s+='</div></div>';scene(9,s)
s=txt('وفي التسويق','marketing',80,200,920,95)
for i in range(6):
 x=-110+(i%3)*440;y=510+(i//3)*700
 s+=f'<div id="reel{i}" class="reel" style="left:{x}px;top:{y}px">'+img(['A27','A28','A29','A30'][i%4],'reelphoto'+str(i),0,0,400,540,'cardphoto')+txt(['إنتاج المحتوى','متابعة الحملات','قراءة النتائج'][i%3],'reellabel'+str(i),20,550,360,48)+'</div>'
scene(10,s)
scene(11,txt('وقت فريقك','teamtime',80,400,920,120)+txt('للقرارات المهمة','decisions',80,620,920,107)+img('A31','lead',390,1010,640)+txt('بدل الشغل المتكرر','repeat',80,1510,850,62))
scene(12,txt('وين يفيدك','whereai',80,420,920,106)+txt('الذكاء الاصطناعي؟','aifinal',80,590,920,94)+txt('راسلنا بكلمة','message',80,660,920,88)+txt('ابدأ','cta',80,820,920,238)+txt('خلنا نحدد أول خطوة تناسبك','last',90,1190,900,57))
css='''@font-face{font-family:Thmanyah;src:url(assets/fonts/thmanyahsans-Regular.woff2);font-weight:400}@font-face{font-family:Thmanyah;src:url(assets/fonts/thmanyahsans-Bold.woff2);font-weight:700}@font-face{font-family:ThmanyahBlack;src:url(assets/fonts/thmanyahsans-Black.woff2);font-weight:900}*{box-sizing:border-box}html,body{margin:0;width:100%;height:100%;overflow:hidden;background:#e9e3d3}#main{width:100%;height:100%;position:relative;overflow:hidden;background:#e9e3d3}.clip,.world{position:absolute;width:1080px;height:1920px;inset:0;overflow:hidden}.world{background:#e9e3d3}#w3{width:3300px;overflow:visible}#w6{overflow:visible}#w3:before{display:none}#copy,#paste{background:#f4eee3;padding:15px;box-shadow:8px 12px 10px #352a2519}#assistant,#marketing{z-index:9;background:#e9e3d3;padding:20px}#w10{overflow:visible}.world:before{content:"";position:absolute;inset:0;opacity:.11;background-image:url(assets/generated/A32_seamless_cream_paper.png);background-size:cover;pointer-events:none}.photo,.plate,.cardphoto{position:absolute;object-fit:contain}.photo{filter:drop-shadow(10px 17px 11px rgba(65,43,25,.14))}.plate{object-fit:cover}.type,.ribbon,.strip{position:absolute;text-align:center;font-family:Thmanyah,sans-serif;font-weight:700;color:#691b24;line-height:1.22}.ribbon{padding:30px;background:#691b24;color:#f4eee3;transform:rotate(-4deg);box-shadow:0 18px 15px #352a2520}.strip{padding:20px 15px;background:#f4eee3;box-shadow:8px 10px 10px #352a2519;color:#292424}.pin{position:absolute;width:60px;height:60px;border-radius:50%;background:#691b24;border:12px solid #f4eee3;box-shadow:7px 9px 6px #352a2525}.screen{position:absolute;overflow:hidden;background:#f4eee3;border:7px solid #d6cbbb;padding:30px;color:#691b24;font-family:Thmanyah;direction:rtl;font-size:33px}.screenhead{font-size:42px;font-weight:700}.rows{display:flex;justify-content:space-between;margin:20px 0}.bar{height:18px;background:#691b2450;margin:16px 0;width:90%}.card{position:absolute;background:#f4eee3;box-shadow:14px 23px 12px #352a2530;overflow:hidden}.reel{position:absolute;width:400px;height:660px;overflow:hidden;background:#f4eee3;box-shadow:10px 18px 14px #352a2520}#three{font-family:ThmanyahBlack;color:#691b24;opacity:.92;line-height:1}#s12 .type{color:#691b24}'''
js='''const T=[0,2.5,4.9333333333,9.8666666667,13.5,16.2666666667,18.1,22.3666666667,26.3,32.2,37.2333333333,41.5,48.3666666667];
window.__timelines={};window.__ready=(async()=>{await document.fonts.ready;await Promise.all([...document.images].map(x=>x.decode()));const tl=gsap.timeline({paused:true});const pop=(sel,t,vars={})=>tl.from(sel,{duration:.28,y:90,opacity:0,ease:'power3.out',...vars},t);const move=(sel,t,vars,d=.35)=>tl.to(sel,{duration:d,ease:'power3.out',...vars},t);
tl.from('#w1',{y:-340,duration:.8,ease:'power3.inOut'},0);pop('#open1',0,{y:-70});pop('#open2',.5,{y:-80});pop('#ribbon',1.55,{y:140,rotation:0});tl.from('#founder',{y:130,scale:.9,duration:.6},.7);
pop('#nice',2.5);pop('#where',3.4);pop('#cliphand',2.8,{x:-400,y:0});pop('#phonehand',3.25,{x:400,y:0});pop('#screenhand',3.65,{x:-600,y:0});pop('#folderhand',4.05,{x:500,y:0});
tl.set('#w3',{x:0},T[2]);move('#w3',6.53,{x:-1100},.17);move('#w3',8.03,{x:-2200},.17);['#over0','#over1','#over2'].forEach((s,i)=>pop(s,4.94+i*1.54,{y:140,rotation:-5}));
pop('#three',9.87,{scale:.5,y:0});pop('#worker',10.2);pop('#garment1',10.5,{duration:.01});tl.set('#garment1',{opacity:0},11.1);pop('#garment2',11.1,{duration:.01});tl.set('#garment2',{opacity:0},11.75);pop('#garment3',11.75,{duration:.01});pop('#copy',11.6,{x:-200,y:0});pop('#paste',12.03,{x:200,y:0});tl.fromTo('#transfer',{x:-300},{x:90,duration:.7,ease:'steps(5)'},11.55);tl.fromTo('#receiver',{x:260},{x:-50,duration:.6,ease:'steps(5)'},11.75);pop('#handoffcard',11.55,{x:-180,y:0,duration:.15});move('#handoffcard',11.75,{x:160,rotation:5},.6);tl.from('#w4',{scale:.96,duration:3.63,ease:'none'},9.87);
pop('#maptitle',13.5);tl.from('#map',{scale:1.6,x:-90,y:250,duration:2.7,ease:'power2.inOut',transformOrigin:'50% 50%'},13.5);tl.from('#route',{strokeDasharray:2600,strokeDashoffset:2600,duration:2.4,ease:'none'},13.7);for(let i=0;i<5;i++){pop('#pin'+i,13.75+i*.43,{y:-110,duration:.18});pop('#pinlabel'+i,13.9+i*.43,{y:20,duration:.15});}
pop('#arrival',16.27);for(let i=0;i<4;i++){pop('#client'+i,16.3+i*.15,{x:140,y:0});pop('#clientlabel'+i,16.5+i*.15,{x:120,y:0});}move('#w6',17.2,{x:-250},.65);move('#arrival',17.2,{x:250},.65);
pop('#late',18.1);pop('#slips',18.3,{rotation:-9});pop('#folders',18.6,{x:180,y:0});pop('#sort',19.3,{x:-140,y:0});pop('#daily',19.8);pop('#slip1',18.6,{x:-120,y:0});pop('#slip2',19.6,{x:200,y:0});move('#sort',20.3,{x:120},.6);tl.from('#w7',{scale:.97,duration:4.27,ease:'none'},18.1);
pop('#connecttitle',22.37);pop('#monitor',22.85,{scale:.83,y:120});pop('#phone',23.4,{x:-180,y:0});tl.from('#wire',{strokeDasharray:1300,strokeDashoffset:1300,duration:1.0,ease:'none'},23.3);pop('#dashboard',24.1,{y:20});tl.to('#dashboard .bar',{x:-30,stagger:.2,duration:.3},24.8);move('#monitor',25,{rotationY:5},.5);
pop('#assistant',26.3);tl.fromTo('#field',{x:300,y:150},{x:-680,y:-1100,duration:5.9,ease:'none'},26.3);for(let i=0;i<9;i++)pop('#card'+i,26.3+Math.floor(i/3)*1.5,{y:60,duration:.25});
pop('#marketing',32.2);for(let i=0;i<6;i++)pop('#reel'+i,32.25+i*.075,{y:(i%2?500:-500),duration:.36});tl.to('#w10',{x:-120,duration:4.7,ease:'none'},32.2);tl.to('#w10',{filter:'invert(1)',duration:.01},35.0);tl.to('#w10',{filter:'invert(0)',duration:.01},35.1);tl.to('#w10',{filter:'invert(1)',duration:.01},36.3);tl.to('#w10',{filter:'invert(0)',duration:.01},36.4);
pop('#teamtime',37.24,{y:35});pop('#decisions',38.76,{y:35});pop('#lead',37.6,{x:80,y:0});pop('#repeat',39.9,{y:20});move('#lead',40.3,{x:280},.65);tl.from('#w11',{scale:1.025,duration:4.26,ease:'none'},37.23);
pop('#whereai',41.5,{y:30});pop('#aifinal',42.8,{y:30});tl.set(['#whereai','#aifinal'],{opacity:0},44.64);pop('#message',44.64,{y:30});pop('#cta',45.54,{scale:.96,y:40});pop('#last',46.12,{y:25});tl.from('#w12',{scale:1.015,duration:6.8667,ease:'none'},41.5);
window.__timelines.main=tl;window.seek=t=>{tl.seek(t,false);document.querySelectorAll('.clip').forEach((el,i)=>el.style.display=t>=T[i]&&t<T[i+1]?'block':'none')};return true;})();'''
html=f'<!doctype html><html lang="ar"><head><meta charset="utf-8"><style>{css}</style><script src="assets/gsap.min.js"></script></head><body><div id="main" data-composition-id="main" data-width="1080" data-height="1920" data-duration="{1451/30}" data-fps="30">'+''.join(parts)+'<audio id="voice" src="input/voiceover.wav" data-start="0" data-duration="48.3526667" data-track-index="20"></audio></div><script>'+js+'</script></body></html>'
html=html.replace('id="three"','id="three" data-layout-allow-overlap="true"');(p/'index.html').write_text(html)
phrases=(p/'analysis/copy_lock.txt').read_text().splitlines();(p/'analysis/scene_timing_generated.json').write_text(json.dumps({'status':'ASR phrase timing, lexical transcription corrected against approved copy','engine':'faster-whisper base int8; phonetic word recognition imperfect','scenes':[{'scene':i+1,'start_frame':round(starts[i]*30),'end_frame':round(starts[i+1]*30)} for i in range(12)],'approved_copy':phrases},ensure_ascii=False,indent=2))
