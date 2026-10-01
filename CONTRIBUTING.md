# Contributing to DM-Cerberus

Welcome to **DM-Cerberus**! We appreciate your interest in contributing to the sovereign local-first memory intelligence engine for AI coding assistants.

Developed by [Dev Maniac's Systems](https://devmaniacs.com.br) and maintained by [Helbert Moura](https://linktr.ee/helbertmoura).

---

## 🧭 Core Principles

1. **Local-First & Sovereign:** DM-Cerberus operates 100% on your machine. Zero outbound telemetry, zero third-party cloud analytics, zero leakage of user code or memories.
2. **Minimal Dependencies:** Core engines are built with Python standard library modules (`sqlite3`, `http.server`, `hashlib`, `urllib`). Keep external dependencies to the absolute minimum.
3. **Safety & Confidentiality:** User project files, secrets, `.cerberus/` runtime databases, and `.env` files must NEVER be tracked or committed to Git.
4. **Human-in-the-Loop:** Automated candidate learning ingestion requires human review or explicit verification before canonical promotion.

---

## 🛠️ Development Setup

### Prerequisites
- Python 3.10+ (tested up to Python 3.14)
- Git
- Modern browser (Chrome, Edge, Firefox, Brave)

### Clone & Run Locally
```bash
git clone https://github.com/HelbertMoura/DM-Cerberus.git
cd DM-Cerberus

# Install development dependencies
pip install -r requirements-dev.txt  # or: pip install pytest anyio

# Run test suite
python -m pytest tests/

# Start local server
python -m engine.cli ui --port 8765
```

---

## 🧪 Testing Guidelines

Before submitting any Pull Request:
1. Ensure all tests pass:
   ```bash
   python -m pytest tests/
   ```
2. For UI changes, verify that the 36 UI hardening tests pass:
   ```bash
   python -m pytest tests/test_ui_hardening.py tests/test_server_api.py
   ```
3. Avoid breaking the Command Workbench contract (`tab-search`, `tab-inbox`, `tab-topology`, `tab-metrics`, `tab-profile`).

---

## 📦 Pull Request Process

1. Fork the repository and create a feature branch (`git checkout -b feature/my-enhancement`).
2. Commit clear, descriptive commits following Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`).
3. Do not include personal tokens, confidential IPs, or private client projects in your commits.
4. Open a Pull Request on GitHub against `main`.

---

## ☕ Support the Project

If DM-Cerberus helps accelerate your development workflow with AI agents, consider supporting our open-source journey:
- 🌐 Official Website: [devmaniacs.com.br](https://devmaniacs.com.br/)
- 💖 Sponsor & Socials: [linktr.ee/helbertmoura](https://linktr.ee/helbertmoura)
- 🚀 Check out our sister project: [ai_launcher](https://github.com/HelbertMoura/ai_launcher)
