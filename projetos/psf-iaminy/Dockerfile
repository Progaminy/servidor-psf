FROM python:3.11-slim

WORKDIR /app

# Copiar arquivos do projeto PSF-IAminy
COPY . .

# Variáveis de ambiente
ENV HOST=0.0.0.0
ENV PORT=8765

EXPOSE 8765

CMD ["python3", "-m", "interface.servidor", "8765"]
