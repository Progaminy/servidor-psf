#!/usr/bin/env bash
# ==============================================================================
# PSF Platform — Gerenciamento de Domínios e Vhosts Nginx (Forma B)
# ==============================================================================

source "$(dirname "${BASH_SOURCE[0]}")/utils.sh"

action="$1"
name="$2"
port="$3"

case "$action" in
    adicionar)
        validate_project_name "$name" || exit 1
        validate_port "$port" || exit 1

        vhost_file="${CONF_D_DIR}/${name}.conf"

        echo -e "${CYAN}🌐 Gerando configuração Nginx para ${name}.psf (Porta ${port})...${NC}"

        cat <<EOF > "$vhost_file"
# Configuration generated dynamically by PSF Platform
server {
    listen 80;
    server_name ${name}.psf *.${name}.psf;

    location / {
        proxy_pass http://${name}:${port};
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF
        echo -e "${GREEN}✅ Configuração VHost criada: ${vhost_file}${NC}"

        # Atualizar /etc/hosts se possível/necessário
        if grep -q "${name}.psf" /etc/hosts 2>/dev/null; then
            echo -e "${YELLOW}ℹ️ Domínio ${name}.psf já está presente em /etc/hosts${NC}"
        else
            echo "127.0.0.1 ${name}.psf" >> /etc/hosts 2>/dev/null || true
        fi
        ;;

    remover)
        validate_project_name "$name" || exit 1
        vhost_file="${CONF_D_DIR}/${name}.conf"
        if [[ -f "$vhost_file" ]]; then
            rm -f "$vhost_file"
            echo -e "${GREEN}✅ Configuração VHost removida: ${vhost_file}${NC}"
        fi
        ;;

    reload)
        echo -e "${CYAN}🔄 Solicitando recarregamento do Nginx Proxy...${NC}"
        docker exec psf-nginx-proxy nginx -s reload 2>/dev/null || echo -e "${YELLOW}ℹ️ Container psf-nginx-proxy não está em execução no momento (será carregado no startup).${NC}"
        ;;

    *)
        echo "Uso: $0 {adicionar|remover|reload} [nome] [porta]"
        exit 1
        ;;
esac
