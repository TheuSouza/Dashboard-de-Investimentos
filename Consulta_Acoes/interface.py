import sys
from datetime import date
from PyQt5.QtWidgets import (
    QApplication, QWidget, QTabWidget, QVBoxLayout,
    QTableWidget, QTableWidgetItem, QLabel, QHeaderView
)
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtCore import Qt
from Outros.projeto_b3 import coleta_acao, coleta_fii, coleta_fiagros


class TabelaAtivos(QWidget):
    def __init__(self, titulo, colunas, dados):
        super().__init__()
        layout = QVBoxLayout()
        self.label = QLabel(titulo)
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(len(colunas))
        self.tabela.setHorizontalHeaderLabels(colunas)
        self.tabela.setRowCount(len(dados))

        self.tabela.resizeColumnsToContents()
        self.tabela.resizeRowsToContents()
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        for i, linha in enumerate(dados):
            for j, valor in enumerate(linha):
                item = QTableWidgetItem(str(valor))
                item.setTextAlignment(Qt.AlignCenter)

                try:
                    if float(valor.replace('%', '').replace(',', '.') if '%,' in str(valor) else valor) < 0:
                        item.setForeground(QBrush(QColor("red")))
                except ValueError:
                    pass

                self.tabela.setItem(i, j, item)

                

        self.tabela.resizeColumnsToContents()
        layout.addWidget(self.tabela)
        self.setLayout(layout)


class InterfaceFinanceira(QTabWidget):
    def __init__(self, dados_acoes, dados_fiis, dados_fiagros):
        super().__init__()

        colunas_acoes = ['Código', 'Nome', 'Valor Atual', 'Dividend Yield', 'Valorização Mês', 'Valorização 12M', 'P/L', 'P/VP', 'Dívida/EBITDA']
        colunas_fii = ['Código', 'Nome', 'Valor Atual', 'Dividend Yield', 'Valorização Mês', 'Valorização 12M']
        colunas_fiagros = colunas_fii

        self.addTab(TabelaAtivos("Ações", colunas_acoes, dados_acoes), "Ações")
        self.addTab(TabelaAtivos("FIIs", colunas_fii, dados_fiis), "FIIs")
        self.addTab(TabelaAtivos("FIAGROs", colunas_fiagros, dados_fiagros), "FIAGROs")



if __name__ == '__main__':
    papeis_acoes = ['brap3', 'bbdc3', 'cmig4', 'jhsf3', 'grnd3', 'itsa4', 'isae4', 'ligt3', 'sapr4', 'bbas3', 'cmin3']
    papeis_fii = ['gare11', 'brcr11', 'trbl11', 'xpin11']
    papeis_fiagro = ['vgia11', 'rura11', 'oiag11', 'xpca11']

    hoje = date.today().isoformat()
    atualizar = False

    try:
        dados_acoes = []
        with open("minhas_acoes.csv", "r", encoding="utf-8") as arquivo:
            linhas = arquivo.readlines()[1:]
            for linha in linhas:
                if linha.strip():
                    dados_acoes.append(linha.strip().split(","))

        dados_fii = []
        with open("meus_fiis.csv", "r", encoding="utf-8") as arquivo:
            linhas = arquivo.readlines()[1:]
            for linha in linhas:
                if linha.strip():
                    dados_fii.append(linha.strip().split(","))

        dados_fiagros = []
        with open("meus_fiagros.csv", "r", encoding="utf-8") as arquivo:
            linhas = arquivo.readlines()[1:]
            for linha in linhas:
                if linha.strip():
                    dados_fiagros.append(linha.strip().split(","))
        
        total_ativos = len(papeis_acoes) + len(papeis_fii) + len(papeis_fiagro)
        total_dados_ativos = len(dados_acoes) + len(dados_fii) + len(dados_fiagros)

        data_consulta = dados_acoes[0][-1]
        if data_consulta != hoje or total_ativos != total_dados_ativos:
            atualizar = True

    except FileNotFoundError:
        print("Arquivo não encontrado. Coletando dados...")
        atualizar = True

    if atualizar:
        dados_acoes = coleta_acao(papeis_acoes)
        dados_fii = coleta_fii(papeis_fii)
        dados_fiagros = coleta_fiagros(papeis_fiagro)

    app = QApplication(sys.argv)
    janela = InterfaceFinanceira(dados_acoes, dados_fii, dados_fiagros)
    janela.setWindowTitle("Painel de Ativos - Ações, FIIs e FIAGROs")
    janela.resize(1000, 600)
    janela.show()
    sys.exit(app.exec_())