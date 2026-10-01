# Buduje postacie w całej sylwetce (figura-A.svg, figura-B.svg) z głów wyciętych z popiersi.
# Układ współrzędnych jak w popiersiach: środek x=110, stopy ok. y=712.
import pathlib
src = pathlib.Path(__file__).parent
headA = (src / '_headA.svg').read_text(); backA = (src / '_backA.svg').read_text(); backB = (src / '_backB.svg').read_text(); headB = (src / '_headB.svg').read_text()

def leg(side, x, pants, thigh_w, shin, shoe):
    return f'''<g class="leg{side}"><g class="thigh{side}"><rect x="{x-thigh_w/2}" y="436" width="{thigh_w}" height="138" rx="{thigh_w/2-2}" fill="{pants}"/></g>
      <g class="shin{side}">{shin}{shoe}</g></g>'''

def figA():
    pants = '#2a2a2e'
    shin = lambda x: f'<rect x="{x-18}" y="554" width="36" height="140" rx="16" fill="{pants}"/><rect x="{x-18}" y="672" width="36" height="12" fill="#1f1f22"/>'
    shoe = lambda x, d: f'<path d="M{x-22},704 C{x-22},690 {x+22},688 {x+22+6*d},700 L{x+24+6*d},712 L{x-24},712 Z" fill="#f4f2ee"/><rect x="{x-24}" y="708" width="{48+6*d if d>0 else 48}" height="5" rx="2" fill="#d6cfc2"/>'
    arm = lambda s, x: f'''<g class="arm{s}"><rect x="{x-14}" y="226" width="28" height="124" rx="14" fill="url(#stripesA)" stroke="#d6cfc2" stroke-width="1.5"/>
      <g class="fore{s}"><rect x="{x-12}" y="334" width="24" height="108" rx="12" fill="url(#stripesA)" stroke="#d6cfc2" stroke-width="1.5"/><rect x="{x-12}" y="430" width="24" height="10" rx="4" fill="#ece8df"/><ellipse cx="{x}" cy="452" rx="11" ry="13" fill="#f2c9aa"/>
      {'<g class="prop notes"><rect x="'+str(x-26)+'" y="418" width="34" height="44" rx="3" fill="#E3CCC1" transform="rotate(-8 '+str(x)+' 440)"/><rect x="'+str(x-22)+'" y="424" width="26" height="3" fill="#6E5446" transform="rotate(-8 '+str(x)+' 440)"/></g>' if s=='L' else '<g class="prop mug"><path d="M'+str(x-15)+',432 L'+str(x+15)+',432 L'+str(x+13)+',462 Q'+str(x)+',468 '+str(x-13)+',462 Z" fill="#F4F2EF"/><path d="M'+str(x+14)+',438 q12,2 8,14 q-2,6 -9,6" fill="none" stroke="#F4F2EF" stroke-width="4"/><ellipse cx="'+str(x)+'" cy="432" rx="15" ry="4" fill="#8a5a3c"/><path class="steam" d="M'+str(x-4)+',424 q-5,-7 0,-14 q5,-7 0,-14" fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round"/></g>'}
      </g></g>'''
    return f'''<g class="fig figA"><ellipse class="shadow" cx="110" cy="714" rx="72" ry="9" fill="#000" opacity=".13"/><g class="body">{backA}
    {leg('L', 86, pants, 40, shin(86), shoe(86,-1))}
    {leg('R', 134, pants, 40, shin(134), shoe(134,1))}
    <path d="M58,424 L162,424 L166,474 L54,474 Z" fill="{pants}"/>
    <path d="M97,160 L97,214 Q110,221 123,214 L123,160 Z" fill="#dca17f"/>
    <path d="M50,240 C54,222 76,212 96,208 Q110,214 124,208 C144,212 166,222 170,240 L164,330 C162,372 160,402 160,440 L60,440 C60,402 58,372 56,330 Z" fill="url(#stripesA)" stroke="#d6cfc2" stroke-width="1.5"/>
    <path d="M50,240 C54,222 76,212 96,208 Q110,214 124,208 C144,212 166,222 170,240 L164,330 C162,372 160,402 160,440 L60,440 C60,402 58,372 56,330 Z" fill="url(#shadeTorso)"/>
    <path d="M90,208 Q110,226 130,208" fill="none" stroke="#ece8df" stroke-width="7" stroke-linecap="round"/>
    {arm('L', 52)}{arm('R', 168)}
    <g class="headWrap">{headA}</g>
  </g></g>'''

def figB():
    pants = '#8a6247'
    shin = lambda x: f'<path d="M{x-24},556 L{x+24},556 L{x+30},694 L{x-30},694 Z" fill="{pants}"/><path d="M{x-4},560 L{x-6},690" stroke="#7a553c" stroke-width="2"/>'
    shoe = lambda x, d: f'<path d="M{x-24},700 C{x-24},688 {x+22},688 {x+22+6*d},700 L{x+24+6*d},712 L{x-24},712 Z" fill="#5a3b28"/>'
    arm = lambda s, x: f'''<g class="arm{s}"><rect x="{x-9}" y="300" width="18" height="50" rx="9" fill="#efc4a8"/><ellipse cx="{x}" cy="272" rx="23" ry="46" fill="#f8f4ea" stroke="#ddd4c3" stroke-width="1.5"/><path d="M{x-18},300 Q{x},312 {x+18},300" fill="none" stroke="#e3dbc9" stroke-width="3"/>
      <g class="fore{s}"><rect x="{x-10}" y="336" width="20" height="108" rx="10" fill="#efc4a8"/><ellipse cx="{x}" cy="452" rx="11" ry="13" fill="#f3cdb3"/>
      {'<g class="prop mug"><path d="M'+str(x-15)+',432 L'+str(x+15)+',432 L'+str(x+13)+',462 Q'+str(x)+',468 '+str(x-13)+',462 Z" fill="#E3CCC1"/><path d="M'+str(x+14)+',438 q12,2 8,14 q-2,6 -9,6" fill="none" stroke="#E3CCC1" stroke-width="4"/><ellipse cx="'+str(x)+'" cy="432" rx="15" ry="4" fill="#8a5a3c"/><path class="steam" d="M'+str(x-4)+',424 q-5,-7 0,-14 q5,-7 0,-14" fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round"/></g>' if s=='R' else '<g class="prop map"><rect x="'+str(x-6)+'" y="410" width="46" height="36" fill="#F2EFEB" transform="rotate(-10 '+str(x)+' 440)"/><path d="M'+str(x)+',420 l12,8 l10,-6 l12,8" stroke="#A4B8B0" stroke-width="3" fill="none" transform="rotate(-10 '+str(x)+' 440)"/></g>'}
      </g></g>'''
    return f'''<g class="fig figB"><ellipse class="shadow" cx="110" cy="714" rx="78" ry="9" fill="#000" opacity=".13"/><g class="body">{backB}
    <g class="pack"><rect x="36" y="246" width="148" height="176" rx="26" fill="#9c6b45"/></g>
    {leg('L', 86, pants, 50, shin(86), shoe(86,-1))}
    {leg('R', 134, pants, 50, shin(134), shoe(134,1))}
    <path d="M48,428 L172,428 L178,478 L42,478 Z" fill="{pants}"/><rect x="48" y="426" width="124" height="10" fill="#6E5446"/>
    <path d="M96,164 L96,208 Q100,228 110,250 Q120,228 124,208 L124,164 Z" fill="#e8b99b"/>
    <path d="M98,206 Q110,228 122,206" fill="none" stroke="#d6b15e" stroke-width="1.2"/><circle cx="110" cy="221" r="2" fill="#d6b15e"/>
    <path d="M48,242 C52,222 76,212 92,206 L110,250 L128,206 C144,212 168,222 172,242 L166,330 C166,372 168,404 170,440 L50,440 C52,404 54,372 54,330 Z" fill="#f6f1e6" stroke="#ddd4c3" stroke-width="1.5"/>
    <path d="M60,300 q10,-3 20,0 t20,0 t20,0 t20,0 t20,0 M58,340 q10,-3 20,0 t20,0 t20,0 t20,0 t20,0 M58,380 q10,-3 20,0 t20,0 t20,0 t20,0 t20,0" fill="none" stroke="#e3dbc9" stroke-width="1.3"/>
    <path d="M48,242 C52,222 76,212 92,206 L110,250 L128,206 C144,212 168,222 172,242 L166,330 C166,372 168,404 170,440 L50,440 C52,404 54,372 54,330 Z" fill="url(#shadeTorso)"/>
    <g class="pack"><path d="M72,214 C66,280 64,340 66,410 M148,214 C154,280 156,340 154,410" stroke="#7d5234" stroke-width="10" fill="none" stroke-linecap="round"/></g>
    {arm('L', 50)}{arm('R', 170)}
    <g class="headWrap">{headB}</g>
  </g></g>'''

(src / 'figura-A.svg').write_text(figA()); (src / 'figura-B.svg').write_text(figB())
print('ok')
