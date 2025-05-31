# Passos para Teste Manual

Este documento descreve os passos para testar manualmente o site da Vidraçaria Bragança.

## Ambiente de Teste:
- Utilize navegadores web modernos (Chrome, Firefox, Safari, Edge nas últimas versões).
- Verifique em diferentes resoluções de tela (desktop, tablet, mobile).
- Use as ferramentas de desenvolvedor do navegador para inspecionar elementos, verificar console e simular dispositivos móveis.

## Testes a Serem Executados:

### 1. Navegação Principal
- [ ] **Abrir `index.html`:** Verifique se a página inicial carrega corretamente.
- [ ] **Links de Navegação (Header):**
    - [ ] Clicar em "Home": Deve levar para `index.html` ou recarregar a página se já estiver nela.
    - [ ] Clicar em "Galeria": Deve levar para `galeria.html`.
    - [ ] Clicar em "Contato": Deve levar para `contato.html`.
- [ ] **Título da Aba:** Em cada página (Home, Galeria, Contato), verifique se o título exibido na aba do navegador corresponde ao conteúdo da tag `<title>` da página.

### 2. Responsividade
Para cada página (`index.html`, `galeria.html`, `contato.html`):
- [ ] **Redimensionar Janela:**
    - [ ] Diminuir gradualmente a largura da janela do navegador.
    - [ ] Verificar se o layout se ajusta de forma fluida (ex: itens da galeria passam de 3 para 2 e depois 1 coluna).
    - [ ] Garantir que o conteúdo permaneça legível e acessível.
    - [ ] Confirmar a ausência de barras de rolagem horizontais desnecessárias.
- [ ] **Simulação de Dispositivos Móveis (Ferramentas do Desenvolvedor):**
    - [ ] Testar em visualizações como iPhone, iPad, Android (diversos tamanhos).
    - [ ] Verificar se o menu de navegação (ainda simples) é funcional. Se um menu "hambúrguer" fosse implementado, testar sua abertura, fechamento e links.

### 3. Conteúdo e SEO
- [ ] **Revisão de Texto:** Em todas as páginas, leia o conteúdo visível para verificar erros de português, clareza e precisão das informações.
- [ ] **Inspeção de Elementos (Ferramentas do Desenvolvedor):**
    - [ ] **Tag `<h1>`:** Confirmar que há apenas um `<h1>` por página e que seu texto reflete o tópico principal da página.
    - [ ] **Meta Description:** No `<head>` de cada página, verificar se a `<meta name="description">` está presente e se seu conteúdo é relevante e conciso.
    - [ ] **JSON-LD (index.html):** Na página inicial, inspecione o `<head>` para encontrar o script `<script type="application/ld+json">`. Verifique se ele está presente e se a sintaxe JSON parece correta (sem erros de formatação). Use uma ferramenta de teste de dados estruturados do Google (online) se possível para validar.
    - [ ] **Placeholders de Tracking:** Verificar se os comentários placeholder para Google Analytics e Search Console estão presentes no código HTML.

### 4. Página da Galeria (`galeria.html`)
- [ ] **Placeholders de Imagem:** Verificar se os 6 placeholders de imagem são exibidos.
- [ ] **Legendas:** Confirmar que cada imagem placeholder tem uma legenda correspondente.
- [ ] **Layout da Grade:** Verificar se os itens da galeria estão dispostos em uma grade (3 colunas em desktop, ajustando em telas menores).
- [ ] **Botões de Filtro:**
    - [ ] Verificar se os botões de filtro (Todos, Box de Banheiro, etc.) estão visíveis.
    - [ ] (A funcionalidade de filtro será testada após implementação do JavaScript. Por enquanto, apenas a presença e aparência).

### 5. Página de Contato (`contato.html`)
- [ ] **Campos do Formulário:** Verificar se todos os campos (Nome, E-mail, Telefone, Assunto, Mensagem) e o botão "Enviar Mensagem" estão presentes.
- [ ] **Validação de Formulário (HTML5):**
    - [ ] Tentar submeter o formulário sem preencher os campos obrigatórios (`required`). O navegador deve impedir o envio e destacar os campos.
    - [ ] Inserir um e-mail inválido no campo de e-mail e tentar submeter. O navegador deve indicar o erro.
- [ ] **Informações de Contato:**
    - [ ] **Links de Telefone:** Clicar nos números de telefone. Em um dispositivo móvel, deve iniciar a discagem. No desktop, pode sugerir um app de telefonia.
    - [ ] **Link do Endereço:** Clicar no link do endereço. Deve abrir o Google Maps (ou similar) na localização correta em uma nova aba.
    - [ ] **Email:** Clicar no link de e-mail. Deve abrir o cliente de e-mail padrão.
    - [ ] **Horário:** Verificar se o horário de funcionamento está claro.
- [ ] **Placeholder do Mapa:** Verificar se o `div` placeholder para o mapa do Google está visível com a mensagem apropriada.

### 6. Acessibilidade (Manual)
- [ ] **Navegação por Teclado:**
    - [ ] Em cada página, use a tecla `Tab` para navegar entre todos os elementos interativos (links, botões, campos de formulário) e `Shift+Tab` para navegar para trás.
    - [ ] Verificar se cada elemento interativo recebe foco visualmente (o `outline` azul definido no CSS deve aparecer).
    - [ ] Usar `Enter` para ativar links e botões, e `Espaço` para botões (se aplicável).
- [ ] **Atributos `alt` (Imagens Reais):** (Quando as imagens reais forem adicionadas) Verificar se todas as imagens `<img>` possuem texto alternativo (`alt`) descritivo e apropriado. Para os placeholders atuais, os `alt` textos devem ser verificados quanto à sua relevância para o placeholder.
- [ ] **Contraste de Cores:** (Avaliação subjetiva sem ferramentas) Avaliar se o contraste entre texto e cor de fundo parece adequado. Para um teste formal, ferramentas específicas seriam necessárias.

### 7. Console do Navegador
- [ ] Em cada página, abra o console do desenvolvedor (geralmente clicando com o botão direito > Inspecionar > aba Console, ou pressionando F12).
- [ ] **Erros de JavaScript:** Verificar se há algum erro de JavaScript. Não deve haver nenhum, pois ainda não adicionamos scripts customizados.
- [ ] **Erros de Carregamento:** Verificar se há erros relacionados ao carregamento de recursos (ex: CSS não encontrado - não deve ocorrer).

### 8. Validação Externa (se o ambiente de teste permitir acesso à internet)
- [ ] **Validar HTML:** Copiar o código fonte de cada página HTML e colar no validador do W3C: [https://validator.w3.org/](https://validator.w3.org/)
- [ ] **Validar CSS:** Copiar o conteúdo de `style.css` e colar no validador Jigsaw do W3C: [https://jigsaw.w3.org/css-validator/](https://jigsaw.w3.org/css-validator/)

Este plano de teste ajudará a garantir a qualidade e funcionalidade do site antes do lançamento.
