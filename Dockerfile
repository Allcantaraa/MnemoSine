# Usa a imagem oficial e mais leve do Python 3.13
FROM python:3.13-slim

# Evita que o Python crie arquivos .pyc e força os logs a aparecerem no terminal
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instala as ferramentas do Linux necessárias para compilar o mysqlclient perfeitamente
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Define a pasta onde o projeto vai morar dentro do container
WORKDIR /app

# Copia a lista de dependências primeiro (otimiza o cache do Docker)
COPY requirements.txt /app/

# Atualiza o pip, instala o requirements e já instala o Gunicorn e WhiteNoise para produção
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install gunicorn whitenoise

# Copia o resto do seu projeto inteiro para dentro do container
COPY . /app/

# Coleta os arquivos estáticos (CSS, JS, Imagens) para uma pasta única
RUN python manage.py collectstatic --noinput

# Avisa o Docker que este container vai se comunicar pela porta 8000
EXPOSE 8000

# O comando mágico que inicia o sistema em modo de produção
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120","--max-requests", "1000", "--max-requests-jitter", "100"]
