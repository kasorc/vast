import opentype from 'opentype.js';
import fs from 'fs';
const F = n => { const b=fs.readFileSync(`node_modules/@fontsource/josefin-sans/files/josefin-sans-latin-${n}-normal.woff`); return opentype.parse(b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength)); };
const thin = F(200), light = F(300);
const out = '/home/user/vast/she-balance/logo';
fs.mkdirSync(out, {recursive:true});

// tekst -> ścieżka, wyśrodkowany w cx, z rozstrzeleniem liter (tracking w em)
function textPath(font, str, size, cx, y, tracking){
  const scale = size / font.unitsPerEm, tr = tracking * size;
  const glyphs = font.stringToGlyphs(str);
  let w = 0; glyphs.forEach((g,i)=>{ w += g.advanceWidth*scale + (i<glyphs.length-1?tr:0); });
  let x = cx - w/2, d = '';
  glyphs.forEach(g=>{ d += g.getPath(x, y, size).toPathData(2); x += g.advanceWidth*scale + tr; });
  return d;
}
// znak: sylwetka z trzech kamieni
const sign = (cx, cy, s, stroke, sw) => `
  <g fill="none" stroke="${stroke}" stroke-width="${sw}" transform="translate(${cx} ${cy}) scale(${s})">
    <circle cx="0" cy="-40" r="9"/>
    <path d="M-17,-13 C-17,-24 -8,-27 0,-27 C8,-27 17,-24 17,-13 C17,-4 9,-1 0,-1 C-9,-1 -17,-4 -17,-13 Z"/>
    <path d="M-29,18 C-29,6 -14,3 0,3 C14,3 29,6 29,18 C29,28 15,32 0,32 C-15,32 -29,28 -29,18 Z"/>
  </g>`;

function full(color, bg){
  const W=600,H=520;
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" width="${W}" height="${H}">
  ${bg?`<rect width="${W}" height="${H}" fill="${bg}"/>`:''}
  ${sign(300,170,2.4,color,1.25)}
  <path fill="${color}" d="${textPath(thin,'SHE BALANCE',58,300,345,0.22)}"/>
  <path fill="${color}" d="${textPath(light,'WOMEN CAMP',19,300,395,0.55)}"/>
  <path fill="${color}" d="${textPath(light,'healthy  ·  networking  ·  self-development',17,300,445,0.12)}"/>
</svg>`;
}
function horiz(color){
  const W=900,H=200;
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" width="${W}" height="${H}">
  ${sign(100,104,1.9,color,1.1)}
  <path fill="${color}" d="${textPath(thin,'SHE BALANCE',60,520,112,0.22)}"/>
  <path fill="${color}" d="${textPath(light,'WOMEN CAMP',18,520,152,0.55)}"/>
</svg>`;
}
function avatar(){
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" width="400" height="400">
  <circle cx="200" cy="200" r="200" fill="#a7b5a6"/>
  ${sign(200,212,2.9,'#ffffff',1.1)}
</svg>`;
}
fs.writeFileSync(`${out}/she-balance-logo.svg`, full('#3d4a3f'));
fs.writeFileSync(`${out}/she-balance-logo-bialy.svg`, full('#ffffff'));
fs.writeFileSync(`${out}/she-balance-logo-na-szalwii.svg`, full('#ffffff','#a7b5a6'));
fs.writeFileSync(`${out}/she-balance-logo-poziome.svg`, horiz('#3d4a3f'));
fs.writeFileSync(`${out}/she-balance-avatar.svg`, avatar());
// podgląd wszystkich wersji
fs.writeFileSync(`${out}/podglad.html`, `<!doctype html><meta charset="utf-8"><title>She Balance logo</title>
<style>body{margin:0;display:grid;grid-template-columns:1fr 1fr;gap:0;font-family:sans-serif}div{display:flex;align-items:center;justify-content:center;padding:30px;min-height:300px}img{max-width:90%;max-height:280px}</style>
<div style="background:#f4f1ea"><img src="she-balance-logo.svg"></div>
<div style="background:#a7b5a6"><img src="she-balance-logo-bialy.svg"></div>
<div style="background:#f4f1ea"><img src="she-balance-logo-poziome.svg"></div>
<div style="background:#f4f1ea"><img src="she-balance-avatar.svg" style="width:220px"></div>`);
