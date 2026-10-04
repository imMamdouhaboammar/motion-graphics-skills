"""Original physical artwork, oversized monitor and diagonal camera field for V2.
Images stay unmodified; cropping is performed by authored compositor masks.
"""
from html import escape


def build(assets):
    def img(a, cls='', style='', ident=''):
        return f'<img {"id="+chr(34)+ident+chr(34) if ident else ""} class="{cls}" src="{escape(assets[a])}" style="{style}"/>'
    # Each print has its own graphic composition, colours and photographed subject.
    def artwork(k, ident, width, height, x, y, angle=0, label=None):
        palette=[('#a64a2c','#fff0d4','A27','المحتوى'),('#64796b','#f3eddc','A30','مع فريقك'),('#711d2d','#f3e5c3','A29','الطلبات'),('#dfbd74','#242e2b','A28','يرتب'),('#193f46','#f2e5ca','A27','يتابع'),('#cf5e35','#fff1da','A30','المتابعة')]
        bg,fg,a,txt=palette[k%6];txt=label or txt
        variant=k%4
        crop=img(a,'cphoto',f'width:230%;height:180%;left:-65%;top:-40%;object-fit:cover;')
        if variant==0:
            content=f'<div class="ccircle" style="background:{fg};left:-20%;top:14%;width:145%;height:65%"></div><div class="cphotozone" style="left:-3%;top:13%;width:106%;height:74%">{crop}</div><div class="cprinttype" style="left:4%;top:4%;width:92%;font-size:{width*.16}px;color:{fg}">{txt}</div><div class="cprinttype" style="left:8%;bottom:5%;width:84%;font-size:{width*.062}px;color:{fg}">إنتاج المحتوى</div>'
        elif variant==1:
            content=f'<div class="cprinttype" style="left:-10%;top:6%;width:120%;font-size:{width*.185}px;color:{fg};line-height:.9">{txt}<br/>{txt}</div><div class="cphotozone" style="left:4%;top:33%;width:92%;height:59%;transform:rotate(5deg)">{crop}</div><div class="csmallmark" style="color:{fg}">متابعة</div>'
        elif variant==2:
            content=f'<div class="cdiagonal" style="background:{fg}"></div><div class="cprinttype" style="left:5%;top:5%;width:90%;font-size:{width*.17}px;color:{fg}">{txt}</div><div class="cphotozone" style="left:-15%;top:25%;width:130%;height:64%;transform:rotate(-9deg)">{crop}</div><div class="cprinttype" style="left:9%;bottom:4%;width:82%;font-size:{width*.071}px;color:{fg}">يعمل مع فريقك</div>'
        else:
            content=f'<div class="cprinttype" style="left:5%;top:5%;width:90%;font-size:{width*.17}px;color:{fg}">{txt}</div><div class="cphotozone" style="left:6%;top:24%;width:88%;height:67%;border:9px solid {fg}">{crop}</div><div class="cprinttype" style="left:8%;bottom:3%;width:84%;font-size:{width*.063}px;color:{fg}">قراءة النتائج</div>'
        return f'<div id="{ident}" class="cprint" style="left:{x}px;top:{y}px;width:{width}px;height:{height}px;background:{bg};transform:rotate({angle}deg)">{content}</div>'
    def workflow(k, ident, width, height, x, y, angle=0):
        # Full-bleed printed workflow campaign: each verb has a physical metaphor.
        mode=k%3
        bg,ink,accent=[('#f1ddab','#732638','#d09b59'),('#742336','#f7e8ca','#c9a76b'),('#24484b','#f4e6c9','#d9a14e')][mode]
        w=width
        if mode==0:
            content=f'<div class="cwfburst" style="color:{ink}">↗</div><div class="cprinttype" style="left:3%;top:4%;width:94%;font-size:{w*.34}px;color:{ink}">يرد</div><div class="cwfslip" style="left:7%;top:39%;width:81%;height:25%;transform:rotate(-9deg);background:#fbf5e8;color:{ink};font-size:{w*.1}px">استفسار العميل<span>كيف تبدأ؟</span></div><div class="cwfslip" style="left:19%;top:57%;width:76%;height:27%;transform:rotate(7deg);background:{ink};color:#fbf5e8;font-size:{w*.1}px">مساعد يعمل<span>مع فريقك</span></div><div class="cprinttype" style="left:6%;bottom:5%;width:88%;font-size:{w*.077}px;color:{ink}">يرد على الاستفسارات</div>'
        elif mode==1:
            person=img(['A17','A18','A19'][(k//3)%3],'cwfperson','left:0;top:-12%;width:100%;height:135%;object-fit:contain;')
            content=f'<div class="cwfbigword" style="color:{ink}">العملاء</div><div class="cprinttype" style="left:4%;top:3%;width:92%;font-size:{w*.31}px;color:{ink}">يرتب</div><div class="cwfportrait" style="left:8%;top:28%;width:75%;height:63%;background:#c8b99c;transform:rotate(-6deg)">{person}</div><div class="cwflabel" style="left:35%;top:68%;width:61%;background:{ink};color:{bg};font-size:{w*.085}px;transform:rotate(6deg)">العملاء<br/>المحتملون</div><div class="cprinttype" style="left:7%;bottom:3%;width:86%;font-size:{w*.067}px;color:{ink}">مع فريقك</div>'
        else:
            folder=img('A25' if k%2==0 else 'A26','cwffolder','left:-23%;top:-8%;width:145%;height:127%;object-fit:contain;')
            content=f'<div class="cprinttype" style="left:2%;top:3%;width:96%;font-size:{w*.30}px;color:{ink}">يتابع</div><div class="cwforder" style="left:9%;top:28%;width:85%;height:63%;transform:rotate(-5deg)">{folder}<div class="cwforderink" style="font-size:{w*.07}px;color:#742336"><b>الطلبات</b><div>✓ استفسار</div><div>✓ متابعة</div><div>✓ مع فريقك</div></div></div><div class="cprinttype" style="left:7%;bottom:3%;width:86%;font-size:{w*.065}px;color:{ink}">يتابع الطلبات مع فريقك</div>'
        return f'<div id="{ident}" class="cprint cworkflow" style="left:{x}px;top:{y}px;width:{width}px;height:{height}px;background:{bg};transform:rotate({angle}deg)">{content}</div>'
    # Interface is a clearly labelled process illustration, with no invented KPIs.
    ui='''<div class="cuihead"><b>مسار العمل</b><span>الأنظمة التي تستخدمها</span></div><div class="cuitabs">الاستفسارات<span>العملاء المحتملون</span>الطلبات</div><div class="cuiflow"><div class="cuicol"><b>استفسار</b><article><i></i>تواصل العميل<small>مساعد يرد على الاستفسارات</small></article><article>تفاصيل الطلب<small>مع فريقك</small></article></div><div class="cuicol"><b>متابعة</b><article>يرتب العملاء المحتملين<small>المتابعة مع الفريق</small></article><article>طلب جديد<small>يتابع الطلبات</small></article></div><div class="cuicol"><b>القرارات</b><article>وقت فريقك<small>للقرارات المهمة</small></article><article>قراءة النتائج<small>بدل الشغل المتكرر</small></article></div></div><div class="cuifoot">تصوّر توضيحي لمسار العمل</div>'''
    monitor=img('A23','cmonitor','left:-390px;top:330px;width:1860px;')
    phone=img('A24','cphone','left:770px;top:1060px;width:410px;')
    postcard=img('A25','cpostcard','left:-240px;top:1210px;width:780px;transform:rotate(-12deg);')
    report=img('A26','creport','left:20px;top:1400px;width:420px;transform:rotate(17deg);')
    html8=f'''<div id="cam8" class="cstage"><div id="c8rig" class="crig">{monitor}<div id="c8screen" class="cuiscreen">{ui}</div>{phone}<div id="c8phonescreen" class="cphonecopy" dir="rtl"><b>استفسار</b><p>يرد على العملاء</p><span>مع فريقك</span></div>{postcard}{report}<svg id="c8connect" class="cconnect" width="1080" height="1920"><path d="M230 1470 C230 1160 965 1460 965 1260 S740 1010 630 920"/><circle cx="230" cy="1470" r="20"/><circle cx="630" cy="920" r="20"/></svg><div class="cstamp" style="left:145px;top:1510px;transform:rotate(17deg)" dir="rtl">نربط الأنظمة</div></div></div>'''
    prints=[]
    # 6x6 plane leaves camera travel room, irregular rotation/size and registration.
    for row in range(6):
        for col in range(6):
            k=row*6+col;w=[405,460,390,440][k%4];h=[530,550,570,520][k%4]
            prints.append(workflow(k,'c9print'+str(k),w,h,col*465+(row%2)*35,row*595,[-2,3,0,-4,2][k%5]))
    html9=f'''<div id="cam9" class="cstage"><div id="c9page" class="cfullpage"><div class="cpagebanner" dir="rtl"><b>مساعد يعمل<br/>مع فريقك</b><span>يرد • يرتب • يتابع</span></div><div class="cpageflow" dir="rtl">{ui}</div></div><div id="c9field" class="cdiagonalfield">{''.join(prints)}</div><div id="c9foreground" class="cforeground">{workflow(2,'c9lens',720,920,0,0,-20)}</div></div>'''
    cols=[]
    for col in range(4):
        cards=[]
        for row in range(3):
            k=col*3+row
            cards.append(artwork(k,'c10print'+str(k),490,840,0,row*885,0,['إنتاج المحتوى','متابعة الحملات','قراءة النتائج'][row]))
        cols.append(f'<div id="c10strip{col}" class="cportstrip" style="left:{col*530}px">{"".join(cards)}</div>')
    html10=f'''<div id="cam10" class="cstage"><div id="c10portfolio" class="cportfolio">{''.join(cols)}</div></div>'''
    css='''
#cam8,#cam9,#cam10{position:absolute;inset:0;width:1080px;height:1920px;background:#ede8db;overflow:hidden;perspective:2400px}
.cwfburst{position:absolute;left:-15%;top:14%;font-family:ThmanyahBlack;font-size:580px;line-height:1;opacity:.12}.cwfslip{position:absolute;padding:25px 12px;text-align:center;direction:rtl;font-family:ThmanyahBlack;line-height:1.1;box-shadow:8px 13px 7px #301c202b}.cwfslip span{display:block;font-family:Thmanyah;font-size:.68em;margin-top:16px}.cwfbigword{position:absolute;left:-25%;top:32%;font-family:ThmanyahBlack;font-size:160px;transform:rotate(-90deg);opacity:.12}.cwfportrait,.cwforder{position:absolute;overflow:hidden}.cwfperson,.cwffolder{position:absolute;filter:drop-shadow(8px 12px 5px #371b2430)}.cwflabel{position:absolute;padding:20px 12px;z-index:4;font-family:ThmanyahBlack;text-align:center;direction:rtl;line-height:1.12;box-shadow:6px 9px 8px #301c2033}.cwforderink{position:absolute;left:22%;top:21%;width:63%;height:60%;font-family:Thmanyah;direction:rtl;z-index:4;transform:rotate(5deg);padding:9px}.cwforderink b{font-family:ThmanyahBlack;font-size:1.65em;display:block;margin-bottom:22px}.cwforderink div{border-bottom:2px solid #73263866;padding:13px 0}.cstage:before{display:none!important}.crig{position:absolute;inset:0;width:1080px;height:1920px;transform-origin:540px 780px}.cmonitor,.cphone,.cpostcard,.creport{position:absolute;object-fit:contain;filter:drop-shadow(12px 20px 14px #27191528)}
.cuiscreen{position:absolute;left:-167px;top:427px;width:1420px;height:738px;background:#f7f4eb;overflow:hidden;padding:38px;font-family:Thmanyah;direction:rtl;color:#392d2c;box-shadow:inset 0 0 16px #0001;font-size:28px}
.cuihead{display:flex;align-items:center;justify-content:space-between;gap:35px;border-bottom:2px solid #bdb6aa;padding-bottom:23px}.cuihead b{font-family:ThmanyahBlack;font-size:62px;color:#6b2330}.cuihead span{font-size:26px}.cuitabs{display:flex;gap:32px;justify-content:space-around;background:#6b2330;color:#f7f0e3;margin:25px -38px;padding:18px;font-size:28px}.cuitabs span{border-bottom:3px solid #dfbe81}.cuiflow{display:flex;gap:24px}.cuicol{flex:1;padding:18px;background:#e9e5db;min-width:0}.cuicol>b{font-size:31px;display:block;margin-bottom:13px}.cuicol article{position:relative;background:#faf8f1;padding:22px 18px;margin:12px 0;font-size:26px;box-shadow:0 5px 8px #28170d0c;border-right:5px solid #7b2837}.cuicol small{display:block;color:#75685e;font-size:20px;margin-top:11px}.cuifoot{font-size:20px;color:#847970;margin-top:20px}.cphonecopy{position:absolute;left:871px;top:1170px;width:211px;height:460px;padding:50px 16px;font-family:Thmanyah;font-size:28px;background:#f7f3e9;border-radius:18px;text-align:center;color:#612631;transform:rotateY(-4deg)}.cphonecopy b{font-size:35px}.cphonecopy span{font-size:23px}.cconnect{position:absolute;inset:0;pointer-events:none}.cconnect path{fill:none;stroke:#7c2434;stroke-width:12;stroke-linecap:round}.cconnect circle{fill:#e4bb65;stroke:#7c2434;stroke-width:8}.cstamp{position:absolute;width:260px;text-align:center;padding:25px 10px;font-family:ThmanyahBlack;font-size:45px;color:#692831}
.cfullpage{position:absolute;inset:0;background:#f5f1e8;font-family:Thmanyah;direction:rtl}.cpagebanner{height:800px;background:#6e2131;color:#f1dfb4;padding:130px 80px;display:flex;flex-direction:column;justify-content:center;gap:35px}.cpagebanner b{font-family:ThmanyahBlack;font-size:126px;line-height:1.04}.cpagebanner span{font-size:42px}.cpageflow{padding:70px 45px;color:#392d2c}.cpageflow .cuihead b{font-size:55px}.cpageflow .cuihead span{font-size:23px}.cpageflow .cuiflow{gap:13px}.cpageflow .cuicol{padding:15px}.cpageflow .cuicol article{font-size:22px;padding:22px 10px}.cpageflow .cuicol small{font-size:18px}
.cdiagonalfield{position:absolute;left:-770px;top:-510px;width:2800px;height:3700px;transform-origin:1250px 1600px;transform:perspective(2400px) rotateX(9deg) rotateZ(-21deg);transform-style:preserve-3d}.cprint{position:absolute;overflow:hidden;box-shadow:16px 25px 15px #3e332635;transform-origin:50% 50%}.cprinttype{position:absolute;font-family:ThmanyahBlack,Thmanyah;font-weight:900;direction:rtl;text-align:center;z-index:3;line-height:1.04}.cphotozone{position:absolute;overflow:hidden;z-index:2}.cphoto{position:absolute;object-fit:cover}.ccircle{position:absolute;border-radius:50%;opacity:.95}.cdiagonal{position:absolute;left:-40%;top:30%;width:180%;height:42%;transform:rotate(-29deg);opacity:.14}.csmallmark{position:absolute;right:7%;bottom:3%;font-family:Thmanyah;font-size:25px;direction:rtl}.cforeground{position:absolute;left:800px;top:1450px;width:720px;height:920px;filter:blur(1px);z-index:6;transform-origin:50% 50%}.cportfolio{position:absolute;left:-240px;top:-155px;width:2260px;height:2840px;transform-origin:50% 50%}.cportstrip{position:absolute;top:0;width:490px;height:2740px}.cportfolio .cprint{box-shadow:10px 16px 11px #34241a22}
'''
    js='''
// Oversized physical monitor, then camera enters its authored mask.
tl.fromTo('#c8rig',{scale:.86,y:170,rotation:-2},{scale:1,y:0,rotation:0,duration:.72,ease:'power3.out'},22.3666667);
tl.from('#c8phone', {x:340,duration:.45,ease:'power3.out'},23.1);
tl.from('#c8connect path',{strokeDasharray:1800,strokeDashoffset:1800,duration:1.1,ease:'power2.inOut'},23.05);
tl.from('#c8screen .cuicol article',{y:38,opacity:0,stagger:.065,duration:.22,ease:'power2.out'},23.25);
tl.to('#c8screen .cuiflow',{y:-100,duration:.65,ease:'power2.inOut'},24.75);
tl.to('#c8rig',{scale:1.72,x:-25,y:160,duration:.9,ease:'power3.inOut'},25.4);
// Page scroll match bridge, hard reveal into a continuously travelling physical print plane.
tl.to('#c9page',{y:-870,duration:.7,ease:'power2.inOut'},26.3);
tl.set('#c9field',{opacity:0},26.3);
tl.set('#c9field',{opacity:1},27.0);
tl.set('#c9page',{opacity:0},27.0);
tl.fromTo('#c9field',{x:150,y:100,scale:1.13,rotationZ:-21,rotationX:9},{x:-670,y:-890,scale:1.04,rotationZ:-17,rotationX:13,duration:5.2,ease:'none'},27.0);
tl.fromTo('#c9foreground',{x:570,y:480,scale:1.07},{x:-1740,y:-2400,scale:.87,duration:5.2,ease:'none'},27.0);
// Paired portfolio strips move in opposing directions while the camera travels across them.
tl.fromTo('#c10portfolio',{x:0,y:-35},{x:-480,y:10,duration:5.0333333,ease:'none'},32.2);
tl.fromTo('#c10strip0,#c10strip2',{y:300},{y:-160,duration:5.0333333,ease:'none'},32.2);
tl.fromTo('#c10strip1,#c10strip3',{y:-220},{y:120,duration:5.0333333,ease:'none'},32.2);
tl.set('#cam10',{filter:'invert(1)'},33.8666667);tl.set('#cam10',{filter:'none'},33.9333333);
tl.set('#cam10',{filter:'invert(1)'},35.5666667);tl.set('#cam10',{filter:'none'},35.6333333);
tl.set('#cam10',{filter:'invert(1)'},36.7333333);tl.set('#cam10',{filter:'none'},36.8);
'''
    # Unique selectors for physical layers used by motion commands.
    html8=html8.replace('class="cphone"','id="c8phone" class="cphone"')
    return dict(html8=html8,html9=html9,html10=html10,css=css,js=js)
