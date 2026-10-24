# QA Selenium Lab

Laboratório pessoal de estudo de automação de testes: interface web com **Selenium 4 + pytest**, rodando no **GitHub Actions** a cada mudança.

**Status:** em construção. Etapa 1 de 3 (esqueleto, CI e testes de login).

## O que existe hoje

- `tests/conftest.py`: fixture `driver` que abre um Chrome novo por teste (headless por padrão) e, quando o teste falha, salva o screenshot e o HTML da página em `screenshots/`.
- `tests/ui/test_login.py`: login do usuário padrão e do usuário bloqueado no [Sauce Demo](https://www.saucedemo.com/), um site feito para treinar automação. Os testes ainda chamam o Selenium direto; a próxima etapa leva esses passos para Page Objects.
- `.github/workflows/ci.yml`: lint, formatação e testes. O relatório HTML e os screenshots de falha ficam como artefato da execução.
- `docs/DECISIONS.md`: as escolhas que mudam o comportamento da suíte, com a alternativa descartada.

## Como rodar

Pré-requisitos: [uv](https://docs.astral.sh/uv/) e Google Chrome. O Selenium Manager baixa o chromedriver sozinho.

```bash
uv sync --locked
uv run pytest                # headless
HEADLESS=0 uv run pytest     # com a janela do navegador visível
uv run ruff check && uv run ruff format --check
```

O relatório sai em `reports/report.html`.

## Como a IA foi usada

O código foi escrito com o **Claude Code como par de programação**. Antes da primeira linha, o plano passou por uma revisão com subagentes do Claude Code, cada um olhando por um ângulo (boas práticas do Selenium, desenho de teste, CI, autenticidade), e por uma etapa adversarial que tentou derrubar cada sugestão. Ficaram de fora, entre outras, as propostas de Selenium Grid, execução em paralelo, Allure e nova tentativa automática de teste falho: nenhuma resolve um problema que esta suíte tem hoje. As decisões que ficaram estão em `docs/DECISIONS.md`. Esta seção cresce a cada etapa.

## Stack

Python 3.12 · pytest · Selenium 4 · uv · ruff · GitHub Actions
