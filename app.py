import logging
import os
from moviepy.editor import VideoFileClip
from PIL import Image, ImageDraw, ImageFont

# Configure logging
logging.basicConfig(level=logging.INFO)

try:
    # Attempt to import moviepy.editor and log success
    from moviepy.editor import * # type: ignore
    logging.info("moviepy.editor importado com sucesso.")
except ImportError as e_import:
    # Log an error if the import fails and re-raise the exception
    logging.error(f"Falha ao importar moviepy.editor: {e_import}", exc_info=True)
    raise # Re-levanta a exceção para interromper a execução se moviepy for crítico

def convert_to_gif(video_path, gif_path, max_duration=10, fps=10):
    """
    Converts a video file to a GIF.

    Args:
        video_path (str): Path to the input video file.
        gif_path (str): Path to save the output GIF.
        max_duration (int, optional): Maximum duration of the GIF in seconds. Defaults to 10.
        fps (int, optional): Frames per second for the GIF. Defaults to 10.
    """
    try:
        # Load the video clip
        clip = VideoFileClip(video_path)

        # Trim the clip if its duration exceeds max_duration
        if clip.duration > max_duration:
            clip = clip.subclip(0, max_duration)

        # Write the GIF file
        clip.write_gif(gif_path, fps=fps)
        logging.info(f"Successfully converted {video_path} to {gif_path}")

    except Exception as e:
        logging.error(f"Error converting video to GIF: {e}")
        # Optionally, re-raise the exception if you want the main app to handle it
        # raise

if __name__ == "__main__":
    # Example usage (optional, could be triggered by a Gradio interface or similar)
    # Create dummy video file for testing if it doesn't exist
    if not os.path.exists("input.mp4"):
        # This requires ffmpeg to be installed to create a dummy video.
        # In a real scenario, the video would be uploaded or already present.
        try:
            from moviepy.video.io.ffmpeg_writer import FFMPEG_VideoWriter
            with FFMPEG_VideoWriter("input.mp4", (640, 480), 1) as writer:
                for i in range(5): # 5 seconds video
                    frame = [[[ (i*50)%255, (i*25)%255, (i*10)%255 ] * 640] * 480] # Create a dummy frame
                    writer.write_frame(frame)
            logging.info("Created dummy input.mp4 for testing.")
        except FileNotFoundError as e_fnf:
            logging.error(f"Erro ao criar dummy input.mp4: Arquivo ou diretório não encontrado. Verifique se o FFMPEG está instalado e no PATH. Detalhes: {e_fnf}", exc_info=True)
        except Exception as e_general:
            logging.error(f"Erro inesperado ao criar dummy input.mp4: {e_general}. Por favor, garanta que FFMPEG está instalado.", exc_info=True)


    if os.path.exists("input.mp4"):
        convert_to_gif("input.mp4", "output.gif")
    else:
        logging.warning("input.mp4 not found. Skipping conversion example.")

    # --- Image Generation Logic ---
    import torch
    from diffusers import StableDiffusionPipeline
    import string # Para remoção de pontuação
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM # Para sumarização
    from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan # Para TTS
    from datasets import load_dataset # Para TTS (speaker embeddings)
    import soundfile as sf # Para salvar áudio TTS
    import gradio as gr # Para interface web
    import time # Para simular progresso no Gradio

    # --- Prompt Refinement ---
    def refinar_prompt_imagem(texto_base: str) -> str:
        # COMENTÁRIO: Para melhores resultados, traduzir palavras-chave para inglês.
        # COMENTÁRIO: Técnicas avançadas (TF-IDF, NER com spaCy/NLTK) podem melhorar a extração.
        
        texto_lower = texto_base.lower()
        
        # Remover pontuações
        translator = str.maketrans('', '', string.punctuation)
        texto_sem_pontuacao = texto_lower.translate(translator)
        
        stopwords_pt = [
            'de', 'a', 'o', 'que', 'e', 'do', 'da', 'em', 'um', 'para', 'com', 'não', 'uma', 'os', 'no', 'na', 'por', 
            'mais', 'as', 'dos', 'como', 'mas', 'foi', 'ao', 'ele', 'das', 'tem', 'à', 'seu', 'sua', 'ou', 'ser', 
            'quando', 'muito', 'há', 'nos', 'já', 'está', 'eu', 'também', 'só', 'pelo', 'pela', 'até', 'isso', 'ela', 
            'entre', 'era', 'depois', 'sem', 'mesmo', 'aos', 'ter', 'seus', 'quem', 'nas', 'me', 'esse', 'eles', 
            'estão', 'você', 'tinha', 'foram', 'essa', 'num', 'nem', 'suas', 'meu', 'às', 'minha', 'numa', 'pelos', 
            'elas', 'havia', 'seja', 'qual', 'será', 'nós', 'tenho', 'lhe', 'deles', 'essas', 'esses', 'pelas', 
            'este', 'fosse', 'dele', 'tu', 'te', 'vocês', 'meus', 'minhas', 'teu', 'tua', 'teus', 'tuas', 'nosso', 
            'nossa', 'nossos', 'nossas', 'dela', 'delas', 'esta', 'estes', 'aquele', 'aquela', 'aqueles', 'aquelas', 
            'isto', 'aquilo', 'estou', 'estamos', 'estavam', 'estive', 'esteve', 'estivemos', 'estiveram', 'estava', 
            'estávamos', 'estivera', 'estivéramos', 'esteja', 'estejamos', 'estejam', 'estivesse', 'estivéssemos', 
            'estivessem', 'estiver', 'estivermos', 'estiverem', 'hei', 'haja', 'hajamos', 'hajam', 
            'houve', 'houvemos', 'houveram', 'houvera', 'houvéramos', 'houvesse', 'houvéssemos', 'houvessem', 
            'houver', 'houvermos', 'houverem', 'houverei', 'houverá', 'houveremos', 'houverão', 'houveria', 
            'houveríamos', 'houveriam'
            # 'há' (presente do indicativo de haver) foi removido da lista de stopwords pois pode ser relevante
        ]
        
        palavras = texto_sem_pontuacao.split()
        palavras_filtradas = [p for p in palavras if p not in stopwords_pt and p.strip()]
        
        # Selecionar as primeiras 5-7 palavras-chave, ou menos se houver poucas
        num_palavras_chave = min(len(palavras_filtradas), 7) 
        palavras_chave_selecionadas = palavras_filtradas[:num_palavras_chave]
        
        if not palavras_chave_selecionadas:
            # Fallback se nenhuma palavra-chave for extraída (ex: texto só com stopwords)
            prompt_keywords = "imagem abstrata"
            logging.warning(f"Nenhuma palavra-chave extraída do texto base: '{texto_base}'. Usando fallback: '{prompt_keywords}'")
        else:
            prompt_keywords = ", ".join(palavras_chave_selecionadas)

        prompt_final = f"{prompt_keywords}. Fotografia detalhada, iluminação cinematográfica, arte digital."
        logging.info(f"Prompt refinado gerado: '{prompt_final}' a partir do texto base: '{texto_base}'")
        return prompt_final

    # --- Placeholder Image Generation ---
    def criar_imagem_placeholder(texto_mensagem, caminho_arquivo, largura=600, altura=400):
        try:
            os.makedirs(os.path.dirname(caminho_arquivo), exist_ok=True)
            img = Image.new('RGB', (largura, altura), color = (200, 200, 200)) # Fundo cinza claro
            draw = ImageDraw.Draw(img)
            
            font_path_preferred = "fonts/LiberationSans-Regular.ttf"
            font_path_alternative = "arial.ttf" # Comum em muitos sistemas
            font_to_use = None

            try:
                # Tentar carregar LiberationSans-Regular de um diretório 'fonts'
                # COMENTÁRIO: O arquivo LiberationSans-Regular.ttf precisaria ser adicionado manualmente a fonts/LiberationSans-Regular.ttf
                # O diretório 'fonts/' também precisaria ser criado na raiz do projeto.
                if not os.path.exists(font_path_preferred):
                    # Esta não é uma exceção real, mas um log para guiar o usuário.
                    logging.info(f"Fonte preferencial '{font_path_preferred}' não encontrada. Tentando alternativas.")
                else:
                    font_to_use = ImageFont.truetype(font_path_preferred, 30)
                    logging.info(f"Usando fonte: {font_path_preferred}")
            except IOError as e_font_pref:
                logging.warning(f"Erro ao carregar fonte preferencial '{font_path_preferred}': {e_font_pref}. Tentando alternativa.", exc_info=True)

            if font_to_use is None: # Se a preferencial não foi carregada
                try:
                    font_to_use = ImageFont.truetype(font_path_alternative, 30)
                    logging.info(f"Usando fonte: {font_path_alternative}")
                except IOError as e_font_alt:
                    logging.warning(f"Erro ao carregar fonte alternativa '{font_path_alternative}': {e_font_alt}. Usando fonte padrão do PIL.", exc_info=True)
                    font_to_use = ImageFont.load_default()
                    logging.info("Usando fonte: Padrão do PIL")
            
            font = font_to_use # Atribui a fonte selecionada
            
            # Lógica simples para quebra de linha e centralização
            # (O restante da lógica de desenho permanece o mesmo)
        # Lógica simples para quebra de linha e centralização
        linhas = []
        palavras = texto_mensagem.split()
        linha_atual = ""
        # Ajustar o tamanho da fonte dinamicamente se o texto for muito grande (muito básico)
        tamanho_fonte = 30
        while True:
            font = font.font_variant(size=tamanho_fonte) # Re-cria o objeto de fonte com novo tamanho
            # Recalcular linhas com o novo tamanho da fonte
            linhas = []
            linha_atual = ""
            for palavra in palavras:
                # Verificar se a palavra em si já é muito grande
                if draw.textsize(palavra, font=font)[0] > largura - 20: # -20 para margens
                    # Se uma única palavra é muito grande, ela vai estourar, mas tentamos prosseguir
                    if linha_atual: # Adiciona a linha anterior se houver
                        linhas.append(linha_atual.strip())
                        linha_atual = ""
                    linhas.append(palavra) # Adiciona a palavra grande como sua própria linha
                    continue # Vai para a próxima palavra

                if draw.textsize(linha_atual + palavra, font=font)[0] <= largura - 20:
                    linha_atual += palavra + " "
                else:
                    linhas.append(linha_atual.strip())
                    linha_atual = palavra + " "
            linhas.append(linha_atual.strip())
            
            # Verificar se o texto cabe verticalmente
            altura_total_texto = sum(draw.textsize("Tg", font=font)[1] for _ in linhas) + (len(linhas) -1) * 5
            if altura_total_texto <= altura - 20 and tamanho_fonte > 10 : # -20 para margens, tamanho minimo 10
                 break # Fonte atual é boa
            elif tamanho_fonte <= 10: # Evita loop infinito se o texto for muito grande mesmo com fonte pequena
                logging.warning("Texto muito longo para caber na imagem de placeholder mesmo com fonte pequena.")
                break
            tamanho_fonte -= 2 # Reduz o tamanho da fonte e tenta novamente
            if tamanho_fonte < 10: tamanho_fonte = 10 # Garante tamanho minimo

        y_text = altura / 2 - (sum(draw.textsize("Tg", font=font)[1] for _ in linhas) + (len(linhas) -1) * 5) / 2
        for linha in linhas:
            text_width, text_height = draw.textsize(linha, font=font)
            x = (largura - text_width) / 2
            draw.text((x, y_text), linha, fill=(50, 50, 50), font=font) # Texto cinza escuro
            y_text += text_height + 5 # Espaçamento entre linhas

        img.save(caminho_arquivo)
        logging.info(f"Imagem de placeholder salva em: {caminho_arquivo} com a mensagem: '{texto_mensagem}'")
        return caminho_arquivo
    except IOError as e_io:
        logging.error(f"Erro de I/O ao criar ou salvar imagem de placeholder em '{caminho_arquivo}': {e_io}", exc_info=True)
        return None # Retornar None se salvar falhar
    except Exception as e_general:
        logging.error(f"Erro inesperado ao criar imagem de placeholder: {e_general}", exc_info=True)
        return None


    # --- Global variables for Image Pipeline ---
    pipeline_imagem = None
    dispositivo_imagem = None

    def inicializar_pipeline_imagem(model_id="runwayml/stable-diffusion-v1-5"):
        nonlocal pipeline_imagem, dispositivo_imagem # Declarar que estamos modificando as globais
        try:
            dispositivo_imagem = "cuda" if torch.cuda.is_available() else "cpu"
            logging.info(f"Dispositivo selecionado para geração de imagem: {dispositivo_imagem}")
            
            pipe = StableDiffusionPipeline.from_pretrained(model_id)
            pipeline_imagem = pipe.to(dispositivo_imagem) # Atribuir à variável global
            logging.info(f"Pipeline StableDiffusion '{model_id}' carregado com sucesso em {dispositivo_imagem}.")
            return True # Sucesso
        except RuntimeError as e_rt: # Comum para problemas de memória CUDA ou incompatibilidade
            logging.error(f"Erro de runtime ao carregar StableDiffusionPipeline '{model_id}': {e_rt}", exc_info=True)
            pipeline_imagem, dispositivo_imagem = None, None
            return False
        except OSError as e_os: # Pode ocorrer se arquivos de modelo estiverem faltando ou corrompidos
            logging.error(f"Erro de OS (possivelmente arquivos de modelo faltando/corrompidos) ao carregar StableDiffusionPipeline '{model_id}': {e_os}", exc_info=True)
            pipeline_imagem, dispositivo_imagem = None, None
            return False
        except Exception as e_general: # Captura qualquer outra exceção
            logging.error(f"Falha inesperada ao carregar StableDiffusionPipeline '{model_id}': {e_general}", exc_info=True)
            pipeline_imagem, dispositivo_imagem = None, None
            return False

    # Inicialize o pipeline (pode ser global ou dentro de uma função principal do Gradio)
    pipeline_imagem_inicializado_com_sucesso = inicializar_pipeline_imagem()


    def gerar_imagem_com_pipeline(texto_base_para_prompt: str):
        prompt_refinado = refinar_prompt_imagem(texto_base_para_prompt)
        
        if not pipeline_imagem_inicializado_com_sucesso or pipeline_imagem is None:
            logging.error("Pipeline de imagem não inicializado. Imagem não pode ser gerada.")
            return criar_imagem_placeholder(f"Pipeline de imagem não inicializado. Tentativa com prompt: {prompt_refinado}", "outputs/placeholder_erro_inicializacao_pipeline.png")

        logging.info(f"Gerando imagem com prompt refinado: '{prompt_refinado}' (a partir de: '{texto_base_para_prompt}') no dispositivo {dispositivo_imagem}")
        try:
            # Otimização para GPU, se aplicável (ex: half precision)
            # if dispositivo_imagem == "cuda":
            # pipeline_imagem.to(torch.float16) # Comentar se causar problemas ou não for desejado

            image = pipeline_imagem(prompt_refinado).images[0] # type: ignore
            logging.info("Imagem gerada com sucesso.")
            
            caminho_imagem_gerada = "outputs/generated_image.png"
            os.makedirs(os.path.dirname(caminho_imagem_gerada), exist_ok=True)
            image.save(caminho_imagem_gerada)
            return caminho_imagem_gerada
        except RuntimeError as e_rt: # Ex: erro de memória CUDA
            logging.error(f"Erro de runtime durante a geração da imagem com Stable Diffusion: {e_rt}", exc_info=True)
            return criar_imagem_placeholder(f"Erro de runtime ao gerar imagem. Detalhes: {str(e_rt)}", "outputs/placeholder_falha_geracao_runtime.png")
        except Exception as e_general:
            logging.error(f"Erro inesperado durante a geração da imagem com Stable Diffusion: {e_general}", exc_info=True)
            return criar_imagem_placeholder(f"Erro inesperado ao gerar imagem. Detalhes: {str(e_general)}", "outputs/placeholder_falha_geracao_inesperado.png")
    
    # --- Text Summarization Logic ---
    tokenizer_sumarizacao = None
    modelo_sumarizacao = None
    dispositivo_sumarizacao = None

    def inicializar_modelo_sumarizacao(model_id="unicamp-dl/ptt5-base-portuguese-samsum"):
        nonlocal tokenizer_sumarizacao, modelo_sumarizacao, dispositivo_sumarizacao
        try:
            dispositivo_sumarizacao = "cuda" if torch.cuda.is_available() else "cpu"
            logging.info(f"Inicializando modelo de sumarização '{model_id}' em {dispositivo_sumarizacao}")
            tokenizer_sumarizacao = AutoTokenizer.from_pretrained(model_id)
            modelo_sumarizacao = AutoModelForSeq2SeqLM.from_pretrained(model_id).to(dispositivo_sumarizacao)
            logging.info(f"Modelo de sumarização '{model_id}' carregado com sucesso.")
            return True
        except RuntimeError as e_rt:
            logging.error(f"Erro de runtime ao carregar modelo de sumarização '{model_id}': {e_rt}", exc_info=True)
            tokenizer_sumarizacao, modelo_sumarizacao, dispositivo_sumarizacao = None, None, None
            return False
        except OSError as e_os: # Problemas como arquivo de modelo não encontrado ou corrompido
            logging.error(f"Erro de OS (arquivos de modelo faltando/corrompidos?) ao carregar '{model_id}': {e_os}", exc_info=True)
            tokenizer_sumarizacao, modelo_sumarizacao, dispositivo_sumarizacao = None, None, None
            return False
        except Exception as e_general:
            logging.error(f"Falha inesperada ao carregar modelo de sumarização '{model_id}': {e_general}", exc_info=True)
            tokenizer_sumarizacao, modelo_sumarizacao, dispositivo_sumarizacao = None, None, None
            return False
        # COMENTÁRIO: A lógica de fallback para 'google/mt5-small' foi removida para simplificar,
        # pois o foco é no tratamento de erro do modelo principal. Se o fallback fosse mantido,
        # ele precisaria de tratamento de erro similar.

    # Chamar a inicialização do modelo de sumarização
    sumarizacao_inicializada_com_sucesso = inicializar_modelo_sumarizacao()

    def sumarizar_texto(texto_noticia: str, min_comprimento_sumario=40, max_comprimento_sumario=200) -> str:
        if not sumarizacao_inicializada_com_sucesso or not modelo_sumarizacao or not tokenizer_sumarizacao:
            logging.error("Modelo de sumarização não inicializado corretamente. Retornando texto original.")
            return texto_noticia 

        logging.info(f"Sumarizando texto (primeiros 100 chars): '{texto_noticia[:100]}...' com min_len={min_comprimento_sumario}, max_len={max_comprimento_sumario} em {dispositivo_sumarizacao}")
        try:
            inputs = tokenizer_sumarizacao(texto_noticia, return_tensors="pt", max_length=1024, truncation=True).to(dispositivo_sumarizacao) # type: ignore
            
            summary_ids = modelo_sumarizacao.generate(inputs.input_ids, # type: ignore
                                                num_beams=4, 
                                                min_length=min_comprimento_sumario,
                                                max_length=max_comprimento_sumario,
                                                early_stopping=True) 
            
            sumario = tokenizer_sumarizacao.decode(summary_ids[0], skip_special_tokens=True) # type: ignore
            logging.info(f"Sumário gerado (primeiros 100 chars): '{sumario[:100]}...'")
            return sumario
        except RuntimeError as e_rt: # Ex: erro de memória CUDA
            logging.error(f"Erro de runtime durante a sumarização: {e_rt}", exc_info=True)
            return f"Erro de runtime ao sumarizar o texto. Detalhes: {str(e_rt)}"
        except Exception as e_general:
            logging.error(f"Erro inesperado durante a sumarização: {e_general}", exc_info=True)
            return f"Erro inesperado ao sumarizar o texto. Detalhes: {str(e_general)}"

    # Example usage for summarization and image generation
    if sumarizacao_inicializada_com_sucesso:
        texto_exemplo_noticia = "Uma forte tempestade solar atingiu a Terra na última terça-feira, desencadeando espetaculares exibições de auroras em latitudes muito mais baixas do que o usual. Cientistas afirmam que este evento, classificado como G4 em uma escala que vai até G5, foi um dos mais intensos dos últimos anos e levanta preocupações sobre possíveis impactos em satélites de comunicação e redes elétricas globais. As operadoras de energia estão em alerta máximo para monitorar e mitigar quaisquer interrupções."
        logging.info(f"Testando sumarização com texto: '{texto_exemplo_noticia}'")
        sumario_teste = sumarizar_texto(texto_exemplo_noticia)
        logging.info(f"Sumário do teste: {sumario_teste}")

        if pipeline_imagem_inicializado_com_sucesso:
            texto_base_para_imagem = sumario_teste
            if "Erro ao sumarizar" in sumario_teste or not sumario_teste.strip() or "Erro inesperado ao sumarizar" in sumario_teste:
                logging.warning("Sumarização falhou ou retornou sumário vazio/inválido. Usando texto original para imagem.")
                texto_base_para_imagem = texto_exemplo_noticia

            logging.info(f"Testando geração de imagem com base no texto: '{texto_base_para_imagem[:100]}...'")
            caminho_imagem_teste = gerar_imagem_com_pipeline(texto_base_para_imagem)
            if caminho_imagem_teste and "placeholder" not in caminho_imagem_teste:
                logging.info(f"Imagem de teste (baseada no texto fornecido) gerada com sucesso em: {caminho_imagem_teste}")
            else:
                logging.warning(f"Geração da imagem de teste (baseada no texto fornecido) resultou em placeholder ou falhou: {caminho_imagem_teste}")
        else:
            logging.error("Pipeline de imagem não inicializado. Teste de geração de imagem não pode ser executado.")
    else: # Se sumarizacao_inicializada_com_sucesso for False
        logging.error("Modelo de sumarização não inicializado. Teste de sumarização e imagem não pode ser executado.")
        # Adicionar um teste de imagem com o texto original se o modelo de sumarização falhar ao inicializar
        if pipeline_imagem_inicializado_com_sucesso:
            logging.warning("Modelo de sumarização não carregado. Tentando gerar imagem com texto original de exemplo.")
            texto_exemplo_noticia_fallback = "Uma forte tempestade solar atingiu a Terra na última terça-feira, desencadeando espetaculares exibições de auroras em latitudes muito mais baixas do que o usual. Cientistas afirmam que este evento, classificado como G4 em uma escala que vai até G5, foi um dos mais intensos dos últimos anos e levanta preocupações sobre possíveis impactos em satélites de comunicação e redes elétricas globais. As operadoras de energia estão em alerta máximo para monitorar e mitigar quaisquer interrupções."
            caminho_imagem_teste = gerar_imagem_com_pipeline(texto_exemplo_noticia_fallback)
            if caminho_imagem_teste and "placeholder" not in caminho_imagem_teste:
                logging.info(f"Imagem de teste (baseada no texto original) gerada com sucesso em: {caminho_imagem_teste}")
            else:
                logging.warning(f"Geração da imagem de teste (baseada no texto original) resultou em placeholder ou falhou: {caminho_imagem_teste}")
        else:
            logging.error("Pipeline de imagem também não inicializado. Nenhum teste de geração de imagem pode ser executado.")

    # --- Text-to-Speech (TTS) Logic ---
    processor_tts = None
    modelo_tts = None
    vocoder_tts = None
    speaker_embedding_tts = None
    dispositivo_tts = None

    def inicializar_modelos_tts(tts_model_id="microsoft/speecht5_tts", vocoder_model_id="microsoft/speecht5_hifigan", speaker_embeddings_dataset_id="Matthijs/cmu-arctic-xvectors"):
        nonlocal processor_tts, modelo_tts, vocoder_tts, speaker_embedding_tts, dispositivo_tts
        try:
            dispositivo_tts = "cuda" if torch.cuda.is_available() else "cpu"
            logging.info(f"Inicializando modelos TTS ({tts_model_id}, {vocoder_model_id}) em {dispositivo_tts}")
            
            processor_tts = SpeechT5Processor.from_pretrained(tts_model_id)
            modelo_tts = SpeechT5ForTextToSpeech.from_pretrained(tts_model_id).to(dispositivo_tts)
            vocoder_tts = SpeechT5HifiGan.from_pretrained(vocoder_model_id).to(dispositivo_tts)
            
            logging.info(f"Carregando dataset de speaker embeddings: {speaker_embeddings_dataset_id}...")
            embeddings_dataset = load_dataset(speaker_embeddings_dataset_id, split="validation", trust_remote_code=True) # Adicionado trust_remote_code=True
            
            speaker_idx_to_try = 0 
            if len(embeddings_dataset) > speaker_idx_to_try: # type: ignore
                speaker_embedding_tts = torch.tensor(embeddings_dataset[speaker_idx_to_try]["xvector"]).unsqueeze(0).to(dispositivo_tts) # type: ignore
                logging.info(f"Speaker embedding (índice {speaker_idx_to_try} de {speaker_embeddings_dataset_id}) carregado com sucesso.")
            else:
                logging.error(f"Índice de speaker embedding {speaker_idx_to_try} fora do alcance para o dataset {speaker_embeddings_dataset_id} com {len(embeddings_dataset)} amostras.") # type: ignore
                raise ValueError(f"Índice de speaker embedding {speaker_idx_to_try} inválido.")

            logging.info("Modelos TTS e vocoder carregados com sucesso.")
            return True
        except RuntimeError as e_rt:
            logging.error(f"Erro de runtime ao carregar modelos TTS ({tts_model_id}, {vocoder_model_id}): {e_rt}", exc_info=True)
        except OSError as e_os: # Erros de arquivo não encontrado, etc.
            logging.error(f"Erro de OS ao carregar modelos TTS ({tts_model_id}, {vocoder_model_id}): {e_os}", exc_info=True)
        except ValueError as e_val: # Para o erro do speaker_idx_to_try
            logging.error(f"Erro de valor (provavelmente speaker embedding) ao carregar modelos TTS: {e_val}", exc_info=True)
        except Exception as e_general: # Captura de exceções da lib 'datasets' ou outras inesperadas
            logging.error(f"Falha inesperada ao carregar modelos TTS ou dataset de embeddings ({speaker_embeddings_dataset_id}): {e_general}", exc_info=True)
        
        # Limpar variáveis globais em caso de qualquer falha
        processor_tts, modelo_tts, vocoder_tts, speaker_embedding_tts, dispositivo_tts = None, None, None, None, None
        return False

    # Chamar a inicialização dos modelos TTS
    tts_inicializado_com_sucesso = inicializar_modelos_tts()

    def gerar_narracao_audio(texto_para_audio: str, caminho_arquivo_audio="outputs/narracao.wav") -> str | None:
        if not tts_inicializado_com_sucesso or not modelo_tts or not processor_tts or not vocoder_tts or not speaker_embedding_tts:
            logging.error("Modelos TTS não inicializados corretamente. Não é possível gerar áudio.")
            return None

        logging.info(f"Gerando narração para texto (primeiros 100 chars): '{texto_para_audio[:100]}...' em {dispositivo_tts}")
        try:
            inputs = processor_tts(text=texto_para_audio, return_tensors="pt").to(dispositivo_tts) # type: ignore
            with torch.no_grad():
                speech = modelo_tts.generate_speech(inputs["input_ids"], speaker_embedding_tts, vocoder=vocoder_tts) # type: ignore
            
            audio_array = speech.cpu().numpy()
            
            os.makedirs(os.path.dirname(caminho_arquivo_audio), exist_ok=True)
            
            sf.write(caminho_arquivo_audio, audio_array, samplerate=16000) 
            logging.info(f"Narração salva em: {caminho_arquivo_audio}")
            return caminho_arquivo_audio
        except RuntimeError as e_rt: # Ex: erro de memória CUDA
            logging.error(f"Erro de runtime durante a geração da narração: {e_rt}", exc_info=True)
        except sf.LibsndfileError as e_sf: # Erro específico do soundfile
            logging.error(f"Erro do Soundfile ao escrever o arquivo de áudio '{caminho_arquivo_audio}': {e_sf}", exc_info=True)
        except Exception as e_general:
            logging.error(f"Erro inesperado durante a geração da narração: {e_general}", exc_info=True)
        return None

    # Atualizar o bloco if __name__ == "__main__": para incluir TTS
    if sumarizacao_inicializada_com_sucesso: 
        texto_exemplo_noticia = "Uma forte tempestade solar atingiu a Terra na última terça-feira, desencadeando espetaculares exibições de auroras em latitudes muito mais baixas do que o usual. Cientistas afirmam que este evento, classificado como G4 em uma escala que vai até G5, foi um dos mais intensos dos últimos anos e levanta preocupações sobre possíveis impactos em satélites de comunicação e redes elétricas globais. As operadoras de energia estão em alerta máximo para monitorar e mitigar quaisquer interrupções."
        logging.info(f"Testando sumarização com texto: '{texto_exemplo_noticia}'")
        sumario_teste = sumarizar_texto(texto_exemplo_noticia)
        logging.info(f"Sumário do teste: {sumario_teste}")

        texto_para_imagem_e_audio = sumario_teste
        if "Erro ao sumarizar" in sumario_teste or not sumario_teste.strip() or "Erro inesperado ao sumarizar" in sumario_teste:
            logging.warning("Sumarização falhou ou retornou sumário vazio/inválido. Usando texto original para imagem e áudio.")
            texto_para_imagem_e_audio = texto_exemplo_noticia
        
        if pipeline_imagem_inicializado_com_sucesso:
            logging.info(f"Testando geração de imagem com base no texto: '{texto_para_imagem_e_audio[:100]}...'")
            caminho_imagem_teste = gerar_imagem_com_pipeline(texto_para_imagem_e_audio) 
            if caminho_imagem_teste and "placeholder" not in caminho_imagem_teste:
                logging.info(f"Imagem de teste (baseada no texto fornecido) gerada com sucesso em: {caminho_imagem_teste}")
            else:
                logging.warning(f"Geração da imagem de teste (baseada no texto fornecido) resultou em placeholder ou falhou: {caminho_imagem_teste}")
        else:
            logging.error("Pipeline de imagem não inicializado. Teste de geração de imagem não pode ser executado.")

        if tts_inicializado_com_sucesso:
            logging.info(f"Testando geração de áudio com base no texto: '{texto_para_imagem_e_audio[:100]}...'")
            caminho_audio_teste = gerar_narracao_audio(texto_para_imagem_e_audio)
            if caminho_audio_teste:
                logging.info(f"Áudio de teste gerado com sucesso em: {caminho_audio_teste}")
            else:
                logging.warning("Geração do áudio de teste falhou.")
        else:
            logging.error("Modelos TTS não inicializados. Teste de geração de áudio não pode ser executado.")

    else: # Se sumarizacao_inicializada_com_sucesso for False
        logging.error("Modelo de sumarização não inicializado. Teste de sumarização, imagem e áudio não pode ser executado completamente.")
        texto_original_para_fallback = "Uma forte tempestade solar atingiu a Terra na última terça-feira, desencadeando espetaculares exibições de auroras em latitudes muito mais baixas do que o usual. Cientistas afirmam que este evento, classificado como G4 em uma escala que vai até G5, foi um dos mais intensos dos últimos anos e levanta preocupações sobre possíveis impactos em satélites de comunicação e redes elétricas globais. As operadoras de energia estão em alerta máximo para monitorar e mitigar quaisquer interrupções."
        
        if pipeline_imagem_inicializado_com_sucesso:
            logging.warning("Modelo de sumarização não carregado. Tentando gerar imagem com texto original de exemplo.")
            caminho_imagem_teste = gerar_imagem_com_pipeline(texto_original_para_fallback)
            if caminho_imagem_teste and "placeholder" not in caminho_imagem_teste:
                logging.info(f"Imagem de teste (baseada no texto original) gerada com sucesso em: {caminho_imagem_teste}")
            else:
                logging.warning(f"Geração da imagem de teste (baseada no texto original) resultou em placeholder ou falhou: {caminho_imagem_teste}")
        else:
            logging.error("Pipeline de imagem também não inicializado. Nenhum teste de geração de imagem pode ser executado.")

        if tts_inicializado_com_sucesso:
            logging.warning("Modelo de sumarização não carregado. Tentando gerar áudio com texto original de exemplo.")
            caminho_audio_teste = gerar_narracao_audio(texto_original_para_fallback)
            if caminho_audio_teste:
                logging.info(f"Áudio de teste (baseado no texto original) gerado com sucesso em: {caminho_audio_teste}")
            else:
                logging.warning("Geração do áudio de teste (baseado no texto original) falhou.")
        else:
            logging.error("Modelos TTS também não inicializados. Nenhum teste de geração de áudio pode ser executado.")


# --- Função Principal de Processamento para o Gradio ---
def processar_noticia_completa(texto_noticia_original: str, progress=gr.Progress(track_tqdm=True)):
    progress(0, desc="Iniciando processamento...")
    time.sleep(0.1) # Pequena pausa para o progresso ser visível

    texto_sumarizado_final = "Falha na sumarização ou modelo não disponível."
    caminho_imagem_final = None
    caminho_audio_final = None
    status_geral = "Processamento iniciado."

    texto_para_conteudo = texto_noticia_original

    # 1. Sumarização
    progress(0.1, desc="Sumarizando texto...")
    if sumarizacao_inicializada_com_sucesso:
        sumario_gerado = sumarizar_texto(texto_noticia_original)
        if "Erro ao sumarizar" in sumario_gerado or "Erro inesperado ao sumarizar" in sumario_gerado or not sumario_gerado.strip():
            status_geral += f" Sumarização falhou ou retornou resultado inválido ('{sumario_gerado[:100]}...'). Usando texto original para demais etapas."
            logging.warning(status_geral)
            texto_sumarizado_final = f"Falha na sumarização. Conteúdo será gerado com base no texto original.\nDetalhe do erro: {sumario_gerado}"
            # texto_para_conteudo já é o original
        else:
            texto_sumarizado_final = sumario_gerado
            texto_para_conteudo = sumario_gerado
            status_geral += " Texto sumarizado com sucesso."
            logging.info("Texto sumarizado com sucesso.")
    else:
        status_geral += " Modelo de sumarização não inicializado. Usando texto original para demais etapas."
        logging.warning(status_geral)
        texto_sumarizado_final = "Modelo de sumarização não disponível. Conteúdo será gerado com base no texto original."
        # texto_para_conteudo já é o original
    
    time.sleep(0.1)

    # 2. Geração de Áudio (TTS)
    progress(0.4, desc="Gerando narração (TTS)...")
    if tts_inicializado_com_sucesso:
        caminho_audio_final = gerar_narracao_audio(texto_para_conteudo)
        if caminho_audio_final:
            status_geral += " Narração gerada com sucesso."
            logging.info(f"Narração gerada: {caminho_audio_final}")
        else:
            status_geral += " Falha na geração da narração."
            logging.error("Falha na geração da narração.")
    else:
        status_geral += " Modelos TTS não inicializados. Narração não pôde ser gerada."
        logging.warning(status_geral)
        # caminho_audio_final permanece None

    time.sleep(0.1)

    # 3. Geração de Imagem
    progress(0.7, desc="Gerando imagem visual...")
    if pipeline_imagem_inicializado_com_sucesso:
        caminho_imagem_final = gerar_imagem_com_pipeline(texto_para_conteudo)
        if caminho_imagem_final and "placeholder" not in caminho_imagem_final:
            status_geral += " Imagem gerada com sucesso."
            logging.info(f"Imagem gerada: {caminho_imagem_final}")
        elif caminho_imagem_final: # É um placeholder
            status_geral += f" Imagem principal não pôde ser gerada, usando placeholder: {caminho_imagem_final}."
            logging.warning(status_geral)
        else: # Falha total na geração da imagem/placeholder
            status_geral += " Falha crítica na geração da imagem (nem placeholder foi gerado)."
            logging.error(status_geral)
            # caminho_imagem_final permanece None, ou poderia ser um placeholder default explícito se criar_imagem_placeholder retornasse None
            caminho_imagem_final = criar_imagem_placeholder("Falha crítica na geração de imagem", "outputs/fallback_imagem_critica.png")

    else:
        status_geral += " Pipeline de imagem não inicializado. Imagem não pôde ser gerada."
        logging.warning(status_geral)
        caminho_imagem_final = criar_imagem_placeholder("Pipeline de imagem não disponível", "outputs/fallback_imagem_pipeline_indisponivel.png")

    time.sleep(0.1)
    progress(1.0, desc="Processamento Concluído!")
    status_geral += " Processamento finalizado."
    
    # Para os componentes gr.File, precisamos fornecer os mesmos caminhos que para visualização
    # se os arquivos existirem, ou None caso contrário.
    download_imagem = caminho_imagem_final if caminho_imagem_final and os.path.exists(caminho_imagem_final) else None
    download_audio = caminho_audio_final if caminho_audio_final and os.path.exists(caminho_audio_final) else None

    return texto_sumarizado_final, caminho_imagem_final, caminho_audio_final, download_imagem, download_audio, status_geral


# --- Definição da Interface Gradio ---
with gr.Blocks(title="Gerador de Notícias em Vídeo com IA", theme=gr.themes.Soft()) as demo:
    gr.Markdown("#  Gerador Automatizado de Notícias em Vídeo com IA")
    gr.Markdown("Insira o texto completo da notícia abaixo e clique em 'Gerar Conteúdo'. O sistema irá sumarizar o texto, gerar uma narração em áudio e uma imagem visual representativa.")

    with gr.Row():
        input_texto_noticia = gr.Textbox(
            label="Texto da Notícia", 
            lines=10, 
            placeholder="Cole o texto completo da notícia aqui..."
        )

    botao_gerar = gr.Button("🚀 Gerar Conteúdo Multimídia")
    
    gr.Markdown("## Resultados Gerados")
    output_status = gr.Markdown(value="Aguardando processamento...") # Para feedback geral e de progresso

    with gr.Row():
        output_texto_sumarizado = gr.Textbox(label="Roteiro Sumarizado / Status da Sumarização", lines=8, interactive=False)
    
    with gr.Row():
        output_imagem_visual = gr.Image(label="Visual Gerado", type="filepath", interactive=False, height=400)
        output_audio_narracao = gr.Audio(label="Narração Gerada", type="filepath", interactive=False)
        
    gr.Markdown("### Baixar Arquivos Gerados")
    with gr.Row():
        output_download_imagem = gr.File(label="Baixar Imagem Gerada", interactive=False)
        output_download_audio = gr.File(label="Baixar Áudio da Narração", interactive=False)

    # Output para vídeo (comentado para uso futuro)
    # output_video = gr.Video(label="Vídeo Gerado") 

    botao_gerar.click(
        fn=processar_noticia_completa,
        inputs=[input_texto_noticia],
        outputs=[
            output_texto_sumarizado, 
            output_imagem_visual, 
            output_audio_narracao,
            output_download_imagem,
            output_download_audio,
            output_status  # Atualiza o status/feedback
        ]
    )

    gr.Markdown("---")
    gr.Markdown("Status dos Modelos de IA:")
    status_sumarizacao_md = "🟢 Carregado com Sucesso" if sumarizacao_inicializada_com_sucesso else "🔴 Falha ao Carregar (Sumarização indisponível)"
    status_imagem_md = "🟢 Carregado com Sucesso" if pipeline_imagem_inicializado_com_sucesso else "🔴 Falha ao Carregar (Geração de Imagem indisponível)"
    status_tts_md = "🟢 Carregado com Sucesso" if tts_inicializado_com_sucesso else "🔴 Falha ao Carregar (TTS indisponível)"
    
    gr.Markdown(f"- **Modelo de Sumarização:** {status_sumarizacao_md}")
    gr.Markdown(f"- **Pipeline de Geração de Imagem:** {status_imagem_md}")
    gr.Markdown(f"- **Modelos de Text-to-Speech (TTS):** {status_tts_md}")


# --- Lançamento da Interface ---
if __name__ == "__main__": # Adicionado para permitir execução direta do script
    logging.info("Verificando status de inicialização dos modelos antes de lançar o Gradio:")
    logging.info(f"  Sumarização: {'OK' if sumarizacao_inicializada_com_sucesso else 'FALHA'}")
    logging.info(f"  Pipeline de Imagem: {'OK' if pipeline_imagem_inicializado_com_sucesso else 'FALHA'}")
    logging.info(f"  TTS: {'OK' if tts_inicializado_com_sucesso else 'FALHA'}")

    if not all([sumarizacao_inicializada_com_sucesso, pipeline_imagem_inicializado_com_sucesso, tts_inicializado_com_sucesso]):
        logging.warning("Um ou mais modelos de IA falharam ao inicializar. A funcionalidade da aplicação pode estar limitada.")
        # Interface ainda será lançada, mas a função processar_noticia_completa lidará com os modelos ausentes.
        # O usuário também verá o status dos modelos na UI.

    demo.queue().launch(debug=True, share=False) # share=False é mais seguro para desenvolvimento
