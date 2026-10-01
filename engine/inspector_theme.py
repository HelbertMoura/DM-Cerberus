"""Graphite Inspector layout; shared login and application visual tokens."""

WORKSPACE_STYLE = r"""
  body { background:var(--bg-canvas); }
  #app-header { margin-left:224px; padding:0 32px; background:var(--bg-canvas); }
  #app-header .brand-text small { text-transform:none; letter-spacing:0; }
  #app-header .brand-text h1 { font-size:15px; font-weight:600; }
  #primary-tabs { position:fixed; inset:0 auto 0 0; width:224px; height:100vh;
    display:flex; flex-direction:column; align-items:stretch; gap:6px; padding:28px 16px;
    background:var(--bg-shell); border-right:1px solid var(--border-subtle); border-bottom:0; z-index:60; }
  .sidebar-brand { display:flex; align-items:center; gap:10px; padding:0 10px 30px;
    font-weight:650; font-size:18px; letter-spacing:-.04em; }
  .brand-mark { display:inline-grid; place-items:center; width:32px; height:32px;
    border:1px solid var(--action); border-radius:6px; color:var(--action); font-family:var(--font-mono); font-size:17px; }
  .nav-caption { padding:8px 12px; color:var(--text-muted); font-size:11px; letter-spacing:.1em; text-transform:uppercase; }
  #primary-tabs button[role="tab"] { flex:none; width:100%; height:48px !important; min-height:48px; display:flex;
    align-items:center; gap:12px; padding:0 12px; border:1px solid transparent;
    border-radius:6px; color:var(--text-muted); text-align:left; background:transparent; font-size:13px; }
  #primary-tabs button[aria-selected="true"] { background:var(--bg-selected); color:var(--text-primary); border-color:var(--border-subtle); }
  #primary-tabs button[role="tab"]::after { display:none; }
  .nav-icon { width:18px; height:18px; flex:none; stroke:currentColor; stroke-width:1.5; fill:none; }
  .sidebar-foot { margin-top:auto; padding:16px 12px 0; border-top:1px solid var(--border-subtle); font-size:12px; color:var(--text-muted); }
  .sidebar-foot strong { display:block; color:var(--text-secondary); font-weight:500; margin-bottom:5px; }
  #evidence-rail { margin-left:224px; padding:12px 32px; background:var(--bg-canvas); min-height:44px; }
  #workspace { width:calc(100% - 224px); margin-left:224px; padding:32px; max-width:1800px; }
  .panel-heading { padding:0 0 24px; border-bottom:0; margin-bottom:0; align-items:flex-start; }
  .panel-heading h1 { font-size:26px; font-weight:600; letter-spacing:-.035em; }
  .spotlight { max-width:none; border-radius:8px; box-shadow:none; background:var(--bg-panel); border-color:var(--border-default); }
  input, select, textarea { border-color:var(--border-default) !important; }
  input:focus, select:focus, textarea:focus { border-color:var(--action) !important; outline:none; }
  .data-panel, .data-pane, #search-results-pane, #search-preview-pane { background:var(--bg-panel); box-shadow:none; }
  .cockpit-hero-grid { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:0;
    border:1px solid var(--border-default); border-radius:8px; margin:24px 0; overflow:hidden; background:var(--bg-panel); }
  .cockpit-card, .cockpit-card.highlight, .cockpit-card.accent, .cockpit-card.success {
    border:0; border-right:1px solid var(--border-default); border-radius:0; padding:22px 24px; background:transparent; box-shadow:none; }
  .cockpit-card:last-child { border-right:0; }
  .cockpit-card .lbl { font-size:12px; text-transform:none; letter-spacing:0; color:var(--text-muted); }
  .cockpit-card .val { font-size:30px; font-weight:550; letter-spacing:-.035em; font-family:var(--font-body); font-variant-numeric:tabular-nums; }
  .cockpit-card .sub { font-size:11px; line-height:1.6; }
  .cockpit-columns { gap:24px; margin-bottom:24px; }
  .data-panel { border-radius:8px; padding:20px; border:1px solid var(--border-default); }
  .data-panel h2 { font-size:14px; font-weight:600; padding:0 0 16px; }
  .cockpit-tag-grid { display:flex; flex-direction:column; gap:0; }
  .cockpit-tag-item { display:flex; align-items:center; justify-content:space-between; gap:16px;
    padding:12px 0; background:transparent; border:0; border-radius:0; border-top:1px solid var(--border-subtle); font-size:12px; }
  .breakdown-table { width:100%; font-size:12px; font-variant-numeric:tabular-nums; }
  .breakdown-table th { font-size:11px; text-transform:none; background:var(--bg-shell); font-weight:500; }
  .breakdown-table th, .breakdown-table td { padding:13px 12px; border-bottom:1px solid var(--border-subtle); }
  .breakdown-table tbody tr:hover { background:var(--bg-hover); }
  .metrics-toolbar { display:flex; flex-wrap:wrap; align-items:center; gap:10px; }
  .metrics-toolbar select { min-height:44px; background:var(--bg-panel); border:1px solid var(--border-default); border-radius:6px; padding:0 12px; }
  .telemetry-note { color:var(--text-muted); font-size:12px; padding:14px 0; margin:0; }
  #cockpit-message { color:var(--text-secondary); }
  .empty-notice { padding:20px 0; font-size:12px; color:var(--text-muted); }
  #profile-avatar { background:var(--bg-selected); color:var(--action); }
  .settings-nav:empty { display:none; }
  .settings-layout { display:block; }
  button, .btn { min-height:44px; }
  .btn.primary, #search-btn { background:var(--action); color:#FFFFFF; border-color:var(--action); }
  .btn.danger { color:#261413; }
  @media(max-width:1100px) {
    #primary-tabs { width:192px; padding:24px 10px; }
    #app-header, #evidence-rail { margin-left:192px; padding-left:24px; padding-right:24px; }
    #workspace { margin-left:192px; width:calc(100% - 192px); padding:24px; }
    .cockpit-hero-grid { grid-template-columns:repeat(2,minmax(0,1fr)); }
    .cockpit-card:nth-child(2) { border-right:0; }
    .cockpit-card:nth-child(-n+2) { border-bottom:1px solid var(--border-default); }
  }
  @media(max-width:719px) {
    #app-header { margin:0; height:64px; padding:0 16px; }
    #app-header .brand svg, #profile-avatar, #app-header .brand-text small { display:none; }
    #primary-tabs { position:sticky; top:64px; width:100%; height:auto; flex-direction:row;
      overflow-x:auto; padding:8px; border-right:0; border-bottom:1px solid var(--border-default); gap:4px; }
    #primary-tabs button[role="tab"] { width:auto; min-width:max-content; min-height:48px; padding:0 12px; font-size:12px; }
    .sidebar-brand, .nav-caption, .sidebar-foot, .nav-icon { display:none; }
    #evidence-rail { margin:0; padding:12px 16px; flex-wrap:wrap; }
    #workspace { margin:0; width:100%; padding:24px 16px; }
    .panel-heading { flex-wrap:wrap; gap:16px; }
    .cockpit-card { padding:18px 14px; }
    .cockpit-card .val { font-size:25px; }
    .cockpit-columns { grid-template-columns:minmax(0,1fr); }
    .data-panel { padding:16px; min-width:0; }
    .metrics-toolbar { width:100%; }
  }
"""

AUTH_STYLE = r"""
body { background:var(--bg-canvas); }
.auth-wrapper { max-width:1100px; width:100%; display:grid; grid-template-columns:1fr 1fr; gap:80px; align-items:center; padding:48px; }
.auth-story { align-self:stretch; display:flex; flex-direction:column; justify-content:center; padding:24px 0; }
.auth-story .sidebar-brand { display:flex; align-items:center; font-size:20px; font-weight:700; letter-spacing:0.04em; padding:0; margin-bottom:64px; }
.auth-wrapper:not(:has(.auth-story)) { display:flex; flex-direction:column; gap:24px; max-width:640px; }
.auth-story h2 { font-family:var(--font-display); font-size:42px; line-height:1.12; font-weight:550; letter-spacing:-.04em; margin:0 0 20px; }
.auth-story p { color:var(--text-muted); font-size:15px; line-height:1.7; max-width:370px; }
.auth-story ul { list-style:none; padding:28px 0 0; margin:20px 0 0; border-top:1px solid var(--border-default); }
.auth-story li { margin-bottom:18px; font-size:13px; color:var(--text-secondary); }
.auth-story li span { color:var(--action); margin-right:12px; font-family:var(--font-mono); font-weight:600; }
.card { background:var(--bg-panel); border:1px solid var(--border-default); border-radius:10px; width:100%; max-width:none; padding:36px; box-shadow:none; }
.brand-header { text-align:left; margin-bottom:24px; }
.brand-title { font-size:24px; letter-spacing:-.03em; font-weight:650; margin:0 0 6px; }
.card-subtitle { text-align:left; font-size:13px; margin:0; color:var(--text-muted); }
.field > span { text-transform:none; letter-spacing:0; color:var(--text-secondary); font-size:13px; }
.field input { min-height:48px; border-radius:6px; background:var(--bg-input); border-color:#707D72; }
.btn-dm { min-height:48px; color:#FFFFFF; background:var(--action); border:1px solid var(--action); font-weight:650; border-radius:6px; }
.btn-dm:hover { background:var(--action-hover); border-color:var(--action-hover); }
.btn-dm:active { background:var(--action-pressed); border-color:var(--action-pressed); }
.password-wrap { position:relative; }
.password-wrap input { padding-right:84px; }
.password-toggle { position:absolute; right:6px; top:2px; min-height:44px; background:transparent; border:0; color:var(--text-muted); cursor:pointer; padding:0 10px; font-size:12px; }
.login-help { margin:20px 0 0; padding-top:16px; border-top:1px solid var(--border-subtle); color:var(--text-muted); font-size:12px; line-height:1.6; }
.login-help code { display:inline-block; background:var(--bg-input); border:1px solid var(--border-default); padding:2px 6px; border-radius:4px; color:var(--text-primary); font-family:var(--font-mono); font-size:11px; margin:2px 0; }
.auth-footer { grid-column:1/-1; margin-top:0; padding-top:0; text-align:center; font-size:11px; }
.auth-footer-links { display:none; }
:focus-visible { outline:2px solid var(--action); outline-offset:3px; }
@media(max-width:800px) { .auth-wrapper { grid-template-columns:minmax(0,1fr); padding:24px; gap:24px; max-width:480px; } .auth-story { padding:0; } .auth-story .sidebar-brand { margin-bottom:0; } .auth-story h2, .auth-story p, .auth-story ul { display:none; } .card { padding:28px 24px; } }
@media(prefers-reduced-motion:reduce) { *,*::before,*::after { animation:none!important; transition:none!important; } }
"""

from engine.institutional_footer import FOOTER_STYLE
WORKSPACE_STYLE += FOOTER_STYLE
AUTH_STYLE += """
body { display:flex; flex-direction:column; align-items:stretch; justify-content:flex-start; min-height:100vh; padding:0; }
.auth-wrapper { margin:auto; flex:1; }
""" + FOOTER_STYLE

AUTH_STORY = """<aside class="auth-story" aria-label="Sobre o Cerberus">
<div class="sidebar-brand">
  <a href="https://devmaniacs.com.br/" target="_blank" rel="noopener noreferrer" style="text-decoration:none;color:var(--text-primary);letter-spacing:0.04em;">
    <span style="font-weight:750;font-family:var(--font-display);font-size:20px;">DEV MANIAC'S</span>
  </a>
</div>
<h2>Memória Soberana.<br>Inteligência Contínua.</h2>
<p>O cérebro unificado de memória local para agentes de IA e desenvolvedores. Zero telemetria, 100% privado, sem dependência de nuvens externas.</p>
<ul>
  <li><span>01</span> <strong>Context Pack:</strong> Arquitetura e decisões entregues aos agentes</li>
  <li><span>02</span> <strong>Inbox Seguro:</strong> Triagem e validação humana de aprendizados</li>
  <li><span>03</span> <strong>Cockpit Pro 5x:</strong> Telemetria de tokens e controle anti-loop em tempo real</li>
</ul>
</aside>"""
