import os
import asyncio
import traceback
from typing import List, Dict, Any

import streamlit as st
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.collection import Collection
from sqlalchemy.orm import Session

from src.api.flow_manager import Flow, FlowStep, FlowManager
from src.api.model_integration import ModelIntegration
from src.config import settings
from src.database import get_db

# Carrega as variáveis de ambiente
load_dotenv()

# Configuração da página
st.set_page_config(
    page_title=settings.APP_NAME,
    page_icon="🤖",
    layout="wide"
)

# Verifica se o diretório data existe
if not os.path.exists("data"):
    os.makedirs("data")

# Inicializa o cliente do modelo
try:
    model_client = ModelIntegration(
        api_key=settings.UFPB_OPENAI_API_KEY
    )
except Exception as e:
    st.error(f"Erro ao inicializar o cliente do modelo: {str(e)}")
    st.stop()

def create_flow_step(step_number: int) -> Dict:
    """Cria um passo do fluxo"""
    st.subheader(f"Passo {step_number}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        step_name = st.text_input(
            "Nome do passo",
            key=f"step_name_{step_number}",
            placeholder="ex: analise_geral"
        )
    
    with col2:
        temperature = st.slider(
            "Temperatura",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1,
            key=f"temperature_{step_number}"
        )
    
    system_prompt = st.text_area(
        "System Prompt",
        key=f"system_prompt_{step_number}",
        placeholder="Digite o prompt do sistema para este passo"
    )
    
    return {
        "step_name": step_name,
        "temperature": temperature,
        "system_prompt": system_prompt,
        "step_order": step_number
    }

def test_flow(db: Collection):
    """Interface para testar um fluxo"""
    st.subheader("Testar Fluxo")
    
    # Lista de fluxos ativos
    flows = list(db.find({"is_active": True}))
    if not flows:
        st.warning("Nenhum fluxo ativo encontrado")
        return
    
    flow_names = [flow["name"] for flow in flows]
    selected_flow_name = st.selectbox("Selecione o fluxo", flow_names)
    
    # Encontra o fluxo selecionado
    selected_flow = next((flow for flow in flows if flow["name"] == selected_flow_name), None)
    if not selected_flow:
        st.error("Fluxo não encontrado")
        return
    
    print(f"Fluxo selecionado: {selected_flow}")
    
    # Campo para a mensagem do usuário
    user_message = st.text_area("Mensagem para testar")
    
    # Slider para temperatura
    temperature = st.slider("Temperatura", 0.0, 1.0, 0.7, 0.1)
    
    if st.button("Testar"):
        try:
            print("Iniciando teste do fluxo...")
            # Inicializa o cliente do modelo
            model_client = ModelIntegration(api_key=settings.UFPB_OPENAI_API_KEY)
            print("Cliente do modelo inicializado")
            
            # Processa o fluxo
            result = asyncio.run(model_client.process_flow(
                user_message=user_message,
                flow=selected_flow,
                temperature=temperature
            ))
            print(f"Resultado do processamento: {result}")
            
            # Exibe o resultado final
            st.subheader("Resposta Final")
            st.write(result["final_response"])
            
            # Exibe os resultados de cada passo
            st.subheader("Resultados por Passo")
            for step_name, step_result in result["steps"].items():
                with st.expander(f"Passo: {step_name}"):
                    st.write(step_result["assistant_message"])
                    
        except Exception as e:
            print(f"Erro durante o teste: {str(e)}")
            st.error(f"Erro ao testar o fluxo: {str(e)}")

def main():
    st.title(f"🤖 {settings.APP_NAME}")
    
    # Obtém a sessão do banco de dados
    try:
        db = next(get_db())
        flow_manager = FlowManager(db)
    except Exception as e:
        st.error(f"Erro ao conectar ao banco de dados: {str(e)}")
        st.stop()
    
    # Sidebar para navegação
    page = st.sidebar.radio(
        "Navegação",
        ["Criar Fluxo", "Testar Fluxo"]
    )

    if page == "Criar Fluxo":
        st.header("Criar Novo Fluxo")
        
        # Formulário para criar fluxo
        with st.form("create_flow_form"):
            flow_id = st.text_input("ID do Fluxo (apenas letras, números e underscores)")
            flow_name = st.text_input("Nome do Fluxo")
            flow_description = st.text_area("Descrição do Fluxo")
            
            # Seção para adicionar passos
            st.subheader("Passos do Fluxo")
            
            # Inicializa a lista de passos na sessão se não existir
            if 'steps' not in st.session_state:
                st.session_state.steps = []
            
            # Mostra os passos já adicionados
            if st.session_state.steps:
                st.subheader("Passos Adicionados")
                for i, step in enumerate(st.session_state.steps):
                    st.write(f"Passo {step['step_order']}: {step['step_name']}")
            
            # Botão para salvar fluxo
            if st.form_submit_button("Salvar Fluxo"):
                try:
                    # Cria o objeto Flow
                    flow = Flow(
                        name=flow_name,
                        description=flow_description,
                        steps=[FlowStep(**step) for step in st.session_state.steps],
                        is_active=True
                    )
                    
                    # Salva no banco
                    flow_manager.create_flow(flow_id, flow)
                    st.success("Fluxo criado com sucesso!")
                    # Limpa os passos após salvar
                    st.session_state.steps = []
                    
                except Exception as e:
                    st.error(f"Erro ao criar fluxo: {str(e)}")

        # Formulário para adicionar passos (fora do formulário principal)
        with st.form("add_step_form"):
            st.subheader("Adicionar Novo Passo")
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                step_name = st.text_input("Nome do Passo")
            with col2:
                step_order = st.number_input("Ordem", min_value=1, value=1)
            with col3:
                system_prompt = st.text_area("System Prompt")
            
            if st.form_submit_button("Adicionar Passo"):
                if step_name and system_prompt:
                    st.session_state.steps.append({
                        "step_name": step_name,
                        "step_order": step_order,
                        "system_prompt": system_prompt
                    })
                    st.success("Passo adicionado com sucesso!")
                    st.experimental_rerun()

    elif page == "Testar Fluxo":
        st.header("Testar Fluxo")
        
        # Lista de fluxos disponíveis
        flows = flow_manager.list_flows()
        if not flows:
            st.warning("Nenhum fluxo cadastrado. Crie um fluxo primeiro.")
        else:
            # Seleção do fluxo
            flow_options = {f"{flow['name']} ({flow['id']})": flow['id'] for flow in flows}
            selected_flow = st.selectbox(
                "Selecione um fluxo para testar",
                options=list(flow_options.keys())
            )
            
            if selected_flow:
                flow_id = flow_options[selected_flow]
                flow = flow_manager.get_flow(flow_id)
                
                # Mostra informações do fluxo
                st.subheader("Informações do Fluxo")
                st.write(f"**Nome:** {flow.name}")
                st.write(f"**Descrição:** {flow.description}")
                st.write(f"**Número de Passos:** {len(flow.steps)}")
                
                # Lista os passos
                st.subheader("Passos do Fluxo")
                for step in sorted(flow.steps, key=lambda x: x.step_order):
                    st.write(f"**Passo {step.step_order}:** {step.step_name}")
                    st.write(f"**Prompt:** {step.system_prompt}")
                    st.write("---")
                
                # Formulário para testar o fluxo
                with st.form("test_flow_form"):
                    user_message = st.text_area("Digite sua mensagem")
                    temperature = st.slider("Temperatura", 0.0, 1.0, 0.7)
                    
                    if st.form_submit_button("Processar"):
                        try:
                            # Processa o fluxo
                            result = asyncio.run(
                                model_client.process_flow(
                                    user_message=user_message,
                                    flow=flow,
                                    temperature=temperature
                                )
                            )
                            
                            # Mostra as respostas
                            st.subheader("Respostas")
                            for step_name, step_response in result["steps"].items():
                                with st.expander(f"Resposta do passo: {step_name}"):
                                    st.write(step_response["assistant_message"])
                            
                            # Mostra a resposta final
                            st.success(f"Resposta final: {result['final_response']}")
                            
                        except Exception as e:
                            st.error(f"Erro ao processar fluxo: {str(e)}")

if __name__ == "__main__":
    main() 