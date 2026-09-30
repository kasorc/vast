// Wypisuje czasy startu scen i długość animacji (do synchronizacji muzyki).
const { chromium } = await import(process.env.PW || '/opt/node22/lib/node_modules/playwright/index.mjs');
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
const p = await b.newPage(); await p.goto('file://' + new URL('../animacje/' + process.argv[2] + '.html?render', import.meta.url).pathname);
await p.waitForFunction(() => window.ready);
const r = await p.evaluate(() => ({ total: window.TOTAL, cuts: window.SCENES.slice(1).map(s => +s.t0.toFixed(3)) }));
console.log(r.total + ' ' + r.cuts.join(',')); await b.close();
