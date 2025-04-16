import streamlit as st
import os
from typing import List, Dict
from dotenv import load_dotenv
from api.flow_manager import Flow, FlowStep, FlowManager
from api.model_integration import ModelIntegration
from config import settings
from database import get_db
from sqlalchemy.orm import Session
import traceback

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
        api_key=settings.API_KEY,
        model_url=settings.MODEL_URL
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

def test_flow(flow: Flow, steps: List[Dict], db: Session):
    """Testa um fluxo"""
    st.subheader("Teste do Fluxo")
    user_message = st.text_area("Digite a mensagem para testar")
    
    if st.button("Testar"):
        try:
            with st.spinner("Processando..."):
                result = model_client.process_flow(
                    user_message=user_message,
                    flow=flow,
                    temperature=steps[0]["temperature"]
                )
            
            st.success("Teste concluído!")
            
            # Mostra as respostas de cada passo
            for step_name, step_result in result["steps"].items():
                with st.expander(f"Passo: {step_name}"):
                    st.write(step_result["assistant_message"])
            
            # Mostra a resposta final
            st.subheader("Resposta Final")
            st.write(result["final_response"])
            
            # Botão para salvar
            if st.button("Salvar Fluxo"):
                try:
                    flow_manager = FlowManager(db)
                    flow_id = f"flow_{len(flow_manager.list_flows()) + 1}"
                    flow_manager.create_flow(flow_id, flow)
                    st.success(f"Fluxo salvo com ID: {flow_id}")
                except Exception as e:
                    st.error(f"Erro ao salvar fluxo: {str(e)}")
                
        except Exception as e:
            st.error(f"Erro ao testar fluxo: {str(e)}")
            if settings.DEBUG:
                st.text(traceback.format_exc())

def main():
    st.title(f"🤖 {settings.APP_NAME}")
    
    # Obtém a sessão do banco de dados
    try:
        db = next(get_db())
        flow_manager = FlowManager(db)
    except Exception as e:
        st.error(f"Erro ao conectar ao banco de dados: {str(e)}")
        st.stop()
    
    # Formulário para criar fluxo
    with st.form("flow_form"):
        st.subheader("Informações do Fluxo")
        flow_name = st.text_input("Nome do Fluxo")
        flow_description = st.text_area("Descrição do Fluxo")
        
        # Lista de passos
        steps = []
        num_steps = st.number_input(
            "Número de Passos",
            min_value=1,
            max_value=10,
            value=2
        )
        
        for i in range(num_steps):
            step = create_flow_step(i + 1)
            steps.append(step)
        
        # Botões de ação
        col1, col2 = st.columns(2)
        with col1:
            test_button = st.form_submit_button("Testar Fluxo")
        with col2:
            save_button = st.form_submit_button("Salvar Fluxo")
    
    # Processa o formulário
    if test_button or save_button:
        try:
            # Validação básica
            if not flow_name:
                st.error("O nome do fluxo é obrigatório")
                return
            
            if not all(step["step_name"] and step["system_prompt"] for step in steps):
                st.error("Todos os passos devem ter nome e prompt")
                return
            
            # Cria o fluxo
            flow = Flow(
                name=flow_name,
                description=flow_description,
                steps=[
                    FlowStep(
                        system_prompt=step["system_prompt"],
                        step_name=step["step_name"],
                        step_order=step["step_order"]
                    )
                    for step in steps
                ]
            )
            
            if test_button:
                test_flow(flow, steps, db)
            elif save_button:
                flow_id = f"flow_{len(flow_manager.list_flows()) + 1}"
                flow_manager.create_flow(flow_id, flow)
                st.success(f"Fluxo salvo com sucesso! ID: {flow_id}")
        except Exception as e:
            st.error(f"Erro ao processar formulário: {str(e)}")
            if settings.DEBUG:
                st.text(traceback.format_exc())
    
    # Lista de fluxos existentes
    st.subheader("Fluxos Existentes")
    try:
        flows = flow_manager.list_flows()
        if flows:
            for flow in flows:
                with st.expander(f"{flow['name']} (ID: {flow['id']})"):
                    st.write(f"Descrição: {flow['description']}")
                    st.write(f"Número de passos: {flow['steps_count']}")
                    st.write(f"Status: {'Ativo' if flow['is_active'] else 'Inativo'}")
                    
                    # Botões de ação para cada fluxo
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"Testar {flow['name']}", key=f"test_{flow['id']}"):
                            try:
                                flow_obj = flow_manager.get_flow(flow['id'])
                                test_flow(flow_obj, flow_obj.steps, db)
                            except Exception as e:
                                st.error(f"Erro ao testar fluxo: {str(e)}")
                    with col2:
                        if st.button(f"Deletar {flow['name']}", key=f"delete_{flow['id']}"):
                            try:
                                flow_manager.delete_flow(flow['id'])
                                st.success(f"Fluxo {flow['name']} deletado com sucesso!")
                                st.experimental_rerun()
                            except Exception as e:
                                st.error(f"Erro ao deletar fluxo: {str(e)}")
        else:
            st.info("Nenhum fluxo criado ainda.")
    except Exception as e:
        st.error(f"Erro ao listar fluxos: {str(e)}")
        if settings.DEBUG:
            st.text(traceback.format_exc())

if __name__ == "__main__":
    main() 