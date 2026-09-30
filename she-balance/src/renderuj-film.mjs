import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
import fs from 'fs'; import { execFileSync } from 'child_process';
const FF='/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2';
const FPS=30, OUT='reelframes';
fs.rmSync(OUT,{recursive:true,force:true}); fs.mkdirSync(OUT);
const b = await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome'});
const probe = await b.newPage(); await probe.goto('file:///home/user/vast/she-balance/index.html?render'); await probe.waitForFunction(()=>window.ready);
const scenes = await probe.evaluate(()=>window.SCENES); const total = await probe.evaluate(()=>window.TOTAL); await probe.close();
const N=Math.round(total*FPS);
const jobs=scenes.map((s,i)=>({i,f0:Math.ceil(s.t0*FPS-1e-6),f1:i<scenes.length-1?Math.ceil(scenes[i+1].t0*FPS-1e-6):N}));
async function worker(){ const p=await b.newPage({viewport:{width:540,height:960},deviceScaleFactor:2});
  await p.goto('file:///home/user/vast/she-balance/index.html?render'); await p.waitForFunction(()=>window.ready);
  while(jobs.length){ const j=jobs.shift();
    if(j.i>0){ const ps=scenes[j.i-1]; await p.evaluate(t=>window.renderAt(t), ps.t0+ps.d-0.02); }
    for(let f=j.f0;f<j.f1;f++){ await p.evaluate(t=>window.renderAt(t), f/FPS+1e-4);
      await p.screenshot({path:`${OUT}/${String(f).padStart(5,'0')}.png`,timeout:120000}); }
    console.log('scena',j.i,'ok'); }
  await p.close(); }
await Promise.all([worker(),worker(),worker(),worker()]); await b.close();
const out='/home/user/vast/she-balance/she-balance-reel.mp4';
execFileSync(FF,['-y','-loglevel','error','-framerate',String(FPS),'-i',OUT+'/%05d.png','-c:v','libx264','-preset','slow','-crf','14','-tune','animation','-pix_fmt','yuv420p','-movflags','+faststart',out]);
console.log('mp4 ok', N, 'klatek');
