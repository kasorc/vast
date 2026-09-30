// Generuje zestaw logo SheBalance: oryginalny sygnet (logo/oryginal/LOGO.svg) + napisy zamienione na krzywe.
// Fonty marki ze strony: Forum (nagłówki) i Mulish (tekst). Wymaga: npm i opentype.js @fontsource/forum @fontsource/mulish
import opentype from 'opentype.js';
import fs from 'fs';
const load = p => { const b = fs.readFileSync(`node_modules/@fontsource/${p}`); return opentype.parse(b.buffer.slice(b.byteOffset, b.byteOffset + b.byteLength)); };
const forum = load('forum/files/forum-latin-400-normal.woff');
const mulish = load('mulish/files/mulish-latin-300-normal.woff');
const out = process.argv[2] || '/home/user/vast/she-balance/logo';
const ds = [...fs.readFileSync(`${out}/oryginal/LOGO.svg`, 'utf8').matchAll(/<path d="([^"]+)"/g)].map(m => m[1]);
const BOX = {cx: 711, cy: 738, h: 1175};           // bbox sygnetu w LOGO.svg

const DARK = '#58756C', SAGE = '#A4B8B0', CREAM = '#F4F2EF', WHITE = '#FFFFFF';

function textPath(font, str, size, cx, y, tracking) {
  const k = size / font.unitsPerEm, tr = tracking * size, gl = [...str].map(ch => font.charToGlyph(ch));
  let w = 0; gl.forEach((g, i) => { w += g.advanceWidth * k + (i < gl.length - 1 ? tr : 0); });
  let x = cx - w / 2, d = '';
  gl.forEach(g => { d += g.getPath(x, y, size).toPathData(2); x += g.advanceWidth * k + tr; });
  return d;
}
const sign = (cx, cy, height, color) => {
  const s = height / BOX.h;
  return `<g fill="${color}" transform="translate(${cx} ${cy}) scale(${s.toFixed(5)}) translate(${-BOX.cx} ${-BOX.cy})">${ds.map(d => `<path d="${d}"/>`).join('')}</g>`;
};
const svg = (W, H, body, bg) => `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" width="${W}" height="${H}">${bg ? `<rect width="${W}" height="${H}" fill="${bg}"/>` : ''}\n${body}\n</svg>\n`;

const full = (c, bg) => svg(600, 520, `${sign(300, 150, 170, c)}
<path fill="${c}" d="${textPath(forum, 'SHE BALANCE', 58, 300, 340, 0.16)}"/>
<path fill="${c}" d="${textPath(mulish, 'WOMEN CAMP', 17, 300, 388, 0.5)}"/>
<path fill="${c}" d="${textPath(mulish, 'healthy  ·  networking  ·  self-development', 16, 300, 440, 0.1)}"/>`, bg);
const horiz = c => svg(800, 200, `${sign(95, 100, 140, c)}
<path fill="${c}" d="${textPath(forum, 'SHE BALANCE', 62, 480, 112, 0.16)}"/>
<path fill="${c}" d="${textPath(mulish, 'WOMEN CAMP', 17, 480, 152, 0.5)}"/>`);
const avatar = () => svg(400, 400, `<circle cx="200" cy="200" r="200" fill="${SAGE}"/>${sign(200, 205, 230, WHITE)}`);

fs.writeFileSync(`${out}/she-balance-logo.svg`, full(DARK));
fs.writeFileSync(`${out}/she-balance-logo-bialy.svg`, full(WHITE));
fs.writeFileSync(`${out}/she-balance-logo-na-szalwii.svg`, full(WHITE, SAGE));
fs.writeFileSync(`${out}/she-balance-logo-poziome.svg`, horiz(DARK));
fs.writeFileSync(`${out}/she-balance-avatar.svg`, avatar());
fs.writeFileSync(`${out}/podglad.html`, `<!doctype html><meta charset="utf-8"><title>SheBalance – logo</title>
<style>body{margin:0;display:grid;grid-template-columns:1fr 1fr}div{display:flex;align-items:center;justify-content:center;padding:30px;min-height:300px}img{max-width:90%;max-height:280px}</style>
<div style="background:${CREAM}"><img src="she-balance-logo.svg"></div>
<div style="background:${SAGE}"><img src="she-balance-logo-bialy.svg"></div>
<div style="background:${CREAM}"><img src="she-balance-logo-poziome.svg"></div>
<div style="background:${CREAM}"><img src="she-balance-avatar.svg" style="width:220px"></div>`);
