# Plano de teste

## Objetivo

Verificar os fluxos de negócio do Sauce Demo (entrar, ver o catálogo, ordenar, montar o carrinho, fechar a compra e sair) e as regras de autenticação e cadastro da API do ServeRest, conferir a parte automatizável da acessibilidade, registrar os defeitos encontrados e deixar claro o que é automatizado, o que fica manual e por quê.

## Escopo

- **Dentro (interface):** login e logout, catálogo e ordenação, carrinho, checkout em três passos, e os usuários de teste que simulam bloqueio (`locked_out_user`), defeitos (`problem_user`, `error_user`) e lentidão (`performance_glitch_user`).
- **Dentro (API, ServeRest 3.2.2 local):** `POST /login`, `POST`, `GET` e `DELETE` de `/usuarios`, e a permissão de `POST /produtos`.
- **Dentro (acessibilidade):** as regras WCAG 2.x A e AA do axe-core no login, no catálogo, no carrinho e no primeiro passo do checkout; e o uso só pelo teclado no login e no catálogo.
- **Fora:** layout em celular, acessibilidade com leitor de tela, desempenho sob carga, outros navegadores além do Chrome, as páginas externas (redes sociais, site da Sauce Labs) e as rotas de carrinho da API.

## Comportamentos esperados

Não há especificação do Sauce Demo: os comportamentos da interface foram **inferidos do próprio app** (mensagens de erro, rótulos, o que os campos exigem). Os da API vêm do **Swagger do ServeRest**, conferido contra as respostas reais. Os de acessibilidade vêm do **WCAG 2.x**, níveis A e AA.

| ID | Comportamento |
|---|---|
| C-LOGIN | Só usuário existente, não bloqueado e com a senha certa entra. Cada motivo de recusa tem sua mensagem. |
| C-SESSION | Sair encerra a sessão: uma página interna aberta depois disso volta para o login. |
| C-SORT | As quatro ordenações reordenam o catálogo sem perder nem repetir produto. |
| C-CART | Adicionar um produto troca o botão para "Remove" e soma 1 no contador do carrinho. |
| C-CHECKOUT-INFO | Nome, sobrenome e CEP são obrigatórios. |
| C-CHECKOUT-TOTAL | Item total é a soma dos preços listados; total é item total mais taxa; o pedido concluído mostra a confirmação. |
| C-API-AUTH | Login devolve um token `Bearer` do próprio usuário. Credencial errada dá 401; requisição malformada dá 400, com o erro por campo. |
| C-API-USERS | Usuário criado fica gravado com os dados enviados; e-mail duplicado é recusado; a lista segue o contrato e não expõe senha. |
| C-API-PERM | Criar produto exige token (401 sem ele) e perfil de administrador (403 para usuário comum). |
| C-A11Y-RULES | As páginas não violam as regras WCAG A e AA que o axe-core verifica. |
| C-A11Y-KEYBOARD | O que funciona com o mouse funciona só com o teclado (WCAG 2.1.1): todo controle recebe foco, na ordem da página. |

## Riscos que orientam a prioridade

| Risco | Probabilidade | Impacto | Como a suíte cobre |
|---|---|---|---|
| R1. A compra não fecha | baixa | alto | teste de compra (marcador `smoke`) |
| R2. O login aceita quem não deveria, ou recusa quem deveria | baixa | alto | tabela de decisão do login |
| R3. Valor errado na tela de pagamento | média | alto | oráculo que soma os preços exibidos em `Decimal` |
| R4. Dado inválido aceito no checkout | média | médio | partição de equivalência do formulário |
| R5. A suíte falhar por motivo que não é defeito (site de terceiros, tempo, ambiente) | média | médio | só espera explícita, navegador novo por teste, evidência em toda falha, triagem abaixo |
| R6. A API deixar passar quem não deveria, ou expor dado sensível | média | alto | 401 contra 403 em `/produtos`, mensagem genérica no login, BUG-005 |
| R7. A resposta da API mudar de formato sem aviso | média | médio | JSON Schema com `additionalProperties: false` |
| R8. Quem não usa mouse, ou usa tecnologia assistiva, não conseguir comprar | média | alto | axe-core nas páginas da compra, navegação por teclado, BUG-006; leitor de tela fica manual |

## Técnicas de desenho de teste

- **Tabela de decisão no login** (usuário × senha). Coberto: válido + senha certa (01), bloqueado + senha certa (02), válido + senha errada (03), usuário inexistente (04), senha vazia (05), usuário vazio (06), os dois vazios (07) e bloqueado + senha errada (08). O caso 08 mostra que o app confere a senha antes de revelar o bloqueio, então não dá para descobrir quais contas existem. Ficaram de fora usuário com maiúsculas (o app trata como inexistente, o mesmo resultado do 04) e espaços antes ou depois do usuário.
- **Partição na API de login:** credencial válida, credencial errada, e-mail inexistente (mesma resposta da senha errada, para não revelar quais e-mails existem), campo vazio e e-mail malformado.
- **Partição de equivalência no checkout:** cada campo tem três classes (vazio, só espaços, preenchido). O formulário valida na ordem nome, sobrenome e CEP, então cada linha deixa vazio o próximo campo obrigatório. A classe "só espaços" é a que reproduz o BUG-001.
- **Valor-limite:** não se aplica aqui. Os campos não declaram tamanho mínimo nem máximo, e eu não invento um limite só para testá-lo.
- **Oráculo independente:** o resultado esperado não sai do próprio app. A ordenação é conferida com `sorted()` do Python sobre o que a página mostra; o total, somando em `Decimal` os preços exibidos. É esse oráculo que pega o BUG-002.
- **Acessibilidade em duas camadas:** o axe-core confere o que dá para ler no HTML (rótulos, papéis, contraste) e devolve três tipos de resultado: violação, aprovado e inconclusivo, que pede olho humano. O uso pelo teclado é testado à parte, apertando Tab e anotando quem recebe o foco, porque o axe não sabe quais elementos têm ação de clique. Foi essa segunda camada que achou o BUG-006, numa página em que o axe não acusou nada.

## Rastreabilidade

| Comportamento | Caso | Teste | Como |
|---|---|---|---|
| C-LOGIN | TC-LOGIN-01 | `test_login.py::test_standard_user_logs_in_and_sees_products` | automatizado |
| C-LOGIN | TC-LOGIN-02 a 08 | `test_login.py::test_login_is_rejected_and_stays_on_login` | automatizado |
| C-LOGIN | lentidão | `test_login.py::test_performance_glitch_user_gets_in_with_a_longer_wait` | automatizado |
| C-SESSION | logout | `test_login.py::test_log_out_ends_the_session` | automatizado |
| C-SORT | TC-SORT-01 a 04 | `test_inventory.py::test_sort_orders_products` | automatizado |
| C-SORT | BUG-004 | `test_inventory.py::test_error_user_sorts_products_without_an_error` | automatizado (xfail) |
| C-CART | BUG-003 | `test_inventory.py::test_problem_user_adds_any_product_to_cart` | automatizado (xfail) |
| C-CART, C-CHECKOUT-TOTAL | compra | `test_checkout.py::test_standard_user_buys_two_products` | automatizado |
| C-CHECKOUT-INFO | TC-CHK-01 a 04 | `test_checkout.py::test_checkout_info_requires_each_field` | automatizado (04 é xfail, BUG-001) |
| C-CHECKOUT-TOTAL | BUG-002 | `test_checkout.py::test_item_total_adds_up_five_products` | automatizado (xfail) |
| C-API-AUTH | TC-API-LOGIN-01 | `api/test_login_api.py::test_login_returns_a_bearer_token_for_that_user` | automatizado |
| C-API-AUTH | TC-API-LOGIN-02 a 05 | `api/test_login_api.py::test_login_is_rejected` | automatizado |
| C-API-USERS | gravação, duplicado, contrato | `api/test_users_api.py` | automatizado |
| C-API-USERS | BUG-005 | `api/test_users_api.py::test_user_list_does_not_expose_passwords` | automatizado (xfail) |
| C-API-PERM | 401, 403, 201 | `api/test_products_api.py` | automatizado |
| C-A11Y-RULES | login, catálogo, carrinho, checkout | `a11y/test_axe.py` | automatizado |
| C-A11Y-KEYBOARD | login e controles do catálogo | `a11y/test_keyboard.py` | automatizado |
| C-A11Y-KEYBOARD | BUG-006 | `a11y/test_keyboard.py::test_cart_link_is_reachable_with_the_keyboard` | automatizado (xfail) |
| Aparência do catálogo | `visual_user`, imagens do `problem_user` | — | manual |
| Contraste no catálogo | `color-contrast` inconclusivo no axe | — | manual |

## O que fica manual, e por quê

- **Aparência (`visual_user`, imagens do `problem_user`):** na exploração, o `problem_user` mostra a mesma foto em todos os produtos e o `visual_user` mostra o catálogo com outros preços. Conferir se uma tela "está certa" visualmente pede julgamento humano ou uma ferramenta de comparação de imagens. Automatizar isso com asserções de atributo geraria teste frágil para pouco ganho neste tamanho de projeto.
- **Exploratório:** os quatro primeiros bugs da interface apareceram em sessões curtas de exploração com cada usuário, e o BUG-006 numa sondagem de navegação por teclado. As técnicas acima transformaram cada um num caso de teste repetível. Exploração vem antes da automação, não no lugar dela.
- **Contraste no catálogo:** o axe deixa a regra `color-contrast` como inconclusiva nessa página: não consegue decidir sozinho a cor de fundo de alguns textos. A conferência é visual, com o medidor de contraste do DevTools.
- **Leitor de tela e celular:** dependem de dispositivo e de percepção. O axe e o teste de teclado cobrem só parte do que uma pessoa com deficiência encontra.
- **Boas práticas de acessibilidade fora do WCAG:** o axe aponta que nenhuma página tem um título `<h1>` e que o logo do login fica fora de qualquer região da página (*landmark*). São sugestões de melhoria, não critérios do WCAG, então não viraram relatório de bug nem fazem o CI falhar.

## Triagem de falha: defeito ou instabilidade?

1. Ler a mensagem do pytest e abrir a evidência do artefato `test-report` (screenshot e HTML da página).
2. Reproduzir só aquele teste várias vezes, na mesma versão:
   ```bash
   for i in 1 2 3 4 5; do uv run pytest -q "tests/ui/test_checkout.py::test_standard_user_buys_two_products"; done
   ```
3. **Falha sempre:** é defeito, do app ou do teste (localizador mudou? expectativa errada?). **Falha às vezes:** procurar a fonte de variação: espera pela coisa errada, estado vazando entre testes, site fora do ar, diferença de ambiente (headless, tamanho de janela, versão do Chrome).
4. **Sem nova tentativa automática:** rodar de novo serve para juntar evidência, não para esconder a falha. Defeito confirmado do app vira um relatório em `BUGS.md` e um teste `xfail(strict=True)`.

Casos reais desta suíte:

- Um script exploratório com `time.sleep(0.3)` indicou que o `standard_user` não conseguia pôr produtos no carrinho. Com espera explícita pelo botão "Remove", 6 de 6 produtos entraram, em duas rodadas. O problema era o script, não o site.
- O clique no menu falhou 3 de 3 vezes com `ElementClickInterceptedException`. Falha determinística aponta para o teste, e era o localizador: o `data-test` estava no ícone, e não no botão que recebe o clique.
- O BUG-003 foi registrado primeiro como "4 dos 6 produtos". Reproduzindo com uma sessão nova por produto, eram 3: o Onesie só falhava depois de outras tentativas na mesma sessão. Lição: o resultado de um passo pode depender do estado deixado pelos anteriores, então a reprodução de um bug começa do zero.
- Apareceu um screenshot de um teste que estava passando. Era evidência de uma execução anterior. A suíte passou a limpar `screenshots/` no início de cada execução.
- Na sondagem de teclado, depois do último elemento do login o foco foi para o `<body>` numa rodada e voltou ao primeiro campo na outra. Um teste que esperasse só um dos dois seria instável, então a função que percorre a página com Tab para nos dois casos.

## Critérios de entrada e de saída

- **Entrada:** o site responde, o ServeRest está no ar e `uv run pytest -m smoke` passa.
- **Saída:** CI verde no `main`, e todo defeito conhecido com relatório em `BUGS.md` e teste `xfail(strict=True)`.

## Limitações conhecidas

- O TC-SORT-01 (A a Z) passaria mesmo se a ordenação não fizesse nada, porque A a Z já é a ordem inicial. Os outros três casos pegam esse defeito.
- No Chrome, o screenshot cobre só a área visível. O HTML salvo junto completa a evidência.
- A suíte depende de um site de terceiros: uma mudança no Sauce Demo pode quebrá-la sem mudança neste código.
- Passar no axe não quer dizer que a página é acessível: o BUG-006 está numa página sem nenhuma violação no axe.
- Na API, `GET /usuarios/{id}` de um id inexistente devolve 400, e não o 404 que REST sugere. Está documentado assim no Swagger, então não virou relatório de bug, mas é o tipo de desvio que eu levaria para a conversa com o time.
