# QA Selenium Lab

Laboratório de automação de testes: interface web com **Selenium 4 + pytest** no padrão **Page Object Model**, testes de **API REST** e execução contínua no **GitHub Actions**.

> 🚧 Em construção. Este README cresce junto com a suíte.

## Escopo planejado

| Camada | Alvo | O que cobre |
|---|---|---|
| Interface web | [Sauce Demo](https://www.saucedemo.com/) | login, catálogo, carrinho e checkout, com os usuários de teste que simulam bloqueio, bugs visuais e lentidão |
| API REST | a definir | autenticação, CRUD, casos negativos e validação de contrato |
| CI | GitHub Actions | navegador headless, relatório e screenshot de falha como artefato |

Também entram aqui o **plano de teste** (o que automatizar e o que fica manual), **relatórios de bug** no formato usado em time e um registro de **como a IA foi usada** na escrita e revisão dos testes.

## Stack

Python · pytest · Selenium 4 · uv · ruff · GitHub Actions
