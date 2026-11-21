from estruturas.cores import Cores


class NoArvore:
    """Nó de uma árvore N-ária (0, 1 ou N filhos).

    categoria: "Sistema", "Subsistema" ou "Condição".
    especie:   None (vale para cão e gato), "Cão" ou "Gato".
    tratamentos: códigos de medicamentos/vacinas/materiais sugeridos (só em Condição).
    """

    def __init__(self, nome, codigo=None, categoria="Sistema", especie=None, tratamentos=None):
        self.nome = nome
        self.codigo = codigo
        self.categoria = categoria
        self.especie = especie
        self.tratamentos = tratamentos or []
        self.filhos = []

    def adicionar_filho(self, filho):
        self.filhos.append(filho)


class ArvoreDiagnostico:
    def __init__(self, raiz):
        self.raiz = raiz

    @staticmethod
    def _visivel(no, especie):
        return not (especie and no.especie and no.especie != especie)

    def contem_suspeita(self, no, suspeitas, especie=None):
        """True se o nó (ou algum descendente) é uma condição suspeita visível para a espécie."""
        if not self._visivel(no, especie):
            return False
        if no.categoria == "Condição":
            return no.codigo in suspeitas
        return any(self.contem_suspeita(f, suspeitas, especie) for f in no.filhos)

    def percorrer_pre_ordem(self, no=None, nivel=0, suspeitas=None, especie=None,
                            nomes_produtos=None, somente_suspeitos=False):
        """Percurso pré-ordem (nó, depois filhos) exibindo a árvore indentada."""
        if no is None:
            no = self.raiz
        suspeitas = suspeitas or []
        nomes_produtos = nomes_produtos or {}

        if not self._visivel(no, especie):
            return
        if somente_suspeitos and not self.contem_suspeita(no, suspeitas, especie):
            return

        espacos = "    " * nivel
        if no.categoria == "Condição":
            tag_especie = f" ({no.especie})" if no.especie else ""
            if no.codigo in suspeitas:
                print(f"{espacos}- {Cores.NEGRITO}{no.nome}{Cores.RESET} [Cód: {no.codigo}]{tag_especie}"
                      f"{Cores.AMARELO} -> [SUSPEITA PELA QUEIXA]{Cores.RESET}")
                nomes = [nomes_produtos.get(c, c) for c in no.tratamentos]
                if nomes:
                    print(f"{espacos}    Tratamento sugerido: {', '.join(nomes)}")
            else:
                print(f"{espacos}- {no.nome} [Cód: {no.codigo}]{tag_especie}")
        else:
            print(f"{espacos}- {no.nome}")

        for filho in no.filhos:
            self.percorrer_pre_ordem(filho, nivel + 1, suspeitas, especie, nomes_produtos, somente_suspeitos)

    def buscar_por_codigo(self, codigo, no=None):
        """Busca em profundidade de uma condição pelo código."""
        if no is None:
            no = self.raiz
        if no.codigo == codigo:
            return no
        for filho in no.filhos:
            achado = self.buscar_por_codigo(codigo, filho)
            if achado:
                return achado
        return None

    def caminho_ate(self, codigo, no=None):
        """Lista de nomes da raiz até a condição (ex.: ['Animal', 'Sistema Digestório', ...])."""
        if no is None:
            no = self.raiz
        if no.codigo == codigo:
            return [no.nome]
        for filho in no.filhos:
            sub = self.caminho_ate(codigo, filho)
            if sub:
                return [no.nome] + sub
        return None
