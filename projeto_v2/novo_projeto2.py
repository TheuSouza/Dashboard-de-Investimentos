import sys
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QMessageBox, QHeaderView, QAbstractItemView,
    QTabWidget
)
from PySide6.QtCore import Qt, Slot
import os

import matplotlib
matplotlib.use("QtAgg")

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

CSV_FILE = "carteira.csv"

class AbasGraficos(QWidget):
    def __init__(self, acoes, fundos, cripto, acoes_usa):
        super().__init__()
        self.setWindowTitle("Distribuição da Carteira - Abas")
        self.setGeometry(150, 150, 800, 800)
        layout = QVBoxLayout(self)

        abas = QTabWidget()
        abas.addTab(self.criar_grafico(acoes, "Ações BR (3 e 4)"), "Ações BR")
        abas.addTab(self.criar_grafico(fundos, "Fundos (11)"), "Fundos")
        abas.addTab(self.criar_grafico(cripto, "Criptomoedas"), "Criptomoedas")
        abas.addTab(self.criar_grafico(acoes_usa, "Ações EUA"), "Ações EUA")

        layout.addWidget(abas)
        self.setLayout(layout)

    def criar_grafico(self, df, titulo):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        canvas = FigureCanvas(Figure(figsize=(5, 5)))
        ax = canvas.figure.subplots()

        if df.empty:
            ax.text(0.5, 0.5, "Sem dados", ha='center', va='center')
        else:
            distribuicao = df.groupby("Código")["Total Investido"].sum()
            labels = distribuicao.index
            valores = distribuicao.values
            ax.pie(valores, labels=labels, autopct='%1.1f%%', startangle=90)
            ax.set_title(titulo)
            ax.axis('equal')

        layout.addWidget(canvas)
        return widget

class PortfolioApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dashboard de Investimentos")
        self.setGeometry(100, 100, 1200, 800)
        self.init_ui()
        self.carregar_dados_csv()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # Entrada (cima)
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

        # Layout horizontal para tabela e gráficos lado a lado 50/50
        content_layout = QHBoxLayout()

        # Tabela (50%)
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(8)
        self.tabela.setHorizontalHeaderLabels([
            "Código", "Qtd", "Preço Médio", "Total Investido",
            "Preço Atual", "Variação (%)", "Status", "Remover"
        ])
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.setEditTriggers(QAbstractItemView.NoEditTriggers)

        content_layout.addWidget(self.tabela, 1)  # stretch=1

        # Área do gráfico (50%)
        self.grafico_container = QWidget()
        self.grafico_layout = QVBoxLayout(self.grafico_container)

        # Botão para atualizar gráfico
        self.grafico_button = QPushButton("Ver Gráfico da Carteira")
        self.grafico_button.clicked.connect(self.atualizar_grafico)

        self.grafico_layout.addWidget(self.grafico_button)

        content_layout.addWidget(self.grafico_container, 1)  # stretch=1

        main_layout.addLayout(content_layout)

        self.setLayout(main_layout)

    def atualizar_grafico(self):
        # Limpa gráficos anteriores
        for i in reversed(range(self.grafico_layout.count())):
            widget = self.grafico_layout.itemAt(i).widget()
            if widget and widget != self.grafico_button:
                widget.deleteLater()

        dados = []
        for row in range(self.tabela.rowCount()):
            linha = []
            for col in range(7):  # Ignora botão Remover
                item = self.tabela.item(row, col)
                linha.append(item.text())
            dados.append(linha)

        if not dados:
            QMessageBox.information(self, "Aviso", "Nenhum dado disponível para o gráfico.")
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
            ~df["Código"].isin(["BTC", "ETH"])
        ]

        # Criar abas com gráficos dentro do painel gráfico
        self.abas = QTabWidget()
        self.abas.addTab(self.criar_grafico(acoes, "Ações BR (3 e 4)"), "Ações BR")
        self.abas.addTab(self.criar_grafico(fundos, "Fundos (11)"), "Fundos")
        self.abas.addTab(self.criar_grafico(cripto, "Criptomoedas"), "Criptomoedas")
        self.abas.addTab(self.criar_grafico(acoes_usa, "Ações EUA"), "Ações EUA")

        self.grafico_layout.addWidget(self.abas)

    def criar_grafico(self, df, titulo):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        canvas = FigureCanvas(Figure(figsize=(5, 5)))
        ax = canvas.figure.subplots()

        if df.empty:
            ax.text(0.5, 0.5, "Sem dados", ha='center', va='center')
        else:
            distribuicao = df.groupby("Código")["Total Investido"].sum()
            labels = distribuicao.index
            valores = distribuicao.values
            ax.pie(valores, labels=labels, autopct='%1.1f%%', startangle=90)
            ax.set_title(titulo)
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
            qtd = float(self.qtd_input.text().strip())
            preco_medio = float(self.preco_medio_input.text().strip())
        except ValueError:
            QMessageBox.warning(self, "Erro", "Valores inválidos.")
            return

        if qtd <= 0 or preco_medio <= 0:
            QMessageBox.warning(self, "Erro", "Quantidade e preço devem ser > 0.")
            return

        codigo_formatado = self.formatar_codigo(codigo_original)
        total_investido = qtd * preco_medio

        try:
            ticker = yf.Ticker(codigo_formatado)
            preco_atual = ticker.history(period="1d")["Close"].iloc[-1]
            if pd.isna(preco_atual):
                raise Exception("Preço inválido")
        except Exception:
            QMessageBox.warning(self, "Erro", f"Erro ao buscar {codigo_formatado}")
            return

        variacao = ((preco_atual - preco_medio) / preco_medio) * 100
        status = "Valorizou" if variacao > 0 else "Desvalorizou"

        dados = [
            codigo_original, qtd, round(preco_medio, 2),
            round(total_investido, 2), round(preco_atual, 2),
            round(variacao, 2), status
        ]

        self.adicionar_na_tabela(dados)
        self.salvar_em_csv()
        self.codigo_input.clear()
        self.qtd_input.clear()
        self.preco_medio_input.clear()

    def adicionar_na_tabela(self, dados):
        row = self.tabela.rowCount()
        self.tabela.insertRow(row)

        for col, valor in enumerate(dados):
            item = QTableWidgetItem(str(valor))
            item.setTextAlignment(Qt.AlignCenter)

            if col == 6:  # Status
                if valor == "Valorizou":
                    item.setForeground(Qt.GlobalColor.darkGreen)
                else:
                    item.setForeground(Qt.GlobalColor.red)

            self.tabela.setItem(row, col, item)

        # Botão de remover
        btn = QPushButton("X")
        btn.setStyleSheet("color: red; font-weight: bold;")
        btn.clicked.connect(lambda _, r=row: self.remover_linha(r))
        self.tabela.setCellWidget(row, 7, btn)

    @Slot()
    def remover_linha(self, row):
        self.tabela.removeRow(row)
        self.salvar_em_csv()

    def salvar_em_csv(self):
        dados = []
        for row in range(self.tabela.rowCount()):
            linha = []
            for col in range(7):  # Ignora botão "Remover"
                item = self.tabela.item(row, col)
                linha.append(item.text())
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
