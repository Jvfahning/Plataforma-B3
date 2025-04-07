# Usa a imagem oficial do Python
FROM python:3.9-slim

# Define o diretório de trabalho
WORKDIR /app

# Instala as dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copia os arquivos de requisitos
COPY requirements.txt .

# Instala as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY . .

# Expõe a porta 8000
EXPOSE 8000

# Define as variáveis de ambiente
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Comando para executar a aplicação
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 