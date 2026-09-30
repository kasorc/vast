# -*- coding: utf-8 -*-
# Składa src/animacje/role-liscie.html z generatora gen.py
import pathlib
HERE = pathlib.Path(__file__).parent
G = {'__file__': str(HERE / 'gen.py')}
exec(open(HERE / 'gen.py', encoding='utf-8').read(), G)
SC = G['SCENES']; SVG = G['SVG']; CSS = G['CSS']; DEFS = G['DEFS']
order = [s[0] for s in SC]
scenes = ''.join('<g class="scene" data-s="%s">%s</g>\n' % (sid, SVG[sid]) for sid in order if sid in SVG)
scjs = ','.join("{id:'%s',d:%s,bg:'%s'}" % (sid, d, bg) for sid, d, bg in SC if sid in SVG)
html = open(HERE / 'szablon.html', encoding='utf-8').read()
html = html.replace('@@CSS@@', '\n'.join(CSS)).replace('@@DEFS@@', DEFS).replace('@@SCENES@@', scenes).replace('@@SCJS@@', scjs)
(HERE.parent / 'role-liscie.html').write_text(html, encoding='utf-8')
print('ok', len(html), 'CSS rules', len(CSS))
