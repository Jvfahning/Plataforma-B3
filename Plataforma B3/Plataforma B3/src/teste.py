import requests

BASE_URL = "http://localhost:8000"

def test_create_flow():
    url = f"{BASE_URL}/createFlows/"
    flow_payload = {
        "name": "Fluxo de Teste",
        "description": "Este é um fluxo de teste.",
        "steps": [
            {
                "step_name": "INICIO",
                "model": "gpt-4o",
                "temperature": 0.5,
                "system_prompt": "responda a mensagem apenas com 1,2,3,4",
                "max_tokens": 100,
                "step_order": 1
            },
            {
                "step_name": "FIM",
                "model": "gpt-4o-mini",
                "temperature": 0.5,
                "system_prompt": "adicione 5 e 6 ao final da resposta anterior",
                "max_tokens": 100,
                "step_order": 2
            }
        ]
    }
    response = requests.post(url, json=flow_payload)
    assert response.status_code == 200, f"Erro ao criar fluxo: {response.json()}"
    print("Criar fluxo:", response.status_code, response.json())

def test_get_all_flows():
    url = f"{BASE_URL}/getFlows/"
    response = requests.get(url)
    assert response.status_code == 200, f"Erro ao obter fluxos: {response.json()}"
    print("Obter todos os fluxos:", response.status_code, response.json())

def test_get_flow_by_id(flow_id):
    url = f"{BASE_URL}/getFlowsById/{flow_id}"
    response = requests.get(url)
    assert response.status_code == 200, f"Erro ao obter fluxo: {response.json()}"
    print("Obter fluxo específico:", response.status_code, response.json())

def test_update_flow(flow_id):
    url = f"{BASE_URL}/updateFlows/{flow_id}"
    updated_flow = {
        "name": "Fluxo Atualizado",
        "description": "Descrição atualizada.",
        "steps": [
            {
                "step_name": "INICIO",
                "model": "gpt-4o",
                "temperature": 0.7,
                "system_prompt": "responda apenas com 1234",
                "max_tokens": 150,
                "step_order": 1
            }
        ]
    }
    response = requests.put(url, json=updated_flow)
    assert response.status_code == 200, f"Erro ao atualizar fluxo: {response.json()}"
    print("Atualizar fluxo:", response.status_code, response.json())

def test_exec_flow(flow_id):
    url = f"{BASE_URL}/flows/{flow_id}/exec_flow"
    payload = {
        "user_message": "Olá, me diga a sequência final dos números?"
    }
    response = requests.post(url, json=payload)
    assert response.status_code == 200, f"Erro ao executar fluxo: {response.json()}"
    print("Executar fluxo:", response.status_code, response.json())

def test_delete_flow(flow_id):
    url = f"{BASE_URL}/deleteFlows/{flow_id}"
    response = requests.delete(url)
    assert response.status_code == 200, f"Erro ao deletar fluxo: {response.json()}"
    print("Deletar fluxo:", response.status_code, response.json())

if __name__ == "__main__":
    print("Criar fluxo\n\n")
    test_create_flow()
    print("\n\nObter todos os fluxos\n\n")
    test_get_all_flows()
    print("\n\nObter fluxo específico\n\n")
    test_get_flow_by_id("67")  
    print("\n\nAtualizar fluxo\n\n")
    test_update_flow("67")  
    print("\n\nExecutar fluxo\n\n")
    test_exec_flow("67")  
    print("\n\nDeletar fluxo\n\n")
    test_delete_flow("67")
    print("\n\nObter todos os fluxos após deleção\n\n")
    test_get_all_flows()