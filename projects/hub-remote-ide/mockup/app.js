/**
 * Dev Maniac's Hub — Mockup
 * JavaScript pra demo (login + 2FA fake + dashboard fake)
 */

// ============================================
// LOGIN
// ============================================
(function initLogin() {
  const form = document.getElementById('loginForm');
  if (!form) return;

  const tfaGroup = document.getElementById('tfaGroup');
  const totpInput = document.getElementById('totp');
  const submitBtn = form.querySelector('.btn-primary span');

  // Toggle password
  const toggleBtn = form.querySelector('.toggle-password');
  const passwordInput = document.getElementById('password');
  if (toggleBtn && passwordInput) {
    toggleBtn.addEventListener('click', () => {
      const isPassword = passwordInput.type === 'password';
      passwordInput.type = isPassword ? 'text' : 'password';
      toggleBtn.setAttribute('aria-label', isPassword ? 'Ocultar senha' : 'Mostrar senha');
    });
  }

  // Submit fake
  form.addEventListener('submit', (e) => {
    e.preventDefault();

    if (tfaGroup.classList.contains('hidden')) {
      // Simula request de 2FA
      submitBtn.textContent = 'Verificando...';
      setTimeout(() => {
        tfaGroup.classList.remove('hidden');
        submitBtn.textContent = 'Validar 2FA';
        totpInput?.focus();
      }, 800);
    } else {
      // Simula login completo
      submitBtn.textContent = 'Autenticando...';
      setTimeout(() => {
        window.location.href = 'dashboard.html';
      }, 1000);
    }
  });

  // Auto-advance 2FA (6 dígitos)
  if (totpInput) {
    totpInput.addEventListener('input', (e) => {
      const value = e.target.value.replace(/\D/g, '').slice(0, 6);
      e.target.value = value;
      if (value.length === 6) {
        form.requestSubmit();
      }
    });
  }
})();

// ============================================
// DASHBOARD
// ============================================
(function initDashboard() {
  if (!document.querySelector('.dashboard-page')) return;

  // Simula heartbeat (status dos IDEs)
  setInterval(() => {
    // Aqui entraria fetch('/api/ides/status') — mock só pra demo
  }, 30000);

  // Conectar IDE (mock)
  document.querySelectorAll('.btn-card-primary:not(:disabled)').forEach(btn => {
    btn.addEventListener('click', () => {
      const card = btn.closest('.ide-card');
      const name = card?.querySelector('.ide-name')?.textContent || 'IDE';
      btn.innerHTML = `
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="spin">
          <line x1="12" y1="2" x2="12" y2="6"></line>
          <line x1="12" y1="18" x2="12" y2="22"></line>
          <line x1="4.93" y1="4.93" x2="7.76" y2="7.76"></line>
          <line x1="16.24" y1="16.24" x2="19.07" y2="19.07"></line>
          <line x1="2" y1="12" x2="6" y2="12"></line>
          <line x1="18" y1="12" x2="22" y2="12"></line>
          <line x1="4.93" y1="19.07" x2="7.76" y2="16.24"></line>
          <line x1="16.24" y1="7.76" x2="19.07" y2="4.93"></line>
        </svg>
        Conectando...
      `;
      setTimeout(() => {
        alert(`🚀 Demo: abriria ${name} em iframe fullscreen.\n\nNa versão real: WebSocket + noVNC/CDP conforme o IDE.`);
        btn.innerHTML = `
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polygon points="5 3 19 12 5 21 5 3"></polygon>
          </svg>
          Conectar
        `;
      }, 1500);
    });
  });

  // Bottom nav active
  document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', (e) => {
      e.preventDefault();
      document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
      item.classList.add('active');
    });
  });

  // CSS: spin animation
  const style = document.createElement('style');
  style.textContent = `
    .spin { animation: spin 1s linear infinite; }
    @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
  `;
  document.head.appendChild(style);

  // PWA install prompt
  let deferredPrompt;
  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    // Poderia mostrar botão "Instalar DM Hub" aqui
    console.log('� PWA: usuário pode instalar o app');
  });
})();
