#!/usr/bin/env bash
# ==============================================================================
# PSF Platform — Remoção Segura de Projetos (Forma B Resiliente)
# ==============================================================================

source "$(dirname "${BASH_SOURCE[0]}")/utils.sh"

name="$1"

validate_project_name "$name" || exit 1

target_dir="${PROJETOS_DIR}/${name}"

if [[ ! -d "$target_dir" ]]; then
    echo -e "${RED}❌ Erro: O projeto '$name' não foi encontrado em ${target_dir}.${NC}"
    exit 1
fi

echo -e "${YELLOW}⚠️ Removendo o projeto '${name}'...${NC}"

# Parar container se estiver rodando
docker stop "psf-app-${name}" 2>/dev/null || true
docker rm "psf-app-${name}" 2>/dev/null || true

# Remover vhost do Nginx (Chamada Resiliente via bash)
bash "${PSF_ROOT}/scripts/gerenciar-dominios.sh" remover "$name"

# Desregistrar do projects.json
unregister_project_json "$name"

# Deletar diretório do projeto
rm -rf "$target_dir"

# Recarregar Nginx se ativo (Chamada Resiliente via bash)
bash "${PSF_ROOT}/scripts/gerenciar-dominios.sh" reload

echo -e "${GREEN}✅ Projeto '${name}' e todas as suas configurações foram removidos com sucesso!${NC}"
