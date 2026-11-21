from modelos.produto import Produto, Lote
from estruturas.cores import Cores
from datetime import datetime


class Estoque:
    def __init__(self, banco):
        self.banco = banco
        self.produtos = {}
        self.reservas = []  # Material reservado para atendimentos em andamento (já saiu da prateleira)

    def carregar_do_banco(self):
        self.produtos = {}
        for prod_id, codigo, nome, cat, preco, min_qtd in self.banco.listar_produtos():
            produto = Produto(nome, codigo, cat, preco, min_qtd, prod_id)
            for id_lote, qtd, preco_compra, data_compra, validade in self.banco.listar_lotes(prod_id):
                produto.adicionar_lote(Lote(id_lote, preco_compra, data_compra, validade, qtd))
            self.produtos[codigo] = produto

    # --- Cadastro e reposição (atualizam memória e banco sem recarregar tudo) ---
    def cadastrar_produto(self, codigo, nome, categoria, preco_venda, estoque_minimo):
        prod_id = self.banco.cadastrar_produto(codigo, nome, categoria, preco_venda, estoque_minimo)
        if prod_id is None:
            return False
        self.produtos[codigo] = Produto(nome, codigo, categoria, preco_venda, estoque_minimo, prod_id)
        return True

    def repor(self, codigo, quantidade, preco_compra, validade):
        produto = self.produtos.get(codigo)
        if not produto:
            return False
        hoje = datetime.now().strftime("%Y-%m-%d")
        id_lote = self.banco.adicionar_lote(produto.id_db, quantidade, preco_compra, hoje, validade)
        produto.adicionar_lote(Lote(id_lote, preco_compra, hoje, validade, quantidade))
        return True

    # --- Alertas automáticos ---
    def verificar_alertas(self):
        print(f"\n{Cores.CIANO}--- VERIFICAÇÃO AUTOMÁTICA DE ESTOQUE ---{Cores.RESET}")
        tem_alerta = False

        for produto in self.produtos.values():
            for lote, qtd in produto.descartar_vencidos():
                prejuizo = qtd * lote.preco_compra
                print(f"{Cores.VERMELHO}[PERDA] {qtd} un. de '{produto.nome}' venceram e foram descartadas "
                      f"(prejuízo R$ {prejuizo:.2f}).{Cores.RESET}")
                self.banco.registrar_perda(produto.nome, qtd, "Vencimento", prejuizo)
                self.banco.atualizar_quantidade_lote(lote.id, 0)
                tem_alerta = True

            if produto.verificar_estoque_minimo():
                print(f"{Cores.AMARELO}[ALERTA] Estoque de '{produto.nome}' abaixo do mínimo! "
                      f"(Atual: {produto.quantidade_disponivel()}, Mín: {produto.estoque_minimo}){Cores.RESET}")
                tem_alerta = True

            menor_dias = None
            for lote in produto.lotes():
                if lote.quantidade > 0 and lote.perto_de_vencer():
                    dias = lote.dias_para_vencer()
                    if menor_dias is None or dias < menor_dias:
                        menor_dias = dias
            if menor_dias is not None:
                print(f"{Cores.MAGENTA}[PROMOÇÃO] '{produto.nome}' possui lotes vencendo em até {menor_dias} dias. "
                      f"Sugerimos aplicar desconto!{Cores.RESET}")
                tem_alerta = True

        if not tem_alerta:
            print(f"{Cores.VERDE}Todos os produtos estão com estoque regular e dentro da validade.{Cores.RESET}")
        print(f"{Cores.CIANO}-----------------------------------------{Cores.RESET}\n")

    # --- Material reservado para o atendimento ---
    def reservar(self, codigo, quantidade, numero_atendimento):
        """Tira da prateleira (FIFO) e reserva para o atendimento. Devolve (ok, mensagem, reserva)."""
        produto = self.produtos.get(codigo)
        if not produto:
            return False, "Produto não encontrado.", None
        disponivel = produto.quantidade_disponivel()
        if disponivel < quantidade:
            return False, f"Estoque insuficiente (disponível: {disponivel}).", None

        consumo = produto.baixar_fifo(quantidade)
        valor = 0.0
        desconto = False
        for lote, qtd in consumo:
            self.banco.atualizar_quantidade_lote(lote.id, lote.quantidade)
            valor += produto.preco_do_lote(lote) * qtd
            desconto = desconto or lote.perto_de_vencer()

        reserva = {
            "produto": produto.nome, "codigo": codigo, "categoria": produto.categoria,
            "quantidade": quantidade, "atendimento": numero_atendimento,
            "consumo": consumo, "valor": valor, "desconto": desconto,
        }
        self.reservas.append(reserva)
        return True, f"{quantidade}x {produto.nome} reservado(s) para o atendimento {numero_atendimento}.", reserva

    def cancelar_reserva(self, reserva):
        """Devolve o material aos lotes de origem (usado no Desfazer)."""
        produto = self.produtos[reserva["codigo"]]
        produto.devolver(reserva["consumo"])
        for lote, _ in reserva["consumo"]:
            self.banco.atualizar_quantidade_lote(lote.id, lote.quantidade)
        self.reservas = [r for r in self.reservas if r is not reserva]

    def confirmar_baixa(self, numero_atendimento):
        """Baixa definitiva (pagamento): o material reservado deixa de existir. Devolve as reservas baixadas."""
        baixadas = [r for r in self.reservas if r["atendimento"] == numero_atendimento]
        self.reservas = [r for r in self.reservas if r["atendimento"] != numero_atendimento]
        return baixadas

    def devolver_todas(self):
        """Ao encerrar o sistema, devolve à prateleira o que não foi pago (evita sumiço de estoque)."""
        pendentes = list(self.reservas)
        for reserva in pendentes:
            self.cancelar_reserva(reserva)
        return len(pendentes)

    def ver_reservas(self):
        if not self.reservas:
            print(f"{Cores.VERDE}Nenhum material reservado no momento.{Cores.RESET}")
            return
        print(f"\n{Cores.CIANO}--- MATERIAL RESERVADO (EM USO NOS PACIENTES) ---{Cores.RESET}")
        for r in self.reservas:
            print(f"{Cores.NEGRITO}{r['quantidade']}x {r['codigo']} - {r['produto']}{Cores.RESET} "
                  f"(Atendimento {r['atendimento']})")
        print(f"{Cores.CIANO}--------------------------------------------------{Cores.RESET}")
