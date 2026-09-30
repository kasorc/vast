import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
import fs from 'fs'; import { execFileSync } from 'child_process';
const FF='/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2';
const DIR='/home/user/vast/she-balance/logo-animacje';
const list=JSON.parse(fs.readFileSync(DIR+'/lista.json','utf8'));
const only=process.argv[2];
const jobs=[]; for(const a of list) for(const k of ['bialy','zielony']) if(!only||only===a.id) jobs.push({...a,k});
fs.mkdirSync(DIR+'/pliki',{recursive:true});
const b = await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome'});
async function run(j){
  const p = await b.newPage({viewport:{width:1080,height:1080}});
  await p.goto(`file://${DIR}/animacje.html?render=${j.id}&kolor=${j.k}`);
  await p.evaluate(()=>document.fonts.ready); await p.waitForTimeout(300);
  const fdir=`frames/${j.id}-${j.k}`; fs.rmSync(fdir,{recursive:true,force:true}); fs.mkdirSync(fdir,{recursive:true});
  const n=Math.round((j.loop? j.d : j.d+0.7)*30);
  for(let i=0;i<n;i++){
    await p.evaluate(t=>window.seek(t),i*1000/30);
    await p.screenshot({path:`${fdir}/${String(i).padStart(4,'0')}.png`,omitBackground:true,timeout:120000,clip:{x:0,y:0,width:1080,height:1080}});
  }
  await p.close();
  const out=`${DIR}/pliki/${j.id}-${j.k}`;
  execFileSync(FF,['-y','-loglevel','error','-framerate','30','-i',fdir+'/%04d.png','-c:v','libvpx-vp9','-pix_fmt','yuva420p','-crf','26','-b:v','0','-row-mt','1',out+'.webm']);
  execFileSync(FF,['-y','-loglevel','error','-framerate','30','-i',fdir+'/%04d.png','-c:v','qtrle','-pix_fmt','argb',out+'.mov']);
  if(!process.env.KEEP) fs.rmSync(fdir,{recursive:true,force:true});
  console.log('done',j.id,j.k,n);
}
const q=jobs.filter(j=>!fs.existsSync(DIR+'/pliki/'+j.id+'-'+j.k+'.mov')); await Promise.all([0,1].map(async()=>{while(q.length) await run(q.shift());}));
await b.close();
