import datetime
from estruturas.fila import Fila


class Lote:
    def __init__(self, id_lote, preco_compra, data_compra, validade=None, quantidade=0):
        self.id = id_lote
        self.preco_compra = preco_compra
        self.data_compra = data_compra
        self.validade = validade
        self.quantidade = quantidade

    def dias_para_vencer(self):
        if not self.validade:
            return 9999  # Não vence
        hoje = datetime.date.today()
        validade_data = datetime.datetime.strptime(self.validade, "%Y-%m-%d").date()
        return (validade_data - hoje).days

    def esta_vencido(self):
        return self.dias_para_vencer() < 0

    def perto_de_vencer(self):
        # Verdadeiro se faltarem 60 dias ou menos para vencer
        return 0 <= self.dias_para_vencer() <= 60


class Produto:
    """Medicamento, vacina ou material. Os lotes ficam numa FILA (FIFO): o mais antigo sai primeiro."""

    def __init__(self, nome, codigo, categoria, preco_venda, estoque_minimo, id_db=None):
        self.id_db = id_db
        self.nome = nome
        self.codigo = codigo
        self.categoria = categoria  # "Vacina", "Medicamento" ou "Material"
        self.preco_venda = preco_venda
        self.estoque_minimo = estoque_minimo
        self.fila_lotes = Fila()

    def adicionar_lote(self, lote):
        # Compras novas são sempre mais recentes: entram no fim da fila
        self.fila_lotes.enfileirar(lote)

    def lotes(self):
        return self.fila_lotes.percorrer()

    def quantidade_total(self):
        return sum(lote.quantidade for lote in self.lotes())

    def quantidade_disponivel(self):
        return sum(lote.quantidade for lote in self.lotes() if not lote.esta_vencido())

    def verificar_estoque_minimo(self):
        return self.quantidade_disponivel() < self.estoque_minimo

    def descartar_vencidos(self):
        """Zera os lotes vencidos e devolve [(lote, quantidade_descartada)]."""
        descartes = []
        for lote in self.lotes():
            if lote.esta_vencido() and lote.quantidade > 0:
                descartes.append((lote, lote.quantidade))
                lote.quantidade = 0
        return descartes

    def baixar_fifo(self, qtd):
        """Retira qtd unidades a partir do lote mais antigo. Devolve [(lote, quantidade_retirada)]."""
        consumo = []
        restante = qtd
        for lote in self.lotes():
            if restante == 0:
                break
            if lote.quantidade == 0 or lote.esta_vencido():
                continue
            retirar = min(lote.quantidade, restante)
            lote.quantidade -= retirar
            restante -= retirar
            consumo.append((lote, retirar))
        return consumo

    def devolver(self, consumo):
        """Desfaz uma baixa: devolve as quantidades aos mesmos lotes de onde saíram."""
        for lote, qtd in consumo:
            lote.quantidade += qtd

    def preco_do_lote(self, lote):
        # Lote perto de vencer: 20% de desconto para evitar perda
        return self.preco_venda * 0.8 if lote.perto_de_vencer() else self.preco_venda
