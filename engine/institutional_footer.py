"""Shared footer based on Dev Maniac's Systems open-source and institutional identity."""
from datetime import date
from html import escape
import json
from pathlib import Path

FOOTER_STYLE = """
.institutional-footer { width:100%; padding:28px 32px 20px; background:var(--bg-shell); border-top:1px solid var(--border-default); color:var(--text-muted); font-size:12px; }
.institutional-footer[data-surface="workspace"] { margin-left:224px; width:calc(100% - 224px); margin-top:auto; }
.footer-top { display:flex; align-items:center; gap:24px; flex-wrap:wrap; padding-bottom:24px; }
.footer-brand { display:flex; align-items:center; gap:12px; color:var(--text-primary); font-size:16px; font-weight:650; min-height:44px; text-decoration:none; }
.footer-brand svg { width:32px; height:32px; color:var(--action); }
.footer-tagline { margin:0; font-size:13px; color:var(--text-muted); }
.footer-contacts { display:flex; flex-wrap:wrap; gap:8px; margin-left:auto; }
.footer-contacts a { display:flex; align-items:center; gap:8px; min-height:44px; padding:0 12px; border:1px solid var(--border-strong); border-radius:5px; color:var(--text-secondary); font-size:12px; text-decoration:none; transition:border-color .15s, background .15s; }
.footer-contacts a:hover { color:var(--action); background:var(--bg-hover); border-color:var(--action); }
.footer-contacts svg { width:16px; height:16px; fill:none; stroke:currentColor; stroke-width:1.6; }
.footer-bottom { display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px 24px; padding-top:16px; border-top:1px solid var(--border-default); font-size:11px; line-height:1.8; }
.footer-legal-group, .footer-legal-nav { display:flex; align-items:center; flex-wrap:wrap; gap:4px 16px; }
.footer-bottom p { margin:0; }
.footer-legal-nav button { background:transparent; color:var(--action); border:0; padding:8px 0; min-height:44px; font:inherit; text-decoration:underline; text-underline-offset:4px; cursor:pointer; }
.footer-credit a { color:var(--action); text-decoration:underline; text-underline-offset:4px; }
.footer-document { color:var(--text-primary); background:var(--bg-panel); border:1px solid var(--border-strong); border-radius:10px; width:min(760px,calc(100vw - 32px)); max-height:85vh; padding:28px; }
.footer-document::backdrop { background:rgba(0,0,0,.65); }
.footer-document header { display:flex; justify-content:space-between; align-items:flex-start; gap:20px; }
.footer-document h2 { margin:0 0 16px; font-size:21px; }
.footer-document h3 { font-size:15px; margin-top:24px; color:var(--text-primary); }
.footer-document p, .footer-document li { font-size:13px; line-height:1.75; color:var(--text-secondary); }
.footer-document .legal-note { border-top:1px solid var(--border-default); padding-top:16px; color:var(--text-muted); font-size:12px; }
.footer-document button { min-height:44px; padding:0 12px; border:1px solid var(--border-strong); background:var(--bg-shell); color:var(--text-primary); font:inherit; cursor:pointer; }
.footer-document a { color:var(--action); text-decoration:underline; }
@media(max-width:1100px) { .institutional-footer[data-surface="workspace"] { margin-left:192px; width:calc(100% - 192px); } }
@media(max-width:719px) { .institutional-footer { padding:24px 16px; } .institutional-footer[data-surface="workspace"] { margin:0; width:100%; } .footer-top { gap:12px; } .footer-tagline { flex-basis:100%; } .footer-contacts { width:100%; margin-left:0; } .footer-contacts a { flex:1 1 auto; min-height:48px; } .footer-legal-nav button { min-height:48px; } .footer-document { padding:20px; } }
"""

def render_institutional_footer(surface='auth'):
    legal_path = Path(__file__).resolve().parents[1] / 'assets/institutional-legal.json'
    legal = json.loads(legal_path.read_text(encoding='utf-8'))
    dialogs = []
    for key in ('privacy', 'terms', 'lgpd'):
        doc = legal[key]
        sections = ''.join(f'<h3>{escape(x["heading"])}</h3><p>{escape(x["content"])}</p>' for x in doc.get('sections', []))
        if key == 'lgpd':
            sections += '<ul>' + ''.join(f'<li>{escape(x)}</li>' for x in doc['rights']) + '</ul>'
            sections += f'<p>{escape(doc["limitationNotice"])}</p><a href="mailto:{escape(doc["email"],quote=True)}">{escape(doc["cta"])}</a>'
        dialogs.append(f'''<dialog class="footer-document" id="footer-{key}" aria-labelledby="footer-{key}-title">
<header><h2 id="footer-{key}-title">{escape(doc['title'])}</h2><form method="dialog"><button type="submit" aria-label="Fechar documento">Fechar</button></form></header>
<p>{escape(doc['intro'])}</p>{sections}<p class="legal-note">{escape(legal['productNote'])}</p>
<a href="https://devmaniacs.com.br/" target="_blank" rel="noopener noreferrer">Dev Maniac's Systems</a></dialog>''')
    links = [
        ('GitHub', 'https://github.com/HelbertMoura/DM-Cerberus', '<path d="m8 6-6 6 6 6m8-12 6 6-6 6M14 4l-4 16"/>'),
        ('Website', 'https://devmaniacs.com.br/', '<circle cx="12" cy="12" r="9"/><path d="M3.6 9h16.8M3.6 15h16.8M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/>'),
        ('Apoiar', 'https://linktr.ee/helbertmoura', '<path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/>'),
        ('E-mail', 'mailto:contato@devmaniacs.com.br', '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 6 9 7 9-7"/>'),
    ]
    contacts = ''.join(f'<a href="{escape(url,quote=True)}"'+(' target="_blank" rel="noopener noreferrer"' if url.startswith('https:') else '')+f'><svg viewBox="0 0 24 24" aria-hidden="true">{icon}</svg>{label}</a>' for label,url,icon in links)
    controls = ''.join(f'<button type="button" onclick="document.getElementById(\'footer-{key}\').showModal()" aria-haspopup="dialog">{label}</button>' for key,label in [('privacy','Privacidade Local'),('terms','Licença MIT'),('lgpd','Soberania')])
    return f'''<footer class="institutional-footer" data-surface="{escape(surface,quote=True)}" aria-label="Dev Maniac's: contatos e informações institucionais">
<div class="footer-top"><a class="footer-brand" href="https://devmaniacs.com.br/" target="_blank" rel="noopener noreferrer">DEV MANIAC'S</a><p class="footer-tagline">Local-First Intelligence &middot; Tecnologia feita de perto.</p><nav class="footer-contacts" aria-label="Canais oficiais e comunidade">{contacts}</nav></div>
<div class="footer-bottom"><div class="footer-legal-group"><p>© {date.today().year} Dev Maniac's Systems &middot; Licença MIT</p><nav class="footer-legal-nav" aria-label="Documentos open source">{controls}</nav></div><p class="footer-credit">Desenvolvido à base de ☕ e ⚡ &middot; <a href="https://linktr.ee/helbertmoura" target="_blank" rel="noopener noreferrer">Redes e contatos</a></p></div>
{''.join(dialogs)}</footer>'''
