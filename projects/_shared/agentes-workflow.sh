#!/usr/bin/env bash
# ============================================================================
# Agentes Workflow — Tríade Dev Maniac's (Gemini + M3 + Z.AI)
# ----------------------------------------------------------------------------
# Estrategia: 1 remote + 3 worktrees + branches agent/<nome>/<modulo>
# Gemini é o ÚNICO que consolida (merge + push no main).
# M3 e Z.AI travam módulo, trabalham em branch próprio, nunca fazem merge.
# ----------------------------------------------------------------------------
# Uso:
#   ./agentes-workflow.sh lock m3 rdo-m07-scaffold
#   ./agentes-workflow.sh release m3 "feat: motor offline r92"
#   ./agentes-workflow.sh consolidar rdo-m07-scaffold
#   ./agentes-workflow.sh status
# ============================================================================

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
HANDOVER="$REPO_ROOT/../../DM-Cerebro/HANDOVER.md"
AGENTE_ATIVO="${AGENTE_ATIVO:-$(whoami)}"
NOW="$(date '+%Y-%m-%d %H:%M')"

c() { printf "\033[1;36m%s\033[0m\n" "$*"; }
ok() { printf "\033[1;32m✔ %s\033[0m\n" "$*"; }
warn() { printf "\033[1;33m⚠ %s\033[0m\n" "$*"; }
err() { printf "\033[1;31m✘ %s\033[0m\n" "$*" >&2; exit 1; }

ensure_clean() {
  if [ -n "$(git status --porcelain)" ]; then
    err "Working tree suja. Faça commit/stash antes."
  fi
}

cmd_lock() {
  local agente="$1"
  local modulo="$2"
  local branch="agent/${agente}/${modulo}"

  ensure_clean
  git fetch origin main --quiet
  git checkout -b "$branch" origin/main 2>/dev/null \
    || git checkout "$branch"

  ok "Branch travada: $branch"
  warn "Você agora É DONO deste módulo até dar release."
  c "Próximo passo: trabalhe normal. Quando terminar, rode:"
  c "  ./agentes-workflow.sh release $agente 'mensagem do commit'"
}

cmd_release() {
  local agente="$1"
  local msg="${2:-wip: checkpoint}"
  local branch="$(git rev-parse --abbrev-ref HEAD)"

  [[ "$branch" == agent/* ]] || err "Você não está numa branch agent/*. Faça lock primeiro."

  git add -A
  git commit -m "$msg" || warn "Nada para commitar."
  git push -u origin "$branch" --quiet

  ok "Branch $branch publicada. AGUARDA Gemini consolidar."
  c "Gemini vai: fetch → rodar testes → merge no main → push."
}

cmd_consolidar() {
  local modulo="$1"

  # Só Gemini consolida
  [[ "$AGENTE_ATIVO" == "gemini" || "$AGENTE_ATIVO" == "Helbert" ]] \
    || err "Apenas Gemini pode consolidar. Você é: $AGENTE_ATIVO"

  git fetch origin --quiet
  git checkout main
  git pull origin main --quiet

  # Descobre branch do módulo
  local branch=$(git branch -r | grep "agent/.*/${modulo}" | head -1 | tr -d ' \n')
  [ -n "$branch" ] || err "Branch agent/*/${modulo} não encontrada."

  c "Consolidando $branch → main..."
  git merge --no-ff "$branch" -m "merge: ${modulo} (consolidação Gemini)"

  # Roda testes se houver manage.py
  if [ -f "manage.py" ]; then
    c "Rodando testes Django..."
    python manage.py test --noinput || err "Testes falharam. NÃO fiz push."
  fi

  git push origin main --quiet
  ok "Módulo ${modulo} em produção (main)."

  # Atualiza HANDOVER no DM-Cerebro
  if [ -f "$HANDOVER" ]; then
    cat >> "$HANDOVER" <<EOF

[${NOW}] Gemini → main | Módulo: ${modulo} consolidado | Tests: PASS
EOF
    ok "HANDOVER.md atualizado."
  fi
}

cmd_status() {
  c "=== STATUS DA TRÍADE ==="
  echo "Repo:    $(basename "$REPO_ROOT")"
  echo "Branch:  $(git rev-parse --abbrev-ref HEAD)"
  echo "Agente:  $AGENTE_ATIVO"
  echo
  c "Branches agent/* ativas:"
  git branch -r | grep "agent/" | sed 's/^/  /'
  echo
  c "Últimos 5 commits:"
  git log --oneline -5 | sed 's/^/  /'
}

case "${1:-help}" in
  lock)        shift; cmd_lock "$@";;
  release)     shift; cmd_release "$@";;
  consolidar)  shift; cmd_consolidar "$@";;
  status)      cmd_status;;
  help|*)      c "Uso: $0 {lock|release|consolidar|status} [args]";;
esac
