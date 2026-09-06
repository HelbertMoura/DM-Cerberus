/**
 * ════════════════════════════════════════════════════════════
 * saiforanocode · visual_audit.mjs
 * ════════════════════════════════════════════════════════════
 * Aplica os 30+ checks visuais da skill saiforanocode em 1 site
 * Gera screenshots desktop + mobile + relatório JSON com score
 *
 * Uso:
 *   node scripts/visual_audit.mjs <site-slug>
 *   URL=https://devmaniacs.com.br node scripts/visual_audit.mjs devmaniacs
 *
 * Requisitos:
 *   - node + playwright (`npm install playwright`)
 *   - Chrome for Testing OU Chromium do sistema
 *
 * Saída:
 *   /root/work/audit-visual/<site-slug>/
 *     ├─ report.json           ← score 0-100 + tells + métricas
 *     ├─ screenshots/
 *     │    ├─ desktop-viewport.png   ← 1280x800 above-the-fold
 *     │    ├─ desktop-full.png       ← full-page desktop
 *     │    ├─ mobile-viewport.png    ← 375x812 above-the-fold
 *     │    └─ mobile-full.png        ← full-page mobile
 *
 * Como adaptar:
 *   - Trocar CHROME_PATH se o binário estiver em outro lugar
 *   - Adicionar novos tells seguindo o padrão `{ id, severity, msg }`
 *   - Severities: 'high' (10pts), 'medium' (5pts), 'low' (2pts)
 *   - Score final = max(0, 100 - soma_das_penalidades)
 *   - Classificação: ≥80 IDENTIDADE_FORTE · 60-79 ACEITAVEL · <60 VIBECODED
 *
 * Origem: sessão 2026-09-02 (Sprint 2 da saiforanocode em 5 sites DevManiacs).
 * Migrado de /tmp/pw-audit/audit-visual.mjs para cá pra ser reutilizável.
 * ════════════════════════════════════════════════════════════
 */

import { chromium } from 'playwright';
import fs from 'node:fs';

const URL = process.env.URL || 'https://example.com';
const NAME = process.argv[2] || 'site';
const OUTDIR = `/root/work/audit-visual/${NAME}`;
fs.mkdirSync(OUTDIR, { recursive: true });
fs.mkdirSync(`${OUTDIR}/screenshots`, { recursive: true });

// Caminho do Chrome — ordem de fallback
const CHROME_CANDIDATES = [
  process.env.CHROME_PATH,
  '/root/.cache/ms-playwright/chromium_headless_shell-1234/chrome-headless-shell-linux64/chrome-headless-shell',
  '/root/.cache/ms-playwright/chromium-1234/chrome-linux/chrome',
  '/usr/bin/chromium-browser',
  '/usr/bin/chromium',
  '/usr/bin/google-chrome',
].filter(Boolean);

const CHROME_PATH = CHROME_CANDIDATES.find(p => fs.existsSync(p));

const log = (k, v) => console.log(`  ${k.padEnd(28, ' ')} ${v}`);
const hr = () => console.log('━'.repeat(72));

const browser = await chromium.launch({
  args: ['--no-sandbox', '--disable-dev-shm-usage'],
  ...(CHROME_PATH ? { executablePath: CHROME_PATH } : {}),
});

const context = await browser.newContext({
  viewport: { width: 1280, height: 800 },
  userAgent: 'Mozilla/5.0 (saiforanocode-audit/1.0; +https://devmaniacs.com.br)',
  locale: 'pt-BR',
});

const page = await context.newPage();
const consoleErrors = [];
const failedRequests = [];
const timing = { ttfb: null, domContentLoaded: null, load: null };

page.on('pageerror', e => console.error(`  pageerror: ${e.message}`));
page.on('console', m => { if (m.type() === 'error') consoleErrors.push(m.text()); });
page.on('requestfailed', r => failedRequests.push(`${r.method()} ${r.url()} ${r.failure()?.errorText}`));
page.on('response', r => {
  const s = r.status();
  if (s >= 400) failedRequests.push(`${s} ${r.url()}`);
});

// ─────────────────────────────────────────────────────────
// COLETA: visitar site desktop + mobile + extrair métricas
// ─────────────────────────────────────────────────────────
console.log('\n');
hr();
log('SITE', `${NAME} → ${URL}`);
hr();

const start = Date.now();
const resp = await page.goto(URL, { waitUntil: 'networkidle', timeout: 30000 });
timing.ttfb = resp ? resp.timingEnd?.() || Date.now() - start : null;
await page.waitForTimeout(2000);
const loadMs = Date.now() - start;

const perfTiming = await page.evaluate(() => {
  const t = performance.getEntriesByType('navigation')[0];
  return t ? { ttfb: t.responseStart - t.requestStart, domInteractive: t.domInteractive - t.startTime } : null;
});
if (perfTiming) timing.domContentLoaded = perfTiming.domInteractive;

// Screenshots desktop
await page.screenshot({ path: `${OUTDIR}/screenshots/desktop-viewport.png`, fullPage: false });
await page.screenshot({ path: `${OUTDIR}/screenshots/desktop-full.png`, fullPage: true });

// Screenshots mobile
await page.setViewportSize({ width: 375, height: 812 });
await page.waitForTimeout(500);
await page.screenshot({ path: `${OUTDIR}/screenshots/mobile-viewport.png`, fullPage: false });
await page.screenshot({ path: `${OUTDIR}/screenshots/mobile-full.png`, fullPage: true });

await page.setViewportSize({ width: 1280, height: 800 });

// ─────────────────────────────────────────────────────────
// EXTRAÇÃO: metadados + contagens
// ─────────────────────────────────────────────────────────
const meta = await page.evaluate(() => {
  const $ = s => document.querySelector(s);
  const $$ = s => Array.from(document.querySelectorAll(s));
  const headings = $$('h1, h2, h3, h4, h5, h6').map(h => ({
    level: h.tagName,
    text: h.textContent.trim().slice(0, 80),
  }));
  return {
    title: $('title')?.textContent?.trim() || null,
    description: $('meta[name="description"]')?.content || null,
    canonical: $('link[rel="canonical"]')?.href || null,
    ogImage: $('meta[property="og:image"]')?.content || null,
    jsonLdScripts: $$('script[type="application/ld+json"]').length,
    headings,
    h1Count: $$('h1').length,
    imgsTotal: $$('img').length,
    imgsNoAlt: $$('img').filter(i => !i.alt || i.alt.trim() === '').length,
    buttonsTotal: $$('button').length,
    buttonsNoLabel: $$('button').filter(b => !b.textContent.trim() && !b.getAttribute('aria-label')).length,
    linksEmpty: $$('a').filter(a => !a.textContent.trim() && !a.getAttribute('aria-label')).length,
    navCount: $$('nav').length,
    cards: $$('[class*="card"], [class*="Card"]').length,
    containers: $$('[class*="container"], [class*="Container"]').length,
    totalSvgs: $$('svg').length,
    bootstrapBtns: $$('.btn, .btn-primary, .btn-light, .btn-ghost').length,
    lucideIcons: $$('[class*="lucide"], [data-lucide]').length,
    bodyBg: getComputedStyle(document.body).backgroundColor,
    h1Font: $$('h1')[0] ? getComputedStyle($$('h1')[0]).fontFamily : null,
  };
});

// ─────────────────────────────────────────────────────────
// SCORE: penalidades por tell
// ─────────────────────────────────────────────────────────
const tells = [];

// AEO/GEO
if (meta.jsonLdScripts === 0) tells.push({ id: 'AEO-01', severity: 'high', msg: 'Zero JSON-LD (AEO/GEO perdido)' });
if (!meta.ogImage) tells.push({ id: 'AEO-02', severity: 'medium', msg: 'Sem og:image' });
else if (meta.ogImage.endsWith('.svg') || /logo|favicon/i.test(meta.ogImage)) {
  tells.push({ id: 'AEO-03', severity: 'high', msg: 'og:image aponta para LOGO (deveria ser social-card 1200x630)' });
}
if (!meta.canonical) tells.push({ id: 'AEO-04', severity: 'low', msg: 'Sem canonical link' });

// SEO
const descLen = meta.description?.length || 0;
if (descLen > 160) tells.push({ id: 'SE-04', severity: 'medium', msg: `Meta description com tamanho ${descLen} (ideal: 120-160 chars)` });
if (meta.h1Count === 0) tells.push({ id: 'SE-05', severity: 'high', msg: 'Zero <h1>' });
if (meta.h1Count > 1) tells.push({ id: 'SE-06', severity: 'medium', msg: `${meta.h1Count} <h1> (deveria ser exatamente 1)` });

// Acessibilidade
if (meta.imgsNoAlt > 0) tells.push({ id: 'A11Y-03', severity: 'medium', msg: `${meta.imgsNoAlt} imagens sem alt text` });
if (meta.linksEmpty > 0) tells.push({ id: 'A11Y-04', severity: 'medium', msg: `${meta.linksEmpty} links sem texto ou aria-label` });
if (meta.buttonsNoLabel > 0) tells.push({ id: 'A11Y-05', severity: 'medium', msg: `${meta.buttonsNoLabel} botões sem texto acessível` });

// Vibecoded
if (meta.cards > 100) tells.push({ id: 'GEN-02', severity: 'medium', msg: `${meta.cards} cards (verificar hierarquia e variação)` });
if (meta.bootstrapBtns > 0) tells.push({ id: 'BS-01', severity: 'medium', msg: `${meta.bootstrapBtns} classes .btn-* (Bootstrap ou pseudo-bootstrap — verificar se CDN real está carregado)` });
if (meta.lucideIcons > 50) tells.push({ id: 'LU-01', severity: 'low', msg: `${meta.lucideIcons} ícones Lucide (verificar uso crítico vs decorativo)` });

// JS / network
if (consoleErrors.length > 0) tells.push({ id: 'JS-01', severity: 'high', msg: `${consoleErrors.length} erros no console JS`, detail: consoleErrors.slice(0, 3) });
if (failedRequests.length > 0) tells.push({ id: 'NET-01', severity: 'medium', msg: `${failedRequests.length} requisições falharam (4xx/5xx)`, detail: failedRequests.slice(0, 3) });

// Tipografia
const onlyInter = meta.h1Font && /^"?Inter/i.test(meta.h1Font) && !/JetBrains|IBM Plex|Playfair|Fraunces|Space Grotesk/i.test(meta.h1Font);
if (onlyInter) tells.push({ id: 'TY-01', severity: 'medium', msg: `Tipografia única (só Inter) — falta serifa ou display de marca` });

// Landmarks ARIA
if (meta.navCount === 0) tells.push({ id: 'UX-01', severity: 'high', msg: 'Zero <nav> (faltam landmarks ARIA)' });

// Container semântico
if (meta.containers === 0) tells.push({ id: 'CSS-01', severity: 'low', msg: 'Zero .container detectados (sem estrutura semântica de grid)' });

// SVGs excessivos
if (meta.totalSvgs > 100) tells.push({ id: 'SVG-01', severity: 'low', msg: `${meta.totalSvgs} SVGs (pode ser ícones demais; verificar propósito)` });

// SCORE
const scoreWeights = { high: 10, medium: 5, low: 2 };
const scorePenalty = tells.reduce((acc, t) => acc + (scoreWeights[t.severity] || 0), 0);
const score = Math.max(0, 100 - scorePenalty);

const report = {
  meta: { site: NAME, url: URL, timestamp: new Date().toISOString(), loadMs },
  performance: timing,
  content: meta,
  tells,
  score,
  classification: score >= 80 ? 'IDENTIDADE_FORTE' : score >= 60 ? 'ACEITAVEL' : 'VIBECODED',
};

fs.writeFileSync(`${OUTDIR}/report.json`, JSON.stringify(report, null, 2));

await browser.close();

// ─────────────────────────────────────────────────────────
// RELATÓRIO
// ─────────────────────────────────────────────────────────
hr();
log('SCORE saiforanocode', `${score}/100 → ${report.classification}`);
log('Load time', `${loadMs}ms`);
if (perfTiming) log('TTFB', `${Math.round(perfTiming.ttfb)}ms`);
if (perfTiming) log('DOM Interactive', `${Math.round(perfTiming.domInteractive)}ms`);
log('h1 count', meta.h1Count);
log('headings', meta.headings.length);
log('imgs sem alt', `${meta.imgsNoAlt}/${meta.imgsTotal}`);
log('JSON-LD scripts', meta.jsonLdScripts);
log('console errors', consoleErrors.length);
log('failed requests', failedRequests.length);
hr();
log('TELLS DETECTADOS', tells.length);
log('  🔴 High: ' + tells.filter(t => t.severity === 'high').length,
  '  🟡 Medium: ' + tells.filter(t => t.severity === 'medium').length +
  '  🟢 Low: ' + tells.filter(t => t.severity === 'low').length);
console.log();
for (const t of tells) {
  const icon = t.severity === 'high' ? '🔴' : t.severity === 'medium' ? '🟡' : '🟢';
  console.log(`  ${icon} [${t.id}] ${t.msg}`);
}
hr();
log('Relatório JSON', `${OUTDIR}/report.json`);
log('Screenshots', `${OUTDIR}/screenshots/`);
hr();
