// node tools/render.js "<query>" out.mp4 [t0] [t1] [fps] [--png]
// Loads index.html?render, calls window.seek() for every frame and pipes frames into ffmpeg (video only).
const {chromium}=require('playwright');
const {spawn}=require('child_process');
(async()=>{
  const a=process.argv.slice(2); const png=a.includes('--png'); const [q,out,t0s,t1s,fpss]=a.filter(x=>x!=='--png');
  const fps=+(fpss||30);
  const b=await chromium.launch({executablePath:process.env.CHROME_PATH||undefined,args:['--force-color-profile=srgb','--disable-lcd-text']});
  const p=await b.newPage({viewport:{width:1080,height:1920},deviceScaleFactor:1});
  const errs=[]; p.on('pageerror',e=>errs.push(e.message));
  await p.goto('http://127.0.0.1:8765/index.html?render'+(q?'&'+q:''));
  await p.evaluate(()=>window.__ready);
  const dur=await p.evaluate(()=>window.DURATION);
  if(!(dur>0)){ console.error('page did not initialise (window.DURATION missing):',errs.join('\n')); process.exit(1); }
  const t0=+(t0s||0), t1=Math.min(+(t1s||dur), dur); const n=Math.round((t1-t0)*fps);
  const ff=spawn('ffmpeg',['-y','-v','error','-f','image2pipe','-framerate',String(fps),'-i','-',
    '-vf','scale=in_range=full:out_range=tv:out_color_matrix=bt709,format=yuv420p',
    '-c:v','libx264','-preset','slow','-crf',process.env.CRF||'18','-maxrate','14M','-bufsize','28M','-profile:v','high','-pix_fmt','yuv420p',
    '-color_range','tv','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-movflags','+faststart',out],{stdio:['pipe','inherit','inherit']});
  const ffDone=new Promise(r=>ff.on('close',r));
  ff.stdin.on('error',e=>{ console.error('ffmpeg input closed early:',e.message); process.exit(1); });
  const T=Date.now();
  for(let i=0;i<n;i++){
    const t=t0+i/fps; await p.evaluate(t=>window.seek(t),t);
    const buf=await p.screenshot({type:png?'png':'jpeg',quality:png?undefined:95});
    if(!ff.stdin.write(buf)) await new Promise(r=>ff.stdin.once('drain',r));
    if(i%150===0) process.stderr.write(`frame ${i}/${n} t=${t.toFixed(2)} ${((Date.now()-T)/1000).toFixed(0)}s\n`);
  }
  ff.stdin.end(); const code=await ffDone;
  if(errs.length) console.log('PAGE ERRORS:\n'+[...new Set(errs)].join('\n'));
  await b.close();
  if(code!==0){ console.error('ffmpeg exited with code',code); process.exit(1); }
  console.log('done',out,n,'frames',((Date.now()-T)/1000).toFixed(0)+'s');
})();
