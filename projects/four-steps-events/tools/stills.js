// node tools/stills.js "<query>" outdir t1 t2 ...   -> outdir/t_<t>.jpg
const {chromium}=require('playwright');
(async()=>{
  const [q,out,...ts]=process.argv.slice(2);
  require('fs').mkdirSync(out,{recursive:true});
  const b=await chromium.launch({args:['--force-color-profile=srgb','--disable-lcd-text']});
  const p=await b.newPage({viewport:{width:1080,height:1920},deviceScaleFactor:1});
  const errs=[]; p.on('pageerror',e=>errs.push(e.message)); p.on('console',m=>{if(m.type()==='error')errs.push(m.text())});
  await p.goto('http://127.0.0.1:8765/index.html?render'+(q?'&'+q:''));
  await p.evaluate(()=>window.__ready);
  for(const t of ts){ await p.evaluate(t=>window.seek(+t),t); await p.screenshot({path:`${out}/t_${(+t).toFixed(2).padStart(6,'0')}.jpg`,type:'jpeg',quality:88}); }
  if(errs.length) console.log('ERRORS:\n'+errs.join('\n'));
  await b.close();
})();
