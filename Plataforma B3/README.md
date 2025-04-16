# Plataforma B3 - Integração com Modelos de IA

Este projeto implementa uma plataforma para integração com modelos de IA, utilizando Streamlit para interface web e SQLite para persistência de dados.

## Estrutura do Projeto

```
├── /src
│   ├── /api
│   │   ├── model_integration.py
│   │   └── flow_manager.py
│   ├── /streamlit_app.py
│   ├── /config.py
│   └── /database.py
├── requirements.txt
└── README.md
```

## Requisitos

- Python 3.8+
- SQLite (já incluído no Python)

## Instalação

1. Clone o repositório
2. Crie um ambiente virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # ou
   .\venv\Scripts\activate  # Windows
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure o ambiente:
   ```bash
   # Copie o arquivo de exemplo
   cp .env.example .env
   
   # Edite o arquivo .env com suas configurações
   # Substitua 'sua_chave_api_aqui' pela sua chave de API real
   ```

## Configuração

O arquivo `.env` deve conter as seguintes variáveis:

```
# Chave de API para acesso ao modelo
API_KEY=sua_chave_api_aqui

# URL do endpoint do modelo
MODEL_URL=https://b3gpt.intraservice.azr/internal-api/b3gpt-llms/v1/openai/deployments/gpt4o/chat/completions

# Configurações do banco de dados (opcional)
DATABASE_URL=sqlite:///./data/flows.db

# Configurações da aplicação
APP_NAME=Plataforma B3 - IA
DEBUG=False
```

## Executando o Projeto

1. Crie o diretório para o banco de dados:
   ```bash
   mkdir data
   ```

2. Execute a interface web:
   ```bash
   streamlit run src/streamlit_app.py
   ```

A interface web oferece:

1. Criação visual de fluxos
2. Configuração de múltiplos passos
3. Teste em tempo real
4. Visualização de fluxos existentes
5. Interface amigável e intuitiva

## Funcionalidades

1. **Criação de Fluxos**:
   - Nome e descrição do fluxo
   - Configuração de múltiplos passos
   - System prompt para cada passo
   - Temperatura configurável

2. **Teste de Fluxos**:
   - Teste em tempo real
   - Visualização de respostas por passo
   - Resposta final consolidada

3. **Gerenciamento de Fluxos**:
   - Listagem de fluxos existentes
   - Teste de fluxos existentes
   - Deleção de fluxos

4. **Persistência**:
   - Armazenamento em banco de dados SQLite
   - Dados mantidos entre execuções
   - Backup automático

## Exemplo de Uso

1. Execute a aplicação:
   ```bash
   streamlit run src/streamlit_app.py
   ```

2. Crie um novo fluxo:
   - Digite o nome e descrição
   - Configure os passos
   - Defina os prompts e temperaturas

3. Teste o fluxo:
   - Digite uma mensagem
   - Veja as respostas de cada passo
   - Analise a resposta final

4. Gerencie fluxos:
   - Visualize fluxos existentes
   - Teste fluxos salvos
   - Delete fluxos quando necessário 