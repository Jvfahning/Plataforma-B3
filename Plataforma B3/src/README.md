# Plataforma B3

API para gerenciamento de workflows e módulos de IA.

## Requisitos

- Python 3.9+
- Docker (opcional)
- Conta no Azure com os seguintes serviços:
  - Azure Cosmos DB
  - Azure Blob Storage
  - Azure Search
  - Azure OpenAI

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/plataforma-b3.git
cd plataforma-b3
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env com suas credenciais
```

## Executando a Aplicação

### Localmente

```bash
uvicorn main:app --reload
```

### Com Docker

```bash
docker build -t plataforma-b3 .
docker run -p 8000:8000 --env-file .env plataforma-b3
```


## Estrutura do Projeto

```
src/
├── auth/           # Autenticação e autorização
├── database/       # Configuração e modelos do banco de dados
├── ia_modules/     # Módulos de IA
├── orchestration/  # Orquestração de workflows
├── workflows/      # Gerenciamento de workflows
├── main.py         # Ponto de entrada da aplicação
└── requirements.txt # Dependências do projeto
```

## Funcionalidades

- Gerenciamento de usuários
- Criação e execução de workflows
- Integração com módulos de IA
- Processamento de documentos
- Análise de sentimentos
- Geração de imagens
- Processamento de PDFs
