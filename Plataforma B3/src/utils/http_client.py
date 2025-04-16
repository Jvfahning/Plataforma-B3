import aiohttp
from typing import Dict, Any, Optional

async def make_post_request(
    url: str,
    headers: Dict[str, str],
    data: Dict[str, Any],
    timeout: Optional[int] = 30
) -> Dict[str, Any]:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                headers=headers,
                json=data,
                timeout=timeout
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Erro na requisição HTTP: {error_text}")
                
                return await response.json()
    except Exception as e:
        raise Exception(f"Erro ao realizar requisição HTTP: {str(e)}")

def prepare_headers(api_key: str) -> Dict[str, str]:
    return {
        "Content-Type": "application/json",
        "api-key": api_key
    } 