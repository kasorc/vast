// Renderuje animację klatka po klatce (1080×1920, 30 fps) do MP4 albo robi podgląd wybranych sekund.
// node renderuj.mjs <nazwa> [--podglad 0.5,2,4.2] [--kontakt]
const { chromium } = await import(process.env.PW || '/opt/node22/lib/node_modules/playwright/index.mjs');
import fs from 'fs'; import path from 'path'; import { execFileSync } from 'child_process';
const [,, name, ...rest] = process.argv;
const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const PAGE = 'file://' + ROOT + '/animacje/' + name + '.html?render';
const FF = process.env.FFMPEG || '/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2';
const EXE = process.env.CHROME || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome';
const TMP = process.env.TMPDIR_RENDER || '/tmp/render-' + name;
const b = await chromium.launch({ executablePath: EXE });
async function open(scale){ const p = await b.newPage({viewport:{width:540,height:960},deviceScaleFactor:scale});
  const errs=[]; p.on('pageerror',e=>errs.push(e.message)); await p.goto(PAGE); await p.waitForFunction(()=>window.ready,null,{timeout:30000}); p.errs=errs; return p; }
const pi = rest.indexOf('--podglad');
if (pi >= 0) { // podgląd: sekundy → PNG w katalogu podglad/<nazwa>/ (przechodzi po kolei, żeby przejścia były poprawne)
  const times = rest[pi+1].split(',').map(Number).sort((a,b)=>a-b);
  const dir = ROOT + '/src/podglad/' + name; fs.mkdirSync(dir, {recursive:true});
  const p = await open(1); const scenes = await p.evaluate(()=>window.SCENES.map(s=>({t0:s.t0,d:s.d})));
  for (const t of times) {
    const i = scenes.findLastIndex(s=>s.t0<=t); if (i>0) await p.evaluate(x=>window.renderAt(x), scenes[i-1].t0+scenes[i-1].d-0.02);
    await p.evaluate(x=>window.renderAt(x), t); await p.screenshot({path:`${dir}/t${t.toFixed(2)}.png`});
  }
  console.log('podgląd zapisany w', dir, p.errs.length? 'BŁĘDY: '+p.errs.join(' | '):'bez błędów JS'); await b.close(); process.exit(0);
}
const FPS = 30; fs.rmSync(TMP,{recursive:true,force:true}); fs.mkdirSync(TMP,{recursive:true});
const probe = await open(1); const scenes = await probe.evaluate(()=>window.SCENES.map(s=>({t0:s.t0,d:s.d}))); const total = await probe.evaluate(()=>window.TOTAL);
if (probe.errs.length) console.log('BŁĘDY JS:', probe.errs); await probe.close();
const N = Math.round(total*FPS);
const jobs = scenes.map((s,i)=>({i, f0:Math.ceil(s.t0*FPS-1e-6), f1: i<scenes.length-1? Math.ceil(scenes[i+1].t0*FPS-1e-6) : N}));
async function worker(){ const p = await open(2);
  while (jobs.length) { const j = jobs.shift();
    if (j.i>0) { const ps=scenes[j.i-1]; await p.evaluate(t=>window.renderAt(t), ps.t0+ps.d-0.02); }
    for (let f=j.f0; f<j.f1; f++) { await p.evaluate(t=>window.renderAt(t), f/FPS+1e-4);
      await p.screenshot({path:`${TMP}/${String(f).padStart(5,'0')}.png`, timeout:120000}); } }
  await p.close(); }
await Promise.all([worker(),worker(),worker(),worker()]); await b.close();
const out = ROOT + '/animacje/' + name + '.mp4';
execFileSync(FF, ['-y','-loglevel','error','-framerate',String(FPS),'-i',TMP+'/%05d.png','-c:v','libx264','-preset','slow','-crf','14','-tune','animation','-pix_fmt','yuv420p','-movflags','+faststart',out]);
fs.rmSync(TMP,{recursive:true,force:true});
console.log('zapisano', out, N, 'klatek');
