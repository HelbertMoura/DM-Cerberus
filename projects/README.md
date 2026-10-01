# 📁 Projetos & Second Brains Locais

Esta pasta armazena as bases de conhecimento e documentações em Markdown de cada projeto gerenciado pelo **DM-Cerberus**.

---

## 🏗️ Estrutura Recomendada por Projeto

Cada subpasta dentro de `projects/<slug-do-projeto>/` representa um projeto independente indexado pelo Cerberus:

```text
projects/
├── README.md                  # Este arquivo
├── example-project/           # Projeto de exemplo / template inicial
│   ├── index.md               # Mapa mestre e roteamento do projeto
│   ├── architecture.md        # Decisões de arquitetura, stack e infraestrutura
│   └── status.md              # Estado atual, backlog e marcos
└── seu-projeto/               # Adicione suas próprias pastas aqui!
    ├── index.md
    └── ...
```

---

## 🔍 Indexação Automática

- O motor Cerberus (`engine.index`) rastreia recursivamente todos os arquivos `.md` nesta pasta.
- Cada arquivo vira um nó na visualização da **Topologia 2D** e é indexado no motor **FTS5 SQLite** para busca híbrida ultrarrápida.
- Para manter a soberania de dados, você pode adicionar projetos proprietários aqui sem medo: o `.gitignore` protege suas pastas privadas contra versionamento acidental.
