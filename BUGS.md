# Relatórios de bug

O [Sauce Demo](https://www.saucedemo.com/) e o [ServeRest](https://serverest.dev/) são aplicações feitas para treinar testes, e parte dos defeitos existe de propósito. Mesmo assim, registro cada um no formato que usaria num time. Nenhum relatório entrou sem o defeito ser reproduzido duas vezes. Cada um tem um teste que falha enquanto o defeito existir: o teste é marcado com `xfail(strict=True)`, e se alguém corrigir o defeito, o teste passa a acusar (XPASS) e o relatório precisa ser revisto.

- **Severidade:** impacto técnico do defeito.
- **Prioridade:** urgência de correção para o negócio. As duas nem sempre andam juntas; o BUG-002 é o exemplo.
- **Ambiente comum (BUG-001 a 004):** https://www.saucedemo.com, Chrome 155 headless, janela 1920×1080, macOS (local) e ubuntu-24.04 (CI). Encontrados em 24/10/2026.
- **Evidência:** a cada execução, a suíte salva screenshot e HTML da página dos testes destes bugs em `screenshots/` (artefato `test-report` no CI). O screenshot do Chrome cobre só a área visível; quando o valor está abaixo da dobra, a prova está no HTML.

| ID | Título | Severidade | Prioridade |
|---|---|---|---|
| BUG-001 | Checkout aceita nome, sobrenome e CEP só com espaços | Média | Média |
| BUG-002 | "Item total" do checkout aparece com erro de ponto flutuante | Baixa | Alta |
| BUG-003 | "Add to cart" não funciona em 3 dos 6 produtos (`problem_user`) | Alta | Alta |
| BUG-004 | Ordenar o catálogo abre um alerta de erro e não ordena (`error_user`) | Média | Média |
| BUG-005 | API: a lista de usuários expõe a senha de todos, sem autenticação | Crítica | Alta |
| BUG-006 | O link do carrinho não recebe foco pelo teclado | Alta | Alta |

---

## BUG-001: Checkout aceita nome, sobrenome e CEP só com espaços

- **Usuário:** `standard_user`
- **Passos:**
  1. Entrar como `standard_user`.
  2. Adicionar "Sauce Labs Backpack" ao carrinho, abrir o carrinho e clicar em **Checkout**.
  3. Preencher **First Name**, **Last Name** e **Zip/Postal Code** com três espaços cada.
  4. Clicar em **Continue**.
- **Esperado:** o formulário recusa, como já recusa campo vazio ("Error: First Name is required"). Não há especificação; a expectativa vem do próprio formulário, que trata o campo como obrigatório.
- **Obtido:** a página segue para "Checkout: Overview" e o pedido pode ser finalizado sem nome nem CEP.
- **Severidade:** média. Entra no sistema um pedido sem dado de entrega utilizável.
- **Prioridade:** média.
- **Evidência:** o HTML salvo pelo teste mostra o título "Checkout: Overview" depois do Continue.
- **Teste:** `tests/ui/test_checkout.py::test_checkout_info_requires_each_field[TC-CHK-04-whitespace-only]`

## BUG-002: "Item total" do checkout aparece com erro de ponto flutuante

- **Usuário:** `standard_user`
- **Passos:**
  1. Entrar como `standard_user`.
  2. Adicionar ao carrinho todos os produtos menos o "Sauce Labs Backpack": Bike Light, Bolt T-Shirt, Fleece Jacket, Onesie e Test.allTheThings() T-Shirt (Red).
  3. Abrir o carrinho, clicar em **Checkout**, preencher dados válidos e clicar em **Continue**.
- **Esperado:** "Item total: $99.95", a soma dos preços listados (9.99 + 15.99 + 49.99 + 7.99 + 15.99).
- **Obtido:** "Item total: $99.94999999999999". Na mesma tela, "Tax: $8.00" e "Total: $107.95" aparecem arredondados.
- **Causa provável:** a soma é feita em ponto flutuante e exibida sem arredondar. Somando os preços um a um em `float`, na ordem do carrinho, o resultado é exatamente 99.94999999999999. No Python, isso vale para `+` em sequência: o `sum()` do Python 3.12+ usa soma compensada e devolve 99.95.
- **Severidade:** baixa. O total cobrado está certo.
- **Prioridade:** alta. Um valor estranho na tela de pagamento derruba a confiança do cliente, e a correção é pequena.
- **Evidência:** HTML da página (o subtotal fica abaixo da área visível do screenshot).
- **Teste:** `tests/ui/test_checkout.py::test_item_total_adds_up_five_products`

## BUG-003: "Add to cart" não funciona em 3 dos 6 produtos (`problem_user`)

- **Usuário:** `problem_user`. O `error_user` tem o mesmo comportamento.
- **Passos:**
  1. Entrar como `problem_user`.
  2. Clicar em **Add to cart** no "Sauce Labs Bolt T-Shirt".
- **Esperado:** o botão vira **Remove** e o ícone do carrinho mostra 1.
- **Obtido:** nada muda. Numa sessão nova para cada produto, Bolt T-Shirt, Fleece Jacket e Test.allTheThings() T-Shirt (Red) **nunca** entram no carrinho; Backpack, Bike Light e Onesie entram. Adicionando os seis em sequência na mesma sessão, o Onesie também falha depois das tentativas anteriores. Na mesma exploração, **Remove** no catálogo não tirou o Backpack do carrinho.
- **Correção deste relatório:** a primeira versão dizia "4 dos 6", porque a exploração só tinha adicionado os produtos em sequência. A revisão reproduziu com uma sessão por produto, e o relato foi corrigido.
- **Severidade:** alta. Impede a compra da maior parte do catálogo.
- **Prioridade:** alta.
- **Evidência:** no screenshot, todos os botões continuam "Add to cart" e o carrinho não tem contador depois do clique.
- **Teste:** `tests/ui/test_inventory.py::test_problem_user_adds_any_product_to_cart`

## BUG-004: Ordenar o catálogo abre um alerta de erro e não ordena (`error_user`)

- **Usuário:** `error_user`
- **Passos:**
  1. Entrar como `error_user`.
  2. No seletor de ordenação, escolher **Name (Z to A)**.
- **Esperado:** a lista passa para a ordem Z→A, sem alerta.
- **Obtido:** abre um alerta JavaScript com o texto "Sorting is broken! This error has been reported to Backtrace.". Depois de aceitar, a lista continua em A→Z e o seletor continua mostrando "Name (A to Z)".
- **Severidade:** média. A função quebra, mas o catálogo continua navegável sem ordenar.
- **Prioridade:** média.
- **Evidência:** o HTML salvo depois do alerta mostra "Name (A to Z)" como opção ativa e "Sauce Labs Backpack" como primeiro item.
- **Teste:** `tests/ui/test_inventory.py::test_error_user_sorts_products_without_an_error`

## BUG-005: API: a lista de usuários expõe a senha de todos, sem autenticação

- **Sistema:** ServeRest 3.2.2 (API REST de estudo), rodando localmente e no CI.
- **Passos:**
  1. Sem token, enviar `GET /usuarios`.
- **Esperado:** a resposta não traz senha de ninguém. Senha não deveria sair da API em nenhuma rota, e listar usuários deveria exigir autenticação.
- **Obtido:** `200 OK` com cada usuário trazendo `password` em texto puro.
- **Observação:** o próprio Swagger do ServeRest documenta esse campo, então o comportamento segue o contrato publicado. Registro como defeito porque, num sistema real, isso seria um vazamento de credenciais. O JSON Schema da suíte aceita o campo, porque é o contrato documentado, mas não o exige, e o teste do bug falha enquanto o campo existir.
- **Severidade:** crítica (exposição de credenciais).
- **Prioridade:** alta.
- **Teste:** `tests/api/test_users_api.py::test_user_list_does_not_expose_passwords`

## BUG-006: O link do carrinho não recebe foco pelo teclado

- **Usuário:** `standard_user`. O cabeçalho é o mesmo em todas as páginas internas.
- **Ambiente:** https://www.saucedemo.com, Chrome 155 headless, janela 1920×1080, macOS. Encontrado em 26/10/2026, numa sondagem de navegação por teclado.
- **Passos:**
  1. Entrar como `standard_user`.
  2. No catálogo, sem usar o mouse, apertar **Tab** repetidamente, do topo da página até o foco dar a volta.
- **Esperado:** o ícone do carrinho recebe o foco em algum momento, e **Enter** abre o carrinho. O que funciona com o mouse deve funcionar pelo teclado (WCAG 2.1, critério 2.1.1 Teclado, nível A).
- **Obtido:** o foco passa pelo menu, pela ordenação, pelos links e botões dos seis produtos e pelos links das redes sociais, 23 paradas ao todo, e nunca pelo carrinho. Nem `element.focus()` por script põe o foco nele. O menu lateral não tem item para o carrinho. Com o mouse, o clique abre `/cart.html` normalmente.
- **Causa provável:** o elemento é `<a class="shopping_cart_link" data-test="shopping-cart-link" role="button" aria-label="Cart, empty">`, sem `href` e sem `tabindex`. Um `<a>` sem `href` não entra na ordem de foco. Um `<button>`, ou um link com `href="/cart.html"`, resolveria.
- **Observação:** o axe-core não acusa nada nesta página. Ele confere o HTML (rótulos, papéis, contraste), mas não sabe que o elemento tem uma ação de clique que o teclado não alcança. Por isso a navegação por teclado tem teste próprio.
- **Severidade:** alta. Quem navega só pelo teclado não consegue abrir o carrinho, e sem carrinho não há compra.
- **Prioridade:** alta. A compra é o fluxo principal, e a correção é pequena.
- **Evidência:** a mensagem da asserção lista as paradas de Tab. O HTML salvo pelo teste mostra o elemento sem `href` e sem `tabindex`.
- **Teste:** `tests/a11y/test_keyboard.py::test_cart_link_is_reachable_with_the_keyboard`
