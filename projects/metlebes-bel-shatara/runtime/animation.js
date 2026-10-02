/* Original deterministic character acting. Time is entirely owned by HyperFrames. */
const tl=gsap.timeline({paused:true});
const q=id=>'#'+id;
function to(id,v,t,d=.4,e='power2.inOut'){tl.to(q(id),{...v,duration:d,ease:e},t)}
function attr(id,v,t,d=.4,e='power2.inOut'){to(id+(Object.hasOwn(v,'d')?' path':''),{attr:v},t,d,e)}
function set(id,v,t=0){tl.set(q(id),v,t)}
const initializedTransforms=new Set();
function tr(id,x=0,y=0,r=0,ox=0,oy=0,t=0,d=0){if(!initializedTransforms.has(id)){initializedTransforms.add(id);attr(id,{transform:`translate(0 0) rotate(0 ${ox} ${oy})`},0,0)}attr(id,{transform:`translate(${x} ${y}) rotate(${r} ${ox} ${oy})`},t,d)}
function arm(id,side,upper,lower,t,d=.35){attr(id+'-'+side,{transform:`rotate(${upper})`},t,d);attr(id+'-'+side+'-forearm',{transform:`translate(0 86) rotate(${lower})`},t,d)}
function head(id,r,x,y,t,d=.35){tr(id+'-head',x,y,r,0,130,t,d)}
function body(id,r,x,y,t,d=.35){tr(id+'-body',x,y,r,0,310,t,d)}
function mouth(id,state,t,d=.12){to(id+'-mouth-open',{opacity:state},t,d);to(id+'-mouth',{opacity:1-state},t,d)}
function speak(id,start,end){for(let t=start,j=0;t<end-.09;t+=.28,j++){mouth(id,1,t,.055);mouth(id,0,Math.min(t+.12,end-.02),.065)}}
function brows(id,state,t,d=.25){let a=state==='sad'?[14,-14]:state==='stern'?[-13,13]:state==='wow'?[0,0]:[0,0];attr(id+'-brow-l',{transform:`translate(0 ${state==='wow'?-13:0}) rotate(${a[0]} -25 43)`},t,d);attr(id+'-brow-r',{transform:`translate(0 ${state==='wow'?-13:0}) rotate(${a[1]} 28 43)`},t,d);to(id+'-tired',{opacity:state==='sad'?1:0},t,d);attr(id+'-mouth',{d:state==='sad'?'M-15 117 Q5 103 28 116':state==='stern'?'M-15 110 Q5 110 28 110':'M-15 108 Q5 116 28 105'},t,d)}
function look(id,x,y,t,d=.25){for(const s of ['l','r'])attr(id+'-pupil-'+s,{transform:`translate(${x} ${y})`},t,d)}
function blink(id,t){for(const s of ['l','r']){to(id+'-lid-'+s,{opacity:1},t,.045);to(id+'-lid-'+s,{opacity:0},t+.075,.08)}}
function camera(n,x,y,k,t,d){attr(`s${String(n).padStart(2,'0')}-camera`,{transform:'translate(0 0) scale(1)'},0,0);attr(`s${String(n).padStart(2,'0')}-camera`,{transform:`translate(${x} ${y}) scale(${k})`},t,d)}
function draw(id,t,d){const el=document.querySelector(q(id));if(!el)return;for(const p of el.querySelectorAll('path')){let len;try{len=p.getTotalLength()}catch{continue}if(p.getAttribute('fill')!=='none')continue;gsap.set(p,{strokeDasharray:len,strokeDashoffset:len});tl.to(p,{strokeDashoffset:0,duration:d,ease:'power2.inOut'},t)}}
const beats=[0,3.02,8.22,13.86,19.36,24.6,30.54,35.36,38.72,41.74,46.98,55.68,62.04,69.28,75.26,88.28,112.3];
// Initialize every rig in an authored, relaxed pose. No wall-clock or stochastic motion.
for(let n=1;n<=16;n++){
 const p='s'+String(n).padStart(2,'0');
 for(const role of ['lead','client']){const id=p+'-'+role;if(!document.querySelector(q(id)))continue;arm(id,'la',6,-12,0,0);arm(id,'ra',-6,12,0,0);head(id,0,0,0,0,0);body(id,0,0,0,0,0);for(let t=beats[n-1]+1.9;t<beats[n]-.25;t+=3.7)blink(id,t)}
}
// 01: invoice cape / heroic confidence, contrasted with the lead's side-eye.
arm('s01-client','la',-54,-98,0,0);arm('s01-client','ra',57,94,0,0);body('s01-client',-4,0,21,0,0);head('s01-client',-7,0,0,0,0);
body('s01-client',0,0,-14,.12,.26);body('s01-client',-2,0,0,.38,.3);head('s01-client',3,0,-6,.15,.35);brows('s01-client','wow',.2);look('s01-client',3,-3,.3);
arm('s01-client','la',104,68,.13,.34);arm('s01-client','ra',-103,-63,.13,.34);
attr('s01-cape',{transform:'rotate(-6 1200 500)'},.22,.4);attr('s01-cape',{transform:'rotate(2 1200 500)'},.62,.7);attr('s01-cape',{transform:'rotate(-2 1200 500)'},1.32,.6);
look('s01-lead',8,-3,.35);head('s01-lead',-7,0,0,1.25,.35);brows('s01-lead','stern',1.3);to('s01-rays',{opacity:0},2.55,.3);camera(1,-24,0,1.03,2.62,.4);
// 02: certainty in the giant watch, bafflement at the simplest line.
arm('s02-client','ra',-114,-34,3.02,0);head('s02-client',7,0,0,3.02,0);speak('s02-client',3.08,5.4);
attr('s02-clock-hand',{transform:'rotate(70)'},3.05,1.08,'power3.out');attr('s02-clock-hand',{transform:'rotate(60)'},4.15,.15);draw('s02-scribble',5.62,1.2);tr('s02-tool',-140,-50,-16,1543,850,5.8,.5);head('s02-client',-12,0,4,6.45,.4);brows('s02-client','sad',6.5);look('s02-client',8,5,6.5);arm('s02-client','ra',-24,-87,6.58,.45);camera(2,30,-8,1.01,7.68,.54);
// 03: tiny finger promise, expanding folded brief.
set('s03-brief',{opacity:0},0);attr('s03-brief',{transform:'translate(640 490) scale(.12) translate(-960 -540)'},0,0);to('s03-brief',{opacity:1},8.55,.18);attr('s03-brief',{transform:'translate(960 540) scale(1) translate(-960 -540)'},10.55,1.1,'power3.inOut');attr('s03-brief',{transform:'translate(960 540) scale(1.06) translate(-960 -540)'},12.08,.7);
arm('s03-client','ra',-76,-66,8.22,0);arm('s03-client','la',73,61,8.22,0);speak('s03-client',8.35,13.08);head('s03-client',-5,0,-3,9.66);head('s03-lead',8,0,0,10.63);look('s03-lead',8,-4,10.8);brows('s03-lead','wow',11.05);body('s03-lead',-6,-8,9,11.1,.4);arm('s03-lead','ra',-21,-54,11.1,.4);
// 04: two incompatible instructions physically pull the same body.
arm('s04-lead','la',92,0,13.86,0);arm('s04-lead','ra',-92,0,13.86,0);head('s04-lead',-5,0,0,13.86,0);brows('s04-lead','sad',13.86,0);look('s04-lead',-8,0,14.2);
tr('s04-logoL',-140,0,-18,0,0,14.05,.45);tr('s04-logoL',-60,0,9,0,0,14.5,.5);body('s04-lead',-8,-16,0,14.15,.38);head('s04-lead',-10,-5,0,14.2);
look('s04-lead',8,0,15.44);tr('s04-logoR',160,0,20,0,0,15.46,.5);body('s04-lead',8,20,0,15.5,.45);head('s04-lead',12,8,0,15.5);
attr('s04-left-rope',{d:'M0 626 C302 280 398 880 792 625'},14.06,.5);attr('s04-right-rope',{d:'M1120 625 C1460 196 1730 940 1950 484'},15.44,.5);
tr('s04-logoL',-155,40,-26,0,0,16.48,.43);tr('s04-logoR',160,-20,20,0,0,17.08,.5);body('s04-lead',-8,-25,10,16.53,.4);body('s04-lead',7,18,0,17.1,.5);head('s04-lead',-5,-3,2,18.12,.4);
arm('s04-client','ra',-68,-58,13.86,0);speak('s04-client',14.1,19.05);tr('s04-split',0,-8,0,0,0,18.1,.35);to('s04-split',{opacity:0},18.75,.25);
// 05: the logo spills an impossible timeline / historical procession.
arm('s05-lead','ra',-77,-43,19.36,0);head('s05-lead',8,0,0,19.36,0);brows('s05-lead','wow',19.36,0);draw('s05-road',19.54,2.1);
for(let j=0;j<6;j++){set(`s05-history${j}`,{opacity:0},0);to(`s05-history${j}`,{opacity:1},20.45+j*.38,.25);tr(`s05-history${j}`,0,40,0,0,0,0,0);tr(`s05-history${j}`,0,0,0,0,0,20.4+j*.38,.4)}
look('s05-lead',8,-5,20.5);head('s05-lead',-8,0,0,22.65,.4);arm('s05-lead','la',-17,-124,22.7,.5);tr('s05-logo',0,55,-12,0,0,23.17,.5);camera(5,-74,0,1.04,23.65,.65);
// 06: tiny, deadly serious art director; pen stroke takes us into the desk.
tr('s06-baby',0,0,-5,676,680,24.6,0);tr('s06-baby',0,-7,3,676,680,25.25,.42);tr('s06-pen',-30,0,-7,1020,737,26.6,.4);tr('s06-pen',25,15,5,1020,737,27.18,.6);draw('s06-stroke',27.1,1.1);tr('s06-pen',-15,-12,-6,1020,737,28.26,.65);tr('s06-baby',0,0,-2,676,680,28.96,.4);camera(6,-124,-62,1.11,29.4,.7);
// 07: purposeful pen / hand work; clean result resolves, then send.
arm('s07-lead','la',6,-30,30.54,0);arm('s07-lead','ra',-10,10,30.54,0);head('s07-lead',8,2,11,30.54,0);look('s07-lead',6,6,30.54,0);set('s07-work',{opacity:0},0);set('s07-send',{opacity:0},0);
arm('s07-lead','ra',-12,12,31.35,.23);arm('s07-lead','ra',-7,7,31.67,.23);arm('s07-lead','la',8,-34,31.93,.24);arm('s07-lead','ra',-12,14,32.2,.2);head('s07-lead',0,0,0,32.4,.5);brows('s07-lead','wow',32.42,.3);to('s07-work',{opacity:1},32.38,.45);tr('s07-work',0,20,0,0,0,0,0);tr('s07-work',0,0,0,0,0,32.38,.45);
arm('s07-lead','ra',-62,-67,33.25,.35);to('s07-send',{opacity:1},33.5,.15);tr('s07-send',110,-57,8,1320,519,33.57,.65);to('s07-send',{opacity:0},34.27,.2);look('s07-lead',8,-2,34.3);head('s07-lead',-4,0,0,34.4);
attr('s08-work',{transform:'translate(966 710) scale(1) translate(-966 -710)'},0,0);
// 08: all value flattened by a giant stopwatch and a dismissive pinch.
arm('s08-client','la',80,-89,35.36,0);head('s08-client',-10,0,0,35.36,0);brows('s08-client','wow',35.4,.15);speak('s08-client',35.47,38.47);attr('s08-clock-hand',{transform:'rotate(360)'},35.6,.6,'power3.out');tr('s08-pinch',125,0,0,0,0,0,0);tr('s08-pinch',0,0,0,0,0,36.55,.48);attr('s08-work',{transform:'translate(966 710) scale(.68) translate(-966 -710)'},37.1,.43);look('s08-lead',9,-2,36.4);head('s08-lead',-8,0,0,37.3,.4);brows('s08-lead','stern',37.58);
// 09: hands snap up with anticipation and settle; pencil is theatrically arrested.
arm('s09-lead','la',7,-12,38.72,0);arm('s09-lead','ra',-7,12,38.72,0);body('s09-lead',0,0,12,38.74,.13);body('s09-lead',0,0,-8,38.88,.17);arm('s09-lead','la',125,85,38.88,.24);arm('s09-lead','ra',-125,-85,38.88,.24);arm('s09-lead','la',114,78,39.13,.27);arm('s09-lead','ra',-114,-78,39.13,.27);body('s09-lead',0,0,0,39.08,.26);attr('s09-lead-la-hand',{transform:'rotate(180 0 94)'},38.88,.24);attr('s09-lead-ra-hand',{transform:'rotate(180 0 94)'},38.88,.24);brows('s09-lead','wow',38.9,.15);head('s09-lead',-7,0,-6,38.9,.24);speak('s09-lead',38.8,41.55);
tr('s09-spot',0,-80,-11,1510,190,0,0);tr('s09-spot',0,0,0,1510,190,38.76,.32);set('s09-beam',{opacity:0},0);to('s09-beam',{opacity:.7},38.9,.14);set('s09-cuffs',{opacity:0},0);tr('s09-cuffs',0,-200,0,0,0,0,0);to('s09-cuffs',{opacity:1},39.73,.1);tr('s09-cuffs',0,0,0,0,0,39.74,.3,'');tr('s09-pencil',0,0,-8,1060,478,40.1,.28);head('s09-client',8,0,0,39.62);arm('s09-client','ra',-50,-58,39.7,.35);camera(9,-130,-65,1.11,40.58,.55);
// 10: the single ring opens into the corridor of years.
set('s10-clock',{opacity:1},0);attr('s10-clock',{transform:'scale(3.4)'},0,0);attr('s10-clock',{transform:'scale(1)'},41.76,.82,'power3.inOut');to('s10-clock',{opacity:0},43.03,.54);
for(let j=0;j<8;j++){set(`s10-arch${j}`,{opacity:0},0);to(`s10-arch${j}`,{opacity:1},42.52+j*.14,.55)}
look('s10-lead',0,-5,42.0);head('s10-lead',-4,0,0,43.2,.5);camera(10,-176,-40,1.18,43.4,3.58);
// 11: attempts that seemed brilliant at night are erased by morning.
arm('s11-lead','la',6,-30,46.98,0);arm('s11-lead','ra',-10,10,46.98,0);head('s11-lead',11,4,12,46.98,0);brows('s11-lead','sad',46.98,0);look('s11-lead',7,7,46.98,0);
for(let j=0;j<6;j++){set(`s11-reject${j}`,{opacity:0},0);to(`s11-reject${j}`,{opacity:1},47.3+j*.58,.3);tr(`s11-reject${j}`,0,50,0,0,0,0,0);tr(`s11-reject${j}`,0,0,0,0,0,47.3+j*.58,.4)}
arm('s11-lead','ra',-12,12,47.25,.3);arm('s11-lead','ra',-7,7,47.72,.3);head('s11-lead',0,0,0,49.95,.4);brows('s11-lead','wow',50.05,.25);arm('s11-lead','ra',-43,-100,50.24,.35);head('s11-lead',-8,0,0,52.5,.4);brows('s11-lead','stern',52.6,.3);
for(let j=0;j<6;j++){tr(`s11-reject${j}`,0,720,22*(j%2?1:-1),960,540,53.2+j*.16,.6);to(`s11-reject${j}`,{opacity:0},53.5+j*.16,.4)}
arm('s11-lead','ra',-10,10,54.1,.5);head('s11-lead',9,0,10,54.18,.45);
// 12: repetitions coil, then doubt envelops the silhouette.
for(let j=0;j<12;j++){tr(`s12-paper${j}`,0,0,0,0,0,55.68,0);tr(`s12-paper${j}`,0,40*(j%2?1:-1),12*(j%2?1:-1),0,0,55.78+j*.16,.4);tr(`s12-paper${j}`,0,0,0,0,0,56.36+j*.16,.45)}
head('s12-lead',-7,0,8,56.1,.5);brows('s12-lead','sad',56.1,.3);arm('s12-lead','la',39,-139,57.1,.4);arm('s12-lead','ra',-30,134,57.24,.45);head('s12-lead',8,0,12,58.62,.45);to('s12-cloud',{opacity:1},58.72,1.1);draw('s12-cloud',58.73,2.2);body('s12-lead',0,0,12,60.2,.6);look('s12-lead',-4,8,60.23,.4);camera(12,-96,-26,1.08,60.9,1.12);
attr('s13-laptop',{transform:'translate(0 750) scale(1 1) translate(0 -750)'},0,0);
// 13: close. A held regret. The small return gesture, then a quiet reopen.
arm('s13-lead','la',6,-30,62.04,0);arm('s13-lead','ra',-10,10,62.04,0);head('s13-lead',13,0,14,62.04,0);brows('s13-lead','sad',62.04,0);look('s13-lead',5,8,62.04,0);
arm('s13-lead','ra',-20,-60,63.15,.65);attr('s13-laptop',{transform:'translate(0 750) scale(1 .075) translate(0 -750)'},63.73,.68);to('s13-warm',{opacity:0},63.83,.62);head('s13-lead',20,-3,24,64.25,.8);body('s13-lead',4,0,12,64.32,.7);arm('s13-lead','ra',-5,35,64.4,.65);arm('s13-lead','la',8,-44,64.44,.65);
// The supplied recording has a short pause here. Do not invent extra silence.
head('s13-lead',6,0,6,66.56,.52);look('s13-lead',9,5,66.64,.3);arm('s13-lead','ra',-10,10,66.66,.62);attr('s13-laptop',{transform:'translate(0 750) scale(1 1) translate(0 -750)'},67.28,.66);arm('s13-lead','ra',-20,-60,67.28,.66);to('s13-warm',{opacity:.075},67.31,.6);brows('s13-lead','neutral',68.04,.5);head('s13-lead',3,0,5,68.04,.6);arm('s13-lead','la',6,-30,68.46,.5);arm('s13-lead','ra',-10,10,68.46,.5);
// 14: week / day / hour collapse into the same piece of work.
arm('s14-lead','ra',-57,-72,69.28,0);head('s14-lead',-4,0,0,69.28,0);for(let j=0;j<3;j++)set(`s14-calendar${j}`,{opacity:j===0?1:0},0);set('s14-clock',{opacity:0},0);
attr('s14-calendar0',{transform:'translate(0 0) scale(1)'},0,0);attr('s14-calendar1',{transform:'translate(0 0) scale(1)'},0,0);for(let r=0;r<3;r++){attr(`s14-marks0-${r}`,{transform:'translate(880 540) scale(1 1) translate(-880 -540)'},0,0);attr(`s14-marks0-${r}`,{transform:'translate(880 540) scale(1 .1) translate(-880 -540)'},70.1+r*.18,.36);to(`s14-marks0-${r}`,{opacity:0},70.15+r*.18,.36)}
attr('s14-calendar0',{transform:'translate(200 0) scale(.82)'},71.37,.55);to('s14-calendar0',{opacity:0},71.56,.4);to('s14-calendar1',{opacity:1},71.66,.35);head('s14-lead',5,0,0,71.7,.4);look('s14-lead',8,0,71.7);
attr('s14-calendar1',{transform:'translate(370 90) scale(.65)'},73.1,.6);to('s14-calendar1',{opacity:0},73.24,.42);to('s14-calendar2',{opacity:1},73.45,.3);to('s14-clock',{opacity:1},74.17,.4);attr('s14-clock-hand',{transform:'rotate(360)'},74.2,.7,'power3.out');brows('s14-lead','wow',74.35,.3);
// 15: expertise rises; fee sinks. The lead silently notices the arithmetic.
arm('s15-lead','ra',-34,-83,75.26,0);head('s15-lead',-5,0,0,75.26,0);look('s15-lead',8,0,75.26,0);
attr('s15-ropes',{d:'M838 397 L845 551 M1558 432 L1555 693'},77.6,.8);tr('s15-expertise',0,-98,0,0,0,77.6,.8);tr('s15-bill',0,160,0,0,0,77.6,.8);attr('s15-bar',{transform:'rotate(12 1160 406)'},77.6,.8);head('s15-lead',8,0,0,79.3,.45);brows('s15-lead','stern',79.32,.4);look('s15-lead',0,0,80.5,.4);arm('s15-lead','ra',-48,-88,81.03,.5);arm('s15-lead','la',42,82,81.4,.5);head('s15-lead',-6,0,0,83.9,.5);body('s15-lead',-3,0,0,84.0,.6);head('s15-lead',8,0,0,86.5,.5);brows('s15-lead','wow',86.52,.3);mouth('s15-lead',.7,86.7,.12);mouth('s15-lead',0,87.13,.14);
// 16: honest result; experience briefly revealed; absurd two-and-a-half-coin return.
arm('s16-lead','ra',-76,-35,88.28,0);head('s16-lead',-3,0,0,88.28,0);arm('s16-client','la',14,-38,88.28,0);arm('s16-client','ra',-14,38,88.28,0);look('s16-client',-5,0,88.28,0);
for(let j=0;j<3;j++){set('s16-coin'+j,{opacity:0},0);tr('s16-coin'+j,720,0,0,0,0,0,0)}
head('s16-lead',4,0,0,89.12,.6);arm('s16-lead','la',21,-66,91.6,.6);arm('s16-lead','ra',-73,-45,93.78,.6);to('s16-history',{opacity:.82},94.1,1.2);draw('s16-history',94.1,2.6);look('s16-lead',5,-2,95.2,.4);to('s16-history',{opacity:0},98.5,.9);
head('s16-lead',-5,0,0,99.3,.6);arm('s16-lead','ra',-35,-64,100.1,.7);head('s16-lead',8,0,7,102.2,.7);brows('s16-lead','sad',103.05,.5);arm('s16-lead','la',6,-12,104.3,.8);arm('s16-lead','ra',-6,12,104.3,.8);head('s16-lead',0,0,0,105.0,.7);
// Anticipate the shift without interrupting or rearranging narration.
look('s16-lead',8,0,107.58,.2);brows('s16-lead','stern',107.58,.2);arm('s16-lead','ra',-86,-22,107.6,.3);head('s16-lead',-8,0,-5,107.64,.28);speak('s16-lead',107.6,109.3);body('s16-client',-3,-8,0,108.45,.35);brows('s16-client','wow',108.5,.25);
to('s16-tray',{opacity:1},109.4,.15);tr('s16-tray',770,0,0,0,0,0,0);tr('s16-tray',0,0,0,0,0,109.42,.52,'');
for(let j=0;j<3;j++){to('s16-coin'+j,{opacity:1},109.49+j*.18,.1);tr('s16-coin'+j,0,0,-360*(j<2?1:0),0,0,109.49+j*.18,.5);}
arm('s16-client','la',62,-55,109.4,.35);arm('s16-client','ra',-62,55,109.4,.35);head('s16-client',-6,0,-5,109.66,.3);mouth('s16-client',1,109.64,.1);mouth('s16-client',0,110.85,.1);to('s16-glints',{opacity:1},110.4,.12);to('s16-glints',{opacity:0},110.7,.15);head('s16-lead',0,0,0,110.63,.25);arm('s16-lead','ra',-6,12,110.64,.25);look('s16-lead',0,0,110.71,.2);brows('s16-lead','stern',110.71,.2);
// Preserve every source sample; the short silent tail is an intentional ending.
to('black',{opacity:1},111.66,.16,'none');
window.__timelines=window.__timelines||{};window.__timelines.main=tl;
