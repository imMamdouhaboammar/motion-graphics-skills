// Reports every platform font Chromium actually used to paint text anywhere in the film.
// Samples every 0.1 s (544 frames), so any text visible for at least 0.1 s is checked.
const {chromium}=require('playwright');
(async()=>{
  const b=await chromium.launch(); const p=await b.newPage({viewport:{width:1080,height:1920}});
  await p.goto('http://127.0.0.1:8765/index.html?render'); await p.evaluate(()=>window.__ready);
  const dur=await p.evaluate(()=>window.DURATION);
  const cdp=await p.context().newCDPSession(p); await cdp.send('DOM.enable'); await cdp.send('CSS.enable');
  const used={}; let nodesChecked=0, cdpErrors=0;
  for(let t=0;t<dur;t+=0.1){
    await p.evaluate(t=>window.seek(t),t);
    const {root}=await cdp.send('DOM.getDocument',{depth:-1});
    const {nodeIds}=await cdp.send('DOM.querySelectorAll',{nodeId:root.nodeId,selector:'#stage *'});
    for(const id of nodeIds){
      let r; try{ r=await cdp.send('CSS.getPlatformFontsForNode',{nodeId:id}); }catch(e){ cdpErrors++; continue; }
      for(const f of r.fonts){ const k=f.familyName+(f.isCustomFont?' (webfont)':' (SYSTEM)'); used[k]=(used[k]||0)+f.glyphCount; nodesChecked++; }
    }
  }
  console.log('text runs checked:',nodesChecked,'| CDP errors:',cdpErrors); console.log(used);
  const sys=Object.keys(used).filter(k=>k.endsWith('(SYSTEM)'));
  const ok=!sys.length && !cdpErrors;
  console.log(sys.length?'FAIL: system fallback used by '+sys.join(', '):cdpErrors?'FAIL: '+cdpErrors+' nodes could not be inspected':'PASS: no system fallback');
  await b.close(); process.exit(ok?0:1);
})();
