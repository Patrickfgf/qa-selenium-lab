# Decisões

Registro curto das escolhas que mudam como a suíte se comporta. Cada uma traz a alternativa descartada e em que cenário eu mudaria de ideia.

## 1. Selenium Manager em vez de webdriver-manager

- **Decisão:** `webdriver.Chrome(options=...)` sem gerenciar o chromedriver à mão.
- **Alternativa descartada:** o pacote `webdriver-manager`.
- **Por quê:** desde o Selenium 4.6, o Selenium Manager vem junto e baixa o driver compatível com o Chrome instalado. Uma dependência a menos e uma fonte a menos de "driver na versão errada".
- **Quando mudaria:** em rede sem acesso à internet, em que o driver precisa vir de um espelho interno ou de um caminho fixo.

## 2. Só espera explícita, sem espera implícita

- **Decisão:** toda espera é `WebDriverWait` com uma condição (`visibility_of_element_located`, `element_to_be_clickable`, `alert_is_present`). A espera implícita fica no padrão do Selenium, que é zero, e nenhum `time.sleep`.
- **Alternativa descartada:** `driver.implicitly_wait(10)` global.
- **Por quê:** a documentação do Selenium recomenda não misturar as duas, porque os tempos se somam de forma imprevisível. A espera explícita também documenta *pelo que* o teste espera. Exemplo real, visto ao explorar o site antes de escrever os testes: depois do login, a URL muda antes de o React terminar de desenhar a página, e ler os elementos logo depois de esperar só pela URL deu `StaleElementReferenceException`. Por isso o Page Object do catálogo espera o contêiner da lista (`inventory-container`) e não a URL.
- **Quando mudaria:** não vejo cenário nesta suíte. O que muda é o timeout de um fluxo específico, sempre numa constante com nome.

## 3. Navegador novo por teste, sem nova tentativa automática

- **Decisão:** a fixture `driver` tem escopo `function`: cada teste abre e fecha o próprio Chrome. Nenhum plugin de *rerun*.
- **Alternativa descartada:** um navegador por sessão, com limpeza de cookies e `localStorage` entre os testes.
- **Por quê:** o Sauce Demo guarda a sessão num cookie e o carrinho no `localStorage`. Com um navegador compartilhado, o isolamento dependeria de a limpeza estar sempre certa, e um carrinho que vaza de um teste para o outro gera o teste que só falha quando a suíte roda inteira. Nova tentativa automática esconde exatamente esse tipo de problema: quando um teste falha, quero a evidência (screenshot e HTML da página), não um segundo sorteio.
- **Quando mudaria:** com centenas de testes, o custo de abrir o navegador passaria a pesar. Aí eu mediria primeiro e consideraria paralelizar (pytest-xdist ou Selenium Grid) antes de compartilhar o navegador.

## 4. Page Objects: localizador na classe, asserção no teste, próxima página como retorno

- **Decisão:** cada página guarda seus localizadores como tuplas `(By, valor)` e nunca um `WebElement`. O construtor espera um elemento-âncora da página. Ação que muda de tela devolve o Page Object da tela seguinte (`login_as` devolve `InventoryPage`). Nenhum `assert` dentro de `pages/`. O cabeçalho (carrinho e menu) é um componente (`pages/components/header.py`) usado pelas páginas, e não uma página.
- **Alternativa descartada:** Page Object que guarda elementos já encontrados e faz as próprias verificações.
- **Por quê:** elemento guardado fica velho quando o React redesenha a tela (`StaleElementReferenceException`). Com a asserção no teste, o mesmo Page Object serve para o caminho feliz e para o caso de erro (`login_as` e `login_expecting_error`).
- **Quando mudaria:** não mudaria a regra; mudaria o tamanho. Com dezenas de páginas, eu separaria componentes menores (linha de produto, formulário).

## 5. `BasePage` só depois da duplicação

- **Decisão:** as esperas comuns (`_visible`, `_click`, `_texts`) foram para uma `BasePage` num commit de refatoração, quando `LoginPage`, `InventoryPage` e `Header` já repetiam o mesmo código.
- **Alternativa descartada:** começar por uma `BasePage` com métodos para tudo o que talvez fosse preciso.
- **Por quê:** método que nenhum teste chama é código para manter sem retorno. O histórico mostra a duplicação aparecendo e sendo removida.

## 6. Login pela "porta dos fundos" fora dos testes de login

- **Decisão:** a fixture `inventory_page` grava o cookie `session-username` e abre o catálogo direto. Só `test_login.py` usa o formulário de login.
- **Alternativa descartada:** passar pelo formulário de login no começo de todo teste.
- **Por quê:** a documentação do Selenium recomenda não usar a interface para preparar o estado de um teste. Isso deixa o teste mais rápido e faz ele falhar só pelo que ele testa. O mecanismo foi conferido ao vivo: sem o cookie, `/inventory.html` volta para o login com erro; com o cookie, abre o catálogo.
- **Quando mudaria:** num sistema real eu prepararia a sessão por uma API de login, e não por um cookie montado à mão. Se o Sauce Demo mudar como guarda a sessão, a fixture volta a usar o formulário.

## 7. Preços em `Decimal` e oráculo a partir da tela

- **Decisão:** todo preço lido da página vira `Decimal`. O teste de compra confere que o item total é a soma dos preços listados e que o total é item total mais taxa. A taxa não é recalculada, porque o percentual não aparece em lugar nenhum.
- **Alternativa descartada:** `float`, ou números fixos copiados da tela no dia em que o teste foi escrito.
- **Por quê:** somas em `float` erram: somados um a um em `float`, os cinco preços do BUG-002 dão 99.94999999999999, exatamente o valor que o site mostra. (O `sum()` do Python 3.12+ compensa o erro e daria 99.95; o `Decimal` não depende disso.) Número fixo quebraria a cada mudança de preço e não diria de onde vem o valor esperado.

## 8. Bug conhecido como `xfail(strict=True, raises=...)`

- **Decisão:** cada defeito do `BUGS.md` tem um teste que descreve o comportamento correto e está marcado como falha esperada, com o ID do bug no motivo e o tipo de exceção esperado.
- **Alternativa descartada:** pular o teste (`skip`), ou deixar o CI vermelho até alguém corrigir.
- **Por quê:** `skip` não executa nada e esconde o bug. Vermelho permanente ensina o time a ignorar o vermelho. Com `strict=True`, se o bug for corrigido, o teste passa a acusar e o relatório é revisto. O `raises=` evita que uma falha por outro motivo (um localizador quebrado, por exemplo) seja confundida com o bug.

## 9. API: ServeRest rodando dentro do job, e não uma instância compartilhada

- **Decisão:** os testes de API usam o ServeRest (`npx serverest@3.2.2`), iniciado no próprio job do CI, que espera a API responder antes dos testes.
- **Alternativa descartada:** a instância pública do ServeRest, ou o restful-booker, que também é compartilhado.
- **Por quê:** numa instância compartilhada, os dados mudam por causa de outras pessoas e a disponibilidade não depende de mim. Teste que falha por isso é instabilidade fabricada. Rodando local, cada execução começa do mesmo estado. Os testes também criam os próprios usuários, com e-mail único, e os apagam no final.
- **Quando mudaria:** para testar um ambiente de homologação de verdade, eu rodaria um conjunto pequeno e só de leitura contra ele, separado desta suíte.

## 10. Contrato com JSON Schema, e não com pydantic

- **Decisão:** as respostas são validadas com `jsonschema` contra schemas em `tests/api/schemas/`, escritos a partir do Swagger da API.
- **Alternativa descartada:** modelos pydantic.
- **Por quê:** o contrato de uma API REST costuma ser publicado em OpenAPI/Swagger, que usa JSON Schema. Um schema em JSON pode ser comparado campo a campo com o Swagger e lido por quem não programa em Python. Com `additionalProperties: false`, um campo novo e não documentado também quebra o teste.
- **Quando mudaria:** se a suíte precisasse montar objetos tipados para reutilizar em várias chamadas, pydantic pagaria o custo.

## 11. Cliente de API fino, e não um "Page Object" de API

- **Decisão:** `tests/api/client.py` só junta a URL base, o timeout e o cabeçalho `Authorization`, e devolve a resposta crua do `requests`.
- **Alternativa descartada:** um cliente com um método por regra de negócio (`create_user`, `login`...) que já devolve o JSON tratado.
- **Por quê:** num teste de API, o status, os cabeçalhos e o corpo *são* o que está sendo testado. Esconder a resposta num método tiraria isso do teste. As ações que só preparam o cenário (criar usuário, fazer login) ficaram em fixtures.

## 12. Acessibilidade em duas camadas: axe-core para as regras, Selenium para o teclado

- **Decisão:** o axe-core roda nas páginas da compra e o CI falha em qualquer violação das regras WCAG 2.x A e AA. O uso pelo teclado tem teste próprio, que aperta Tab e anota quem recebe o foco (`switch_to.active_element`).
- **Alternativa descartada:** só o axe, e com todas as regras ligadas, inclusive as de boa prática.
- **Por quê:** o axe lê o HTML, mas não sabe quais elementos têm ação de clique. Na exploração, ele não acusou nada no catálogo, e o teste de teclado achou o carrinho fora do alcance do Tab (BUG-006), uma falha de nível A. As regras de boa prática (página sem `<h1>`, por exemplo) são sugestões, não critérios do WCAG; ficam anotadas no `TEST_PLAN.md` em vez de quebrar o build. O que o axe devolve como inconclusivo, como o contraste no catálogo, vira conferência manual.
- **Quando mudaria:** num sistema obrigado a seguir uma norma específica, como o eMAG em sites de governo, eu ligaria as regras que a norma cobra e tiraria as outras.

## 13. axe-core instalado pelo npm, com lockfile

- **Decisão:** `package.json` fixa o `axe-core` na versão exata, o `package-lock.json` guarda o hash, e o CI instala com `npm ci --ignore-scripts`. Sem o pacote, o teste é pulado na máquina local e falha no CI, a mesma regra da API.
- **Alternativas descartadas:** copiar o `axe.min.js` (650 KB) para dentro do repositório; o pacote Python `axe-selenium-python`; baixar o script de uma CDN na hora do teste.
- **Por quê:** o arquivo copiado ninguém revisa, e atualizar vira trabalho manual. O pacote Python traz a própria cópia do axe-core (a versão 3.0.0, de abril de 2026, usa o 4.10.2, e o atual é o 4.14.0), então a versão das regras fica presa ao ritmo de lançamento dele, para poupar umas vinte linhas de código que injetam o script. A CDN põe rede e versão fora de controle no meio do teste. Pelo npm, a versão e o hash ficam no lockfile, e o Node já está no job por causa do ServeRest. O `--ignore-scripts` impede que um script de instalação rode no CI.
- **Quando mudaria:** se o projeto deixasse de ter Node em qualquer outro lugar, copiar o script com a versão no nome do arquivo seria aceitável.
