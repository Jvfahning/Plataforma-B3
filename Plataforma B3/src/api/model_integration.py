import aiohttp
from typing import List, Dict, Any, Optional
import json
from urllib.parse import urlparse
from .flow_manager import Flow, FlowStep

class ModelIntegration:
    def __init__(self, api_key: str, model_url: str):
        if not api_key:
            raise ValueError("API_KEY não pode ser vazia")
        
        try:
            parsed_url = urlparse(model_url)
            if not all([parsed_url.scheme, parsed_url.netloc]):
                raise ValueError("URL do modelo inválida")
        except Exception as e:
            raise ValueError(f"URL do modelo inválida: {str(e)}")
        
        self.api_key = api_key
        self.model_url = model_url
        self.headers = {
            "Content-Type": "application/json",
            "api-key": api_key
        }

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        model: str = "gpt4o",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Realiza uma chamada para o modelo de IA.
        
        Args:
            messages: Lista de mensagens para o chat
            temperature: Nível de criatividade do modelo
            model: Nome do modelo a ser utilizado
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
            "max_tokens": kwargs.get("max_tokens", 3000),
            "stop": kwargs.get("stop", "\n"),
            "model": model,
            "stream": False
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.model_url,
                    headers=self.headers,
                    json=payload,
                    timeout=30
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"Erro na chamada ao modelo: {error_text}")
                    
                    return await response.json()
        except aiohttp.ClientError as e:
            raise Exception(f"Erro na conexão com o modelo: {str(e)}")
        except Exception as e:
            raise Exception(f"Erro ao processar resposta do modelo: {str(e)}")

    async def process_flow(
        self,
        user_message: str,
        flow: Flow,
        temperature: float = 0.7,
        model: str = "gpt4o"
    ) -> Dict[str, Any]:
        """
        Processa uma mensagem do usuário através de um fluxo de passos.
        
        Args:
            user_message: Mensagem do usuário
            flow: Fluxo de processamento
            temperature: Nível de criatividade do modelo
            model: Nome do modelo a ser utilizado
            
        Returns:
            Respostas de cada passo do fluxo
        """
        if not user_message:
            raise ValueError("A mensagem do usuário não pode estar vazia")
        
        if not flow.is_active:
            raise ValueError("O fluxo está inativo")

        # Ordena os passos
        sorted_steps = sorted(flow.steps, key=lambda x: x.step_order)
        
        # Inicializa a lista de mensagens com a mensagem do usuário
        messages = [{"role": "user", "content": user_message}]
        responses = {}

        # Processa cada passo do fluxo
        for step in sorted_steps:
            # Adiciona o system prompt do passo atual
            step_messages = [
                {"role": "system", "content": step.system_prompt}
            ] + messages

            # Faz a chamada ao modelo
            response = await self.chat_completion(
                messages=step_messages,
                temperature=temperature,
                model=model
            )

            # Extrai a resposta do assistente
            assistant_message = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # Adiciona a resposta do assistente à lista de mensagens
            messages.append({"role": "assistant", "content": assistant_message})
            
            # Armazena a resposta do passo
            responses[step.step_name] = {
                "response": response,
                "assistant_message": assistant_message
            }

        return {
            "flow_name": flow.name,
            "steps": responses,
            "final_response": messages[-1]["content"] if messages else None
        } 