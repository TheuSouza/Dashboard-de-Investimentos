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

3. Instale as dependências:
   
   ````bash
   pip install PySide6 pandas matplotlib yfinance

## Como usar

1. Execute o arquivo principal do projeto:
   
   ````bash
   python nome_do_arquivo.py

3. Na interface que abrir:

- No campo **Código do ativo**, digite o código do ativo que deseja adicionar. Exemplos:
  - Ações brasileiras: PETR4, VALE3
  - Ações americanas: AAPL, MSFT (Valores em Dólares)
  - Criptomoedas: BTC, ETH (Valores em Reais)
  - Renda fixa: TESOURO, CDB, CDI

- No campo **Quantidade**, informe a quantidade de ativos que possui.

- No campo **Preço médio**, informe o preço médio que você pagou pelo ativo (por unidade).

- Clique no botão **Adicionar** para incluir o ativo na carteira.

- O sistema irá buscar automaticamente o preço atual do ativo usando o Yahoo Finance, calcular a variação percentual, atualizar a tabela e os gráficos.

- Para remover um ativo, clique no botão vermelho **X** na última coluna da linha correspondente.

- Os dados ficam salvos localmente no arquivo CSV `projeto_v3/carteira.csv`, assim você pode fechar e abrir o programa sem perder seus dados.

---

## Estrutura dos dados

O arquivo CSV `projeto_v3/carteira.csv` contém as seguintes colunas:

| Código | Quantidade | Preço Médio | Total Investido | Preço Atual | Variação (%) | Status |
|--------|------------|-------------|-----------------|-------------|--------------|--------|

---

## Detalhes Técnicos

- Usa o `yfinance` para buscar cotações financeiras em tempo real.

- Interface construída com PySide6, framework Qt para Python.

- Gráficos gerados com Matplotlib incorporados via `FigureCanvasQTAgg`.

- Atualização dinâmica de gráficos agrupando ativos por categoria.

- Paleta de cores customizada para melhor visualização.

- Tratamento especial para ativos de renda fixa e criptomoedas (conversão para reais).

- Possibilidade de múltiplos tipos de ativos no mesmo dashboard.

---

## Observações Importantes

- Para ações brasileiras, é fundamental usar o sufixo `.SA` para o código funcionar corretamente.

- Criptomoedas (`BTC`, `ETH`) têm seus preços convertidos para reais usando a cotação do dólar atual.

- Ativos de renda fixa (`TESOURO`, `CDB`, `CDI`) não sofrem variação e o preço médio representa o total investido.

- É necessário conexão com internet para atualização dos preços.

- Caso não tenha conexão ou o código não seja encontrado, será exibido um aviso.

---

## Licença

Este projeto está licenciado sob a licença MIT.

---

## Contato

Dúvidas, sugestões e contribuições são bem-vindas!  
Abra uma issue no GitHub ou envie uma mensagem.

