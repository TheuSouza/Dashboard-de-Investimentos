import sys
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from PySide6.QtWidgets import QGridLayout
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QMessageBox, QHeaderView, QAbstractItemView,
)
from PySide6.QtCore import Qt, Slot
import os

import matplotlib
matplotlib.use("QtAgg")

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

CSV_FILE = "projeto_v3/carteira.csv"

PALETA_CORES = [
    "#e6194b",  # vermelho
    "#f58231",  # laranja
    "#ffe119",  # amarelo
    "#bfef45",  # verde limão
    "#3cb44b",  # verde
    "#42d4f4",  # ciano
    "#4363d8",  # azul
    "#911eb4",  # roxo
    "#f032e6",  # rosa
    "#fabebe",  # rosa claro
    "#ffd8b1",  # pêssego
    "#dcbeff",  # lavanda
    "#aaffc3",  # verde menta
    "#fffac8",  # amarelo pastel
]


class PortfolioApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dashboard de Investimentos")
        self.init_ui()
        self.carregar_dados_csv()
        self.atualizar_graficos()
        self.showMaximized()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        input_layout = QHBoxLayout()
        self.codigo_input = QLineEdit()
        self.codigo_input.setPlaceholderText("Código do ativo (ex: PETR4.SA)")
        input_layout.addWidget(self.codigo_input)

        self.qtd_input = QLineEdit()
        self.qtd_input.setPlaceholderText("Quantidade")
        input_layout.addWidget(self.qtd_input)

        self.preco_medio_input = QLineEdit()
        self.preco_medio_input.setPlaceholderText("Preço médio")
        input_layout.addWidget(self.preco_medio_input)

        self.add_button = QPushButton("Adicionar")
        self.add_button.clicked.connect(self.adicionar_ativo)
        input_layout.addWidget(self.add_button)

        main_layout.addLayout(input_layout)

        # Tabela à esquerda e gráfico comparativo à direita
        content_layout = QHBoxLayout()

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(8)
        self.tabela.setHorizontalHeaderLabels([
            "Código", "Qtd", "Preço Médio", "Total Investido",
            "Preço Atual", "Variação (%)", "Status", "Remover"
        ])
        
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.setEditTriggers(QAbstractItemView.NoEditTriggers)
        content_layout.addWidget(self.tabela, 7)

        self.grafico_comparativo_container = QWidget()
        self.grafico_comparativo_layout = QVBoxLayout(self.grafico_comparativo_container)
        content_layout.addWidget(self.grafico_comparativo_container, 3)

        main_layout.addLayout(content_layout)

        # Gráficos detalhados abaixo
        self.grafico_container = QWidget()
        self.grafico_layout = QVBoxLayout(self.grafico_container)
        main_layout.addWidget(self.grafico_container)

        self.setLayout(main_layout)


    def atualizar_graficos(self):
        # Limpa gráficos detalhados anteriores
        for i in reversed(range(self.grafico_layout.count())):
            item = self.grafico_layout.itemAt(i)
            if item.widget():
                item.widget().setParent(None)
            elif item.layout():
                layout = item.layout()
                while layout.count():
                    child = layout.takeAt(0)
                    if child.widget():
                        child.widget().setParent(None)
                self.grafico_layout.removeItem(layout)

        dados = []
        for row in range(self.tabela.rowCount()):
            linha = [self.tabela.item(row, col).text() for col in range(7)]
            dados.append(linha)

        if not dados:
            aviso = QLabel("Nenhum dado disponível para gráficos.")
            aviso.setAlignment(Qt.AlignCenter)
            self.grafico_layout.addWidget(aviso)
            return

        df = pd.DataFrame(dados, columns=[
            "Código", "Qtd", "Preço Médio", "Total Investido",
            "Preço Atual", "Variação (%)", "Status"
        ])
        df["Total Investido"] = df["Total Investido"].astype(float)

        acoes = df[df["Código"].str.endswith(("3", "4"))]
        fundos = df[df["Código"].str.endswith("11")]
        cripto = df[df["Código"].isin(["BTC", "ETH"])]
        acoes_usa = df[
            ~df["Código"].str.endswith(("3", "4", "11")) &
            ~df["Código"].isin(["BTC", "ETH"]) &
            ~df["Código"].isin(["CDB", "TESOURO", "CDI"])
        ]
        fixa = df[df["Código"].isin(["CDB", "TESOURO", "CDI"])]

        grid_layout = QGridLayout()
        grid_layout.addWidget(self.criar_grafico(acoes, "Ações BR"), 0, 0)
        grid_layout.addWidget(self.criar_grafico(fundos, "FIIs"), 0, 1)
        grid_layout.addWidget(self.criar_grafico(acoes_usa, "Ações EUA"), 0, 2)
        grid_layout.addWidget(self.criar_grafico(cripto, "Criptomoedas"), 0, 3)
        grid_layout.addWidget(self.criar_grafico(fixa, "Renda Fixa"), 0, 4)

        self.grafico_layout.addLayout(grid_layout)

        # Atualiza gráfico geral
        self.atualizar_grafico_comparativo_geral(df)


    def atualizar_grafico_comparativo_geral(self, df):
        for i in reversed(range(self.grafico_comparativo_layout.count())):
            widget = self.grafico_comparativo_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        if df.empty:
            aviso = QLabel("Sem dados para gráfico geral.")
            aviso.setAlignment(Qt.AlignCenter)
            self.grafico_comparativo_layout.addWidget(aviso)
            return

        categorias = {
            "Ações EUA": df[
                ~df["Código"].str.endswith(("3", "4", "11")) &
                ~df["Código"].isin(["BTC", "ETH", "CDB", "TESOURO", "CDI"])
            ],
            "Ações BR": df[df["Código"].str.endswith(("3", "4"))],
            "FII BR": df[df["Código"].str.endswith("11")],
            "Cripto": df[df["Código"].isin(["BTC", "ETH"])],
            "Renda Fixa": df[df["Código"].isin(["CDB", "TESOURO", "CDI"])],
        }

        totais = {
            nome: grupo["Total Investido"].sum()
            for nome, grupo in categorias.items() if not grupo.empty
        }
        totais_series = pd.Series(totais).sort_values(ascending=False)

        if not totais:
            aviso = QLabel("Sem valores para gráfico comparativo.")
            aviso.setAlignment(Qt.AlignCenter)
            self.grafico_comparativo_layout.addWidget(aviso)
            return

        # Label com total geral
        total_geral = sum(totais.values())
        label_total = QLabel(f"Total da Carteira: R$ {total_geral:,.2f}")
        label_total.setAlignment(Qt.AlignCenter)
        label_total.setStyleSheet("font-weight: bold; font-size: 16px; margin-bottom: 10px;")
        self.grafico_comparativo_layout.addWidget(label_total)

        # Gráfico de pizza
        canvas = FigureCanvas(Figure(figsize=(6, 6)))
        ax = canvas.figure.subplots()
        ax.pie(
            totais_series.values,
            labels=totais_series.index,
            autopct='%1.1f%%',
            startangle=90,
            colors=PALETA_CORES,
            wedgeprops={'width': 0.6},
            textprops={'fontsize': 8},
            pctdistance=0.75
        )

        centre_circle = plt.Circle((0, 0), 0.55, fc='white')
        ax.add_artist(centre_circle)
        ax.set_title("")
        ax.axis('equal')
        self.grafico_comparativo_layout.addWidget(canvas)



    def criar_grafico(self, df, titulo):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        total = df["Total Investido"].sum() if not df.empty else 0.0
        label = QLabel(f"{titulo} - Total: R$ {total:,.2f}")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(label)  # Adiciona o texto acima do gráfico

        canvas = FigureCanvas(Figure(figsize=(5, 5)))
        ax = canvas.figure.subplots()

        if df.empty:
            ax.text(0.5, 0.5, "Sem dados", ha='center', va='center')
        else:
            distribuicao = df.groupby("Código", sort=False)["Total Investido"].sum()
            distribuicao = distribuicao.sort_values(ascending=False)
            labels = distribuicao.index
            valores = distribuicao.values
            cores = [PALETA_CORES[i % len(PALETA_CORES)] for i in range(len(labels))]

            wedges, texts, autotexts = ax.pie(
                valores,
                labels=labels,
                autopct='%1.1f%%',
                startangle=90,
                colors=cores,
                wedgeprops={'width': 0.6},
                textprops={'fontsize': 8},
                pctdistance=0.75
            )

            centre_circle = plt.Circle((0, 0), 0.55, fc='white')
            ax.add_artist(centre_circle)
            ax.axis('equal')

        layout.addWidget(canvas)
        return widget


    def formatar_codigo(self, codigo):
        if codigo == "BTC":
            return "BTC-USD"
        elif codigo == "ETH":
            return "ETH-USD"
        elif codigo.endswith(("3", "4", "5", "6", "7", "8", "11")):
            return f"{codigo}.SA"
        return codigo


    def adicionar_ativo(self):
        codigo_original = self.codigo_input.text().strip().upper()
        try:
            qtd_nova = float(self.qtd_input.text().strip())
            preco_entrada = float(self.preco_medio_input.text().strip())
        except ValueError:
            QMessageBox.warning(self, "Erro", "Valores inválidos.")
            return

        if qtd_nova <= 0 or preco_entrada <= 0:
            QMessageBox.warning(self, "Erro", "Quantidade e preço devem ser > 0.")
            return

        is_fixo = codigo_original in ["TESOURO", "CDB", "CDI"]

        if is_fixo:
            # Preço médio = total investido
            preco_medio_novo = preco_entrada
            total_investido_novo = preco_entrada
            preco_atual = preco_medio_novo
            variacao = 0.0
            status = "Fixo"
        else:
            dolar_em_reais = 1.0
            if not codigo_original.endswith(".SA") or codigo_original in ["BTC", "ETH"]:
                try:
                    dolar_ticker = yf.Ticker("USDBRL=X")
                    dolar_em_reais = dolar_ticker.history(period="1d")["Close"].iloc[-1]
                except Exception:
                    QMessageBox.warning(self, "Erro", "Erro ao obter cotação do dólar.")
                    return

            codigo_formatado = self.formatar_codigo(codigo_original)
            try:
                ticker = yf.Ticker(codigo_formatado)
                preco_atual = ticker.history(period="1d")["Close"].iloc[-1]
                if pd.isna(preco_atual):
                    raise Exception("Preço inválido")
            except Exception:
                QMessageBox.warning(self, "Erro", f"Erro ao buscar {codigo_formatado}")
                return

            if not codigo_formatado.endswith(".SA") or codigo_original in ["BTC", "ETH"]:
                preco_entrada *= dolar_em_reais
                preco_atual *= dolar_em_reais

            preco_medio_novo = preco_entrada
            total_investido_novo = qtd_nova * preco_medio_novo
            variacao = ((preco_atual - preco_medio_novo) / preco_medio_novo) * 100
            status = "Valorizou" if variacao > 0 else "Desvalorizou"

        # Verifica se já existe na tabela
        for row in range(self.tabela.rowCount()):
            if self.tabela.item(row, 0).text() == codigo_original:
                qtd_existente = float(self.tabela.item(row, 1).text())
                preco_medio_existente = float(self.tabela.item(row, 2).text())

                if is_fixo:
                    # Soma direto os investimentos
                    qtd_total = qtd_existente + qtd_nova
                    total_investido_total = preco_medio_existente + preco_medio_novo
                    preco_medio_total = total_investido_total  # Para exibição apenas
                    preco_atual = preco_medio_total
                    variacao = 0.0
                    status_final = "Fixo"
                else:
                    qtd_total = qtd_existente + qtd_nova
                    preco_medio_total = (
                        (qtd_existente * preco_medio_existente + qtd_nova * preco_medio_novo)
                        / qtd_total
                    )
                    total_investido_total = qtd_total * preco_medio_total
                    variacao = ((preco_atual - preco_medio_total) / preco_medio_total) * 100
                    status_final = "Valorizou" if variacao > 0 else "Desvalorizou"

                self.tabela.setItem(row, 1, QTableWidgetItem(str(round(qtd_total, 2))))
                self.tabela.setItem(row, 2, QTableWidgetItem(str(round(preco_medio_total, 2))))
                self.tabela.setItem(row, 3, QTableWidgetItem(str(round(total_investido_total, 2))))
                self.tabela.setItem(row, 4, QTableWidgetItem(str(round(preco_atual, 2))))
                self.tabela.setItem(row, 5, QTableWidgetItem(str(round(variacao, 2))))

                status_item = QTableWidgetItem(status_final)
                status_item.setTextAlignment(Qt.AlignCenter)
                if status_final == "Valorizou":
                    status_item.setForeground(Qt.GlobalColor.darkGreen)
                elif status_final == "Desvalorizou":
                    status_item.setForeground(Qt.GlobalColor.red)
                self.tabela.setItem(row, 6, status_item)

                self.salvar_em_csv()
                self.atualizar_graficos()
                self.codigo_input.clear()
                self.qtd_input.clear()
                self.preco_medio_input.clear()
                return

        # Novo ativo
        dados = [
            codigo_original,
            qtd_nova,
            round(preco_medio_novo, 2),
            round(total_investido_novo, 2),
            round(preco_atual, 2),
            round(variacao, 2),
            status,
        ]

        self.adicionar_na_tabela(dados)
        self.salvar_em_csv()
        self.atualizar_graficos()
        self.codigo_input.clear()
        self.qtd_input.clear()
        self.preco_medio_input.clear()



    def adicionar_na_tabela(self, dados):
        row = self.tabela.rowCount()
        self.tabela.insertRow(row)

        for col, valor in enumerate(dados):
            item = QTableWidgetItem(str(valor))
            item.setTextAlignment(Qt.AlignCenter)

            if col == 6:
                item.setForeground(Qt.darkGreen if valor == "Valorizou" else Qt.red)

            self.tabela.setItem(row, col, item)

        btn = QPushButton("X")
        btn.setStyleSheet("color: red; font-weight: bold;")
        btn.clicked.connect(lambda _, r=row: self.remover_linha(r))
        self.tabela.setCellWidget(row, 7, btn)


    @Slot()
    def remover_linha(self, row):
        self.tabela.removeRow(row)
        self.salvar_em_csv()
        self.atualizar_graficos()


    def salvar_em_csv(self):
        dados = []
        for row in range(self.tabela.rowCount()):
            linha = [self.tabela.item(row, col).text() for col in range(7)]
            dados.append(linha)
        df = pd.DataFrame(dados, columns=[
            "Código", "Qtd", "Preço Médio", "Total Investido",
            "Preço Atual", "Variação (%)", "Status"
        ])
        df.to_csv(CSV_FILE, index=False)


    def carregar_dados_csv(self):
        if os.path.exists(CSV_FILE):
            df = pd.read_csv(CSV_FILE)
            for _, row in df.iterrows():
                self.adicionar_na_tabela(row.tolist())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PortfolioApp()
    window.show()
    sys.exit(app.exec())
