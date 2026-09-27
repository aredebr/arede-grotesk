"""Generates documentation/specimen.html (self-contained, fonts embedded) from the built fonts,
plus specimen.png (README cover) and social-preview.png (1280x640) when Playwright is available."""
import base64, json, os, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / 'documentation'
WOFF2 = ROOT / 'fonts/webfonts/AredeGrotesk-Regular.woff2'
LOGO = ROOT / 'sources/logo/arede-wordmark-letters.json'


def b64(p):
    return base64.b64encode(Path(p).read_bytes()).decode()


arede = b64(WOFF2)
logo = json.loads(LOGO.read_text())
paths = ''.join(f'<path d="{logo[k]}"/>' for k in ['a', 'r', 'e1', 'd', 'e2'])
logo_svg = f'<svg viewBox="392 200 388 108" xmlns="http://www.w3.org/2000/svg" fill="currentColor">{paths}</svg>'

NEW = set('aredbpqnmhuocfi')
SHIFT = set('kljAMNVW')


def colorize(s):
    out = []
    for ch in s:
        cls = 'new' if ch in NEW else ('shift' if ch in SHIFT else 'old')
        out.append(f'<span class="{cls}">{ch}</span>')
    return ''.join(out)


html = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Arede Grotesk — specimen</title>
<meta name="description" content="Arede Grotesk, the typeface of the Arede brand. Free and open source under the SIL Open Font License.">
<style>
@font-face {{ font-family: "Arede Grotesk"; src: url(data:font/woff2;base64,{arede}) format("woff2"); font-weight: 600; }}
:root {{ --verde: #29553D; --verde2: #6A8D82; --bege: #F6EBDB; --terra: #8F5447; --laranja: #D67457; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: #fff; color: #111; font-family: "Arede Grotesk", "Space Grotesk", sans-serif; }}
.pg {{ padding: 48px 56px; max-width: 1400px; margin: 0 auto; }}
h1 {{ font-size: 22px; font-weight: 600; margin: 0 0 6px; color: #666; }}
h1 a {{ color: var(--verde); text-decoration: none; }}
.sec {{ margin-top: 34px; border-top: 1px solid #e5e5e5; padding-top: 18px; }}
.lbl {{ font-size: 15px; color: #888; margin-bottom: 10px; }}
.big {{ font-size: clamp(90px, 14vw, 200px); line-height: 1; }}
.row {{ display: flex; gap: 60px; align-items: baseline; flex-wrap: wrap; }}
.logo {{ width: min(690px, 90vw); color: #111; display: inline-block; }}
.alpha {{ font-size: clamp(34px, 4.5vw, 64px); line-height: 1.25; }}
.new {{ color: var(--verde); }} .shift {{ color: var(--laranja); }} .old {{ color: #b5b5b5; }}
.legend span {{ display: inline-block; margin-right: 22px; font-size: 14px; }}
.legend i {{ display: inline-block; width: 12px; height: 12px; border-radius: 3px; margin-right: 6px; vertical-align: -1px; }}
.txt {{ font-size: clamp(24px, 2.9vw, 40px); line-height: 1.22; max-width: 1260px; }}
.txt.s {{ font-size: 22px; line-height: 1.4; max-width: 1100px; }}
.txt.m {{ font-size: 30px; line-height: 1.3; }}
.pitch {{ font-size: clamp(44px, 5.5vw, 76px); line-height: 1.05; }}
.n2 {{ font-size: clamp(70px, 10vw, 150px); line-height: 1; }}
.n2 .ss {{ font-feature-settings: "ss06"; }}
.dark {{ background: var(--verde); color: var(--bege); padding: 40px 56px; }}
.foot {{ font-size: 14px; color: #888; padding: 24px 56px 40px; }}
.foot a {{ color: var(--verde); }}
@media (max-width: 700px) {{ .pg, .dark, .foot {{ padding-left: 16px; padding-right: 16px; }} .txt.m {{ font-size: 22px; }} }}
</style></head><body>
<div class="pg">
<h1><a href="https://github.com/aredebr/arede-grotesk">Arede Grotesk</a> · version 1.1 · the typeface of the Arede brand, grown out of the arede wordmark and derived from Space Grotesk (OFL)</h1>

<div class="sec"><div class="lbl">1 · Wordmark (vector from the logo) vs. the word typed with the font</div>
<div class="row"><span class="logo">{logo_svg}</span><span class="big">arede</span></div></div>

<div class="sec"><div class="lbl">2 · State of the alphabet</div>
<div class="legend"><span><i style="background:var(--verde)"></i>taken from the wordmark (a r e d) or derived from it (b c f h i m n o p q u)</span><span><i style="background:var(--laranja)"></i>Space Grotesk, adjusted (k l j to the new ascender height; joints of A M N V W)</span><span><i style="background:#b5b5b5"></i>inherited from Space Grotesk</span></div>
<div class="alpha">{colorize("abcdefghijklm")}<br>{colorize("nopqrstuvwxyz")}<br>{colorize("ABCDEFGHIJKLM")}<br>{colorize("NOPQRSTUVWXYZ")}<br><span class="old">0123456789</span> <span class="new">áàâãç éêí óôõú</span></div></div>

<div class="sec"><div class="lbl">3 · The r and the n: the corner of the r becomes the arch of n, m, h, u · on the right, ss06 rounds the left corner too</div>
<div class="n2">rn m h u <span class="ss">n m h u</span></div></div>

<div class="sec"><div class="lbl">4 · Portuguese text — the language the typeface was made for</div>
<div class="pitch">A rede é nossa,<br>o sistema é seu.</div>
<div class="txt" style="margin-top:22px">Organização, ação, coração, mãe, pão, açaí, Belém, Pará, Amazônia, você, também, música, saúde, informação, país, ônibus, cêdilha, ünico, à noite.</div>
<div class="txt m" style="margin-top:18px">arede.me · arede.dev · onde a rede encontra a empresa · um método para quem produz cultura na Amazônia</div>
<div class="txt s" style="margin-top:18px">O arede.me é um framework de infraestrutura para implantar sistemas de clientes em VPS compartilhada. Cada cliente ganha um tenant próprio, com identidade, arquivos, financeiro e CRM, e a Ampli é a primeira cliente da rede. A fonte precisa funcionar em títulos, em botões e em parágrafos como este, sem perder a personalidade do r.</div></div>

<div class="sec"><div class="lbl">5 · English text</div>
<div class="txt m">The quick brown fox jumps over the lazy dog. Arede designs, builds and operates software systems and digital infrastructure for organizations. Flat terminals, squared bowls, and a hooked r.</div></div>
</div>
<div class="dark"><div class="pitch">arede<span style="color:var(--verde2)">.me</span> &nbsp; arede<span style="color:var(--laranja)">.dev</span></div></div>
<div class="foot">Arede Grotesk is free and open source under the <a href="https://openfontlicense.org">SIL Open Font License 1.1</a>. Derived from <a href="https://github.com/floriankarsten/space-grotesk">Space Grotesk</a> by Florian Karsten and Květoslav Bartoš. <a href="https://github.com/aredebr/arede-grotesk/releases/latest">Download</a> · <a href="https://github.com/aredebr/arede-grotesk">Source on GitHub</a></div>
</body></html>'''
(DOC / 'specimen.html').write_text(html, encoding='utf-8')
(DOC / 'index.html').write_text(html, encoding='utf-8')

social = f'''<!doctype html><html><head><meta charset="utf-8"><style>
@font-face {{ font-family: "Arede Grotesk"; src: url(data:font/woff2;base64,{arede}) format("woff2"); }}
body {{ margin:0; width:1280px; height:640px; background:#29553D; color:#F6EBDB; font-family:"Arede Grotesk",sans-serif; position:relative; overflow:hidden; }}
.w {{ position:absolute; left:80px; top:150px; font-size:300px; line-height:1; letter-spacing:-.01em; }}
.t {{ position:absolute; left:84px; top:470px; font-size:36px; }}
.s {{ position:absolute; left:84px; top:520px; font-size:26px; color:#6A8D82; }}
</style></head><body><div class="w">arede</div><div class="t">Arede Grotesk · free &amp; open source typeface</div><div class="s">SIL Open Font License · github.com/aredebr/arede-grotesk</div></body></html>'''
(DOC / '_social.html').write_text(social, encoding='utf-8')

if '--png' in sys.argv:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={'width': 1400, 'height': 900})
        pg.goto((DOC / 'specimen.html').as_uri()); pg.wait_for_timeout(800)
        pg.screenshot(path=str(DOC / 'specimen.png'), full_page=True)
        pg2 = b.new_page(viewport={'width': 1280, 'height': 640})
        pg2.goto((DOC / '_social.html').as_uri()); pg2.wait_for_timeout(600)
        pg2.screenshot(path=str(DOC / 'social-preview.png'))
        b.close()
os.remove(DOC / '_social.html')
print('specimen written')
