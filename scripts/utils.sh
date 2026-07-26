#!/usr/bin/env bash
# ==============================================================================
# PSF Platform — Single Source of Truth & Utility Functions (Forma B)
# ==============================================================================

# Diretório Raiz do Projeto
PSF_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJETOS_DIR="${PSF_ROOT}/projetos"
NGINX_DIR="${PSF_ROOT}/nginx"
CONF_D_DIR="${NGINX_DIR}/conf.d"
PORTAL_REGISTRY="${PROJETOS_DIR}/portal/projects.json"

# Auto-atribuição de permissões de execução (Garantia de Ambiente POSIX - Forma B)
chmod +x "${PSF_ROOT}/scripts/"*.sh 2>/dev/null || true

# Portas Reservadas do Sistema
PORTA_NGINX_HTTP=80
PORTA_PORTAL_CENTRAL=8000
PORTA_MIN=3000
PORTA_MAX=9000

# Catálogo de Stacks Suportadas
SUPPORTED_STACKS=("node" "python" "php" "go" "java" "csharp" "rust" "react" "static")

# Cores e Formatação de Saída
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# ------------------------------------------------------------------------------
# Validações Estritas
# ------------------------------------------------------------------------------

# Validar se o nome do projeto segue o padrão ^[a-z0-9-]+$
validate_project_name() {
    local name="$1"
    if [[ -z "$name" ]]; then
        echo -e "${RED}❌ Erro: O nome do projeto não pode ser vazio.${NC}"
        return 1
    fi
    if [[ ! "$name" =~ ^[a-z0-9-]+$ ]]; then
        echo -e "${RED}❌ Erro: Nome do projeto '$name' inválido. Use apenas letras minúsculas, números e hífens (ex: minha-loja-1).${NC}"
        return 1
    fi
    if [[ "$name" == "portal" || "$name" == "admin" || "$name" == "nginx" || "$name" == "_template" ]]; then
        echo -e "${RED}❌ Erro: Nome '$name' é um identificador reservado do sistema PSF.${NC}"
        return 1
    fi
    return 0
}

# Validar se a stack informada pertence ao catálogo de fontes da verdade
validate_stack() {
    local stack="$1"
    for s in "${SUPPORTED_STACKS[@]}"; do
        if [[ "$s" == "$stack" ]]; then
            return 0
        fi
    done
    echo -e "${RED}❌ Erro: Stack '$stack' não suportada.${NC}"
    echo -e "${YELLOW}Stacks disponíveis: ${SUPPORTED_STACKS[*]}${NC}"
    return 1
}

# Validar se a porta está no intervalo 3000-9000 e não conflita com portas reservadas
validate_port() {
    local port="$1"
    if ! [[ "$port" =~ ^[0-9]+$ ]]; then
        echo -e "${RED}❌ Erro: Porta '$port' deve ser um número inteiro.${NC}"
        return 1
    fi
    if (( port < PORTA_MIN || port > PORTA_MAX )); then
        echo -e "${RED}❌ Erro: Porta '$port' fora do intervalo permitido ($PORTA_MIN - $PORTA_MAX).${NC}"
        return 1
    fi
    if (( port == PORTA_PORTAL_CENTRAL )); then
        echo -e "${RED}❌ Erro: Porta $PORTA_PORTAL_CENTRAL é reservada para o Portal Central PSF.${NC}"
        return 1
    fi
    return 0
}

# ------------------------------------------------------------------------------
# Manipulação Segura do Registro de Projetos (projects.json)
# ------------------------------------------------------------------------------

ensure_registry_exists() {
    if [[ ! -f "$PORTAL_REGISTRY" ]]; then
        mkdir -p "$(dirname "$PORTAL_REGISTRY")"
        echo '[]' > "$PORTAL_REGISTRY"
    fi
}

register_project_json() {
    local name="$1"
    local stack="$2"
    local port="$3"
    local created_at
    created_at=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    ensure_registry_exists

    python3 - "$PORTAL_REGISTRY" "$name" "$stack" "$port" "$created_at" << 'EOF'
import sys, json

registry_file, name, stack, port, created_at = sys.argv[1:]
port = int(port)

try:
    with open(registry_file, 'r') as f:
        data = json.load(f)
except Exception:
    data = []

# Filtrar entrada pré-existente se houver
data = [item for item in data if item.get('name') != name]

data.append({
    "name": name,
    "domain": f"{name}.psf",
    "stack": stack,
    "port": port,
    "status": "ONLINE",
    "createdAt": created_at
})

with open(registry_file, 'w') as f:
    json.dump(data, f, indent=2)
EOF
}

unregister_project_json() {
    local name="$1"
    ensure_registry_exists

    python3 - "$PORTAL_REGISTRY" "$name" << 'EOF'
import sys, json

registry_file, name = sys.argv[1:]

try:
    with open(registry_file, 'r') as f:
        data = json.load(f)
except Exception:
    data = []

data = [item for item in data if item.get('name') != name]

with open(registry_file, 'w') as f:
    json.dump(data, f, indent=2)
EOF
}
