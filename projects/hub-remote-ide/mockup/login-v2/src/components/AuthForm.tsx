import { useState, useEffect, useRef } from 'react';
import Button from './Button.tsx';
import '../styles/auth-forms.css';

type Stage = 'credentials' | 'two-factor' | 'two-factor-setup';

interface LoginState {
  stage: Stage;
  loading: boolean;
  error: string | null;
  email: string;
  // 2FA setup (primeira vez)
  setupSecret?: string;
  setupUri?: string;
}

export default function AuthForm() {
  const [state, setState] = useState<LoginState>({
    stage: 'credentials',
    loading: false,
    error: null,
    email: '',
  });

  const [showPassword, setShowPassword] = useState(false);
  const [remember, setRemember] = useState(false);
  const emailRef = useRef<HTMLInputElement>(null);
  const passwordRef = useRef<HTMLInputElement>(null);
  const codeRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (state.stage === 'two-factor') {
      codeRef.current?.focus();
    }
  }, [state.stage]);

  async function handleCredentials(e: React.FormEvent) {
    e.preventDefault();
    setState(s => ({ ...s, loading: true, error: null }));

    const email = emailRef.current!.value.trim();
    const password = passwordRef.current!.value;

    try {
      const r = await fetch('/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, remember }),
      });
      const data = await r.json();

      if (!r.ok || !data.ok) {
        const errMap: Record<string, string> = {
          invalid_credentials: 'E-mail ou senha incorretos',
          brute_force: 'Muitas tentativas. Tente em 1 minuto.',
          invalid_email: 'E-mail inválido',
        };
        setState(s => ({
          ...s,
          loading: false,
          error: errMap[data.error] ?? data.error ?? 'Erro desconhecido',
        }));
        passwordRef.current?.focus();
        return;
      }

      if (data.next === '2fa_setup') {
        // Primeira vez: busca secret + otpauth URI
        const sr = await fetch('/auth/2fa/setup', { credentials: 'same-origin' });
        const sd = await sr.json();
        if (sr.ok && sd.ok) {
          setState(s => ({
            ...s,
            loading: false,
            stage: 'two-factor-setup',
            email,
            setupSecret: sd.secret,
            setupUri: sd.otpauth_url,
          }));
        } else {
          setState(s => ({ ...s, loading: false, error: 'Falha ao gerar 2FA' }));
        }
      } else if (data.next === '2fa') {
        setState(s => ({ ...s, loading: false, stage: 'two-factor', email }));
      }
    } catch (err) {
      setState(s => ({ ...s, loading: false, error: 'Falha de rede' }));
    }
  }

  async function handle2FA(e: React.FormEvent) {
    e.preventDefault();
    setState(s => ({ ...s, loading: true, error: null }));

    const code = codeRef.current!.value.trim();
    if (!/^\d{6}$/.test(code)) {
      setState(s => ({ ...s, loading: false, error: 'Código deve ter 6 dígitos' }));
      return;
    }

    try {
      const r = await fetch('/auth/2fa', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code }),
      });
      const data = await r.json();

      if (!r.ok || !data.ok) {
        setState(s => ({
          ...s,
          loading: false,
          error: data.error === 'invalid_2fa' ? 'Código incorreto' : (data.error ?? 'Erro'),
        }));
        if (codeRef.current) codeRef.current.value = '';
        codeRef.current?.focus();
        return;
      }

      window.location.href = data.redirect ?? '/hub.html';
    } catch (err) {
      setState(s => ({ ...s, loading: false, error: 'Falha de rede' }));
    }
  }

  async function copySecret() {
    if (!state.setupSecret) return;
    try {
      await navigator.clipboard.writeText(state.setupSecret);
      const btn = document.getElementById('copy-btn');
      if (btn) {
        const orig = btn.textContent;
        btn.textContent = 'copiado!';
        setTimeout(() => { if (btn) btn.textContent = orig; }, 1500);
      }
    } catch {
      /* clipboard não disponível */
    }
  }

  function backToCredentials() {
    setState(s => ({ ...s, stage: 'credentials', error: null, loading: false }));
  }

  return (
    <div className="auth-form-wrap">
      {/* STAGE: Credentials (email + senha) */}
      {state.stage === 'credentials' && (
        <form className="auth-form" onSubmit={handleCredentials} autoComplete="on">
          <label className="auth-field">
            <span className="auth-field-label">E-mail</span>
            <input
              ref={emailRef}
              type="email"
              name="email"
              required
              autoComplete="username"
              placeholder="seu@email.com"
              className="auth-input"
              disabled={state.loading}
            />
          </label>

          <label className="auth-field">
            <span className="auth-field-label">Senha</span>
            <div className="auth-input-wrap">
              <input
                ref={passwordRef}
                type={showPassword ? 'text' : 'password'}
                name="password"
                required
                minLength={8}
                autoComplete="current-password"
                placeholder="••••••••"
                className="auth-input"
                disabled={state.loading}
              />
              <button
                type="button"
                className="auth-input-toggle"
                onClick={() => setShowPassword(v => !v)}
                aria-label={showPassword ? 'Ocultar senha' : 'Mostrar senha'}
                tabIndex={-1}
              >
                {showPassword ? 'ocultar' : 'mostrar'}
              </button>
            </div>
          </label>

          <label className="auth-check">
            <input
              type="checkbox"
              checked={remember}
              onChange={e => setRemember(e.target.checked)}
              disabled={state.loading}
            />
            <span>manter conectado por 30 dias</span>
          </label>

          {state.error && (
            <div className="auth-error" role="alert">
              {state.error}
            </div>
          )}

          <Button type="submit" variant="primary" fullWidth loading={state.loading}>
            Continuar
          </Button>
        </form>
      )}

      {/* STAGE: 2FA code (já configurado) */}
      {state.stage === 'two-factor' && (
        <form className="auth-form" onSubmit={handle2FA} autoComplete="off">
          <div className="auth-2fa-context">
            <span className="auth-2fa-context-label">conectando como</span>
            <span className="auth-2fa-context-email">{state.email}</span>
          </div>
          <p className="auth-2fa-hint">
            Digite o código de 6 dígitos do seu app autenticador.
          </p>
          <label className="auth-field">
            <span className="auth-field-label">Código 2FA</span>
            <input
              ref={codeRef}
              type="text"
              name="code"
              required
              pattern="[0-9]{6}"
              maxLength={6}
              inputMode="numeric"
              autoComplete="one-time-code"
              placeholder="000000"
              className="auth-input auth-input--code"
              disabled={state.loading}
            />
          </label>

          {state.error && (
            <div className="auth-error" role="alert">
              {state.error}
            </div>
          )}

          <Button type="submit" variant="primary" fullWidth loading={state.loading}>
            Entrar
          </Button>

          <button type="button" className="auth-back-link" onClick={backToCredentials}>
            ← voltar
          </button>
        </form>
      )}

      {/* STAGE: 2FA setup (primeira vez) */}
      {state.stage === 'two-factor-setup' && (
        <form className="auth-form" onSubmit={handle2FA} autoComplete="off">
          <p className="auth-2fa-hint">
            Escaneie o QR code no seu app autenticador (Google Authenticator / Authy / 1Password / Bitwarden).
          </p>

          <div className="auth-qr-wrap">
            {state.setupUri && (
              <img
                src={`/auth/2fa/qr?uri=${encodeURIComponent(state.setupUri)}`}
                alt="QR code para configurar 2FA"
                className="auth-qr-img"
                width={180}
                height={180}
              />
            )}
          </div>

          <details className="auth-secret-details">
            <summary>ou digite o secret manualmente</summary>
            <div className="auth-secret-box">
              <code className="auth-secret-code">{state.setupSecret}</code>
              <button type="button" id="copy-btn" className="auth-copy-btn" onClick={copySecret}>
                copiar
              </button>
            </div>
          </details>

          <p className="auth-2fa-hint">
            Depois, digite o código de 6 dígitos pra confirmar:
          </p>

          <label className="auth-field">
            <span className="auth-field-label">Código de confirmação</span>
            <input
              ref={codeRef}
              type="text"
              name="code"
              required
              pattern="[0-9]{6}"
              maxLength={6}
              inputMode="numeric"
              autoComplete="one-time-code"
              placeholder="000000"
              className="auth-input auth-input--code"
              disabled={state.loading}
            />
          </label>

          {state.error && (
            <div className="auth-error" role="alert">
              {state.error}
            </div>
          )}

          <Button type="submit" variant="primary" fullWidth loading={state.loading}>
            Confirmar e entrar
          </Button>
        </form>
      )}
    </div>
  );
}
