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

def create_flow_step(step_number: int, step_data: Dict = None) -> Dict:
    """Cria ou edita um passo do fluxo"""
    st.subheader(f"Passo {step_number}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        step_name = st.text_input(
            "Nome do passo",
            value=step_data["step_name"] if step_data else "",
            key=f"step_name_{step_number}",
            placeholder="ex: analise_geral"
        )
    
    with col2:
        temperature = st.slider(
            "Temperatura",
            min_value=0.0,
            max_value=1.0,
            value=step_data["temperature"] if step_data else 0.7,
            step=0.1,
            key=f"temperature_{step_number}"
        )
    
    system_prompt = st.text_area(
        "System Prompt",
        value=step_data["system_prompt"] if step_data else "",
        key=f"system_prompt_{step_number}",
        placeholder="Digite o prompt do sistema para este passo"
    )
    
    max_tokens = st.number_input(
        "Máximo de Tokens",
        min_value=1,
        value=step_data["max_tokens"] if step_data else 100,
        key=f"max_tokens_{step_number}"
    )
    
    return {
        "step_name": step_name,
        "temperature": temperature,
        "system_prompt": system_prompt,
        "max_tokens": max_tokens,
        "step_order": step_number
    }

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
        ["Criar Fluxo", "Gerenciar Fluxos"]
    )

    if page == "Criar Fluxo":
        st.header("Criar Novo Fluxo")
        
        # Formulário para criar fluxo
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
        
        # Formulário para adicionar passos
        st.subheader("Adicionar Novo Passo")
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            step_name = st.text_input("Nome do Passo")
        with col2:
            step_order = st.number_input("Ordem", min_value=1, value=1)
        with col3:
            system_prompt = st.text_area("System Prompt")
        
        temperature = st.slider(
            "Temperatura",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1,
            key=f"temperature_{step_order}"
        )
        
        max_tokens = st.number_input(
            "Máximo de Tokens",
            min_value=1,
            value=100,
            key=f"max_tokens_{step_order}"
        )
        
        if st.button("Adicionar Passo"):
            if step_name and system_prompt:
                st.session_state.steps.append({
                    "step_name": step_name,
                    "step_order": step_order,
                    "system_prompt": system_prompt,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                })
                st.success("Passo adicionado com sucesso!")

        # Botão para salvar fluxo
        if st.button("Salvar Fluxo"):
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

    elif page == "Gerenciar Fluxos":
        st.header("Gerenciar Fluxos")
        
        # Lista de fluxos disponíveis
        flows = flow_manager.list_flows()
        if not flows:
            st.warning("Nenhum fluxo cadastrado. Crie um fluxo primeiro.")
        else:
            # Seleção do fluxo
            flow_options = {f"{flow['name']} ({flow['id']})": flow['id'] for flow in flows}
            selected_flow = st.selectbox(
                "Selecione um fluxo para gerenciar",
                options=list(flow_options.keys())
            )
            
            if selected_flow:
                flow_id = flow_options[selected_flow]
                flow = flow_manager.get_flow(flow_id)
                
                # Verifica se estamos no modo de edição
                if 'editing_flow' not in st.session_state:
                    st.session_state.editing_flow = False
                
                if st.session_state.editing_flow:
                    st.subheader("Editar Fluxo")
                    flow_name = st.text_input("Nome do Fluxo", value=flow.name)
                    flow_description = st.text_area("Descrição do Fluxo", value=flow.description)
                    
                    # Editar passos
                    st.subheader("Editar Passos")
                    edited_steps = []
                    for step in flow.steps:
                        edited_step = create_flow_step(step.step_order, step_data=step.__dict__)
                        edited_steps.append(edited_step)
                    
                    if st.button("Salvar Alterações"):
                        try:
                            updated_flow = Flow(
                                name=flow_name,
                                description=flow_description,
                                steps=[FlowStep(**step) for step in edited_steps],
                                is_active=True
                            )
                            flow_manager.update_flow(flow_id, updated_flow)
                            st.success("Fluxo atualizado com sucesso!")
                            st.session_state.editing_flow = False
                        except Exception as e:
                            st.error(f"Erro ao atualizar fluxo: {str(e)}")
                    
                    if st.button("Cancelar"):
                        st.session_state.editing_flow = False
                else:
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
                    
                    # Botões para editar, excluir ou testar o fluxo
                    if st.button("Editar Fluxo"):
                        st.session_state.editing_flow = True
                    
                    if st.button("Excluir Fluxo"):
                        try:
                            flow_manager.delete_flow(flow_id)
                            st.success("Fluxo excluído com sucesso!")
                        except Exception as e:
                            st.error(f"Erro ao excluir fluxo: {str(e)}")
                    
                    if st.button("Testar Fluxo"):
                        st.subheader("Testar Fluxo")
                        user_message = st.text_area("Digite sua mensagem de teste")
                        if st.button("Executar Teste"):
                            if user_message.strip() == "":
                                st.error("Por favor, digite uma mensagem de teste.")
                            else:
                                with st.spinner("Executando teste..."):
                                    try:
                                        # Usar asyncio.run pode não ser ideal em alguns ambientes, então vamos tentar uma abordagem diferente
                                        loop = asyncio.new_event_loop()
                                        asyncio.set_event_loop(loop)
                                        result = loop.run_until_complete(
                                            model_client.process_flow(
                                                user_message=user_message,
                                                flow=flow
                                            )
                                        )
                                        loop.close()

                                        st.subheader("Respostas")
                                        for step_name, step_response in result["steps"].items():
                                            with st.expander(f"Resposta do passo: {step_name}"):
                                                st.write(step_response["assistant_message"])

                                        st.success(f"Resposta final: {result['final_response']}")
                                    except Exception as e:
                                        st.error(f"Erro ao testar fluxo: {str(e)}")

if __name__ == "__main__":
    main() 
