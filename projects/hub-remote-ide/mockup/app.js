/**
 * Dev Maniac's Hub — Mockup
 * Interações JS demo
 */

(function () {
  'use strict';

  /* ============================================================
     LOGIN
     ============================================================ */
  const loginForm = document.getElementById('loginForm');
  if (loginForm) {
    const submitBtn = document.getElementById('submitBtn');
    const totpStep = document.getElementById('totpStep');
    const totpInput = document.getElementById('totp');
    const submitLabel = submitBtn.querySelector('span');
    const togglePassword = document.getElementById('togglePassword');
    const passwordInput = document.getElementById('password');

    // Toggle visibilidade senha
    if (togglePassword && passwordInput) {
      togglePassword.addEventListener('click', () => {
        const isPassword = passwordInput.type === 'password';
        passwordInput.type = isPassword ? 'text' : 'password';
        togglePassword.setAttribute('aria-label', isPassword ? 'Ocultar senha' : 'Mostrar senha');
      });
    }

    // Submit fake (2 steps)
    loginForm.addEventListener('submit', (e) => {
      e.preventDefault();

      if (totpStep.classList.contains('hidden')) {
        // Step 1: pedir senha
        submitLabel.textContent = 'Verificando...';
        submitBtn.disabled = true;
        setTimeout(() => {
          totpStep.classList.remove('hidden');
          submitLabel.textContent = 'Validar';
          submitBtn.disabled = false;
          totpInput.focus();
        }, 700);
      } else {
        // Step 2: validar TOTP
        submitLabel.textContent = 'Autenticando...';
        submitBtn.disabled = true;
        setTimeout(() => {
          window.location.href = '/hub.html';
        }, 900);
      }
    });

    // Auto-submit quando TOTP completa 6 dígitos
    if (totpInput) {
      totpInput.addEventListener('input', (e) => {
        const value = e.target.value.replace(/\D/g, '').slice(0, 6);
        e.target.value = value;
        if (value.length === 6) {
          loginForm.requestSubmit();
        }
      });
    }
  }

  /* ============================================================
     DASHBOARD
     ============================================================ */
  if (!document.body.classList.contains('dashboard-page')) return;

  // Conectar IDEs (mock)
  document.querySelectorAll('[data-ide]').forEach((btn) => {
    btn.addEventListener('click', () => {
      const ide = btn.getAttribute('data-ide');
      const card = btn.closest('.ide-card');
      const name = card?.querySelector('.ide-name')?.textContent || ide;

      btn.disabled = true;
      btn.innerHTML = `
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="animation: spin 1s linear infinite;" aria-hidden="true">
          <line x1="12" y1="2" x2="12" y2="6"></line>
          <line x1="12" y1="18" x2="12" y2="22"></line>
          <line x1="4.93" y1="4.93" x2="7.76" y2="7.76"></line>
          <line x1="16.24" y1="16.24" x2="19.07" y2="19.07"></line>
          <line x1="2" y1="12" x2="6" y2="12"></line>
          <line x1="18" y1="12" x2="22" y2="12"></line>
        </svg>
        Conectando
      `;

      setTimeout(() => {
        alert(`Conectando ao ${name}...\n\nNa versão real:\n- iframe com sessão autenticada\n- WebSocket para clipboard + arquivos\n- 2FA context-aware para ações sensíveis`);
        btn.disabled = false;
        btn.innerHTML = `
          Conectar
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <polyline points="9 18 15 12 9 6"></polyline>
          </svg>
        `;
      }, 1500);
    });
  });

  // Bottom nav active state
  document.querySelectorAll('.bottom-link').forEach((link) => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      document.querySelectorAll('.bottom-link').forEach((l) => l.classList.remove('is-active'));
      link.classList.add('is-active');
    });
  });

  // Inject spin keyframes
  const style = document.createElement('style');
  style.textContent = '@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }';
  document.head.appendChild(style);

  // PWA install prompt (futuro)
  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    // console.log('PWA disponível para instalação');
  });
})();
