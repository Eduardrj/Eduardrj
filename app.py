# agente_multifuncional_gradio.py

import gradio as gr
import os

# ====== Configurações de modelos ======
def gerar_resposta_openai(prompt):
    import openai
    openai.api_key = os.getenv("OPENAI_API_KEY")
    try:
        resposta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return resposta.choices[0].message.content.strip()
    except Exception as e:
        return f"Erro OpenAI: {str(e)}"

def gerar_resposta_hf(prompt):
    from transformers import pipeline
    try:
        generator = pipeline("text-generation", model="tiiuae/falcon-7b-instruct")
        resultado = generator(prompt, max_length=200, do_sample=True)
        return resultado[0]['generated_text']
    except Exception as e:
        return f"Erro HF: {str(e)}"

# ====== Agentes especializadas ======
def agente_pesquisador(prompt, modelo):
    return f"[Pesquisador]: {escolher_modelo(prompt, modelo)}"

def agente_escritor(prompt, modelo):
    prompt_final = f"Escreva um artigo sobre: {prompt}"
    return f"[Escritor]: {escolher_modelo(prompt_final, modelo)}"

def agente_analista(prompt, modelo):
    prompt_final = f"Analise os seguintes dados ou texto: {prompt}"
    return f"[Analista]: {escolher_modelo(prompt_final, modelo)}"

def agente_automatizador(prompt, modelo):
    prompt_final = f"Gere um script Python para: {prompt}"
    return f"[Automatizador]: {escolher_modelo(prompt_final, modelo)}"

def agente_consultor(prompt, modelo):
    prompt_final = f"Responda como um consultor especializado: {prompt}"
    return f"[Consultor]: {escolher_modelo(prompt_final, modelo)}"

# Escolha de modelo

def escolher_modelo(prompt, modelo):
    if modelo == "OpenAI (GPT-3.5)":
        return gerar_resposta_openai(prompt)
    else:
        return gerar_resposta_hf(prompt)

# Interface Gradio

def executar_agente(funcao, prompt, modelo):
    agentes = {
        "Pesquisador": agente_pesquisador,
        "Escritor": agente_escritor,
        "Analista": agente_analista,
        "Automatizador": agente_automatizador,
        "Consultor": agente_consultor
    }
    return agentes[funcao](prompt, modelo)

funcao_dropdown = gr.Dropdown(label="Escolha o tipo de agente", choices=["Pesquisador", "Escritor", "Analista", "Automatizador", "Consultor"], value="Escritor")
modelo_dropdown = gr.Dropdown(label="Modelo de linguagem", choices=["OpenAI (GPT-3.5)", "HuggingFace (Falcon-7B)"], value="OpenAI (GPT-3.5)")
prompt_input = gr.Textbox(label="Digite seu comando ou pergunta")
output = gr.Textbox(label="Resposta do agente")

app_interface = gr.Interface(
    fn=executar_agente,
    inputs=[funcao_dropdown, prompt_input, modelo_dropdown],
    outputs=output,
    title="Agente Multifuncional com Gradio",
    description="Escolha um agente, digite um comando, e receba a resposta gerada com GPT-3.5 ou Falcon."
)

if __name__ == "__main__":
    app_interface.launch()
