# 🧠 DM-Cerberus — Inteligencia de Memoria Local-First & Cockpit Pro para Asistentes de Código IA

<p align="center">
  <a href="https://devmaniacs.com.br/" target="_blank" rel="noopener noreferrer">
    <img src="assets/cerberus_cockpit.png" alt="Logo DM-Cerberus" width="128" height="128" />
  </a>
</p>

<p align="center">
  <strong>El cerebro soberano en el dispositivo de memoria continua, búsqueda híbrida y radar de tokens para agentes de IA.</strong><br>
  Diseñado para <strong>Google Antigravity</strong>, <strong>OpenAI Codex</strong>, <strong>Claude Code</strong>, <strong>Cursor</strong> y <strong>Windsurf</strong>.
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/Licencia-MIT-emerald.svg" alt="Licencia MIT" /></a>
  <img src="https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue.svg" alt="Versiones de Python" />
  <img src="https://img.shields.io/badge/Arquitectura-Local--First-success.svg" alt="Local First" />
  <img src="https://img.shields.io/badge/Privacidad-100%25%20En%20Dispositivo-brightgreen.svg" alt="100% Local" />
  <img src="https://img.shields.io/badge/Telemetr%C3%ADa-Cero%20Salida-lightgrey.svg" alt="Sin Telemetría" />
  <img src="https://img.shields.io/badge/Protocolo-MCP%20Standard-purple.svg" alt="Protocolo MCP" />
  <a href="https://devmaniacs.com.br/"><img src="https://img.shields.io/badge/Dev%20Maniac's-Systems-red.svg" alt="Dev Maniac's Systems" /></a>
</p>

<p align="center">
  <a href="#-características-principales">Características</a> •
  <a href="#-galería-visual">Galería</a> •
  <a href="#-inicio-rápido">Inicio Rápido</a> •
  <a href="#-integración-mcp">Configuración de Agentes</a> •
  <a href="#-arquitectura">Arquitectura</a> •
  <a href="#-comunidad-y-apoyo">Apoyar</a> •
  <a href="README.md">English</a> •
  <a href="README.pt-BR.md">Português (Brasil)</a>
</p>

---

## ⚡ El Problema: Amnesia de Contexto y Desperdicio de Tokens en IA

Al programar sistemas complejos con agentes autónomos (Codex, Antigravity, Claude Code, Cursor, Windsurf), los ingenieros sufren problemas constantes:
1. **Amnesia de Contexto:** Cada sesión de terminal parte desde cero. Las decisiones de arquitectura, esquemas de bases de datos y soluciones a bugs anteriores deben explicarse repetidamente.
2. **Loops Infinitos y Gasto Desmedido:** Los agentes pueden quedar atrapados en ciclos de lectura y reintentos de pruebas, consumiendo cientos de miles de tokens sin avanzar.
3. **Fugas de Privacidad en la Nube:** Subir el conocimiento interno a bases vectoriales de terceros expone la propiedad intelectual de tu software.
4. **Alucinación:** Sin una fuente canónica y verificada de la verdad, los agentes toman decisiones contradictorias.

**DM-Cerberus** soluciona esto por completo. Operando 100% en tu máquina local, actúa como cerebro corporativo y torre de control de costos.

---

## ✨ Características Principales

### 🔍 1. Búsqueda Híbrida SQLite FTS5 con Clasificación BM25 por Autoridad
- Búsqueda instantánea en documentación Markdown, ADRs, contratos de API y reglas de negocio.
- Combina la **precisión léxica de SQLite BM25** con niveles de autoridad (desde notas de trabajo hasta decisiones canónicas nivel 50).
- Respuestas en submilisegundos sin depender de nubes externas.

### 📥 2. Pipeline de Aprendizaje & Inbox de Revisión Humana
- Los agentes proponen aprendizajes y patrones de forma autónoma con `capture_learning`.
- Verificación **Human-in-the-Loop**: revisa los cambios diff en el navegador y promueve el conocimiento a la base canónica con un clic.
- Sistema tolerante a fallos que omite archivos dañados sin interrumpir la operación.

### 📊 3. Cockpit Pro 5x & Radar Anti-Loop en Tiempo Real
- Contabilidad de tokens de Entrada (Prompt), Salida (Completion) y Razonamiento (Reasoning).
- Modelos de costos locales para `gpt-6.1-sol`, `gpt-6-luna`, `gpt-6-astra`, `claude-3-7-sonnet` y `gemini-2.5-pro`.
- **Radar Anti-Loop**: Detecta patrones repetitivos y consultas en bucle, alertando antes de consumir tu cuota.
- Exportación completa de métricas a CSV.

### 🌐 4. Grafo Visual Interactivo de Topología de Memoria
- Mapa 2D con fuerzas dinámicas que muestra las conexiones entre proyectos, documentos canónicos, decisiones y agentes.
- Inspección de nodos, zoom y desplazamiento fluido en Canvas HTML5.

### 🛡️ 5. Seguridad Corporativa y Soberanía Local
- **100% En Tu Equipo:** Los datos nunca salen de `127.0.0.1`. Cero telemetría externa.
- Hash de contraseñas con **PBKDF2-HMAC-SHA256** (200.000 iteraciones).
- **Autenticación en Dos Pasos (2FA TOTP RFC 6238)** compatible con Google Authenticator, Authy y 1Password.
- Cookies de sesión firmadas con HMAC-SHA256 en tiempo constante.

### 🔌 6. Servidor Nativo Model Context Protocol (MCP)
- Compatibilidad nativa con el estándar **Anthropic MCP**.
- Conecta DM-Cerberus a Codex, Antigravity, Claude Code, Cursor, Windsurf o workflows en CrewAI/LangFlow.

---

## 📸 Galería Visual

| Cockpit Pro 5x & Radar de Tokens | Búsqueda FTS5 & Previsualización |
|:---:|:---:|
| ![Cockpit Pro 5x](assets/showcase/showcase_cockpit.png) | ![Búsqueda & Preview](assets/showcase/showcase_search.png) |

| Inbox de Revisión | Topología Interactiva de Memoria |
|:---:|:---:|
| ![Inbox](assets/showcase/showcase_inbox.png) | ![Topología](assets/showcase/showcase_topology.png) |

| Login Soberano & Tema Dev Maniac's | Cuenta & Seguridad 2FA |
|:---:|:---:|
| ![Login](assets/showcase/showcase_login.png) | ![Seguridad](assets/showcase/showcase_profile.png) |

---

## 🚀 Inicio Rápido

### Opción A: Ejecución Directa en Python (Recomendado)

1. **Clona el repositorio:**
   ```bash
   git clone https://github.com/HelbertMoura/DM-Cerberus.git
   cd DM-Cerberus
   ```

2. **Indexa la memoria de tu proyecto:**
   ```bash
   python -m engine.cli index
   ```

3. **Inicia el panel Cockpit:**
   ```bash
   python -m engine.cli ui --port 8765
   ```
   Abre `http://127.0.0.1:8765` en tu navegador.

4. **Acceso directo en Windows:**
   Ejecuta `bin/launch_cockpit.pyw` para abrir silenciosamente en segundo plano con icono dedicado sin ventana de consola.

---

### Opción B: Docker Compose

```bash
cp .env.example .env
# Configura tus credenciales en .env
docker compose up -d
```
Accede al panel en `http://127.0.0.1:7331`.

---

## 🤖 Integración de Agentes (MCP)

Configura DM-Cerberus como servidor MCP:

### 1. Google Antigravity / Gemini CLI
Agrega a tu `mcp_servers.json`:
```json
{
  "mcpServers": {
    "cerberus-memory": {
      "command": "python",
      "args": ["-m", "engine.cli", "mcp"],
      "cwd": "C:/ruta/a/DM-Cerberus"
    }
  }
}
```

### 2. Claude Code (`~/.claude/config.json`)
```json
{
  "mcpServers": {
    "cerberus": {
      "command": "python",
      "args": ["-m", "engine.cli", "mcp"],
      "cwd": "/ruta/a/DM-Cerberus"
    }
  }
}
```

### 3. Cursor & Windsurf (`cursor_mcp.json` / `settings.json`)
```json
{
  "mcpServers": {
    "cerberus-memory": {
      "command": "python",
      "args": ["-m", "engine.cli", "mcp"],
      "cwd": "/ruta/a/DM-Cerberus"
    }
  }
}
```

---

## 📜 Licencia

Distribuido bajo la **Licencia MIT**. Consulta [LICENSE](LICENSE) para más detalles.

---

## ☕ Comunidad y Apoyo

**DM-Cerberus** es desarrollado con ☕ y ⚡ por **Helbert Moura** y el equipo de **Dev Maniac's Systems**.

- 🌐 **Sitio Oficial:** [devmaniacs.com.br](https://devmaniacs.com.br/)
- 💖 **Apoyar el Proyecto:** [linktr.ee/helbertmoura](https://linktr.ee/helbertmoura)
- 🚀 **Proyecto Hermano:** [AI Launcher](https://github.com/HelbertMoura/ai_launcher)
- 🐛 **Reportar Incidencias:** [GitHub Issues](https://github.com/HelbertMoura/DM-Cerberus/issues)
