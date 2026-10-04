/* All visual states belong to the paused GSAP composition timeline. */
(() => {
const tl=gsap.timeline({paused:true}); window.__timelines=window.__timelines||{}; window.__timelines.diabetes=tl;
const scenes=['.s1','.s2','.s3','.s4','.s5','.s6'];
tl.set(scenes.slice(1),{autoAlpha:0},0);
function reveal(sel,time,type){tl.set(sel,{autoAlpha:1},time);if(type==='circle')tl.fromTo(sel,{clipPath:'circle(0% at 72% 74%)'},{clipPath:'circle(160% at 72% 74%)',duration:.8,ease:'power3.inOut'},time);else if(type==='sheet')tl.fromTo(sel,{clipPath:'inset(0% 0% 0% 100%)'},{clipPath:'inset(0% 0% 0% 0%)',duration:.8,ease:'power3.inOut'},time);else tl.fromTo(sel,{clipPath:'inset(100% 0% 0% 0%)'},{clipPath:'inset(0% 0% 0% 0%)',duration:.85,ease:'power3.inOut'},time);}
/* The first frame is a finished composition; fragments resolve its physical depth. */
tl.fromTo('.frag1',{x:32,y:-36,rotation:-5},{x:0,y:0,rotation:0,duration:.85,ease:'power3.out'},0);
tl.fromTo('.frag2',{x:-24,y:25,rotation:4},{x:0,y:0,rotation:0,duration:1,ease:'power3.out'},.15);
tl.fromTo('.frag3',{x:18,y:40},{x:0,y:0,duration:1,ease:'back.out(1.1)'},.35);
tl.fromTo('.s1 .pancreas',{x:-60,rotation:-15},{x:0,rotation:-9,duration:1.2,ease:'power3.out'},.1);
tl.fromTo('.s1 .orange-rule',{scaleX:.35},{scaleX:1,duration:1.15,ease:'power2.out'},.15);
/* Question-mark dot becomes the human scene's circular cutout frame. */
tl.set('.disc-transition',{autoAlpha:1},3).fromTo('.bridge-disc',{scale:1,x:0,y:0},{scale:16,x:-300,y:-250,duration:.65,ease:'power3.inOut'},3);
reveal('.s2',3.5,'circle');tl.fromTo('.disc-transition',{clipPath:'circle(160% at 72% 74%)'},{clipPath:'circle(0% at 72% 74%)',duration:.7,ease:'power2.inOut'},3.65);tl.set('.disc-transition',{autoAlpha:0},4.35);
tl.fromTo('.s2 .window',{x:-180,rotation:-6},{x:0,rotation:0,duration:1.1,ease:'power3.out'},3.6);
tl.fromTo('.s2 .adult',{x:-110,y:50},{x:0,y:0,duration:1.5,ease:'power3.out'},3.7);
tl.fromTo('.s2 .meter',{x:220,rotation:-20},{x:0,rotation:9,duration:1.2,ease:'back.out(1.1)'},4.3);
tl.fromTo('.s2 .calendar',{y:250,rotation:16},{y:0,rotation:-5,duration:1.2,ease:'power3.out'},5.2);
tl.fromTo('.s2 .human-copy',{clipPath:'inset(0 0 100% 0)'},{clipPath:'inset(0 0 0% 0)',duration:1.1,ease:'power3.out'},4.1);
tl.fromTo('.s2 .care',{clipPath:'inset(0 100% 0 0)'},{clipPath:'inset(0 0% 0 0)',duration:1.1},7.4);
/* Meter geometry opens an observation field. */
tl.to('.s2 .meter',{x:-325,y:-130,rotation:0,duration:.7,ease:'power2.inOut'},10);
reveal('.s3',10.7,'circle');tl.fromTo('.s3 .scope',{scale:.5,rotation:-15},{scale:1,rotation:0,duration:1.2,ease:'power3.out'},10.7);
tl.fromTo('.s3 .cells',{clipPath:'circle(0% at 50% 50%)',rotation:-9},{clipPath:'circle(75% at 50% 50%)',rotation:0,duration:1.3,ease:'power2.out'},11.1);
tl.fromTo('.s3 .researcher',{x:250,y:30},{x:0,y:0,duration:1.35,ease:'power3.out'},10.85);
tl.fromTo('.s3 .micro',{y:340,rotation:15},{y:0,rotation:-5,duration:1.25,ease:'power3.out'},11.7);
tl.fromTo('.s3 .leader',{scaleX:0},{scaleX:1,duration:.8},12.6);
tl.fromTo('.s3 .annotation',{clipPath:'inset(0 0 100% 0)'},{clipPath:'inset(0 0 0% 0)',duration:.65},13.1);
tl.fromTo('.s3 .cell-label',{x:120},{x:0,duration:.8,ease:'power2.out'},14.25);
/* Annotation becomes a linear evidence route; sheets unfold in progression. */
tl.set('.line-transition',{autoAlpha:1},16.5).fromTo('.bridge-line',{scaleX:0,y:-240},{scaleX:1,y:0,duration:.65,ease:'power3.inOut'},16.5);
reveal('.s4',17,'sheet');tl.set('.line-transition',{autoAlpha:0},17.8);
tl.fromTo('.s4 .research-line',{scaleX:0},{scaleX:1,duration:6.2,ease:'none'},17.5);
['.sheet1','.sheet2','.sheet3','.sheet4','.sheet5'].forEach((s,i)=>{let at=17.4+i*1.18;tl.fromTo(s,{rotationY:-86,x:0,y:65,scaleX:.2},{rotationY:0,x:0,y:0,scaleX:1,duration:1.05,ease:'power3.out'},at);tl.fromTo(s+' h2, '+s+' .number',{clipPath:'inset(0 0 100% 0)'},{clipPath:'inset(0 0 0% 0)',duration:.35},at+.7)});
tl.fromTo('.s4 .footnote',{clipPath:'inset(0 100% 0 0)'},{clipPath:'inset(0 0% 0 0)',duration:.8},23.65);
/* The research sheets hinge into an open publication spread. */
tl.to('.s4 .sheet',{y:-60,rotation:0,scaleY:.86,stagger:.06,duration:.55,ease:'power2.inOut'},25.15);
reveal('.s5',25.7,'sheet');tl.fromTo('.s5 .spread-page:first-child',{rotationY:-55,transformOrigin:'left center'},{rotationY:0,duration:1.15,ease:'power3.out'},25.7);tl.fromTo('.s5 .spread-page:last-child',{rotationY:55,transformOrigin:'right center'},{rotationY:0,duration:1.15,ease:'power3.out'},25.7);
tl.fromTo('.s5 .cell',{clipPath:'inset(100% 0 0 0)'},{clipPath:'inset(0% 0 0 0)',duration:1.1},27.3);tl.fromTo('.s5 .pending',{y:65,rotation:-15},{y:0,rotation:0,duration:1,ease:'back.out(1)'},29.1);
tl.fromTo('.s5 .spread-caption',{clipPath:'inset(0 100% 0 0)'},{clipPath:'inset(0 0% 0 0)',duration:.85},31.1);
/* Pages collect into the physical book structure. */
tl.to('.s5 .spread-page:first-child',{rotationY:-75,transformOrigin:'left center',duration:.65,ease:'power2.in'},33.55);
tl.to('.s5 .spread-page:last-child',{rotationY:75,transformOrigin:'right center',duration:.65,ease:'power2.in'},33.55);
reveal('.s6',34.1,'sheet');
['.leaf1','.leaf2','.leaf3','.leaf4'].forEach((s,i)=>tl.fromTo(s,{x:180+i*25,y:-190+i*100,rotation:20+i*8},{x:8+i*7,y:5+i*5,rotation:-6+i*1.2,duration:1.5,ease:'power3.inOut'},34.1+i*.16));
tl.fromTo('.s6 .book',{rotationY:-84,x:160,rotation:-6},{rotationY:0,x:0,rotation:-6,duration:1.5,ease:'power3.inOut'},43);
tl.fromTo('.s6 .final-copy',{clipPath:'inset(0 0 100% 0)'},{clipPath:'inset(0 0 0% 0)',duration:1.25},34.8);
tl.fromTo('.s6 .ending-rule',{scaleX:0},{scaleX:1,duration:1},35.1);
tl.fromTo('.s6 .ending-label',{clipPath:'inset(0 100% 0 0)'},{clipPath:'inset(0 0% 0 0)',duration:.9},44.5);
tl.set('.s1',{autoAlpha:0},4.25);tl.set('.s2',{autoAlpha:0},11.5);tl.set('.s3',{autoAlpha:0},17.8);tl.set('.s4',{autoAlpha:0},26.5);tl.set('.s5',{autoAlpha:0},34.9);tl.to({}, {duration:.1},49.4);
window.seek=(t)=>{tl.seek(Math.max(0,Math.min(49.5,Number(t))),false);return tl.time();};
window.compositionReady=document.fonts.ready.then(()=>{tl.seek(0);window.__READY__=true;});
})();
