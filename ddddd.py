
# PRIMEIRO CODIGO




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

        self.atualizar_visibilidade_botoes_filtro()



# SEGUNDO CODIGO


def adicionar_ativo(self):
        codigo_original = self.codigo_input.text().strip().upper()
        try:
            qtd_nova = float(self.qtd_input.text().strip().replace(',', '.'))
            preco_entrada = float(self.preco_medio_input.text().strip().replace(',', '.'))
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
            total_atual = preco_entrada
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
            total_atual = qtd_nova * preco_atual
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
                    total_atual = qtd_total * preco_atual
                    variacao = ((preco_atual - preco_medio_total) / preco_medio_total) * 100
                    status_final = "Valorizou" if variacao > 0 else "Desvalorizou"

                self.tabela.setItem(row, 1, QTableWidgetItem(str(round(qtd_total, 2))))
                self.tabela.setItem(row, 2, QTableWidgetItem(str(round(preco_medio_total, 2))))
                self.tabela.setItem(row, 3, QTableWidgetItem(str(round(total_investido_total, 2))))
                self.tabela.setItem(row, 4, QTableWidgetItem(str(round(preco_atual, 2))))
                self.tabela.setItem(row, 5, QTableWidgetItem(str(round(total_atual, 2))))
                self.tabela.setItem(row, 6, QTableWidgetItem(str(round(variacao, 2))))

                status_item = QTableWidgetItem(status_final)
                status_item.setTextAlignment(Qt.AlignCenter)
                if status_final == "Valorizou":
                    status_item.setForeground(Qt.GlobalColor.darkGreen)
                elif status_final == "Desvalorizou":
                    status_item.setForeground(Qt.GlobalColor.red)
                else:
                    status_item.setForeground(Qt.black)
                self.tabela.setItem(row, 7, status_item)

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
            round(total_atual, 2),
            round(variacao, 2),
            status,
        ]

        self.adicionar_na_tabela(dados)
        self.salvar_em_csv()
        self.atualizar_graficos()
        self.codigo_input.clear()
        self.qtd_input.clear()
        self.preco_medio_input.clear()





def adicionar_ativo(self):
    codigo = self.codigo_input.text().upper().strip()

    try:
        qtd_nova = float(self.qtd_input.text())
        preco_entrada = float(self.preco_input.text())
    except ValueError:
        QMessageBox.warning(self, "Erro", "Valores inválidos.")
        return

    if qtd_nova <= 0 or preco_entrada <= 0:
        QMessageBox.warning(self, "Erro", "Quantidade e preço devem ser maiores que zero.")
        return

    is_fixo = codigo in ["TESOURO", "CDB", "CDI"]

    # ===============================
    # TRATAMENTO DE ATIVOS FIXOS
    # ===============================
    if is_fixo:
        preco_atual = preco_entrada
        total_novo = preco_entrada
        variacao = 0.0
        status = "Fixo"
    else:
        preco_atual = preco_entrada
        total_novo = qtd_nova * preco_atual
        variacao = 0.0
        status = "Fixo"

    # ===============================
    # VERIFICA SE JÁ EXISTE NO DF
    # ===============================
    if codigo in self.df_completo["Código"].values:
        idx = self.df_completo[self.df_completo["Código"] == codigo].index[0]

        qtd_existente = float(self.df_completo.at[idx, "Qtd"])
        preco_medio_existente = float(self.df_completo.at[idx, "Preço Médio"])
        total_investido_existente = float(self.df_completo.at[idx, "Total Investido"])

        qtd_total = qtd_existente + qtd_nova

        if is_fixo:
            total_investido_total = total_investido_existente + total_novo
            preco_medio_total = total_investido_total
            total_atual = total_investido_total
            variacao = 0.0
            status = "Fixo"
        else:
            total_investido_total = (
                qtd_existente * preco_medio_existente
                + qtd_nova * preco_entrada
            )

            preco_medio_total = total_investido_total / qtd_total
            total_atual = qtd_total * preco_atual
            variacao = ((preco_atual - preco_medio_total) / preco_medio_total) * 100
            status = "Valorizou" if variacao > 0 else "Desvalorizou"

        # Atualiza linha existente
        self.df_completo.loc[idx, [
            "Qtd",
            "Preço Médio",
            "Total Investido",
            "Preço Atual",
            "Total",
            "Variação (%)",
            "Status"
        ]] = [
            qtd_total,
            round(preco_medio_total, 2),
            round(total_investido_total, 2),
            round(preco_atual, 2),
            round(total_atual, 2),
            round(variacao, 2),
            status
        ]

    else:
        # ===============================
        # NOVO ATIVO
        # ===============================
        novo = {
            "Código": codigo,
            "Qtd": qtd_nova,
            "Preço Médio": round(preco_entrada, 2),
            "Total Investido": round(total_novo, 2),
            "Preço Atual": round(preco_atual, 2),
            "Total": round(total_novo, 2),
            "Variação (%)": round(variacao, 2),
            "Status": status
        }

        self.df_completo = pd.concat(
            [self.df_completo, pd.DataFrame([novo])],
            ignore_index=True
        )

    # ===============================
    # FINALIZAÇÃO
    # ===============================
    self.salvar_em_csv()
    self.aplicar_filtro(self.filtro_atual)
    self.atualizar_graficos()
    self.atualizar_visibilidade_botoes_filtro()

    self.codigo_input.clear()
    self.qtd_input.clear()
    self.preco_input.clear()
