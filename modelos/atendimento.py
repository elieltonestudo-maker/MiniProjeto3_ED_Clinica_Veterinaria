from estruturas.pilha import Pilha


class Atendimento:
    """Ficha de atendimento de um animal (equivalente à Ordem de Serviço da oficina)."""

    def __init__(self, numero, tutor, animal, veterinario, prioridade, sala, queixa):
        self.numero = numero
        self.tutor = tutor
        self.animal = animal
        self.veterinario = veterinario
        self.prioridade = prioridade
        self.sala = sala
        self.queixa = queixa
        self.status = "Em Atendimento"
        self.itens = []      # medicamentos, vacinas e materiais
        self.servicos = []   # consultas e procedimentos
        self.historico_acoes = Pilha()  # Undo (LIFO)

    def adicionar_item(self, item):
        self.itens.append(item)
        self.historico_acoes.empilhar({"tipo": "add_item", "dados": item})

    def adicionar_servico(self, descricao, valor):
        servico = {"descricao": descricao, "valor": valor}
        self.servicos.append(servico)
        self.historico_acoes.empilhar({"tipo": "add_servico", "dados": servico})

    def desfazer_ultima_acao(self):
        """Desempilha a última ação, remove o lançamento e devolve a ação (ou None)."""
        acao = self.historico_acoes.desempilhar()
        if acao is None:
            return None
        if acao["tipo"] == "add_item":
            self.itens.pop()
        else:
            self.servicos.pop()
        return acao

    def total_itens(self):
        return sum(i["valor"] for i in self.itens)

    def total_servicos(self):
        return sum(s["valor"] for s in self.servicos)

    def total(self):
        return self.total_itens() + self.total_servicos()
