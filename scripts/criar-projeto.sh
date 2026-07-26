#!/usr/bin/env bash
# ==============================================================================
# PSF Platform — Factory de Projetos Multi-Stack (Forma B Resiliente)
# ==============================================================================

source "$(dirname "${BASH_SOURCE[0]}")/utils.sh"

name="$1"
stack="${2:-node}"
port="$3"

# Validações dos parâmetros recebidos
validate_project_name "$name" || exit 1
validate_stack "$stack" || exit 1

# Escolha de porta livre se não fornecida
if [[ -z "$port" ]]; then
    ensure_registry_exists
    used_ports=$(python3 -c "import json; data=json.load(open('$PORTAL_REGISTRY')); print([x['port'] for x in data])" 2>/dev/null || echo "[]")
    
    found_port=3001
    for p in $(seq 3001 8999); do
        if [[ "$p" -eq 8000 ]]; then continue; fi
        if ! echo "$used_ports" | grep -q "$p"; then
            found_port=$p
            break
        fi
    done
    port=$found_port
fi

validate_port "$port" || exit 1

target_dir="${PROJETOS_DIR}/${name}"

if [[ -d "$target_dir" ]]; then
    echo -e "${RED}❌ Erro: O projeto '$name' já existe em ${target_dir}.${NC}"
    exit 1
fi

echo -e "${CYAN}🏗️ Criando novo projeto PSF...${NC}"
echo -e "${BOLD}📌 Nome: ${name}${NC}"
echo -e "${BOLD}🛠️ Stack: ${stack}${NC}"
echo -e "${BOLD}🔌 Porta: ${port}${NC}"
echo -e "${BOLD}🌐 Domínio: ${name}.psf${NC}"

mkdir -p "${target_dir}/src"

# Gerar arquivos específicos de acordo com a stack escolhida
case "$stack" in
    node|react)
        cat <<EOF > "${target_dir}/package.json"
{
  "name": "${name}",
  "version": "1.0.0",
  "main": "src/index.js",
  "scripts": {
    "start": "node src/index.js"
  },
  "dependencies": {
    "express": "^4.18.2"
  }
}
EOF
        cat <<EOF > "${target_dir}/src/index.js"
const express = require('express');
const app = express();
const PORT = process.env.PORT || ${port};

app.get('/', (req, res) => {
  res.send(\`
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
      <meta charset="UTF-8">
      <title>${name}.psf</title>
      <style>
        body { font-family: system-ui, sans-serif; background: #0f172a; color: #f8fafc; display: grid; place-content: center; height: 100vh; margin: 0; }
        .card { background: #1e293b; padding: 2rem; border-radius: 12px; border: 1px solid #334155; text-align: center; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }
        h1 { color: #38bdf8; margin-top: 0; }
        .badge { background: #0284c7; padding: 4px 12px; border-radius: 20px; font-weight: bold; font-size: 0.85rem; }
      </style>
    </head>
    <body>
      <div class="card">
        <h1>🚀 Projeto ${name}.psf</h1>
        <p>Hospedado no <strong>servidor-psf</strong></p>
        <p><span class="badge">Stack: ${stack}</span> <span class="badge">Porta: ${port}</span></p>
      </div>
    </body>
    </html>
  \`);
});

app.listen(PORT, () => console.log(\`Servidor ${name} rodando na porta \${PORT}\`));
EOF
        cat <<EOF > "${target_dir}/Dockerfile"
FROM node:18-alpine
WORKDIR /app
COPY package.json ./
RUN npm install
COPY . .
EXPOSE ${port}
CMD ["npm", "start"]
EOF
        ;;

    python)
        cat <<EOF > "${target_dir}/src/app.py"
import os
from flask import Flask

app = Flask(__name__)
PORT = int(os.environ.get("PORT", ${port}))

@app.route("/")
def home():
    return f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
      <meta charset="UTF-8">
      <title>${name}.psf</title>
      <style>
        body {{ font-family: system-ui, sans-serif; background: #0f172a; color: #f8fafc; display: grid; place-content: center; height: 100vh; margin: 0; }}
        .card {{ background: #1e293b; padding: 2rem; border-radius: 12px; border: 1px solid #334155; text-align: center; }}
        h1 {{ color: #4ade80; margin-top: 0; }}
        .badge {{ background: #16a34a; padding: 4px 12px; border-radius: 20px; font-weight: bold; }}
      </style>
    </head>
    <body>
      <div class="card">
        <h1>🐍 Projeto Python ${name}.psf</h1>
        <p>Hospedado no <strong>servidor-psf</strong></p>
        <p><span class="badge">Stack: Python Flask</span> <span class="badge">Porta: {PORT}</span></p>
      </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
EOF
        cat <<EOF > "${target_dir}/requirements.txt"
flask==3.0.0
EOF
        cat <<EOF > "${target_dir}/Dockerfile"
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE ${port}
CMD ["python", "src/app.py"]
EOF
        ;;

    php)
        cat <<EOF > "${target_dir}/src/index.php"
<?php
$name = "${name}";
$port = "${port}";
?>
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <title><?php echo $name; ?>.psf</title>
  <style>
    body { font-family: system-ui, sans-serif; background: #0f172a; color: #f8fafc; display: grid; place-content: center; height: 100vh; margin: 0; }
    .card { background: #1e293b; padding: 2rem; border-radius: 12px; border: 1px solid #334155; text-align: center; }
    h1 { color: #c084fc; margin-top: 0; }
    .badge { background: #9333ea; padding: 4px 12px; border-radius: 20px; font-weight: bold; }
  </style>
</head>
<body>
  <div class="card">
    <h1>🐘 Projeto PHP <?php echo $name; ?>.psf</h1>
    <p>Hospedado no <strong>servidor-psf</strong></p>
    <p><span class="badge">Stack: PHP</span> <span class="badge">Porta: <?php echo $port; ?></span></p>
  </div>
</body>
</html>
EOF
        cat <<EOF > "${target_dir}/Dockerfile"
FROM php:8.2-cli-alpine
WORKDIR /app
COPY . .
EXPOSE ${port}
CMD ["php", "-S", "0.0.0.0:${port}", "-t", "src"]
EOF
        ;;

    go)
        cat <<EOF > "${target_dir}/src/main.go"
package main

import (
	"fmt"
	"net/http"
	"os"
)

func main() {
	port := os.Getenv("PORT")
	if port == "" {
		port = "${port}"
	}

	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		html := fmt.Sprintf(\`
			<!DOCTYPE html>
			<html lang="pt-BR">
			<head>
			  <meta charset="UTF-8">
			  <title>%s.psf</title>
			  <style>
			    body { font-family: system-ui, sans-serif; background: #0f172a; color: #f8fafc; display: grid; place-content: center; height: 100vh; margin: 0; }
			    .card { background: #1e293b; padding: 2rem; border-radius: 12px; border: 1px solid #334155; text-align: center; }
			    h1 { color: #38bdf8; margin-top: 0; }
			    .badge { background: #0284c7; padding: 4px 12px; border-radius: 20px; font-weight: bold; }
			  </style>
			</head>
			<body>
			  <div class="card">
			    <h1>🐹 Projeto Go %s.psf</h1>
			    <p>Hospedado no <strong>servidor-psf</strong></p>
			    <p><span class="badge">Stack: Go</span> <span class="badge">Porta: %s</span></p>
			  </div>
			</body>
			</html>
		\`, "${name}", "${name}", port)
		fmt.Fprint(w, html)
	})

	fmt.Printf("Servidor Go rodando na porta %s\n", port)
	http.ListenAndServe(":"+port, nil)
}
EOF
        cat <<EOF > "${target_dir}/Dockerfile"
FROM golang:1.21-alpine AS builder
WORKDIR /app
COPY . .
RUN go build -o server src/main.go

FROM alpine:latest
WORKDIR /app
COPY --from=builder /app/server .
EXPOSE ${port}
CMD ["./server"]
EOF
        ;;

    static|*)
        cat <<EOF > "${target_dir}/src/index.html"
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <title>${name}.psf</title>
  <style>
    body { font-family: system-ui, sans-serif; background: #0f172a; color: #f8fafc; display: grid; place-content: center; height: 100vh; margin: 0; }
    .card { background: #1e293b; padding: 2rem; border-radius: 12px; border: 1px solid #334155; text-align: center; }
    h1 { color: #f43f5e; margin-top: 0; }
    .badge { background: #e11d48; padding: 4px 12px; border-radius: 20px; font-weight: bold; }
  </style>
</head>
<body>
  <div class="card">
    <h1>🌐 Projeto Estático ${name}.psf</h1>
    <p>Hospedado no <strong>servidor-psf</strong></p>
    <p><span class="badge">Stack: Static Nginx</span> <span class="badge">Porta: ${port}</span></p>
  </div>
</body>
</html>
EOF
        cat <<EOF > "${target_dir}/Dockerfile"
FROM nginx:alpine
COPY src/index.html /usr/share/nginx/html/index.html
EXPOSE 80
EOF
        ;;
esac

# Gerar docker-compose.yml individual do projeto
cat <<EOF > "${target_dir}/docker-compose.yml"
version: '3.8'

networks:
  psf-network:
    external: true

services:
  ${name}:
    build: .
    container_name: psf-app-${name}
    restart: always
    ports:
      - "${port}:${port}"
    networks:
      - psf-network
EOF

# Registrar VHost Nginx e atualizar Registro de Projetos (Chamada Resiliente via bash)
bash "${PSF_ROOT}/scripts/gerenciar-dominios.sh" adicionar "$name" "$port"
register_project_json "$name" "$stack" "$port"

echo -e "${GREEN}✅ Projeto '${name}' criado com sucesso!${NC}"
echo -e "${GREEN}🌐 Domínio registrado: http://${name}.psf${NC}"
echo -e "${GREEN}📁 Caminho: ${target_dir}${NC}"
