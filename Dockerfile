FROM python:3.11-slim

WORKDIR /app

# Instalar dependências de sistema necessárias para PostgreSQL e GeoPandas
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gdal-bin \
    libgdal-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "ui.py", "--server.address=0.0.0.0", "--server.port=8501"]
