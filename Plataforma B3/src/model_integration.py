import json
import aiohttp
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse
import logging

from flow_manager import Flow, FlowStep
from config import settings

# Configuração básica de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelIntegration:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("API_KEY não pode ser vazia")
        
        self.api_key = api_key
        self.model_url = settings.MODEL_URL
        
        # Valida a URL do modelo
        self._validate_model_url(self.model_url)
        
        self.headers = {
            "Content-Type": "application/json",
            "api-key": api_key
        }
        
        # Valida a conexão com o modelo
        self._validate_connection()

    def _validate_model_url(self, url: str):
        """Valida a URL do modelo."""
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise ValueError("URL do modelo inválida")

    def _validate_connection(self):
        """Valida a conexão com o modelo."""
        try:
            self._validate_model_url(self.model_url)
        except Exception as e:
            raise ValueError(f"Erro ao validar URL do modelo: {str(e)}")

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 100,
        **kwargs
    ) -> Dict[str, Any]:
        """Realiza uma chamada de conclusão de chat ao modelo."""
        # Validação dos parâmetros
        if not messages:
            raise ValueError("A lista de mensagens não pode estar vazia")
        
        if not isinstance(temperature, (int, float)) or not 0 <= temperature <= 1:
            raise ValueError("Temperatura deve ser um número entre 0 e 1")
        
        payload = {
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": kwargs.get("top_p", 0.9),
            "frequency_penalty": kwargs.get("frequency_penalty", 1.0),
            "presence_penalty": kwargs.get("presence_penalty", 0.5),
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.model_url,
                    headers=self.headers,
                    json=payload
                ) as response:
                    if response.status == 401:
                        raise ValueError("Erro de autenticação: Chave de API inválida ou endpoint incorreto")
                    elif response.status == 404:
                        raise ValueError("Endpoint não encontrado. Verifique a URL do modelo")
                    elif response.status != 200:
                        error_text = await response.text()
                        raise ValueError(f"Erro na chamada ao modelo: {error_text}")
                    
                    response_data = await response.json()
                    return response_data
                    
        except aiohttp.ClientError as e:
            logger.error(f"Erro de conexão: {str(e)}")
            raise ValueError(f"Erro de conexão: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao processar resposta do modelo: {str(e)}")
            raise ValueError(f"Erro ao processar resposta do modelo: {str(e)}")
        except Exception as e:
            logger.error(f"Erro inesperado: {str(e)}")
            raise ValueError(f"Erro inesperado: {str(e)}")

    async def process_flow(
        self,
        user_message: str,
        flow: Flow
    ) -> Dict[str, Any]:
        """Processa uma mensagem de usuário através de um fluxo."""
        if not user_message:
            raise ValueError("A mensagem do usuário não pode estar vazia")
        
        if not flow or not flow.steps:
            raise ValueError("O fluxo deve ter pelo menos um passo")
        
        if not flow.is_active:
            raise ValueError("O fluxo não está ativo")
        
        # Ordena os passos
        sorted_steps = sorted(flow.steps, key=lambda x: x.step_order)
        
        # Inicializa a lista de mensagens
        messages = []
        last_response = user_message
        step_responses = {}
        
        # Processa cada passo
        for step in sorted_steps:
            # Cria a mensagem para o passo atual
            messages = [
                {"role": "system", "content": step.system_prompt},
                {"role": "user", "content": last_response}
            ]
            
            try:
                # Chama o modelo
                response = await self.chat_completion(
                    messages=messages,
                    temperature=step.temperature,
                    max_tokens=step.max_tokens
                )
                
                # Extrai a resposta do assistente
                assistant_message = response["choices"][0]["message"]["content"]
                
                # Armazena a resposta
                step_responses[step.step_name] = {
                    "assistant_message": assistant_message,
                    "messages": messages
                }
                
                # Atualiza a última resposta para o próximo passo
                last_response = assistant_message
                
            except Exception as e:
                logger.error(f"Erro ao processar passo '{step.step_name}': {str(e)}")
                raise ValueError(f"Erro ao processar passo '{step.step_name}': {str(e)}")
        
        return {
            "flow_name": flow.name,
            "steps": step_responses,
            "final_response": last_response
        }