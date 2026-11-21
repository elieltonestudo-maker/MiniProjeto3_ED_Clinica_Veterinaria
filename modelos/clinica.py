import random
from datetime import datetime, date, timedelta
from estruturas.fila import Fila
from estruturas.cores import Cores
from modelos.atendimento import Atendimento
from modelos.diagnostico import criar_arvore_animal, analisar_queixa, CONDICOES
from modelos.triagem import NIVEIS, etiqueta

DIAS_RETORNO = 15           # retorno gratuito após o atendimento
INTERVALO_VACINA_DIAS = 365  # reforço anual

# Salas: 0 e 1 = cirurgia/emergência (preferenciais); 2, 3 e 4 = consulta
SALAS_INICIAIS = {
    0: "Cirurgia",
    1: "Cirurgia",
    2: "Consulta",
    3: "Consulta",
    4: "Consulta",
}

# Em que tipo de sala cada nível de triagem pode ser atendido (em ordem de preferência)
PREFERENCIA_SALA = {
    "Emergência": ["Cirurgia", "Consulta"],
    "Urgente": ["Consulta", "Cirurgia"],
    "Rotina": ["Consulta"],
}

VETERINARIOS = [
    {"nome": "Dra. Helena (Clínica Geral)", "salas": ["Consulta"], "especie": None},
    {"nome": "Dr. Marcos (Cirurgia)", "salas": ["Cirurgia"], "especie": None},
    {"nome": "Dra. Beatriz (Felinos)", "salas": ["Consulta"], "especie": "Gato"},
    {"nome": "Dr. Rafael (Emergência)", "salas": ["Cirurgia", "Consulta"], "especie": None},
]

# Algumas vacinas são específicas de uma espécie
ESPECIE_PRODUTO = {"V001": "Cão", "V004": "Cão", "V003": "Gato"}


class Clinica:
    def __init__(self, banco, estoque, cadastro):
        self.banco = banco
        self.estoque = estoque
        self.cadastro = cadastro

        # Uma fila FIFO por nível de triagem: Emergência > Urgente > Rotina
        self.filas = {nivel: Fila() for nivel in NIVEIS}

        self.salas = {
            num: {"status": "Livre", "atendimento": None, "tipo": tipo}
            for num, tipo in SALAS_INICIAIS.items()
        }
        self.arvore_diagnostico = criar_arvore_animal()
        self.atendimentos = {}  # atendimentos abertos
        self.proximo_numero = banco.proximo_numero_atendimento()

    # ------------------------------------------------------------------ fila
    def animal_ocupado(self, animal):
        """True se o animal já está em alguma fila ou em atendimento."""
        for fila in self.filas.values():
            for paciente in fila.percorrer():
                if paciente["animal"] is animal:
                    return True
        return any(at.animal is animal for at in self.atendimentos.values())

    def registrar_chegada(self, tutor, animal, queixa, prioridade):
        if self.animal_ocupado(animal):
            print(f"{Cores.VERMELHO}{animal.nome} já está na fila ou em atendimento.{Cores.RESET}")
            return None
        paciente = {
            "tutor": tutor, "animal": animal, "queixa": queixa, "prioridade": prioridade,
            "chegada": datetime.now().strftime("%H:%M"),
        }
        self.filas[prioridade].enfileirar(paciente)
        print(f"{animal.nome} ({animal.especie}) - Tutor: {tutor.nome} entrou na fila {etiqueta(prioridade)}.")
        return paciente

    # ----------------------------------------------------------------- salas
    def escolher_sala(self, prioridade):
        for tipo in PREFERENCIA_SALA[prioridade]:
            for num, sala in self.salas.items():
                if sala["tipo"] == tipo and sala["status"] == "Livre":
                    return num
        return None

    def _escolher_veterinario(self, tipo_sala, especie):
        candidatos = [v for v in VETERINARIOS
                      if tipo_sala in v["salas"] and v["especie"] in (None, especie)]
        return random.choice(candidatos)["nome"]

    def chamar_proximo(self):
        """Chama o paciente de maior prioridade para uma sala livre. Devolve o Atendimento (ou None)."""
        for nivel in NIVEIS:
            fila = self.filas[nivel]
            if fila.esta_vazia():
                continue
            sala_num = self.escolher_sala(nivel)
            if sala_num is None:
                continue

            paciente = fila.desenfileirar()
            sala = self.salas[sala_num]
            animal, tutor = paciente["animal"], paciente["tutor"]
            veterinario = self._escolher_veterinario(sala["tipo"], animal.especie)

            numero = self.proximo_numero
            self.proximo_numero += 1
            atendimento = Atendimento(numero, tutor, animal, veterinario, nivel, sala_num, paciente["queixa"])
            self.atendimentos[numero] = atendimento
            sala["status"] = "Ocupada"
            sala["atendimento"] = numero

            print(f"\n{Cores.AZUL}--- SALA {sala_num} ({sala['tipo']}) CHAMANDO ---{Cores.RESET}")
            print(f"Paciente {Cores.NEGRITO}{animal.nome}{Cores.RESET} ({animal.especie}, {animal.raca}) "
                  f"- Tutor: {tutor.nome} -> Sala {sala_num}.")
            print(f"Atendimento {numero} aberto {etiqueta(nivel)}. Queixa: {paciente['queixa']}")
            print(f"Veterinário responsável: {Cores.CIANO}{veterinario}{Cores.RESET}")
            if sala["tipo"] == "Cirurgia" and nivel != "Emergência":
                print(f"{Cores.AMARELO}Nota: a sala {sala_num} é de cirurgia/emergência, mas foi usada porque "
                      f"não havia emergência na fila nem sala de consulta livre.{Cores.RESET}")
            return atendimento

        if any(not f.esta_vazia() for f in self.filas.values()):
            print(f"{Cores.AMARELO}Nenhuma sala disponível no momento para o próximo da fila.{Cores.RESET}")
        else:
            print("Não há pacientes aguardando.")
        return None

    def liberar_sala(self, num_sala):
        sala = self.salas.get(num_sala)
        if not sala or sala["status"] != "Ocupada":
            print(f"Sala {num_sala} já está livre ou não existe.")
            return
        at = self.atendimentos.get(sala["atendimento"])
        if at:
            at.sala = None
            print(f"Sala {num_sala} liberada. Atendimento {at.numero} aguardando pagamento.")
        sala["status"] = "Livre"
        sala["atendimento"] = None

    # ------------------------------------------------------- diagnóstico
    def suspeitas_do_atendimento(self, at):
        return analisar_queixa(at.queixa, at.animal.especie)

    def sugerir_tratamentos(self, at):
        codigos = {}
        for cod in self.suspeitas_do_atendimento(at):
            for tratamento in CONDICOES[cod]["tratamentos"]:
                codigos[tratamento] = True
        return list(codigos)

    # --------------------------------------------------- lançamentos
    def prescrever(self, at, codigo, quantidade):
        especie_exigida = ESPECIE_PRODUTO.get(codigo)
        if especie_exigida and especie_exigida != at.animal.especie:
            return False, f"Este produto é exclusivo para {especie_exigida}; o paciente é {at.animal.especie}."
        ok, mensagem, reserva = self.estoque.reservar(codigo, quantidade, at.numero)
        if not ok:
            return False, mensagem
        item = {
            "codigo": codigo, "nome": reserva["produto"], "categoria": reserva["categoria"],
            "qtd": quantidade, "valor": reserva["valor"], "desconto": reserva["desconto"],
            "reserva": reserva,
        }
        at.adicionar_item(item)
        return True, mensagem

    def desfazer(self, at):
        """Desfaz a última ação do atendimento. Material volta para a prateleira (lotes de origem)."""
        acao = at.desfazer_ultima_acao()
        if acao is None:
            return None
        if acao["tipo"] == "add_item":
            self.estoque.cancelar_reserva(acao["dados"]["reserva"])
        return acao

    # ------------------------------------------------------ orçamento
    def imprimir_resumo(self, at, titulo):
        print(f"\n{Cores.NEGRITO}=== {titulo} - ATENDIMENTO {at.numero} ==={Cores.RESET}")
        print(f"Tutor: {at.tutor.nome} | Animal: {at.animal.descricao()} | Veterinário: {at.veterinario}")

        print(f"\n{Cores.NEGRITO}Medicamentos, vacinas e materiais:{Cores.RESET}")
        if not at.itens:
            print("  (nenhum)")
        for i in at.itens:
            if i["desconto"]:
                print(f"  - {i['qtd']}x {i['nome']} -> {Cores.MAGENTA}[DESCONTO 20% - LOTE PRÓXIMO DO "
                      f"VENCIMENTO] R$ {i['valor']:.2f}{Cores.RESET}")
            else:
                print(f"  - {i['qtd']}x {i['nome']}: R$ {i['valor']:.2f}")

        print(f"\n{Cores.NEGRITO}Consultas e procedimentos:{Cores.RESET}")
        if not at.servicos:
            print("  (nenhum)")
        for s in at.servicos:
            print(f"  - {s['descricao']}: R$ {s['valor']:.2f}")

        print(f"\n{Cores.NEGRITO}Total: R$ {at.total():.2f}{Cores.RESET}")

    def gerar_orcamento(self, at):
        if at.status not in ("Em Atendimento", "Aguardando Aprovação"):
            return False, f"Não é possível gerar orçamento. Status atual: {at.status}."
        if not at.itens and not at.servicos:
            return False, "Nada foi lançado neste atendimento ainda."
        self.imprimir_resumo(at, "ORÇAMENTO")
        at.status = "Aguardando Aprovação"
        return True, "Aguardando aprovação do tutor."

    def responder_orcamento(self, at, aprovado):
        if at.status != "Aguardando Aprovação":
            return False, f"Status atual: {at.status}"
        if aprovado:
            at.status = "Aguardando Pagamento"
            return True, "Orçamento APROVADO!"
        at.status = "Em Atendimento"  # tutor recusou: o veterinário pode ajustar o que foi lançado
        return True, "Orçamento recusado. O atendimento voltou para 'Em Atendimento' para ajustes."

    # -------------------------------------------------------- pagamento
    def fechar_e_pagar(self, at, forma, parcelas):
        if at.status != "Aguardando Pagamento":
            return False
        total = at.total()

        print("\n--- BAIXA DE ESTOQUE ---")
        for reserva in self.estoque.confirmar_baixa(at.numero):
            print(f"Baixa definitiva de {reserva['quantidade']}x {reserva['produto']}.")
        print("Estoque atualizado com sucesso.")

        dados = {
            "numero": at.numero, "tutor_cpf": at.tutor.cpf, "tutor": at.tutor.nome,
            "animal_id": at.animal.id, "animal": at.animal.nome, "especie": at.animal.especie,
            "veterinario": at.veterinario, "prioridade": at.prioridade, "queixa": at.queixa,
            "servicos": "; ".join(s["descricao"] for s in at.servicos),
            "forma_pagamento": forma, "parcelas": parcelas, "valor_total": total,
            "data_hora": datetime.now().strftime("%Y-%m-%d %H:%M"), "retorno_dias": DIAS_RETORNO,
        }
        itens_db = [{"nome": i["nome"], "qtd": i["qtd"], "valor": i["valor"] / i["qtd"]} for i in at.itens]
        self.banco.registrar_pagamento(dados, itens_db)

        # Vacinas aplicadas entram na carteira de vacinação do animal
        hoje = date.today()
        proxima = (hoje + timedelta(days=INTERVALO_VACINA_DIAS)).strftime("%Y-%m-%d")
        for item in at.itens:
            if item["categoria"] == "Vacina":
                self.cadastro.registrar_vacina(at.animal, item["nome"], hoje.strftime("%Y-%m-%d"), proxima)
                print(f"{Cores.VERDE}Carteira de vacinação de {at.animal.nome} atualizada: {item['nome']} "
                      f"(próxima dose em {proxima}).{Cores.RESET}")

        # Se a sala ainda estiver ocupada por este atendimento, libera
        if at.sala is not None and self.salas[at.sala]["atendimento"] == at.numero:
            self.salas[at.sala]["status"] = "Livre"
            self.salas[at.sala]["atendimento"] = None
            at.sala = None

        at.status = "Fechada"
        del self.atendimentos[at.numero]
        print(f"\n{Cores.VERDE}Atendimento {at.numero} pago via {forma} ({parcelas}x). Total: R$ {total:.2f}. "
              f"Retorno gratuito em até {DIAS_RETORNO} dias. Obrigado!{Cores.RESET}")
        return True
