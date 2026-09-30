/* ===== Silnik animacji SheBalance =====
   Strona definiuje przed tym skryptem: window.SCENES = [{id, d, bg?, o?:[x,y], onShow?(el)}]
   - Każda scena to <g class="scene" data-s="id"> (może być kilka warstw z tym samym data-s).
   - Animacje CSS wewnątrz .scene startują, gdy scena staje się aktywna (klasa .active).
   - Elementy z klasą .sr (scene-relative) liczą czas od początku sceny, a z .go są restartowane w show().
   - #bg + #wipe (opcjonalnie): tło i przejście kołem; #cam (opcjonalnie): powolny zoom kamery.
   - ?render → tryb klatek: window.renderAt(sekundy) ustawia DOKŁADNY stan animacji. */
(function(){
const scenes=window.SCENES; let acc=0; scenes.forEach(s=>{s.t0=acc; acc+=s.d;}); const total=acc;
window.TOTAL=total;
const NS='http://www.w3.org/2000/svg'; window.NS=NS;
let seed=window.SEED||11; window.rnd=()=>(seed=(seed*16807)%2147483647)/2147483647;
const stage=document.getElementById('stage'), bg=document.getElementById('bg'), wipe=document.getElementById('wipe'), cam=document.getElementById('cam');
const prog=document.getElementById('prog'), dots=document.getElementById('dots'), playBtn=document.getElementById('play');
function restart(el,cls){el.classList.remove(cls);void el.getBoundingClientRect();el.classList.add(cls);} window.restart=restart;
function splitText(){ // <text class="split"> → litery w osobnych <text class="ch" style="--i:n">
  document.querySelectorAll('text.split').forEach(t=>{
    const g=document.createElementNS(NS,'g'); const n=t.getNumberOfChars(); const cls=t.getAttribute('class').replace('split','').trim();
    for(let i=0;i<n;i++){const ch=t.textContent[i]; if(ch===' ') continue; const p=t.getStartPositionOfChar(i);
      const c=document.createElementNS(NS,'text'); c.textContent=ch; c.setAttribute('x',p.x.toFixed(2)); c.setAttribute('y',p.y.toFixed(2));
      c.setAttribute('font-size',t.getAttribute('font-size')); c.setAttribute('text-anchor','start'); c.setAttribute('class',(cls+' ch').trim());
      ['fill','stroke','stroke-width','opacity'].forEach(a=>{if(t.getAttribute(a)) c.setAttribute(a,t.getAttribute(a));});
      c.style.cssText=(t.getAttribute('style')||'')+`;--i:${i}`; g.appendChild(c);}
    t.replaceWith(g);
  });
}
if(dots) scenes.forEach((s,i)=>{const b=document.createElement('button');b.setAttribute('aria-label','Scena '+(i+1));b.onclick=()=>{t=s.t0+.001;current=-1;};dots.appendChild(b);});
let current=-1;
function show(i){
  const prev=current; current=i; const s=scenes[i];
  stage.dataset.scene=s.id;
  if(bg&&s.bg) bg.setAttribute('fill', prev<0||!scenes[prev].bg? s.bg : scenes[prev].bg);
  if(wipe&&s.bg){ const o=s.o||[270,480]; wipe.setAttribute('fill',s.bg); wipe.setAttribute('cx',o[0]); wipe.setAttribute('cy',o[1]); wipe.style.transformOrigin=`${o[0]}px ${o[1]}px`; restart(wipe,'go'); }
  if(cam){ cam.style.animationDuration=s.d+'s'; restart(cam,'go'); }
  document.querySelectorAll('.go-on-scene').forEach(h=>restart(h,'go'));
  document.querySelectorAll('.scene').forEach(el=>el.classList.toggle('active',el.dataset.s===s.id));
  if(dots) [...dots.children].forEach((d,j)=>d.classList.toggle('on',j===i));
  if(s.onShow) s.onShow(stage);
}
const sceneAt=t=>{let i=0;while(i<scenes.length-1&&t>=scenes[i+1].t0)i++;return i;};
window.renderAt=function(sec){
  const i=sceneAt(sec); if(i!==current) show(i);
  getComputedStyle(stage).opacity;
  const local=(sec-scenes[i].t0)*1000;
  document.getAnimations().forEach(a=>{a.pause(); const el=a.effect&&a.effect.target;
    const rel = a instanceof CSSTransition || (el && el.closest && (el.closest('.scene')||el.closest('.sr')||el===cam||el===wipe||el.classList.contains('go-on-scene')));
    a.currentTime = rel ? local : sec*1000; });
};
const params=new URLSearchParams(location.search);
let t=0,last=performance.now(),playing=!params.has('render');
if(params.has('rec')||params.has('render')) document.body.classList.add('rec');
document.fonts.ready.then(()=>{
  if(window.beforeSplit) window.beforeSplit();
  splitText(); window.ready=true;
  if(params.has('render')) return;
  const q=params.get('scene'); if(q){const s=scenes.find(s=>s.id===q); if(s) t=s.t0+.001;}
  function frame(now){ if(playing){t+=(now-last)/1000; if(t>=total){t=0;current=-1;}} last=now;
    const i=sceneAt(t); if(i!==current) show(i); if(prog) prog.style.width=(t/total*100)+'%'; requestAnimationFrame(frame);}
  requestAnimationFrame(frame);
});
if(playBtn){ playBtn.onclick=()=>{playing=!playing;playBtn.textContent=playing?'Pauza':'Odtwórz';document.getAnimations().forEach(a=>playing?a.play():a.pause());};
  document.getElementById('restart').onclick=()=>{t=0;current=-1;};
  document.addEventListener('keydown',e=>{if(e.code==='Space'){e.preventDefault();playBtn.click();}}); }
})();
