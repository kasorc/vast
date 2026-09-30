import pathlib, re
src=pathlib.Path('.')
A=(src/'figura-A.svg').read_text(); B=(src/'figura-B.svg').read_text()
defs=(src/'defs.svg').read_text()+(src/'defs-fig.svg').read_text()
css=(src/'fonty.css').read_text()+(src/'fig.css').read_text()
base=re.search(r'/\* postacie \*/(.*?)\.arm\{', (src/'szablon.html').read_text(), re.S).group(1)
poses=[('A','idle'),('B','walk has-pack'),('A','wave'),('B','hold has-mug'),('A','sit has-mug hold'),('B','yoga'),('A','cheer'),('B','stretch')]
cells=''
for i,(w,cls) in enumerate(poses):
    fig=(A if w=='A' else B).replace(f'class="fig fig{w}"',f'class="fig fig{w} {cls}"',1)
    x=(i%4)*270; y=(i//4)*480
    cells+=f'<g transform="translate({x+25},{y+40}) scale(.55)">{fig}</g><text x="{x+135}" y="{y+470}" text-anchor="middle" font-size="16" font-family="Mulish">{w}: {cls}</text>'
html=f'<!doctype html><meta charset="utf-8"><style>{css}{base}</style><body style="margin:0;background:#F2EFEB"><svg viewBox="0 0 1080 960" width="1080" height="960"><defs>{defs}</defs>{cells}</svg><script>window.ready=1</script>'
(src/'_test_fig.html').write_text(html)
