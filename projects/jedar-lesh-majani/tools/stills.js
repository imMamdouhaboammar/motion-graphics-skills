const {chromium}=require('playwright');
(async()=>{const ts=process.argv.slice(3).map(Number);const out=process.argv[2];
const b=await chromium.launch({executablePath:process.env.CHROME_PATH||undefined,args:['--force-color-profile=srgb']});const p=await b.newPage({viewport:{width:1080,height:1920}});
const errs=[];p.on('pageerror',e=>errs.push(e.message));p.on('console',m=>{if(m.type()==='error')errs.push(m.text())});
await p.goto('http://127.0.0.1:8765/index.html?render');await p.evaluate(()=>window.__ready);
for(const t of ts){await p.evaluate(t=>window.seek(t),t);await p.screenshot({path:`${out}/t_${t.toFixed(2)}.jpg`,type:'jpeg',quality:80});}
if(errs.length)console.log('ERR',errs.join('\n'));await b.close();})();
