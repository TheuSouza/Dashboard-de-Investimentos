import sys
import os
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView, QAbstractItemView, QProgressDialog
)
from PySide6.QtCore import Qt, Slot

import matplotlib
matplotlib.use("QtAgg")

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


# ======================================================
# CONFIGURAÇÕES
# ======================================================
CSV_FILE = "projeto_v5/carteira_1.csv"

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


# ======================================================
# APLICAÇÃO
# ======================================================
class PortfolioApp(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dashboard de Investimentos")

        self.df_completo = pd.DataFrame()
        self.filtro_atual = "Todos"

        self.init_ui()
        self.carregar_dados_csv()
        self.renderizar_tabela(self.df_completo)
        self.atualizar_graficos()

        self.showMaximized()

    # --------------------------------------------------
    # UI
    # --------------------------------------------------
    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # ================= INPUTS =================
        input_layout = QHBoxLayout()

        estilo_input = """
        QLineEdit {
            border: 2px solid #1C1C1C;
            border-radius: 6px;
            padding: 6px 10px;
            font-size: 14px;
            background-color: #F5F5F5;
        }
        """

        self.codigo_input = QLineEdit()
        self.codigo_input.setPlaceholderText("Código do ativo")
        self.codigo_input.setStyleSheet(estilo_input)

        self.qtd_input = QLineEdit()
        self.qtd_input.setPlaceholderText("Quantidade")
        self.qtd_input.setStyleSheet(estilo_input)

        self.preco_input = QLineEdit()
        self.preco_input.setPlaceholderText("Preço médio")
        self.preco_input.setStyleSheet(estilo_input)

        estilo_botao = """
        QPushButton {
            background-color: #1C1C1C;
            color: white;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: bold;
        }
        QPushButton:hover { background-color: #4682B4; }
        """

        btn_add = QPushButton("Adicionar")
        btn_add.setStyleSheet(estilo_botao)
        btn_add.clicked.connect(self.adicionar_ativo)

        btn_update = QPushButton("Atualizar")
        btn_update.setStyleSheet(estilo_botao)
        btn_update.clicked.connect(self.atualizar_valores_ativos)

        for w in [self.codigo_input, self.qtd_input, self.preco_input, btn_add, btn_update]:
            input_layout.addWidget(w)

        main_layout.addLayout(input_layout)

        # ================= FILTROS =================
        filtro_layout = QHBoxLayout()
        self.botoes_filtro = {}

        estilo_filtro = """
        QPushButton {
            background-color: #2c2c2c;
            color: white;
            border-radius: 6px;
            padding: 6px 14px;
            font-weight: bold;
        }
        QPushButton:checked {
            background-color: #4682B4;
        }
        """

        filtros = ["Todos", "Ações BR", "FIIs", "Ações EUA", "Cripto", "Renda Fixa"]

        for nome in filtros:
            btn = QPushButton(nome)
            btn.setCheckable(True)
            btn.setStyleSheet(estilo_filtro)
            btn.clicked.connect(lambda _, n=nome: self.aplicar_filtro(n))
            filtro_layout.addWidget(btn)
            self.botoes_filtro[nome] = btn

        self.botoes_filtro["Todos"].setChecked(True)
        main_layout.addLayout(filtro_layout)

        # ================= TABELA + GRÁFICO GERAL =================
        content_layout = QHBoxLayout()

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(9)
        self.tabela.setHorizontalHeaderLabels([
            "Código", "Qtd", "Preço Médio", "Total Investido",
            "Preço Atual", "Total", "Variação (%)", "Status", "Remover"
        ])
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.setEditTriggers(QAbstractItemView.NoEditTriggers)

        content_layout.addWidget(self.tabela, 7)

        self.grafico_geral_container = QWidget()
        self.grafico_geral_layout = QVBoxLayout(self.grafico_geral_container)
        content_layout.addWidget(self.grafico_geral_container, 3)

        main_layout.addLayout(content_layout)

        # ================= GRÁFICOS MENORES =================
        self.grafico_container = QWidget()
        self.grafico_layout = QVBoxLayout(self.grafico_container)
        main_layout.addWidget(self.grafico_container)

        self.grafico_comparativo_container = QWidget()
        self.grafico_comparativo_layout = QVBoxLayout(self.grafico_comparativo_container)

    # --------------------------------------------------
    # FILTRO
    # --------------------------------------------------
    def aplicar_filtro(self, nome):
        self.filtro_atual = nome

        for btn in self.botoes_filtro.values():
            btn.setChecked(False)
        self.botoes_filtro[nome].setChecked(True)

        df = self.df_completo.copy()

        if nome == "Ações BR":
            df = df[df["Código"].str.endswith(("3", "4"))]
        elif nome == "FIIs":
            df = df[df["Código"].str.endswith("11")]
        elif nome == "Ações EUA":
            df = df[
                ~df["Código"].str.endswith(("3", "4", "11")) &
                ~df["Código"].isin(["BTC", "ETH", "CDB", "TESOURO", "CDI"])
            ]
        elif nome == "Cripto":
            df = df[df["Código"].isin(["BTC", "ETH"])]
        elif nome == "Renda Fixa":
            df = df[df["Código"].isin(["CDB", "TESOURO", "CDI"])]

        self.renderizar_tabela(df)

    # --------------------------------------------------
    # TABELA
    # --------------------------------------------------
    def renderizar_tabela(self, df):
        self.tabela.setRowCount(0)
        for _, row in df.iterrows():
            self.adicionar_na_tabela(row.tolist())

    def adicionar_na_tabela(self, dados):
        row = self.tabela.rowCount()
        self.tabela.insertRow(row)

        for col, valor in enumerate(dados):
            item = QTableWidgetItem(str(valor))
            item.setTextAlignment(Qt.AlignCenter)
            if col == 7:
                if valor == "Valorizou":
                    item.setForeground(Qt.darkGreen)
                elif valor == "Desvalorizou":
                    item.setForeground(Qt.red)
            self.tabela.setItem(row, col, item)

        btn = QPushButton("X")
        btn.setStyleSheet("color: red; font-weight: bold;")
        btn.clicked.connect(lambda _, r=row: self.remover_linha(r))
        self.tabela.setCellWidget(row, 8, btn)



    def criar_label_total_e_variacao(self, titulo, total, variacao):
        formato_texto = 'font-weight: bold; font-size: 14px; margin-bottom: 10px'
        
        layout_info = QHBoxLayout()
        label_total = QLabel(f"{titulo} - Total: R$ {total:,.2f}")
        label_total.setAlignment(Qt.AlignCenter)
        label_total.setStyleSheet(formato_texto)

        if variacao > 0:
            cor, seta = "green", "↑"
        elif variacao == 0:
            cor, seta = "black", "↮"
        else:
            cor, seta = "red", "↓"

        label_variacao = QLabel(f" {seta} {variacao:,.2f}%")
        label_variacao.setAlignment(Qt.AlignCenter)
        label_variacao.setStyleSheet(f"color: {cor}; {formato_texto}")

        layout_info.addWidget(label_total)
        layout_info.addWidget(label_variacao)
        layout_info.setAlignment(Qt.AlignCenter)
        layout_info.setSpacing(10)

        return layout_info
    

    # --------------------------------------------------
    # GRÁFICOS
    # --------------------------------------------------
    def atualizar_graficos(self):
        for layout in [self.grafico_layout, self.grafico_geral_layout]:
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

        df = self.df_completo.copy()
        if df.empty:
            return

        # ---------- GRÁFICO GERAL ----------
        totais = {
            "Ações BR": df[df["Código"].str.endswith(("3", "4"))]["Total"].sum(),
            "FIIs": df[df["Código"].str.endswith("11")]["Total"].sum(),
            "Ações EUA": df[
                ~df["Código"].str.endswith(("3", "4", "11")) &
                ~df["Código"].isin(["BTC", "ETH", "CDB", "TESOURO", "CDI"])
            ]["Total"].sum(),
            "Cripto": df[df["Código"].isin(["BTC", "ETH"])]["Total"].sum(),
            "Renda Fixa": df[df["Código"].isin(["CDB", "TESOURO", "CDI"])]["Total"].sum(),
        }

        totais = {k: v for k, v in totais.items() if v > 0}

        total_geral = sum(totais.values())
        titulo = 'Total da Carteira: R$ '
        total_investido = df['Total Investido'].astype(float).sum()
        varicao = (total_geral / total_investido - 1) * 100

        self.grafico_geral_layout.addLayout(self.criar_label_total_e_variacao(titulo=titulo, total=total_geral, variacao=varicao))

        canvas = FigureCanvas(Figure(figsize=(6, 6)))
        ax = canvas.figure.subplots()
        ax.pie(totais.values(), 
               labels=totais.keys(), 
               autopct="%1.1f%%",
               startangle=90, 
               colors=PALETA_CORES,
               wedgeprops={'width': 0.5},
               textprops={'fontsize': 8},
               pctdistance=0.75)
        ax.axis("equal")

        self.grafico_geral_layout.addWidget(canvas)

        # ---------- GRÁFICOS MENORES ----------
        grid = QGridLayout()
        categorias = [
            ("Ações BR", df[df["Código"].str.endswith(("3", "4"))]),
            ("FIIs", df[df["Código"].str.endswith("11")]),
            ("Ações EUA", df[
                ~df["Código"].str.endswith(("3", "4", "11")) &
                ~df["Código"].isin(["BTC", "ETH", "CDB", "TESOURO", "CDI"])
            ]),
            ("Cripto", df[df["Código"].isin(["BTC", "ETH"])]),
            ("Renda Fixa", df[df["Código"].isin(["CDB", "TESOURO", "CDI"])])
        ]

        for i, (titulo, dfx) in enumerate(categorias):
            widget = self.criar_grafico(dfx, titulo)
            grid.addWidget(widget, 0, i)

        self.grafico_layout.addLayout(grid)

        # Atualiza gráfico geral
        self.atualizar_grafico_comparativo_geral(df)



    def atualizar_grafico_comparativo_geral(self, df):
        for i in reversed(range(self.grafico_comparativo_layout.count())):
            item = self.grafico_comparativo_layout.itemAt(i)
            widget = item.widget()
            layout = item.layout()
            if widget is not None:
                widget.setParent(None)
            elif layout is not None:
                while layout.count():
                    child = layout.takeAt(0)
                    if child.widget():
                        child.widget().setParent(None)
                self.grafico_comparativo_layout.removeItem(layout)


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
            nome: grupo["Total"].astype(float).sum()
            for nome, grupo in categorias.items() if not grupo.empty
        }
        totais_series = pd.Series(totais).sort_values(ascending=False)

        if not totais:
            aviso = QLabel("Sem valores para gráfico comparativo.")
            aviso.setAlignment(Qt.AlignCenter)
            self.grafico_comparativo_layout.addWidget(aviso)
            return

        total_geral = sum(totais.values())
        titulo = 'Total da Carteira: R$ '
        total_investido = df['Total Investido'].astype(float).sum()
        varicao = (total_geral / total_investido - 1) * 100

        self.grafico_comparativo_layout.addLayout(self.criar_label_total_e_variacao(titulo=titulo, total=total_geral, variacao=varicao))


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
        
        total = df["Total"].astype(float).sum() if not df.empty else 0.0
        total_investido = df['Total Investido'].astype(float).sum()

        if total_investido > 0:
            variacao = (total / total_investido - 1) * 100
        else:
            variacao = 0.0

        layout.addLayout(self.criar_label_total_e_variacao(titulo=titulo, total=total, variacao=variacao))

        canvas = FigureCanvas(Figure(figsize=(5, 5)))
        ax = canvas.figure.subplots()

        if df.empty:
            ax.text(0.5, 0.5, "Sem dados", ha='center', va='center')
        else:
            distribuicao = df.groupby("Código", sort=False)["Total"].sum()
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
                pctdistance=0.75,
            )

            centre_circle = plt.Circle((0, 0), 0.55, fc='white')
            ax.add_artist(centre_circle)
            ax.axis('equal')

        layout.addWidget(canvas)
        return widget



    # --------------------------------------------------
    # CSV / DADOS
    # --------------------------------------------------
    def carregar_dados_csv(self):
        if os.path.exists(CSV_FILE):
            self.df_completo = pd.read_csv(CSV_FILE)
        else:
            self.df_completo = pd.DataFrame(columns=[
                "Código", "Qtd", "Preço Médio", "Total Investido",
                "Preço Atual", "Total", "Variação (%)", "Status"
            ])

    def salvar_em_csv(self):
        self.df_completo.to_csv(CSV_FILE, index=False)

    # --------------------------------------------------
    # ATIVOS
    # --------------------------------------------------
    def adicionar_ativo(self):
        codigo = self.codigo_input.text().upper().strip()
        qtd = float(self.qtd_input.text())
        preco = float(self.preco_input.text())

        total = qtd * preco

        novo = {
            "Código": codigo,
            "Qtd": qtd,
            "Preço Médio": preco,
            "Total Investido": total,
            "Preço Atual": preco,
            "Total": total,
            "Variação (%)": 0.0,
            "Status": "Fixo"
        }

        self.df_completo = pd.concat(
            [self.df_completo, pd.DataFrame([novo])],
            ignore_index=True
        )

        self.salvar_em_csv()
        self.aplicar_filtro(self.filtro_atual)
        self.atualizar_graficos()

    # --------------------------------------------------
    # REMOVER
    # --------------------------------------------------
    @Slot()
    def remover_linha(self, row):
        self.df_completo.drop(self.df_completo.index[row], inplace=True)
        self.df_completo.reset_index(drop=True, inplace=True)

        self.salvar_em_csv()
        self.aplicar_filtro(self.filtro_atual)
        self.atualizar_graficos()
    

    def formatar_codigo(self, codigo):
        if codigo == "BTC":
            return "BTC-USD"
        elif codigo == "ETH":
            return "ETH-USD"
        elif codigo.endswith(("3", "4", "5", "6", "7", "8", "11")):
            return f"{codigo}.SA"
        return codigo
    

    def atualizar_valores_ativos(self):
        total_linhas = self.tabela.rowCount()
        if total_linhas == 0:
            QMessageBox.information(self, "Aviso", "Não há ativos para atualizar.")
            return

        # ⬇️ INÍCIO: Cria a barra de progresso
        progresso = QProgressDialog("Buscando cotações...", None, 0, total_linhas, self)
        progresso.setWindowTitle("Atualizando Carteira")
        progresso.setWindowModality(Qt.WindowModal)
        progresso.setMinimumDuration(0)
        progresso.resize(400, 100)

        progresso.setStyleSheet("""
            QProgressBar {
                border: 1px solid #fff;
                border-radius: 4px;
                text-align: center;
                height: 20px;
                font-weight: bold;
                color: #fff;
                background-color: #1C1C1C;
            }
            QProgressBar::chunk {
                background-color: #228B22;
                width: 20px;
            }
            QLabel {
                color: #1C1C1C;
                font-size: 14px;
            }
        """)
        # ⬆️ FIM


        for row in range(total_linhas):
            if progresso.wasCanceled():
                break

            codigo_original = self.tabela.item(row, 0).text()
            qtd = float(self.tabela.item(row, 1).text())
            preco_medio = float(self.tabela.item(row, 2).text())

            is_fixo = codigo_original in ["TESOURO", "CDB", "CDI"]
            if is_fixo:
                preco_atual = preco_medio
                total_atual = preco_atual
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

                if not codigo_formatado.endswith(".SA"):
                    preco_atual *= dolar_em_reais

                if codigo_original in ["BTC", "ETH"]:
                    preco_atual = preco_atual


                total_atual = qtd * preco_atual
                variacao = ((preco_atual - preco_medio) / preco_medio) * 100
                status = "Valorizou" if variacao > 0 else "Desvalorizou"

            self.tabela.setItem(row, 4, QTableWidgetItem(str(round(preco_atual, 2))))
            self.tabela.setItem(row, 5, QTableWidgetItem(str(round(total_atual, 2))))
            self.tabela.setItem(row, 6, QTableWidgetItem(str(round(variacao, 2))))

            status_item = QTableWidgetItem(status)
            status_item.setTextAlignment(Qt.AlignCenter)
            if status == "Valorizou":
                status_item.setForeground(Qt.GlobalColor.darkGreen)
            elif status == "Desvalorizou":
                status_item.setForeground(Qt.GlobalColor.red)
            self.tabela.setItem(row, 7, status_item)

            # ⬇️ Atualiza a barra de progresso
            progresso.setValue(row + 1)
            QApplication.processEvents()
            # ⬆️

        progresso.close()
        self.salvar_em_csv()
        self.atualizar_graficos()



# ======================================================
# EXECUÇÃO
# ======================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PortfolioApp()
    sys.exit(app.exec())
