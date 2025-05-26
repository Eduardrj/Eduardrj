# Agente Multifuncional com Gradio

## 🎯 Objetivo do Projeto

Este projeto implementa um agente de inteligência artificial multifuncional com uma interface web construída usando Gradio. Ele permite que os usuários interajam com diferentes personas de IA (agentes especializados) e utilizem diversos modelos de linguagem para gerar respostas.

## ✨ Funcionalidades

*   **Seleção de Agente Especializado:** Escolha entre diferentes agentes, cada um com um propósito específico:
    *   Pesquisador
    *   Escritor
    *   Analista
    *   Automatizador
    *   Consultor
*   **Seleção de Modelo de Linguagem:** Opte por diferentes modelos de linguagem para gerar as respostas:
    *   OpenAI GPT-3.5-turbo
    *   TIIUAE Falcon-7B-Instruct (via Hugging Face Transformers)
*   **Entrada de Comando do Usuário:** Forneça um prompt ou pergunta para o agente processar.
*   **Interface Web com Gradio:** Interaja facilmente com o agente através do seu navegador.

## 🚀 Configuração e Uso

Siga os passos abaixo para configurar e executar o projeto localmente:

### 1. Pré-requisitos

*   Python 3.7 ou superior
*   pip (gerenciador de pacotes Python)

### 2. Clone o Repositório (se aplicável)

Se você baixou os arquivos, pule esta etapa. Caso contrário, clone o repositório:
```bash
git clone [URL_DO_REPOSITORIO]
cd [NOME_DO_DIRETORIO]
```

### 3. Crie e Ative um Ambiente Virtual (Recomendado)

```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

### 4. Instale as Dependências

Instale todas as bibliotecas necessárias listadas no arquivo `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 5. Configure as Chaves de API

Este projeto requer chaves de API para acessar os modelos de linguagem:

*   **OpenAI API Key:**
    *   Crie uma conta na [OpenAI](https://openai.com/).
    *   Obtenha sua chave de API.
    *   Defina a variável de ambiente `OPENAI_API_KEY` com sua chave:
        ```bash
        export OPENAI_API_KEY="sua_chave_openai_aqui"
        # No Windows (PowerShell): $env:OPENAI_API_KEY="sua_chave_openai_aqui"
        # Ou defina permanentemente nas configurações do sistema.
        ```

*   **Hugging Face API Token (Opcional/Contextual):**
    *   O modelo Falcon-7B-Instruct (`tiiuae/falcon-7b-instruct`) usado neste projeto é geralmente acessível publicamente através da biblioteca `transformers` sem a necessidade de um token dedicado, desde que você tenha as bibliotecas `transformers` e `torch` instaladas.
    *   No entanto, se você pretende usar modelos privados ou outros modelos da Hugging Face que exijam autenticação, você precisará de um token:
        *   Crie uma conta no [Hugging Face](https://huggingface.co/).
        *   Vá para suas Configurações (Settings) > Tokens de Acesso (Access Tokens) para gerar um token.
        *   Defina a variável de ambiente `HF_API_TOKEN` (ou `HUGGING_FACE_HUB_TOKEN`):
            ```bash
            export HF_API_TOKEN="seu_token_hf_aqui"
            # No Windows (PowerShell): $env:HF_API_TOKEN="seu_token_hf_aqui"
            ```
    *   *Observação:* O script `agente_multifuncional_gradio.py` atual não usa explicitamente o `HF_API_TOKEN` para o modelo Falcon-7B. A integração com a API da Hugging Face mencionada no issue original pode se referir à capacidade geral da biblioteca `transformers` de interagir com o Hub.

### 6. Execute o Aplicativo Gradio

Após a instalação e configuração, inicie o servidor Gradio:
```bash
python agente_multifuncional_gradio.py
```

Abra seu navegador e acesse o endereço local fornecido (geralmente `http://127.0.0.1:7860` ou similar).

## 📝 Arquivos do Projeto

*   `agente_multifuncional_gradio.py`: Script principal Python com a lógica do agente e a interface Gradio.
*   `requirements.txt`: Lista de dependências Python para o projeto.
*   `README.md`: Este arquivo, contendo a documentação do projeto.
