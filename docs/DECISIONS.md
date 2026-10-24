# Decisões

Registro curto das escolhas que mudam como a suíte se comporta. Cada uma traz a alternativa descartada e em que cenário eu mudaria de ideia.

## 1. Selenium Manager em vez de webdriver-manager

- **Decisão:** `webdriver.Chrome(options=...)` sem gerenciar o chromedriver à mão.
- **Alternativa descartada:** o pacote `webdriver-manager`.
- **Por quê:** desde o Selenium 4.6, o Selenium Manager vem junto e baixa o driver compatível com o Chrome instalado. Uma dependência a menos e uma fonte a menos de "driver na versão errada".
- **Quando mudaria:** em rede sem acesso à internet, em que o driver precisa vir de um espelho interno ou de um caminho fixo.

## 2. Só espera explícita, sem espera implícita

- **Decisão:** toda espera é `WebDriverWait` com uma condição (`visibility_of_element_located`, `url_contains`...). A espera implícita fica no padrão do Selenium, que é zero, e nenhum `time.sleep`.
- **Alternativa descartada:** `driver.implicitly_wait(10)` global.
- **Por quê:** a documentação do Selenium recomenda não misturar as duas, porque os tempos se somam de forma imprevisível. A espera explícita também documenta *pelo que* o teste espera. Exemplo real, visto ao explorar o site antes de escrever os testes: depois do login, a URL muda antes de o React terminar de desenhar a página, e ler os elementos logo depois de esperar só pela URL deu `StaleElementReferenceException`. Por isso o teste espera o título da página nova.
- **Quando mudaria:** não vejo cenário nesta suíte. O que muda é o timeout de um fluxo específico, sempre numa constante com nome.

## 3. Navegador novo por teste, sem nova tentativa automática

- **Decisão:** a fixture `driver` tem escopo `function`: cada teste abre e fecha o próprio Chrome. Nenhum plugin de *rerun*.
- **Alternativa descartada:** um navegador por sessão, com limpeza de cookies e `localStorage` entre os testes.
- **Por quê:** o Sauce Demo guarda a sessão num cookie e o carrinho no `localStorage`. Com um navegador compartilhado, o isolamento dependeria de a limpeza estar sempre certa, e um carrinho que vaza de um teste para o outro gera o teste que só falha quando a suíte roda inteira. Nova tentativa automática esconde exatamente esse tipo de problema: quando um teste falha, quero a evidência (screenshot e HTML da página), não um segundo sorteio.
- **Quando mudaria:** com centenas de testes, o custo de abrir o navegador passaria a pesar. Aí eu mediria primeiro e consideraria paralelizar (pytest-xdist ou Selenium Grid) antes de compartilhar o navegador.
