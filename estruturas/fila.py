from estruturas.lista import Lista


class Fila:
    """Fila FIFO implementada sobre a lista encadeada (enfileirar e desenfileirar em O(1))."""

    def __init__(self):
        self.itens = Lista()

    def enfileirar(self, valor):
        self.itens.inserir(valor)

    def desenfileirar(self):
        return self.itens.remover_inicio()

    def primeiro(self):
        return None if self.itens.esta_vazia() else self.itens.inicio.valor

    def percorrer(self):
        return self.itens.percorrer()

    def esta_vazia(self):
        return self.itens.esta_vazia()

    def tamanho(self):
        return self.itens.tamanho
