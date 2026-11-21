from datetime import datetime, date

from banco.conexao import BancoDados
from estruturas.cores import Cores
from modelos.catalogo import popular_catalogo, popular_tutores_demo
from modelos.clinica import Clinica
from modelos.diagnostico import CONDICOES
from modelos.estoque import Estoque
from modelos.triagem import NIVEIS, classificar_prioridade, etiqueta
from modelos.tutor import CadastroTutores, formatar_cpf


# ============================================================ utilitários de entrada
def entrada(msg):
    return input(msg).strip()


def pedir_inteiro(msg):
    texto = entrada(msg)
    if texto == "":
        return None
    try:
        return int(texto)
    except ValueError:
        print(f"{Cores.VERMELHO}Erro: digite apenas números inteiros.{Cores.RESET}")
        return None


def pedir_decimal(msg):
    texto = entrada(msg)
    if texto == "":
        return None
    try:
        return float(texto.replace(",", "."))
    except ValueError:
        print(f"{Cores.VERMELHO}Erro: valor numérico inválido.{Cores.RESET}")
        return None


def pedir_data(msg):
    """Pede uma data AAAA-MM-DD. ENTER devolve None."""
    while True:
        texto = entrada(msg)
        if texto == "":
            return None
        try:
            datetime.strptime(texto, "%Y-%m-%d")
            return texto
        except ValueError:
            print(f"{Cores.VERMELHO}Data inválida. Use o formato AAAA-MM-DD.{Cores.RESET}")


def confirmar(msg):
    return input(f"{Cores.AMARELO}{msg} (S/N): {Cores.RESET}").strip().upper() == "S"


def erro(msg):
    print(f"{Cores.VERMELHO}{msg}{Cores.RESET}")


def ok(msg):
    print(f"{Cores.VERDE}{msg}{Cores.RESET}")


def selecionar_atendimento(clinica, msg="Número do atendimento (ou ENTER para cancelar): "):
    numero = pedir_inteiro(msg)
    if numero is None:
        return None
    atendimento = clinica.atendimentos.get(numero)
    if not atendimento:
        erro("Atendimento não encontrado.")
    return atendimento


def cabecalho(at):
    print(f"Atendimento: {at.numero} | Tutor: {Cores.NEGRITO}{at.tutor.nome}{Cores.RESET} | "
          f"Animal: {Cores.NEGRITO}{at.animal.descricao()}{Cores.RESET} | {etiqueta(at.prioridade)}")


# ======================================================= cadastros (tutores/animais)
def exibir_tutor(tutor):
    print(f"\n{Cores.NEGRITO}{formatar_cpf(tutor.cpf)} | {tutor.nome}{Cores.RESET} | "
          f"{tutor.telefone} | {tutor.endereco}")
    if tutor.animais.esta_vazia():
        print("   (sem animais cadastrados)")
    for a in tutor.animais.percorrer():
        castrado = "castrado(a)" if a.castrado else "não castrado(a)"
        print(f"   - {a.nome} | {a.especie} | {a.raca} | {a.sexo} | {a.idade()} | {a.peso:.1f} kg | {castrado}")


def fluxo_cadastrar_tutor(cadastro, cpf=None):
    if cpf is None:
        cpf = entrada("CPF do tutor (somente números, ENTER para cancelar): ")
    if not cpf:
        return None
    nome = entrada("Nome do tutor: ")
    if not nome:
        return None
    telefone = entrada("Telefone: ")
    endereco = entrada("Endereço: ")
    sucesso, mensagem, tutor = cadastro.cadastrar_tutor(cpf, nome, telefone, endereco)
    (ok if sucesso else erro)(mensagem)
    return tutor


def fluxo_cadastrar_animal(cadastro, tutor):
    print(f"\n{Cores.AZUL}--- CADASTRAR ANIMAL (Tutor: {tutor.nome}) ---{Cores.RESET}")
    nome = entrada("Nome do animal (ENTER para cancelar): ")
    if not nome:
        return None
    print("Espécie: 1. Cão   2. Gato")
    especie = {"1": "Cão", "2": "Gato"}.get(entrada("Escolha: "))
    if not especie:
        erro("Espécie inválida.")
        return None
    raca = entrada("Raça (ENTER = SRD): ") or "SRD"
    sexo = entrada("Sexo (M/F): ").upper()
    if sexo not in ("M", "F"):
        erro("Sexo inválido. Use M ou F.")
        return None
    nascimento = pedir_data("Data de nascimento (AAAA-MM-DD): ")
    if not nascimento:
        return None
    if nascimento > date.today().strftime("%Y-%m-%d"):
        erro("A data de nascimento não pode estar no futuro.")
        return None
    peso = pedir_decimal("Peso (kg): ")
    if peso is None or peso <= 0:
        erro("Peso inválido.")
        return None
    castrado = confirmar("O animal é castrado?")
    sucesso, mensagem, animal = cadastro.cadastrar_animal(tutor, nome, especie, raca, sexo, nascimento, peso, castrado)
    (ok if sucesso else erro)(mensagem)
    return animal


def selecionar_animal(cadastro, permitir_cadastro=True):
    """Pede o CPF do tutor e deixa escolher um dos animais. Devolve (tutor, animal)."""
    cpf = entrada("CPF do tutor (ENTER para cancelar): ")
    if not cpf:
        return None, None
    tutor = cadastro.buscar_por_cpf(cpf)
    if not tutor:
        erro("Tutor não encontrado.")
        if permitir_cadastro and confirmar("Deseja cadastrar este tutor agora?"):
            tutor = fluxo_cadastrar_tutor(cadastro, cpf)
        if not tutor:
            return None, None

    animais = list(tutor.animais.percorrer())
    if not animais:
        print(f"{tutor.nome} ainda não tem animais cadastrados.")
        if permitir_cadastro:
            return tutor, fluxo_cadastrar_animal(cadastro, tutor)
        return tutor, None

    print(f"\nAnimais de {Cores.NEGRITO}{tutor.nome}{Cores.RESET}:")
    for i, a in enumerate(animais, 1):
        print(f"  {i}. {a.nome} ({a.especie}, {a.raca})")
    if permitir_cadastro:
        print("  0. Cadastrar novo animal")
    numero = pedir_inteiro("Escolha o animal (ENTER para cancelar): ")
    if numero is None:
        return tutor, None
    if numero == 0 and permitir_cadastro:
        return tutor, fluxo_cadastrar_animal(cadastro, tutor)
    if 1 <= numero <= len(animais):
        return tutor, animais[numero - 1]
    erro("Opção inválida.")
    return tutor, None


def acao_cadastrar_tutor(cadastro):
    tutor = fluxo_cadastrar_tutor(cadastro)
    if tutor and confirmar("Deseja cadastrar um animal para este tutor agora?"):
        fluxo_cadastrar_animal(cadastro, tutor)


def acao_cadastrar_animal(cadastro):
    cpf = entrada("CPF do tutor (ENTER para cancelar): ")
    if not cpf:
        return
    tutor = cadastro.buscar_por_cpf(cpf)
    if not tutor:
        erro("Tutor não encontrado. Cadastre o tutor primeiro (opção 1).")
        return
    fluxo_cadastrar_animal(cadastro, tutor)


def acao_consultar(cadastro):
    print("\n--- CONSULTAR TUTORES E ANIMAIS ---")
    print("1. Listar todos\n2. Buscar tutor por CPF\n3. Buscar animal por nome")
    opcao = entrada("Escolha (ENTER para cancelar): ")
    if opcao == "1":
        if cadastro.tutores.esta_vazia():
            print("Nenhum tutor cadastrado.")
        for tutor in cadastro.tutores.percorrer():
            exibir_tutor(tutor)
    elif opcao == "2":
        tutor = cadastro.buscar_por_cpf(entrada("CPF: "))
        exibir_tutor(tutor) if tutor else erro("Tutor não encontrado.")
    elif opcao == "3":
        achados = cadastro.buscar_animais_por_nome(entrada("Nome (ou parte do nome): "))
        if not achados:
            erro("Nenhum animal encontrado.")
        for tutor, animal in achados:
            print(f"- {animal.nome} ({animal.especie}, {animal.raca}) | Tutor: {tutor.nome} "
                  f"({formatar_cpf(tutor.cpf)})")


def acao_remover(cadastro, clinica):
    print("\n--- REMOVER ---")
    print("1. Remover um animal\n2. Remover tutor (e todos os seus animais)")
    opcao = entrada("Escolha (ENTER para cancelar): ")
    if opcao == "1":
        tutor, animal = selecionar_animal(cadastro, permitir_cadastro=False)
        if not animal:
            return
        if clinica.animal_ocupado(animal):
            erro(f"{animal.nome} está na fila ou em atendimento e não pode ser removido agora.")
            return
        if confirmar(f"Remover {animal.nome} de {tutor.nome}? Carteira de vacinação também será apagada"):
            cadastro.remover_animal(tutor, animal)
            ok("Animal removido.")
    elif opcao == "2":
        tutor = cadastro.buscar_por_cpf(entrada("CPF do tutor: "))
        if not tutor:
            erro("Tutor não encontrado.")
            return
        if any(clinica.animal_ocupado(a) for a in tutor.animais.percorrer()):
            erro("Há animais deste tutor na fila ou em atendimento.")
            return
        qtd = tutor.animais.tamanho
        if confirmar(f"Remover {tutor.nome} e seus {qtd} animal(is)?"):
            cadastro.remover_tutor(tutor)
            ok("Tutor e animais removidos (cascata).")


# ================================================================ atendimento
def acao_registrar_chegada(cadastro, clinica):
    print(f"\n{Cores.AZUL}--- REGISTRAR CHEGADA / TRIAGEM ---{Cores.RESET}")
    tutor, animal = selecionar_animal(cadastro)
    if not animal:
        return
    if clinica.animal_ocupado(animal):
        erro(f"{animal.nome} já está na fila ou em atendimento.")
        return
    queixa = entrada("Queixa relatada pelo tutor: ")
    if not queixa:
        return

    nivel, termo = classificar_prioridade(queixa)
    motivo = f"palavra-chave '{termo}'" if termo else "nenhum sinal de gravidade"
    print(f"Triagem sugerida: {etiqueta(nivel)} ({motivo})")
    if not confirmar("Aceitar a triagem sugerida?"):
        print("1. Emergência   2. Urgente   3. Rotina")
        escolha = entrada("Nível (ENTER para manter a sugestão): ")
        nivel = {"1": NIVEIS[0], "2": NIVEIS[1], "3": NIVEIS[2]}.get(escolha, nivel)
    clinica.registrar_chegada(tutor, animal, queixa, nivel)


def acao_chamar_proximo(clinica, estoque):
    at = clinica.chamar_proximo()
    if not at:
        return
    suspeitas = clinica.suspeitas_do_atendimento(at)
    if suspeitas:
        nomes = [CONDICOES[c]["nome"] for c in suspeitas]
        print(f"{Cores.AMARELO}Alerta: condições suspeitas pela queixa: {', '.join(nomes)}{Cores.RESET}")


def acao_ver_arvore(clinica, estoque):
    at = selecionar_atendimento(clinica)
    if not at:
        return
    suspeitas = clinica.suspeitas_do_atendimento(at)
    print(f"\n--- ÁRVORE DE DIAGNÓSTICO ---")
    cabecalho(at)
    print(f"Queixa: {at.queixa}")
    somente_suspeitos = False
    if suspeitas:
        print(f"\n{Cores.AMARELO}Atenção: suspeitas pela queixa:{Cores.RESET}")
        for cod in suspeitas:
            caminho = " > ".join(clinica.arvore_diagnostico.caminho_ate(cod)[1:])
            print(f"  [{cod}] {CONDICOES[cod]['nome']} ({caminho})")
        somente_suspeitos = not confirmar("\nMostrar a árvore completa? (N = só os ramos suspeitos)")
    else:
        print("Nenhuma suspeita detectada pela queixa. Exibindo a árvore completa.")
    nomes_produtos = {c: p.nome for c, p in estoque.produtos.items()}
    print()
    clinica.arvore_diagnostico.percorrer_pre_ordem(
        suspeitas=suspeitas, especie=at.animal.especie,
        nomes_produtos=nomes_produtos, somente_suspeitos=somente_suspeitos)
    print("-----------------------------\n")


def acao_prescrever(clinica, estoque):
    at = selecionar_atendimento(clinica)
    if not at:
        return
    print(f"\n{Cores.AZUL}--- PRESCREVER MEDICAMENTO / VACINA / MATERIAL ---{Cores.RESET}")
    cabecalho(at)
    if at.status != "Em Atendimento":
        erro(f"Não é possível lançar itens. O atendimento está '{at.status}'.")
        return

    sugeridos = clinica.sugerir_tratamentos(at)
    print(f"\n{Cores.CIANO}--- CATÁLOGO ---{Cores.RESET}")
    for categoria in ["Vacina", "Medicamento", "Material"]:
        print(f"{Cores.NEGRITO}[{categoria}]{Cores.RESET}")
        for cod, prod in estoque.produtos.items():
            if prod.categoria == categoria:
                marca = f"  {Cores.AMARELO}* sugerido pela queixa{Cores.RESET}" if cod in sugeridos else ""
                print(f"  {cod} - {prod.nome} (Estoque: {prod.quantidade_disponivel()}){marca}")
    print(f"{Cores.CIANO}-------------------------------------------------------{Cores.RESET}")

    while True:
        codigo = entrada("Digite o CÓDIGO do item (ou ENTER para cancelar): ").upper()
        if not codigo:
            return
        if codigo not in estoque.produtos:
            erro("Produto não cadastrado no estoque. Tente novamente.")
            continue
        produto = estoque.produtos[codigo]
        ok(f"Produto selecionado: {produto.nome}")
        quantidade = pedir_inteiro("Quantidade (ou ENTER para cancelar): ")
        if quantidade is None:
            return
        if quantidade <= 0:
            erro("A quantidade deve ser maior que zero.")
            continue
        if not confirmar(f"Confirmar {quantidade}x {codigo} - {produto.nome} para o atendimento {at.numero}?"):
            print("Ação cancelada.")
            return
        sucesso, mensagem = clinica.prescrever(at, codigo, quantidade)
        if sucesso:
            ok(mensagem)
            estoque.ver_reservas()
        else:
            erro(f"Erro: {mensagem}")
        return


def acao_adicionar_servico(clinica):
    at = selecionar_atendimento(clinica)
    if not at:
        return
    print(f"\n{Cores.AZUL}--- ADICIONAR CONSULTA / PROCEDIMENTO ---{Cores.RESET}")
    cabecalho(at)
    if at.status != "Em Atendimento":
        erro(f"Não é possível adicionar serviços. O atendimento está '{at.status}'.")
        return

    servicos = clinica.banco.buscar_servicos()
    print(f"\n{Cores.CIANO}--- TABELA DE SERVIÇOS ---{Cores.RESET}")
    for s in servicos:
        print(f"{s[0]} - {s[1]}: R$ {s[2]:.2f}")

    while True:
        codigo = entrada("Digite o CÓDIGO do serviço (ou ENTER para cancelar): ").upper()
        if not codigo:
            return
        servico = next((s for s in servicos if s[0] == codigo), None)
        if not servico:
            erro("Código inválido! Tente novamente.")
            continue
        if confirmar(f"Confirmar '{servico[1]}' (R$ {servico[2]:.2f}) no atendimento {at.numero}?"):
            at.adicionar_servico(servico[1], servico[2])
            ok("Serviço adicionado com sucesso!")
        else:
            print("Ação cancelada.")
        return


def acao_gerar_orcamento(clinica):
    at = selecionar_atendimento(clinica, "Número do atendimento para gerar orçamento (ou ENTER para cancelar): ")
    if not at:
        return
    sucesso, mensagem = clinica.gerar_orcamento(at)
    print(f"{Cores.AMARELO if sucesso else Cores.VERMELHO}{mensagem}{Cores.RESET}")


def acao_aprovar_orcamento(clinica):
    at = selecionar_atendimento(clinica, "Número do atendimento para aprovar (ou ENTER para cancelar): ")
    if not at:
        return
    if at.status != "Aguardando Aprovação":
        erro(f"Status atual: {at.status}. Gere o orçamento primeiro.")
        return
    aprovado = confirmar(f"O tutor {at.tutor.nome} aprovou o orçamento de R$ {at.total():.2f}?")
    sucesso, mensagem = clinica.responder_orcamento(at, aprovado)
    (ok if aprovado else erro)(mensagem)


def mapa_salas(clinica):
    print(f"\n{Cores.CIANO}--- MAPA DAS SALAS ---{Cores.RESET}")
    for num, sala in clinica.salas.items():
        rotulo = "Cirurgia/Emergência" if sala["tipo"] == "Cirurgia" else "Consulta"
        if sala["status"] == "Ocupada":
            at = clinica.atendimentos.get(sala["atendimento"])
            if at:
                print(f"Sala {num} ({rotulo}): {Cores.AMARELO}Ocupada{Cores.RESET} | Atend. {at.numero} | "
                      f"{at.animal.descricao()} - {at.tutor.nome} | {etiqueta(at.prioridade)} | {at.status}")
        else:
            print(f"Sala {num} ({rotulo}): {Cores.VERDE}Livre{Cores.RESET}")
    print(f"{Cores.CIANO}----------------------{Cores.RESET}")


def acao_liberar_sala(clinica):
    mapa_salas(clinica)
    numero = pedir_inteiro("Número da sala que deseja liberar (ou ENTER para cancelar): ")
    if numero is None:
        print("Ação cancelada. Voltando ao menu...")
        return
    sala = clinica.salas.get(numero)
    if not sala or sala["status"] != "Ocupada":
        erro("Sala já está livre ou inválida.")
        return
    at = clinica.atendimentos.get(sala["atendimento"])
    if at.status != "Aguardando Pagamento":
        erro(f"O atendimento {at.numero} está '{at.status}'. Gere e aprove o orçamento primeiro.")
        return
    if confirmar(f"Procedimento da sala {numero} ({at.animal.nome}, tutor {at.tutor.nome}) concluído?"):
        clinica.liberar_sala(numero)


def acao_pagar(clinica):
    at = selecionar_atendimento(clinica)
    if not at:
        return
    if at.status != "Aguardando Pagamento":
        erro(f"O atendimento não está aguardando pagamento (Status: {at.status}).")
        return
    clinica.imprimir_resumo(at, "RESUMO")
    print("\n--- FORMA DE PAGAMENTO ---")
    print("1. PIX\n2. Cartão\n3. Dinheiro")
    escolha = entrada("Escolha (1-3) ou ENTER para cancelar: ")
    if escolha == "":
        return
    if escolha == "1":
        forma, parcelas = "PIX", 1
    elif escolha == "2":
        parcelas = pedir_inteiro("Parcelas: ")
        if parcelas is None or parcelas < 1:
            erro("Número de parcelas inválido.")
            return
        forma = "Cartão"
    elif escolha == "3":
        forma, parcelas = "Dinheiro", 1
    else:
        erro("Opção inválida.")
        return
    clinica.fechar_e_pagar(at, forma, parcelas)


def acao_desfazer(clinica):
    at = selecionar_atendimento(clinica, "Número do atendimento para desfazer (ou ENTER para cancelar): ")
    if not at:
        return
    if at.status != "Em Atendimento":
        erro(f"Só é possível desfazer enquanto o atendimento está 'Em Atendimento' (atual: {at.status}).")
        return
    ultima = at.historico_acoes.espiar()
    if ultima is None:
        erro("Não há ações para desfazer.")
        return
    if ultima["tipo"] == "add_item":
        d = ultima["dados"]
        descricao = f"{d['qtd']}x {d['codigo']} - {d['nome']}"
    else:
        descricao = ultima["dados"]["descricao"]
    if confirmar(f"Desfazer o lançamento de {descricao} no atendimento {at.numero}?"):
        clinica.desfazer(at)
        ok("Lançamento desfeito." + (" Material devolvido à prateleira." if ultima["tipo"] == "add_item" else ""))
    else:
        print("Ação cancelada.")


# ===================================================================== gestão
def acao_gestao_estoque(estoque):
    print("\n--- GESTÃO DE ESTOQUE ---")
    print("1. Cadastrar Novo Produto")
    print("2. Repor Estoque (Adicionar Lote)")
    print("3. Relatório de Estoque Mínimo / Vencimentos / Promoções")
    print("4. Relatório de Perdas")
    print("5. Ver Estoque Completo (lotes na ordem FIFO)")
    print("0. Voltar ao Menu Principal")
    sub = entrada("Escolha: ")

    if sub == "1":
        codigo = entrada("Código (ex.: M020, V005, T004 - ENTER para cancelar): ").upper()
        if not codigo:
            return
        nome = entrada("Nome: ")
        print("Categoria: 1. Vacina  2. Medicamento  3. Material")
        categoria = {"1": "Vacina", "2": "Medicamento", "3": "Material"}.get(entrada("Escolha: "))
        if not nome or not categoria:
            erro("Nome ou categoria inválidos.")
            return
        preco = pedir_decimal("Preço de venda: R$ ")
        minimo = pedir_inteiro("Estoque mínimo: ")
        if preco is None or minimo is None:
            return
        if estoque.cadastrar_produto(codigo, nome, categoria, preco, minimo):
            ok("Produto cadastrado!")
        else:
            erro("Código já existe.")

    elif sub == "2":
        codigo = entrada("Código do produto (ou ENTER para cancelar): ").upper()
        if not codigo:
            return
        produto = estoque.produtos.get(codigo)
        if not produto:
            erro("Produto não cadastrado!")
            return
        ok(f"Produto: {produto.nome} | Estoque atual: {produto.quantidade_total()}")
        quantidade = pedir_inteiro("Quantidade a adicionar: ")
        if quantidade is None or quantidade <= 0:
            return
        preco_compra = pedir_decimal("Preço de compra (unitário): R$ ")
        if preco_compra is None:
            return
        validade = pedir_data("Validade (AAAA-MM-DD) ou ENTER para nenhuma: ")
        if estoque.repor(codigo, quantidade, preco_compra, validade):
            ok("Lote adicionado ao fim da fila!")

    elif sub == "3":
        estoque.verificar_alertas()

    elif sub == "4":
        perdas = estoque.banco.relatorio_perdas()
        print(f"\n{Cores.NEGRITO}--- RELATÓRIO DE PERDAS ---{Cores.RESET}")
        if not perdas:
            print("Nenhuma perda registrada.")
        for nome, qtd, prejuizo in perdas:
            print(f"{nome} | Qtd: {qtd} | Prejuízo: R$ {prejuizo:.2f}")

    elif sub == "5":
        print(f"\n{Cores.NEGRITO}--- ESTOQUE COMPLETO (cada produto: fila de lotes, o 1º sai primeiro) ---{Cores.RESET}")
        for cod, prod in estoque.produtos.items():
            print(f"{Cores.CIANO}{cod} - {prod.nome}{Cores.RESET} [{prod.categoria}] "
                  f"Total: {prod.quantidade_total()} | Mín: {prod.estoque_minimo} | Venda: R$ {prod.preco_venda:.2f}")
            for posicao, lote in enumerate(prod.lotes(), 1):
                if lote.quantidade == 0:
                    continue
                validade = lote.validade or "sem validade"
                aviso = ""
                if lote.esta_vencido():
                    aviso = f" {Cores.VERMELHO}[VENCIDO]{Cores.RESET}"
                elif lote.perto_de_vencer():
                    aviso = f" {Cores.MAGENTA}[PERTO DE VENCER - {lote.dias_para_vencer()} dias]{Cores.RESET}"
                print(f"     {posicao}º lote | {lote.quantidade} un. | compra {lote.data_compra} | "
                      f"validade {validade}{aviso}")


def acao_relatorios(db):
    print("\n--- RELATÓRIOS GERENCIAIS ---")
    mais_usado = db.relatorio_metodo_mais_usado()
    if mais_usado:
        print(f"Método de pagamento mais usado: {Cores.VERDE}{mais_usado[0]}{Cores.RESET} ({mais_usado[1]} vezes)")
    else:
        print("Nenhum pagamento registrado ainda.")
    print(f"Faturamento Total: R$ {db.relatorio_faturamento_total():.2f}")
    print(f"Ticket Médio: R$ {db.relatorio_ticket_medio():.2f}")

    print("\nTop 5 Medicamentos / Vacinas / Materiais:")
    itens = db.relatorio_principais_itens()
    if not itens:
        print("Nenhum item registrado.")
    for nome, qtd in itens:
        print(f" - {nome}: {qtd} unidades")

    print("\nDesempenho dos Veterinários:")
    vets = db.relatorio_veterinarios()
    if not vets:
        print("Nenhum atendimento fechado ainda.")
    for vet, qtd, total in vets:
        print(f" - {vet}: {qtd} atendimento(s) | Faturamento: R$ {total:.2f}")

    print("\nAtendimentos por Prioridade:")
    for prioridade, qtd, total in db.relatorio_por_prioridade():
        print(f" - {prioridade}: {qtd} | R$ {total:.2f}")

    print("\nAtendimentos por Espécie:")
    for especie, qtd, total in db.relatorio_por_especie():
        print(f" - {especie}: {qtd} | R$ {total:.2f}")
    print("-----------------------------\n")


def acao_painel(clinica):
    print(f"\n{Cores.NEGRITO}========= PAINEL DE CONTROLE ========={Cores.RESET}")
    mapa_salas(clinica)
    print(f"\n{Cores.CIANO}--- FILAS DE ESPERA (ordem de atendimento: Emergência > Urgente > Rotina) ---{Cores.RESET}")
    for nivel in NIVEIS:
        print(f"{etiqueta(nivel)}")
        fila = clinica.filas[nivel]
        if fila.esta_vazia():
            print("  (Vazia)")
        for p in fila.percorrer():
            print(f"  {p['chegada']} | {p['animal'].nome} ({p['animal'].especie}) - {p['tutor'].nome} | {p['queixa']}")
    print(f"{Cores.NEGRITO}======================================{Cores.RESET}\n")


def texto_vacina(dose):
    hoje = date.today().strftime("%Y-%m-%d")
    proxima = dose["proxima"]
    if not proxima:
        return ""
    if proxima < hoje:
        return f"{Cores.VERMELHO}ATRASADA (reforço era em {proxima}){Cores.RESET}"
    dias = (datetime.strptime(proxima, "%Y-%m-%d").date() - date.today()).days
    if dias <= 30:
        return f"{Cores.AMARELO}vence em {dias} dia(s) ({proxima}){Cores.RESET}"
    return f"{Cores.VERDE}em dia (próxima em {proxima}){Cores.RESET}"


def acao_ficha_animal(cadastro, db):
    tutor, animal = selecionar_animal(cadastro, permitir_cadastro=False)
    if not animal:
        return
    castrado = "castrado(a)" if animal.castrado else "não castrado(a)"
    print(f"\n{Cores.NEGRITO}=== FICHA DE {animal.nome.upper()} ==={Cores.RESET}")
    print(f"{animal.especie} | {animal.raca} | {animal.sexo} | {animal.idade()} | {animal.peso:.1f} kg | {castrado}")
    print(f"Tutor: {tutor.nome} ({formatar_cpf(tutor.cpf)}) | {tutor.telefone}")

    print(f"\n{Cores.CIANO}--- CARTEIRA DE VACINAÇÃO ---{Cores.RESET}")
    ultimas = animal.ultimas_vacinas()
    if not ultimas:
        print("Nenhuma vacina registrada.")
    for dose in ultimas:
        print(f"  {dose['vacina']} | aplicada em {dose['data']} | {texto_vacina(dose)}")

    print(f"\n{Cores.CIANO}--- PRONTUÁRIO (atendimentos anteriores) ---{Cores.RESET}")
    prontuario = db.buscar_prontuario(animal.id)
    if not prontuario:
        print("Nenhum atendimento anterior.")
    for numero, data_hora, vet, prioridade, queixa, servicos, total in prontuario:
        print(f"  [{data_hora}] Atend. {numero} | {prioridade} | {vet} | R$ {total:.2f}")
        print(f"      Queixa: {queixa}")
        itens = db.buscar_itens_atendimento(numero)
        if itens:
            print("      Itens: " + ", ".join(f"{q}x {n}" for n, q in itens))
        if servicos:
            print(f"      Procedimentos: {servicos}")


def alertar_vacinas_atrasadas(cadastro):
    atrasos = cadastro.vacinas_em_atraso()
    if not atrasos:
        return
    print(f"{Cores.AMARELO}--- LEMBRETES: VACINAS ATRASADAS (avisar os tutores) ---{Cores.RESET}")
    for tutor, animal, dose in atrasos:
        print(f"{Cores.AMARELO}[VACINA] {animal.nome} ({tutor.nome}, {tutor.telefone}): "
              f"{dose['vacina']} atrasada desde {dose['proxima']}.{Cores.RESET}")
    print()


# ================================================================ dados iniciais
def carregar_dados_iniciais(clinica, cadastro):
    """Simula a chegada de pacientes. A triagem é sugerida automaticamente pela queixa."""
    print("Carregando pacientes de demonstração...")
    chegadas = [
        ("33333333333", "Nina", "Vacina anual V4 e antirrábica"),
        ("11111111111", "Thor", "Vômito e diarreia desde ontem"),
        ("22222222222", "Bolt", "Atropelado na rua, sangrando e sem conseguir levantar"),
        ("44444444444", "Pipoca", "Coceira intensa e queda de pelo"),
        ("55555555555", "Rex", "Mordida profunda na pata traseira"),
        ("66666666666", "Luna", "Cadela em trabalho de parto há 6 horas, filhote preso"),
        ("77777777777", "Mingau", "Gato não consegue urinar, miando de dor"),
        ("88888888888", "Frajola", "Check-up e vermifugação"),
    ]
    for cpf, nome_animal, queixa in chegadas:
        tutor = cadastro.buscar_por_cpf(cpf)
        animal = tutor.buscar_animal(nome_animal) if tutor else None
        if animal:
            nivel, _ = classificar_prioridade(queixa)
            clinica.registrar_chegada(tutor, animal, queixa, nivel)

    # Chama os 2 primeiros: as emergências furam a fila e ocupam as salas de cirurgia
    for _ in range(2):
        clinica.chamar_proximo()
    print("Dados carregados com sucesso! (2 atendimentos abertos e filas populadas)\n")


def menu():
    db = BancoDados()
    db.popular_servicos_iniciais()
    if db.contar_produtos() == 0:
        popular_catalogo(db)
    if db.contar_tutores() == 0:
        popular_tutores_demo(db)

    estoque = Estoque(db)
    estoque.carregar_do_banco()
    estoque.verificar_alertas()

    cadastro = CadastroTutores(db)
    cadastro.carregar_do_banco()
    alertar_vacinas_atrasadas(cadastro)

    clinica = Clinica(db, estoque, cadastro)
    carregar_dados_iniciais(clinica, cadastro)

    while True:
        print(f"\n{Cores.CIANO}========================================{Cores.RESET}")
        print(f"{Cores.CIANO}{Cores.NEGRITO}   SISTEMA DE CLÍNICA VETERINÁRIA   {Cores.RESET}")
        print(f"{Cores.CIANO}========================================{Cores.RESET}")

        print(f"{Cores.NEGRITO}--- CADASTROS ---{Cores.RESET}")
        print("1. Cadastrar Tutor")
        print("2. Cadastrar Animal")
        print("3. Consultar Tutores e Animais")
        print("4. Remover Animal / Tutor")

        print(f"\n{Cores.NEGRITO}--- FLUXO DE ATENDIMENTO ---{Cores.RESET}")
        print("5. Registrar Chegada (Triagem)")
        print("6. Chamar Próximo para a Sala")
        print("7. Ver Árvore de Diagnóstico")
        print("8. Prescrever Medicamento / Vacina / Material")
        print("9. Adicionar Consulta / Procedimento")
        print("10. Gerar Orçamento")
        print("11. Aprovar Orçamento")
        print("12. Liberar Sala (Procedimento Concluído)")
        print("13. Fechar Atendimento e Pagar")
        print("14. Desfazer Última Ação do Atendimento (Undo)")

        print(f"\n{Cores.NEGRITO}--- GESTÃO E RELATÓRIOS ---{Cores.RESET}")
        print("15. Ver Material Reservado (em uso nos pacientes)")
        print("16. Gestão de Estoque e Compras")
        print("17. Relatórios Gerenciais (SQL)")
        print("18. Painel de Controle (Filas e Salas)")
        print("19. Ficha do Animal (Vacinas e Prontuário)")
        print("0. Sair")
        print(f"{Cores.CIANO}========================================{Cores.RESET}")

        opcao = entrada("Escolha uma opção: ")

        if opcao == "1":
            acao_cadastrar_tutor(cadastro)
        elif opcao == "2":
            acao_cadastrar_animal(cadastro)
        elif opcao == "3":
            acao_consultar(cadastro)
        elif opcao == "4":
            acao_remover(cadastro, clinica)
        elif opcao == "5":
            acao_registrar_chegada(cadastro, clinica)
        elif opcao == "6":
            acao_chamar_proximo(clinica, estoque)
        elif opcao == "7":
            acao_ver_arvore(clinica, estoque)
        elif opcao == "8":
            acao_prescrever(clinica, estoque)
        elif opcao == "9":
            acao_adicionar_servico(clinica)
        elif opcao == "10":
            acao_gerar_orcamento(clinica)
        elif opcao == "11":
            acao_aprovar_orcamento(clinica)
        elif opcao == "12":
            acao_liberar_sala(clinica)
        elif opcao == "13":
            acao_pagar(clinica)
        elif opcao == "14":
            acao_desfazer(clinica)
        elif opcao == "15":
            estoque.ver_reservas()
        elif opcao == "16":
            acao_gestao_estoque(estoque)
        elif opcao == "17":
            acao_relatorios(db)
        elif opcao == "18":
            acao_painel(clinica)
        elif opcao == "19":
            acao_ficha_animal(cadastro, db)
        elif opcao == "0":
            devolvidos = estoque.devolver_todas()
            if devolvidos:
                print(f"{Cores.AMARELO}{devolvidos} reserva(s) de material de atendimentos não pagos "
                      f"foram devolvidas à prateleira.{Cores.RESET}")
            print("Encerrando...")
            db.fechar_conexao()
            break
        else:
            erro("Opção inválida!")


if __name__ == "__main__":
    menu()
