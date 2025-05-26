# Diretrizes de Teste: Gerador Automatizado de Notícias em Vídeo com IA

## 1. Introdução Breve

O objetivo principal destes testes é garantir a robustez da aplicação, a qualidade dos resultados gerados (sumário, imagem, narração) e o bom funcionamento da interface em diversos cenários de entrada. Buscamos identificar possíveis falhas, inconsistências e áreas para melhoria.

## 2. Ambiente de Teste

*   **Interface Principal:** Todos os testes funcionais devem ser conduzidos através da interface Gradio, que é lançada executando o script `app.py`.
*   **Verificação Inicial:** Antes de iniciar os testes com diferentes notícias, verifique a seção "Status dos Modelos de IA" na parte inferior da interface Gradio. Confirme se os modelos de Sumarização, Geração de Imagem e TTS foram carregados corretamente. Problemas aqui podem indicar falhas no ambiente ou na configuração.
*   **Console de Logs:** Mantenha o console (terminal) onde `app.py` foi executado visível. Logs de erro ou avisos importantes podem ser exibidos ali, auxiliando na identificação de problemas não visíveis diretamente na UI.
*   **Diretório `outputs/`**: Os artefatos gerados (imagens, áudios, placeholders) são salvos neste diretório. Verifique seu conteúdo se necessário, especialmente se os downloads via UI apresentarem problemas.

## 3. Tipos de Textos de Notícias para Testar

É crucial testar com uma variedade de textos para cobrir diferentes casos de uso e identificar limitações.

### 3.1. Comprimento do Texto:

*   **Textos Curtos:**
    *   Exemplo: 1-2 parágrafos concisos.
    *   Observar: Qualidade do sumário (pode ser muito similar ao original), relevância da imagem e áudio.
*   **Textos Médios:**
    *   Exemplo: 3-5 parágrafos.
    *   Observar: Capacidade de sumarização em extrair pontos chave, qualidade geral dos artefatos.
*   **Textos Longos:**
    *   Exemplo: Mais de 5 parágrafos.
    *   Observar:
        *   Qualidade e coerência do sumário (limite de tokens do modelo de sumarização, ~1024 tokens, pode ser atingido, resultando em truncamento do texto de entrada para o sumário).
        *   Performance geral da aplicação (tempo de processamento).
        *   Qualidade da narração para textos mais extensos.

### 3.2. Tópicos Diversificados:

*   Teste com notícias de diferentes editorias:
    *   Tecnologia
    *   Política Nacional e Internacional
    *   Esportes (diversas modalidades)
    *   Entretenimento (cinema, música, celebridades)
    *   Ciência e Saúde
    *   Economia
    *   Cotidiano/Local
*   Observar:
    *   A relevância e adequação da imagem gerada em relação ao tópico da notícia.
    *   A capacidade do modelo de sumarização em lidar com jargões específicos de cada área.

### 3.3. Linguagem e Estilo:

*   **Linguagem Formal:** Textos de portais de notícias tradicionais.
*   **Linguagem Mais Informal:** Notícias de blogs, colunas de opinião (se aplicável ao escopo da IA).
*   **Estruturas Frasais:** Textos com frases curtas e diretas vs. textos com orações mais complexas e subordinadas.
*   Observar:
    *   Impacto na qualidade da sumarização e da narração.
    *   O refino do prompt para imagem pode ser afetado por estilos muito diferentes.

### 3.4. Conteúdo Específico:

*   **Menção Clara a Entidades:** Textos que mencionem pessoas famosas, lugares conhecidos ou eventos específicos.
    *   Observar: Como o prompt de imagem (derivado do sumário) lida com essas entidades. A imagem gerada tenta representá-las?
*   **Pouca Informação Visual Explícita:** Textos mais conceituais ou abstratos.
    *   Observar: Qualidade e criatividade da imagem gerada.
*   **Citações e Discurso Direto:** Textos com muitas aspas ou falas.
    *   Observar: Como são tratadas na sumarização e na narração.

### 3.5. Textos Problemáticos (Teste de Limite):

*   **Textos Muito Curtos:**
    *   Exemplo: Uma única frase ou poucas palavras.
    *   Observar: Comportamento da sumarização (pode retornar o texto original ou um erro/aviso), qualidade da imagem/áudio.
*   **Textos Extremamente Longos:**
    *   Exemplo: Artigos de opinião muito extensos, documentos.
    *   Observar: Truncamento na sumarização, performance, possíveis timeouts ou erros de memória (ver console).
*   **Caracteres Especiais e Formatação:**
    *   Exemplo: Textos com muitos emojis, símbolos não usuais, ou formatação HTML copiada acidentalmente.
    *   Observar: A interface Gradio (Textbox) pode normalizar parte disso, mas o backend precisa ser resiliente. Verificar se há quebras ou comportamentos estranhos.
*   **Textos em Outros Idiomas:**
    *   Exemplo: Notícias em inglês, espanhol, etc.
    *   Observar:
        *   **Sumarização:** O modelo `unicamp-dl/ptt5-base-portuguese-samsum` é focado em português. O resultado para outros idiomas será provavelmente de baixa qualidade ou sem sentido.
        *   **TTS:** O modelo SpeechT5 com o embedding atual (CMU ARCTIC) é primariamente para inglês. A pronúncia de outros idiomas será provavelmente ruim.
        *   **Geração de Imagem:** O prompt refinado será baseado no texto (possivelmente mal sumarizado). Se o texto original (ou o sumário ruim) for em outro idioma, o prompt final para o Stable Diffusion pode não ser eficaz.
*   **Texto Vazio:** Clicar em "Gerar Conteúdo" sem inserir texto.
    *   Observar: A aplicação deve lidar com isso de forma graciosa (ex: mensagem de erro, não processar).

## 4. Critérios de Avaliação para Cada Componente

### 4.1. Sumarização:

*   **Clareza e Concisão:** O sumário é fácil de entender e vai direto ao ponto?
*   **Retenção dos Pontos Principais:** As informações mais importantes da notícia original estão presentes no sumário?
*   **Gramática e Ortografia:** O sumário está gramaticalmente correto e sem erros de ortografia? (O modelo pode cometer pequenos erros).
*   **Adequação do Comprimento:** O sumário gerado respeita os parâmetros de `min_comprimento_sumario` e `max_comprimento_sumario` (definidos no código)? (Atualmente ~40 e ~200 tokens).
*   **Não Invenção:** O sumário não adiciona informações que não estavam no texto original?
*   **Feedback de Erro:** Se a sumarização falhar, a mensagem na UI é clara? (Ex: "Falha na sumarização. Conteúdo será gerado com base no texto original.")

### 4.2. Geração de Imagem:

*   **Relevância Temática:** A imagem gerada tem relação com o conteúdo do texto (sumarizado ou original, dependendo do fluxo)?
*   **Qualidade Visual:** A imagem é esteticamente aceitável? Há artefatos óbvios, distorções, ou incoerências visuais gritantes?
*   **Interpretação do Prompt:** A imagem reflete os elementos-chave que foram provavelmente extraídos para o prompt interno?
*   **Placeholder:** Em caso de falha na geração da imagem principal (ou se o pipeline de imagem não estiver carregado), o placeholder é exibido corretamente? A mensagem no placeholder é informativa?

### 4.3. Narração (TTS):

*   **Clareza e Inteligibilidade:** O áudio é fácil de entender? A dicção é clara?
*   **Naturalidade da Voz:** A voz soa robótica ou possui alguma naturalidade? (Considerar que o speaker embedding atual é para inglês e pode impactar a naturalidade em português).
*   **Pronúncia (Português):** As palavras em português são pronunciadas corretamente? Há erros grosseiros de pronúncia?
*   **Ritmo e Pausas:** O ritmo da fala é adequado? As pausas são naturais?
*   **Qualidade do Áudio:** Há ruídos de fundo, estalos, ou falhas excessivas no áudio?
*   **Volume:** O volume do áudio é adequado?

### 4.4. Interface Gradio:

*   **Responsividade:** A interface responde bem aos comandos? Há lentidão excessiva ao clicar no botão ou ao carregar os resultados?
*   **Clareza das Mensagens:**
    *   As mensagens de status durante o processamento (`gr.Progress`) são informativas?
    *   As mensagens de erro (ex: falha na sumarização, modelo não carregado) são claras para o usuário?
*   **Exibição dos Resultados:** O texto sumarizado, a imagem e o áudio são exibidos corretamente nos seus respectivos componentes?
*   **Funcionamento dos Downloads:** Os botões/links de download para a imagem e o áudio funcionam como esperado? Os arquivos baixados estão corretos e íntegros?
*   **Consistência Geral:** A experiência do usuário é fluida e intuitiva?

## 5. Relato de Problemas

Ao encontrar um problema, tente fornecer o máximo de informações possível para facilitar a reprodução e correção. Um formato sugerido é:

*   **ID do Teste (Opcional):** Um identificador único se estiver seguindo um plano de teste formal.
*   **Componente Afetado:** (Ex: Sumarização, Geração de Imagem, TTS, Interface Gradio, Geral).
*   **Texto de Entrada Completo:** Cole o texto da notícia que causou o problema.
*   **Passos para Reproduzir (se não for óbvio):**
    1.  ...
    2.  ...
*   **Comportamento Esperado:** O que você esperava que acontecesse?
*   **Comportamento Observado:** O que realmente aconteceu? Inclua mensagens de erro da UI ou do console, se relevantes.
*   **Capturas de Tela/Gravações (Opcional mas útil):** Se possível, anexe screenshots da UI ou pequenos vídeos/áudios demonstrando o problema.
*   **Gravidade (Opcional):** (Ex: Crítico, Alto, Médio, Baixo).
*   **Informações do Ambiente (se relevante):** Navegador, Sistema Operacional, status dos modelos na UI.

**Exemplo de Relato:**

*   **Componente Afetado:** Geração de Imagem
*   **Texto de Entrada Completo:** "A sonda espacial Juno da NASA capturou novas imagens impressionantes das luas de Júpiter, Io e Europa. As fotos revelam detalhes vulcânicos em Io e possíveis plumas de água em Europa."
*   **Comportamento Esperado:** Uma imagem relacionada ao espaço, Júpiter, ou suas luas.
*   **Comportamento Observado:** A imagem gerada foi um retrato abstrato de um gato. Nenhum erro na UI, mas o log do prompt refinado foi "gato, animal, estimação, fotografia detalhada...".
*   **Gravidade:** Médio (funcionalidade principal afetada, mas não crítica).

---

Ao seguir estas diretrizes, podemos coletivamente melhorar a qualidade e a confiabilidade do Gerador Automatizado de Notícias em Vídeo com IA.
