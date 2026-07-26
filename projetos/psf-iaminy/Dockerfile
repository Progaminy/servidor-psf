FROM python:3.11-slim

WORKDIR /app

COPY . .

ENV HOST=0.0.0.0
ENV PORT=8765
ENV PYTHONPATH=/app

EXPOSE 8765

CMD ["python3", "-m", "interface.servidor", "8765"]
