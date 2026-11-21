class No:
    def __init__(self, valor):
        self.valor = valor
        self.proximo = None


class Lista:
    """Lista encadeada simples com ponteiros de início e fim.

    Inserir no fim é O(1) graças ao ponteiro `fim`; buscar e remover são O(n).
    """

    def __init__(self):
        self.inicio = None
        self.fim = None
        self.tamanho = 0

    def inserir(self, valor):
        novo = No(valor)
        if self.inicio is None:
            self.inicio = novo
        else:
            self.fim.proximo = novo
        self.fim = novo
        self.tamanho += 1

    def percorrer(self):
        atual = self.inicio
        while atual:
            yield atual.valor
            atual = atual.proximo

    def buscar(self, criterio):
        """Retorna o primeiro valor para o qual criterio(valor) é verdadeiro."""
        for valor in self.percorrer():
            if criterio(valor):
                return valor
        return None

    def remover(self, criterio):
        """Remove o primeiro nó que satisfaz o critério e devolve o seu valor."""
        anterior = None
        atual = self.inicio
        while atual:
            if criterio(atual.valor):
                if anterior is None:
                    self.inicio = atual.proximo
                else:
                    anterior.proximo = atual.proximo
                if atual is self.fim:
                    self.fim = anterior
                self.tamanho -= 1
                return atual.valor
            anterior = atual
            atual = atual.proximo
        return None

    def remover_inicio(self):
        if self.inicio is None:
            return None
        valor = self.inicio.valor
        self.inicio = self.inicio.proximo
        if self.inicio is None:
            self.fim = None
        self.tamanho -= 1
        return valor

    def esta_vazia(self):
        return self.inicio is None

    def __len__(self):
        return self.tamanho

    def __iter__(self):
        return self.percorrer()
