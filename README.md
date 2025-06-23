# Dashboard de Investimentos

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![PySide6](https://img.shields.io/badge/PySide6-6.5-green)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

## Descrição

Aplicação desktop em Python para monitorar e visualizar sua carteira de investimentos.  
Permite adicionar ativos (ações, FIIs, criptomoedas, renda fixa) com quantidade e preço médio, atualiza preços em tempo real usando a API do Yahoo Finance (`yfinance`) e exibe gráficos comparativos interativos com PySide6 e Matplotlib.

---

## Funcionalidades

- Adicionar ativos com código, quantidade e preço médio.
- Buscar preços atuais de ações brasileiras (`.SA`), ações americanas, criptomoedas (BTC, ETH) e renda fixa.
- Cálculo automático de variação percentual e status do ativo (valorizou/desvalorizou).
- Tabela interativa com informações resumidas e botão para remover ativos.
- Gráficos de pizza detalhados para categorias: Ações BR, FIIs, Ações EUA, Criptomoedas e Renda Fixa.
- Gráfico geral da carteira mostrando participação percentual por categoria.
- Armazenamento local dos dados em arquivo CSV (`projeto_v3/carteira.csv`) para persistência entre sessões.

---

## Pré-requisitos

- Python 3.8 ou superior
- Bibliotecas Python:
  - PySide6
  - pandas
  - matplotlib
  - yfinance

---

## Instalação

1. Clone este repositório ou baixe o código.

2. Crie um ambiente virtual (opcional, mas recomendado):

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
