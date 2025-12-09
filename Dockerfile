FROM python:3.11-slim

# Definir diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Criar diretório para dados
RUN mkdir -p /app/data

# Definir variáveis de ambiente
ENV FLASK_ENV=production
ENV PYTHONPATH=/app/src

# Expor porta
EXPOSE 5000

# Comando para inicializar e executar a aplicação
CMD ["sh", "-c", "cd src && python init_production.py && gunicorn app_production:app --bind 0.0.0.0:5000 --workers 4 --timeout 120"]
