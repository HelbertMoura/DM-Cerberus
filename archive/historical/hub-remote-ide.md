---
titulo: Hub Remoto de IDEs — Histórico (descontinuado)
tags: [archive, historical, hub-remote-ide, descontinuado, superseded]
atualizado: 2026-08-26
status: historical
---

# 🛰️ Hub Remoto de IDEs — Histórico (descontinuado em 23/08/2026)

> **Status:** **HISTORICAL** — projeto descontinuado pelo PO em 23/08/2026 conforme registro em `HANDOVER.md` (entrada `[2026-08-23 17:50] Gemini ➔ Helbert`).
> **Diretrizes:** este arquivo usa **apenas fatos já documentados** no DM-CEREBRO e em `HANDOVER.md`. Nenhum conteúdo inventado.
> **Conteúdo residual:** `projects/hub-remote-ide/mockup/` permanece no disco (não-deletado, conforme política de não-destruição sem aprovação do PO).

---

## 1. Identidade e Finalidade (fatos documentados)

- **Slug:** `hub-remote-ide` (legado).
- **Função:** central operacional de orquestração das 3 Desktop IDEs de IA da Dev Maniac's para qualquer projeto (conforme `HANDOVER.md` 2026-08-23 17:45).
- **Stack registrada (no `HANDOVER.md`):** Antigravity 2.0 (Gemini 3.7 Flash High) + MiniMax Code (M3) + Z.AI ZCode (Hermes GLM-5.3) + VSCode Web com SSO via `dm_sso`.
- **Hospedagem:** Rocky Linux 10.2 (`192.168.226.103`) com túneis Cloudflare `dm-hub` e `dm-code` (registrados em `HANDOVER.md` 2026-08-23 17:50).

## 2. Eventos Documentados (linha do tempo factual)

- **2026-08-23 08:30** — SSO Hub ↔ code-server; cookie `dm_sso` HMAC; `forward_auth` via `hub-auth` container (HANDOVER.md 2026-08-23 08:30).
- **2026-08-23 08:45** — Auditoria UI/UX + mobile + PWA; assets 404 corrigidos via rota `/assets/*`; fontes Inter + JetBrains Mono; Service Worker v2; LEARN-006 registrada (HANDOVER.md 2026-08-23 08:45).
- **2026-08-23 09:10** — Auditoria continuou; login v1.3 (console Dev Maniac's) + fix de cache Cloudflare no `sw.js`; SW bump `dm-hub-v4` (HANDOVER.md 2026-08-23 09:10).
- **2026-08-23 09:30** — Login Google-only; cache-buster `?v=2026-08-23` + purge total do cache Cloudflare; allowlist por e-mail (HANDOVER.md 2026-08-23 09:30).
- **2026-08-23 10:15** — Z.AI Hermes redesenha login v1.3; fix sw.js cache; `15095de` e `7806502` (HANDOVER.md 2026-08-23 10:15).
- **2026-08-23 11:20** — Retrabalho do zero da tela de login (CSS isolado `login.css` v2.1); LEARN-008 + ADR-011 (HANDOVER.md 2026-08-23 11:20).
- **2026-08-23 17:25** — Auth local email+senha+2FA TOTP (PHP + SQLite); ADR-012; LEARN-010/011; commits `f40b1bd` (HANDOVER.md 2026-08-23 17:25).
- **2026-08-23 17:30** — Reconstrução 100% do Hub Remoto v3.0 (5 workspaces, `hub.css` isolado, `hub.js`); ADR-013 refinada; LEARN-012 (HANDOVER.md 2026-08-23 17:30).
- **2026-08-23 17:45** — Refinamento do Hub v3.0; avatar oficial integrado; rodapé harmonizado; fix "CMD piscando" (VBS silencioso); qr-test.svg removido (HANDOVER.md 2026-08-23 17:45).
- **2026-08-23 17:50** — **Descomissionamento total**: túneis `dm-hub` e `dm-code` excluídos do Cloudflare; processos `php.exe` e `cloudflared` encerrados; tarefa agendada `DM Hub Watchdog` removida; `projects/hub-remote-ide/` marcada para remoção (HANDOVER.md 2026-08-23 17:50). Túnel principal corporativo (`devmaniacs-tunnel`), SSH (`devmaniacs-vm-ssh`), Biolar, Teenus e HelpDev **continuam** 100% ativos e intocados.
- **2026-08-26** — `proposed-migration.md` propõe mover o conteúdo histórico para `archive/historical/hub-remote-ide/`. **Conteúdo residual** `mockup/` ainda existe em `projects/hub-remote-ide/mockup/`. **Esta entrada** documenta o que é fato (de `HANDOVER.md`) sem inventar detalhes.

## 3. O que NÃO está documentado (UNKNOWN — Needs PO)

- A relação exata entre `hub-remote-ide` (descontinuado) e o suposto `dm-desk` (registrado como `UNKNOWN` em `projects/dm-desk/index.md`). Pode ser sucessor, rebranding, ou sem relação.
- Status atual de `mockup/` (deve ser removido? mantido como referência?). **Não** deletar sem aprovação do PO (política de não-destruição).
- Detalhes de implementação pós-descontinuamento que podem ter ficado em outros lugares (wiki/, prompts/, _shared/).
- Quem era o owner técnico além do Helbert (não documentado no DM-CEREBRO).

## 4. Cross-references

- `HANDOVER.md` (raiz) — entrada `[2026-08-23 17:50] Gemini ➔ Helbert` registra o descomissionamento e o estado dos túneis Cloudflare.
- `proposed-migration.md` §2.3 — proposta de mover `projects/hub-remote-ide/` para `archive/historical/hub-remote-ide/` (pendente gate do PO).
- `LEARNINGS.md` — LEARN-006 a LEARN-012 foram registradas durante a vida do projeto.
- `git log` — commits `15095de`, `7806502`, `f40b1bd`, e o commit de descomissionamento `05fd128` (visíveis no log do repositório).

## 5. Política de Conteúdo Residual

- O diretório `projects/hub-remote-ide/mockup/` **permanece no disco** e **NÃO** deve ser deletado por esta task.
- Movimentos destrutivos exigem gate do PO (ver `proposed-migration.md` §2.3).
- Este stub é um **placeholder** para que referências futuras (cross-references em `HANDOVER.md`, `LEARNINGS.md`, ADRs) tenham onde apontar.

---

**Última atualização:** 26 de Agosto de 2026 · **Status:** HISTORICAL · **Owner:** Helbert Moura — Dev Maniac's Systems
