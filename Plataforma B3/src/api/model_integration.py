import json
import aiohttp
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse

from src.api.flow_manager import Flow, FlowStep
from src.config import settings

class ModelIntegration:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("API_KEY não pode ser vazia")
        
        self.api_key = api_key
        self.model_url = settings.MODEL_URL
        
        # Valida a URL do modelo
        parsed_url = urlparse(self.model_url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise ValueError("URL do modelo inválida")
        
        self.headers = {
            "Content-Type": "application/json",
            "api-key": api_key
        }
        
        # Valida a conexão com o modelo
        self._validate_connection()

    def _validate_connection(self):
        """Valida a conexão com o modelo"""
        try:
            parsed_url = urlparse(self.model_url)
            if not parsed_url.scheme or not parsed_url.netloc:
                raise ValueError("URL do modelo inválida")
        except Exception as e:
            raise ValueError(f"Erro ao validar URL do modelo: {str(e)}")

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Realiza uma chamada para o modelo de IA.
        
        Args:
            messages: Lista de mensagens para o chat
            temperature: Nível de criatividade do modelo
            **kwargs: Parâmetros adicionais para a requisição
            
        Returns:
            Resposta do modelo em formato JSON
        """
        # Validação dos parâmetros
        if not messages:
            raise ValueError("A lista de mensagens não pode estar vazia")
        
        if not isinstance(temperature, (int, float)) or not 0 <= temperature <= 1:
            raise ValueError("Temperatura deve ser um número entre 0 e 1")
        
        payload = {
            "messages": messages,
            "temperature": temperature,
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
            raise ValueError(f"Erro de conexão: {str(e)}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Erro ao processar resposta do modelo: {str(e)}")
        except Exception as e:
            raise ValueError(f"Erro inesperado: {str(e)}")

    async def process_flow(
        self,
        user_message: str,
        flow: Flow,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Processa um fluxo de passos com o modelo de IA.
        
        Args:
            user_message: Mensagem do usuário
            flow: Objeto Flow com os passos
            temperature: Nível de criatividade do modelo
            
        Returns:
            Resposta do fluxo com as respostas de cada passo
        """
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
                    temperature=temperature
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
                raise ValueError(f"Erro ao processar passo '{step.step_name}': {str(e)}")
        
        return {
            "flow_name": flow.name,
            "steps": step_responses,
            "final_response": last_response
        } 