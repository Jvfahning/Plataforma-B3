import streamlit as st
from openai import OpenAI
import os

# ⚠️ Ideal: usar variável de ambiente para segurança
client = OpenAI(api_key="sk-proj-34g6vxddqvYemlu1V47PT3BlbkFJrTyoQHZ4YKiqpU9bi4HS")

if "history" not in st.session_state:
    st.session_state.history = []

def enviar_mensagem(messages):
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            temperature=0.8,
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erro na resposta: {str(e)}"

prompt = st.text_area("Digite sua dúvida ou código:", height=200)

if st.button("Enviar"):
    if prompt:
        st.session_state.history.append({"role": "user", "content": prompt})

        with st.spinner("Aguarde, estou processando sua solicitação..."):
            resposta = enviar_mensagem(st.session_state.history)

        st.session_state.history.append({"role": "assistant", "content": resposta})
        st.write(f"**Assistente:** {resposta}")
    else:
        st.warning("Por favor, insira uma dúvida ou código.")

if st.button("Resetar Conversa"):
    st.session_state.history.clear()
    st.success("Histórico resetado.")

with st.expander("Histórico da Conversa"):
    for msg in st.session_state.history:
        role = "Usuário" if msg["role"] == "user" else "Assistente"
        st.write(f"**{role}:** {msg['content']}")
