FROM python:3.8-slim

WORKDIR /app

# Copia os arquivos de requisitos
COPY requirements.txt .

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código fonte
COPY src/ ./src/

# Expõe a porta que o FastAPI usará
EXPOSE 8000

# Comando para executar a aplicação
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"] 