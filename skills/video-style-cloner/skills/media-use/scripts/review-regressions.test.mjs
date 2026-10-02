import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, writeFileSync, rmSync, chmodSync, readFileSync, existsSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { spawnSync } from 'node:child_process';
import { speechSpans, duckLane, duckKeyframes } from './lib/duck.mjs';
import { isPublicMediaUrl, fetchMedia } from './lib/media-fetch.mjs';
import { parseFormat } from '../../faceless-explainer/scripts/lib/dimensions.mjs';
import { resolveVoiceId } from '../audio/scripts/lib/tts.mjs';
const voices = {voices:[{id:'empty',duration_s:5,words:[]},{id:'spoken',words:[{text:'hi',start:0,end:1}]}]};
test('empty voice retains its sequential duration and later voice ID',()=>{
 assert.deepEqual(speechSpans(voices,{sequential:true}),[{start:5,end:6}]);
 assert.deepEqual(speechSpans(voices,{offsets:{empty:0,spoken:9}}),[{start:9,end:10}]);
});
test('CLI rejects malformed offsets',()=>{
 const dir=mkdtempSync(join(tmpdir(),'duck-review-'));
 try { const meta=join(dir,'meta.json');writeFileSync(meta,JSON.stringify({words:[{text:'hi',start:0,end:1}]}));
 for(const value of ['0=', '0=nope', '', '=2', '0=Infinity','0=1=2']) {
 const r=spawnSync(process.execPath,[new URL('./audio-duck.mjs',import.meta.url).pathname,'--meta',meta,'--target','#bgm','--offsets',value,'--json'],{encoding:'utf8',env:{...process.env,DO_NOT_TRACK:'1'}});
 assert.equal(r.status,1,value);assert.match(r.stdout,/offsets/,value);
 }
 } finally {rmSync(dir,{recursive:true,force:true});}
});
test('duck lane starts at envelope value and keeps only unfinished transitions',()=>{
 const k=[{time:1,volume:0.25,duration:1},{time:5,volume:1,duration:2}];
 const points=(clipStart)=>duckLane(k,{clipStart}).lanes[0].points;
 assert.deepEqual(points(3),[{t:0,v:0.25},{t:2,v:0.25},{t:4,v:1}]);
 assert.deepEqual(points(1.5),[{t:0,v:0.625},{t:0.5,v:0.25},{t:3.5,v:0.25},{t:5.5,v:1}]);
 assert.deepEqual(points(8),[{t:0,v:1}]);
});
test('NAT64 translation URLs and redirects are blocked before fetch',async()=>{
 for(const host of ['64:ff9b::a00:1','64:ff9b::c0a8:101','64:ff9b:1::a00:1']) assert.equal(isPublicMediaUrl(`https://[${host}]/x`),false);
 let calls=0;
 await assert.rejects(fetchMedia('https://example.com/x',{fetchImpl:async()=>{calls++;return new Response(null,{status:302,headers:{location:'https://[64:ff9b::7f00:1]/'}});}}),/blocked/);
 assert.equal(calls,1);assert.equal(isPublicMediaUrl('https://[2606:4700::1111]/'),true);
});
test('inherited format keys fall back to landscape',()=>{
 for(const format of ['constructor','toString','__proto__']) assert.deepEqual(parseFormat(format),{width:1920,height:1080,source:'default(landscape)'});
});
test('HeyGen default matches requested language and fails when unavailable',async()=>{
 const original=globalThis.fetch;const previousKey=process.env.HEYGEN_API_KEY;process.env.HEYGEN_API_KEY='test';
 try {globalThis.fetch=async()=>new Response(JSON.stringify({data:[{voice_id:'english',language:'English'},{voice_id:'french',language:'French'}]}));
 assert.equal(await resolveVoiceId({provider:'heygen',lang:'fr'}),'french');
 assert.equal(await resolveVoiceId({provider:'heygen',lang:'fr-FR'}),'french');
 await assert.rejects(resolveVoiceId({provider:'heygen',lang:'ja'}),/voice.*ja|ja.*voice/);
 }finally{globalThis.fetch=original;if(previousKey === undefined) delete process.env.HEYGEN_API_KEY;else process.env.HEYGEN_API_KEY=previousKey;}
});
test('resolve delegates argv to installed HyperFrames and preserves status',()=>{
 const dir=mkdtempSync(join(tmpdir(),'resolve-review-'));
 try {const command=join(dir,'hyperframes');writeFileSync(command,'#!/usr/bin/env node\nconsole.log(JSON.stringify(process.argv.slice(2)));process.exit(7);\n');chmodSync(command,0o755);
 const r=spawnSync(process.execPath,[new URL('./resolve.mjs',import.meta.url).pathname,'--intent','value with spaces'],{encoding:'utf8',env:{...process.env,PATH:dir+':'+process.env.PATH}});
 assert.equal(r.status,7);assert.deepEqual(JSON.parse(r.stdout),['media-use','resolve','--intent','value with spaces']);
 }finally{rmSync(dir,{recursive:true,force:true});}
});

test('shipped SFX manifest advertises only files that exist',()=>{
 const dir=new URL('../audio/assets/sfx/',import.meta.url);
 const manifest=JSON.parse(readFileSync(new URL('manifest.json',dir),'utf8'));
 for(const entry of Object.values(manifest)) assert.ok(existsSync(new URL(entry.file,dir)),entry.file);
});

test('duck lanes reject unsupported zero and invalid ramp durations',()=>{
 for(const duration of [0,-1,Infinity,NaN]) {
  assert.throws(()=>duckLane([{time:10,volume:0.25,duration}],{clipStart:5}),/positive finite/);
 }
 assert.throws(()=>duckLane(duckKeyframes([{start:10,end:12}],{attack:0,release:0.4}),{clipStart:5}),/positive finite/);
});
test('CLI rejects unsupported zero and invalid attack or release',()=>{
 const dir=mkdtempSync(join(tmpdir(),'duck-duration-review-'));
 try {
  const meta=join(dir,'meta.json');writeFileSync(meta,JSON.stringify({words:[{text:'hi',start:10,end:12}]}));
  for(const name of ['attack','release']) for(const value of ['0','-1','Infinity','nope','']) {
   const r=spawnSync(process.execPath,[new URL('./audio-duck.mjs',import.meta.url).pathname,'--meta',meta,'--target','#bgm',`--${name}=${value}`,'--json'],{encoding:'utf8',env:{...process.env,DO_NOT_TRACK:'1'}});
   assert.equal(r.status,1,`${name}=${value}`);assert.match(r.stdout,new RegExp(`--${name} must be positive finite`));
  }
 }finally{rmSync(dir,{recursive:true,force:true});}
});
