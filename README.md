# 🌐 **servidor-psf**

## Ambiente de Execução e Hospedagem Multi-Projetos

---

### 📋 **CONCEITO FUNDAMENTAL**

**PSF (.psf)** é um **Ambiente de Execução Linux Containerizado** hospedado no GitHub Codespaces, projetado como uma **plataforma universal de hospedagem multi-projetos**.

Não é um projeto único - é uma **infraestrutura viva** onde você pode criar, executar e hospedar **infinitos projetos** sob o domínio `.psf`, cada um com seu próprio subdomínio, porta e stack tecnológica independente.

---

### 🏗️ **ARQUITETURA DO SISTEMA**

```
┌─────────────────────────────────────────────────────────────┐
│                    PLATAFORMA .PSF                          │
│            Ambiente de Execução Universal                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  🌐 REVERSE PROXY (Nginx)                                    │
│  ┌───────────────────────────────────────────────────┐    │
│  │  *.psf → Roteamento Inteligente por Subdomínio    │    │
│  └───────────────────────────────────────────────────┘    │
│                           │                                  │
│                           ▼                                  │
│  ┌───────────────────────────────────────────────────┐    │
│  │           ORQUESTRADOR (Docker Compose & CLI)      │    │
│  │     Gerencia múltiplos containers simultâneos      │    │
│  └───────────────────────────────────────────────────┘    │
│                           │                                  │
│         ┌─────────────────┼─────────────────┐              │
│         ▼                 ▼                 ▼              │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐            │
│  │ Projeto 1│    │ Projeto 2│    │ Projeto N│            │
│  │ Container│    │ Container│    │ Container│            │
│  │ :8081    │    │ :3000    │    │ :XXXX    │            │
│  └──────────┘    └──────────┘    └──────────┘            │
│                                                              │
│  📁 SISTEMA DE ARQUIVOS COMPARTILHADO                      │
│  ┌───────────────────────────────────────────────────┐    │
│  │  /workspace/                                      │    │
│  │    ├── projetos/                                  │    │
│  │    │   ├── loja/        → loja.psf               │    │
│  │    │   ├── blog/        → blog.psf               │    │
│  │    │   ├── api/         → api.psf                │    │
│  │    │   └── [novo]/      → [novo].psf             │    │
│  │    ├── nginx/           (configurações)           │    │
│  │    └── scripts/         (automação CLI psf)       │    │
│  └───────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

### 🛠️ **CLI PSF - Comandos Principais**

```bash
./scripts/psf.sh criar <nome> <stack> <porta>     # Criar novo projeto
./scripts/psf.sh remover <nome>                   # Remover projeto
./scripts/psf.sh listar                           # Listar todos os projetos
./scripts/psf.sh iniciar <nome>                   # Iniciar container
./scripts/psf.sh parar <nome>                     # Parar container
./scripts/psf.sh reiniciar <nome>                 # Reiniciar container
./scripts/psf.sh logs <nome>                      # Ver logs do projeto
./scripts/psf.sh dominio <nome>                   # Exibir URL do projeto
./scripts/psf.sh status                           # Status da plataforma
./scripts/psf.sh backup                           # Gerar backup .tar.gz
./scripts/psf.sh atualizar                        # Recarregar Nginx e Docker
```

---

### 🌐 **SISTEMA DE DOMÍNIOS .PSF**

- **Domínio Raiz**: `.psf`
- **Portal Central**: `http://portal.psf` (ou `:8000`)
- **Projetos**: `http://<nome>.psf`

---

### 🌟 **METODOLOGIA DE CONSTRUÇÃO (Forma B)**

Este projeto foi desenhado sob a metodologia **Forma B — Cega, mas não burra**:
- **Plano 1**: Definição completa do organismo e das suas responsabilidades.
- **Plano 2**: Fonte única de verdade, contratos entre CLI, Nginx, Docker e Portal, matriz de capacidades e cobertura antes do Julgamento Final.
