# Usar uma imagem leve do Python
FROM python:3.11-slim

# Instalar dependências de sistema necessárias (ex: compilação, geospacial)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar e instalar dependências do Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo o código-fonte para o container
COPY . .

# Expor a porta padrão do Streamlit
EXPOSE 8501

# Configurações do Healthcheck para monitorar o container
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Comando para iniciar a aplicação Streamlit
CMD ["streamlit", "run", "prime_dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
