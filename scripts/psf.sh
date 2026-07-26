#!/usr/bin/env bash
# ==============================================================================
# PSF Platform — CLI Principal `psf` (Forma B Resiliente)
# ==============================================================================

# Auto-atribuição de permissões POSIX de segurança
chmod +x "$(dirname "${BASH_SOURCE[0]}")"/*.sh 2>/dev/null || true

source "$(dirname "${BASH_SOURCE[0]}")/utils.sh"

command="$1"
shift || true

show_help() {
    echo -e "${BOLD}${CYAN}🌐 PSF CLI — Gerenciador da Plataforma Multi-Projetos (.psf)${NC}"
    echo -e "Uso: ${BOLD}psf <comando> [argumentos]${NC}\n"
    echo -e "${BOLD}Comandos Disponíveis:${NC}"
    echo -e "  ${GREEN}criar <nome> [stack] [porta]${NC}  - Criar um novo projeto containerizado"
    echo -e "  ${GREEN}remover <nome>${NC}               - Parar e remover um projeto"
    echo -e "  ${GREEN}listar${NC}                       - Listar todos os projetos .psf ativos"
    echo -e "  ${GREEN}iniciar <nome>${NC}               - Iniciar container de um projeto"
    echo -e "  ${GREEN}parar <nome>${NC}                 - Parar container de um projeto"
    echo -e "  ${GREEN}reiniciar <nome>${NC}             - Reiniciar container de um projeto"
    echo -e "  ${GREEN}logs <nome>${NC}                  - Exibir logs em tempo real de um projeto"
    echo -e "  ${GREEN}dominio <nome>${NC}               - Exibir URL de acesso ao projeto .psf"
    echo -e "  ${GREEN}status${NC}                       - Status completo da plataforma e containers"
    echo -e "  ${GREEN}backup${NC}                       - Realizar backup completo dos projetos"
    echo -e "  ${GREEN}atualizar${NC}                    - Atualizar infraestrutura e proxy da plataforma"
    echo -e "  ${GREEN}help${NC}                         - Exibir esta mensagem de ajuda"
}

case "$command" in
    criar)
        bash "${PSF_ROOT}/scripts/criar-projeto.sh" "$@"
        ;;

    remover)
        bash "${PSF_ROOT}/scripts/remover-projeto.sh" "$1"
        ;;

    listar)
        echo -e "${BOLD}${CYAN}🌟 PLATAFORMA PSF - Projetos Cadastrados:${NC}"
        ensure_registry_exists
        python3 - "$PORTAL_REGISTRY" << 'EOF'
import sys, json

try:
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    if not data:
        print("  (Nenhum projeto cadastrado no momento)")
    for p in data:
        print(f"   🛍️  {p['name']}.psf -> Porta {p['port']} ({p['stack']}) [{p.get('status', 'ONLINE')}]")
except Exception as e:
    print(f"Erro ao ler cadastro: {e}")
EOF
        ;;

    iniciar)
        name="$1"
        validate_project_name "$name" || exit 1
        echo -e "${CYAN}🚀 Iniciando container psf-app-${name}...${NC}"
        docker start "psf-app-${name}" 2>/dev/null || (cd "${PROJETOS_DIR}/${name}" && docker compose up -d)
        ;;

    parar)
        name="$1"
        validate_project_name "$name" || exit 1
        echo -e "${YELLOW}⏸️ Parando container psf-app-${name}...${NC}"
        docker stop "psf-app-${name}"
        ;;

    reiniciar)
        name="$1"
        validate_project_name "$name" || exit 1
        echo -e "${CYAN}🔄 Reiniciando container psf-app-${name}...${NC}"
        docker restart "psf-app-${name}"
        ;;

    logs)
        name="$1"
        validate_project_name "$name" || exit 1
        echo -e "${CYAN}📋 Exibindo logs do container psf-app-${name}...${NC}"
        docker logs -f "psf-app-${name}"
        ;;

    dominio)
        name="$1"
        validate_project_name "$name" || exit 1
        echo -e "${GREEN}🌐 URL do Projeto: http://${name}.psf${NC}"
        ;;

    status)
        echo -e "${BOLD}${CYAN}📊 Status da Plataforma PSF:${NC}"
        echo -e "----------------------------------------"
        echo -e "  🐧 SO Base: Ubuntu 22.04 LTS"
        echo -e "  🐳 Docker Engine: $(docker --version 2>/dev/null || echo 'não detectado')"
        echo -e "  🌐 Proxy Nginx: $(docker inspect -f '{{.State.Status}}' psf-nginx-proxy 2>/dev/null || echo 'parado')"
        echo -e "  🌟 Portal Central: $(docker inspect -f '{{.State.Status}}' psf-portal 2>/dev/null || echo 'parado')"
        echo -e "----------------------------------------"
        bash "${PSF_ROOT}/scripts/psf.sh" listar
        ;;

    backup)
        backup_file="${PSF_ROOT}/backup_psf_$(date +%Y%m%d_%H%M%S).tar.gz"
        echo -e "${CYAN}📦 Gerando backup completo da plataforma em ${backup_file}...${NC}"
        tar -czf "$backup_file" -C "$PSF_ROOT" projetos nginx scripts docker-compose.psf.yml
        echo -e "${GREEN}✅ Backup concluído com sucesso: ${backup_file}${NC}"
        ;;

    atualizar)
        echo -e "${CYAN}🔄 Atualizando e recarregando infraestrutura PSF...${NC}"
        docker compose -f "${PSF_ROOT}/docker-compose.psf.yml" up -d --build
        bash "${PSF_ROOT}/scripts/gerenciar-dominios.sh" reload
        echo -e "${GREEN}✅ Plataforma atualizada!${NC}"
        ;;

    help|--help|-h|"")
        show_help
        ;;

    *)
        echo -e "${RED}❌ Comando desconhecido: $command${NC}"
        show_help
        exit 1
        ;;
esac
