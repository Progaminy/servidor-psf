.PHONY: help setup up down psf-status criar listar

help:
	@echo "🌐 PSF Platform CLI - Makefile Shortcuts"
	@echo "----------------------------------------"
	@echo "  make setup     - Prepara permissões +x e ambiente"
	@echo "  make up        - Inicia a infraestrutura (Nginx + Portal)"
	@echo "  make down      - Para todos os serviços da plataforma"
	@echo "  make status    - Exibe o status da plataforma e projetos"
	@echo "  make listar    - Lista todos os projetos .psf ativos"
	@echo "  make criar NOME=app STACK=node PORTA=8081"

setup:
	@chmod +x scripts/*.sh 2>/dev/null || true
	@echo "✅ Permissões dos scripts atualizadas (+x)."

up: setup
	docker compose -f docker-compose.psf.yml up -d

down:
	docker compose -f docker-compose.psf.yml down

status: setup
	@bash ./scripts/psf.sh status

listar: setup
	@bash ./scripts/psf.sh listar

criar: setup
	@if [ -z "$(NOME)" ]; then echo "❌ Erro: Especifique NOME=exemplo"; exit 1; fi
	@bash ./scripts/psf.sh criar $(NOME) $(or $(STACK),node) $(or $(PORTA),8080)
