from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
import os
from dotenv import load_dotenv
import aiohttp
import asyncio
from src.api.flow_manager import Flow, FlowStep, FlowManager

# Carrega variáveis de ambiente
load_dotenv()

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

async def process_flow(user_message: str, flow: Flow):
    api_key = os.getenv("API_KEY")
    model_url = os.getenv("MODEL_URL")
    
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key
    }

    sorted_steps = sorted(flow.steps, key=lambda x: x.step_order)
    messages = [{"role": "user", "content": user_message}]
    responses = {}

    async with aiohttp.ClientSession() as session:
        for step in sorted_steps:
            step_messages = [
                {"role": "system", "content": step.system_prompt}
            ] + messages

            payload = {
                "messages": step_messages,
                "temperature": 0.7,
                "top_p": 0.9,
                "frequency_penalty": 1.0,
                "presence_penalty": 0.5,
                "max_tokens": 3000,
                "stop": "\n",
                "model": "gpt4o",
                "stream": False
            }

            async with session.post(model_url, headers=headers, json=payload) as response:
                if response.status != 200:
                    raise Exception(f"Erro na chamada ao modelo: {await response.text()}")
                step_response = await response.json()
                assistant_message = step_response.get("choices", [{}])[0].get("message", {}).get("content", "")
                messages.append({"role": "assistant", "content": assistant_message})
                responses[step.step_name] = {
                    "response": step_response,
                    "assistant_message": assistant_message
                }

    return {
        "flow_name": flow.name,
        "steps": responses,
        "final_response": messages[-1]["content"] if messages else None
    }

def process_chat_messages(**context):
    flow_manager = FlowManager()
    flow = Flow(
        name="Análise de ESG",
        description="Fluxo para análise de ESG em empresas",
        steps=[
            FlowStep(
                system_prompt="Você é um especialista em análise de mercado. Analise a pergunta e forneça uma resposta detalhada.",
                step_name="análise_geral",
                step_order=1
            ),
            FlowStep(
                system_prompt="Você é um especialista em ESG. Revise a resposta anterior e adicione insights específicos sobre ESG.",
                step_name="análise_esg",
                step_order=2
            ),
            FlowStep(
                system_prompt="Você é um especialista em recomendações. Baseado nas análises anteriores, forneça recomendações práticas.",
                step_name="recomendações",
                step_order=3
            )
        ]
    )

    user_message = "Qual é o impacto do ESG nas empresas brasileiras?"
    
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(process_flow(user_message, flow))
    
    print("Processamento concluído:")
    print("Respostas dos passos:", result["steps"])
    print("Resposta final:", result["final_response"])

# Define o DAG
dag = DAG(
    'b3_chat_processing',
    default_args=default_args,
    description='DAG para processamento de mensagens do chat B3 com fluxos personalizados',
    schedule_interval=timedelta(hours=1),
    start_date=days_ago(1),
    catchup=False,
)

# Define a tarefa
process_task = PythonOperator(
    task_id='process_chat_messages',
    python_callable=process_chat_messages,
    dag=dag,
)

# Define as dependências
process_task 