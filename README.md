# QA Selenium Lab

Laboratório pessoal de estudo de automação de testes: interface web com **Selenium 4 + pytest**, rodando no **GitHub Actions** a cada mudança.

**Status:** em construção. Etapas 1 e 2 de 3 concluídas: esqueleto e CI; Page Objects, plano de teste e relatórios de bug. Falta a etapa de API.

## O que existe hoje

- `pages/`: um Page Object por tela do Sauce Demo (login, catálogo, carrinho e os três passos do checkout), mais o cabeçalho como componente. As esperas comuns ficam em `pages/base_page.py`.
- `tests/ui/`: login (tabela de decisão), logout, ordenação, compra completa, validação do checkout (partição de equivalência) e os usuários que simulam bloqueio, defeitos e lentidão.
- `tests/conftest.py`: Chrome novo por teste (headless por padrão); em falha, ou em bug conhecido, salva o screenshot e o HTML da página em `screenshots/`.
- [`TEST_PLAN.md`](TEST_PLAN.md): o que a suíte cobre e por quê, o que fica manual e como separo defeito de teste instável.
- [`BUGS.md`](BUGS.md): quatro defeitos encontrados, cada um com um teste `xfail(strict=True)` que o reproduz.
- [`docs/DECISIONS.md`](docs/DECISIONS.md): as escolhas que mudam o comportamento da suíte, com a alternativa descartada.
- `.github/workflows/ci.yml`: lint, formatação e testes a cada mudança; o relatório e a evidência ficam como artefato da execução.

## Como rodar

Pré-requisitos: [uv](https://docs.astral.sh/uv/) e Google Chrome. O Selenium Manager baixa o chromedriver sozinho.

```bash
uv sync --locked
uv run pytest                # suíte completa, headless
uv run pytest -m smoke       # só login e compra
HEADLESS=0 uv run pytest     # com a janela do navegador visível
uv run ruff check && uv run ruff format --check
```

O relatório sai em `reports/report.html`.

## Localizadores

1. `data-test`, o atributo que o site expõe para teste, em seletor CSS: `[data-test="username"]`.
2. `id` quando o elemento certo não tem `data-test`. No menu, o `data-test` está no ícone, mas quem recebe o clique é o botão, então o alvo é `id="react-burger-menu-btn"`.
3. XPath só quando o CSS não alcança, que é ao casar texto: o botão "Add to cart" é encontrado pelo nome do produto do card. Nunca XPath por posição (`/div[3]/...`).

## Como a IA foi usada

O código foi escrito com o **Claude Code como par de programação**: o Claude Code escreveu os Page Objects, os testes e os relatórios de bug. A minha parte foi definir o recorte, aprovar o plano de cada etapa e revisar o resultado.

- **Etapa 1:** antes da primeira linha, o plano passou por uma revisão com subagentes do Claude Code. Cada um olhou por um ângulo (boas práticas do Selenium, desenho de teste, CI, autenticidade), e uma etapa adversarial tentou derrubar cada sugestão. Ficaram de fora, entre outras, Selenium Grid, execução em paralelo, Allure e nova tentativa automática de teste falho: nenhuma resolve um problema que esta suíte tem hoje.
- **Etapa 2:** os seletores e as mensagens vieram do site ao vivo, não da memória do modelo. Um script exploratório escrito pelo Claude Code com `time.sleep` apontou defeitos que não existiam; refeito com espera explícita, o resultado mudou (caso descrito no `TEST_PLAN.md`). Também foi rejeitada uma versão do teste de ordenação que escolhia o método por nome em texto (`getattr`): funcionava, mas era difícil de ler. Nenhum bug entrou no `BUGS.md` sem ser reproduzido duas vezes.

## Stack

Python 3.12 · pytest · Selenium 4 · uv · ruff · GitHub Actions
