from datetime import date, datetime
from estruturas.lista import Lista


def limpar_cpf(cpf):
    return "".join(c for c in cpf if c.isdigit())


def formatar_cpf(cpf):
    d = limpar_cpf(cpf)
    if len(d) == 11:
        return f"{d[:3]}.{d[3:6]}.{d[6:9]}-{d[9:]}"
    return cpf


class Animal:
    def __init__(self, nome, especie, raca, sexo, nascimento, peso, castrado, id_db=None):
        self.id = id_db
        self.nome = nome
        self.especie = especie  # "Cão" ou "Gato"
        self.raca = raca
        self.sexo = sexo
        self.nascimento = nascimento  # AAAA-MM-DD
        self.peso = peso
        self.castrado = castrado
        self.carteira = Lista()  # carteira de vacinação: lista encadeada de doses aplicadas

    def idade(self):
        nasc = datetime.strptime(self.nascimento, "%Y-%m-%d").date()
        hoje = date.today()
        meses = (hoje.year - nasc.year) * 12 + hoje.month - nasc.month - (1 if hoje.day < nasc.day else 0)
        anos, resto = divmod(max(0, meses), 12)
        if anos == 0:
            return f"{resto} mes(es)"
        return f"{anos} ano(s)" + (f" e {resto} mes(es)" if resto else "")

    def descricao(self):
        return f"{self.nome} ({self.especie}, {self.raca})"

    def registrar_vacina(self, vacina, data_aplicacao, proxima_dose):
        self.carteira.inserir({"vacina": vacina, "data": data_aplicacao, "proxima": proxima_dose})

    def ultimas_vacinas(self):
        """Dose mais recente de cada vacina (a que vale para saber se está em dia)."""
        ultimas = {}
        for dose in self.carteira.percorrer():
            atual = ultimas.get(dose["vacina"])
            if atual is None or dose["data"] >= atual["data"]:
                ultimas[dose["vacina"]] = dose
        return list(ultimas.values())

    def vacinas_atrasadas(self):
        hoje = date.today().strftime("%Y-%m-%d")
        return [d for d in self.ultimas_vacinas() if d["proxima"] and d["proxima"] < hoje]


class Tutor:
    """Um tutor possui uma lista encadeada de animais (0, 1 ou quantos forem, sem limite)."""

    def __init__(self, cpf, nome, telefone, endereco):
        self.cpf = limpar_cpf(cpf)
        self.nome = nome
        self.telefone = telefone
        self.endereco = endereco
        self.animais = Lista()

    def buscar_animal(self, nome):
        return self.animais.buscar(lambda a: a.nome.lower() == nome.lower())


class CadastroTutores:
    """Lista encadeada de tutores; cada nó guarda outra lista encadeada de animais (relação 1:N)."""

    def __init__(self, banco):
        self.banco = banco
        self.tutores = Lista()

    def carregar_do_banco(self):
        self.tutores = Lista()
        for cpf, nome, tel, end in self.banco.listar_tutores():
            tutor = Tutor(cpf, nome, tel, end)
            for id_a, nome_a, esp, raca, sexo, nasc, peso, cast in self.banco.listar_animais(cpf):
                animal = Animal(nome_a, esp, raca, sexo, nasc, peso, bool(cast), id_a)
                for vacina, data, proxima in self.banco.listar_vacinas(id_a):
                    animal.registrar_vacina(vacina, data, proxima)
                tutor.animais.inserir(animal)
            self.tutores.inserir(tutor)

    # --- Tutores ---
    def buscar_por_cpf(self, cpf):
        cpf = limpar_cpf(cpf)
        return self.tutores.buscar(lambda t: t.cpf == cpf)

    def cadastrar_tutor(self, cpf, nome, telefone, endereco):
        cpf = limpar_cpf(cpf)
        if len(cpf) != 11:
            return False, "CPF inválido: informe 11 dígitos.", None
        if self.buscar_por_cpf(cpf):
            return False, "Já existe um tutor com esse CPF.", None
        self.banco.inserir_tutor(cpf, nome, telefone, endereco)
        tutor = Tutor(cpf, nome, telefone, endereco)
        self.tutores.inserir(tutor)
        return True, f"Tutor {nome} cadastrado!", tutor

    def remover_tutor(self, tutor):
        """Remoção em cascata: o tutor sai e leva todos os animais (e carteiras) junto."""
        self.banco.remover_tutor(tutor.cpf)
        self.tutores.remover(lambda t: t is tutor)

    # --- Animais ---
    def cadastrar_animal(self, tutor, nome, especie, raca, sexo, nascimento, peso, castrado):
        if tutor.buscar_animal(nome):
            return False, "Esse tutor já tem um animal com esse nome.", None
        id_animal = self.banco.inserir_animal(tutor.cpf, nome, especie, raca, sexo, nascimento, peso, castrado)
        animal = Animal(nome, especie, raca, sexo, nascimento, peso, castrado, id_animal)
        tutor.animais.inserir(animal)
        return True, f"{nome} ({especie}) cadastrado(a) para {tutor.nome}!", animal

    def remover_animal(self, tutor, animal):
        self.banco.remover_animal(animal.id)
        tutor.animais.remover(lambda a: a is animal)

    def registrar_vacina(self, animal, vacina, data_aplicacao, proxima_dose):
        self.banco.inserir_vacina(animal.id, vacina, data_aplicacao, proxima_dose)
        animal.registrar_vacina(vacina, data_aplicacao, proxima_dose)

    # --- Consultas ---
    def buscar_animais_por_nome(self, nome):
        achados = []
        for tutor in self.tutores.percorrer():
            for animal in tutor.animais.percorrer():
                if nome.lower() in animal.nome.lower():
                    achados.append((tutor, animal))
        return achados

    def vacinas_em_atraso(self):
        atrasos = []
        for tutor in self.tutores.percorrer():
            for animal in tutor.animais.percorrer():
                for dose in animal.vacinas_atrasadas():
                    atrasos.append((tutor, animal, dose))
        return atrasos
