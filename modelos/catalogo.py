"""Dados iniciais de demonstração: catálogo de produtos, tutores e animais."""
from datetime import date, timedelta


def _data(dias_de_diferenca):
    return (date.today() + timedelta(days=dias_de_diferenca)).strftime("%Y-%m-%d")


# (codigo, nome, categoria, preco_venda, estoque_minimo,
#  lotes[(quantidade, preco_compra, comprado_ha_X_dias, validade_em_X_dias | None)])
CATALOGO = [
    ("V001", "Vacina V10 (Cães)", "Vacina", 120.0, 10, [(10, 55.0, 120, 40), (20, 58.0, 15, 400)]),
    ("V002", "Vacina Antirrábica", "Vacina", 70.0, 10, [(20, 30.0, 20, 330)]),
    ("V003", "Vacina V4 (Gatos)", "Vacina", 130.0, 8, [(15, 60.0, 20, 300)]),
    ("V004", "Vacina Tosse dos Canis", "Vacina", 110.0, 5, [(8, 50.0, 30, 250)]),
    ("M001", "Anti-inflamatório (Meloxicam)", "Medicamento", 45.0, 10, [(30, 15.0, 60, 500)]),
    ("M002", "Antibiótico (Amoxicilina + Clavulanato)", "Medicamento", 60.0, 10,
     [(6, 25.0, 400, -10), (30, 28.0, 30, 365)]),
    ("M003", "Antiemético (Maropitant)", "Medicamento", 55.0, 8, [(20, 22.0, 40, 400)]),
    ("M004", "Protetor Gástrico (Omeprazol)", "Medicamento", 35.0, 8, [(20, 10.0, 40, 600)]),
    ("M005", "Probiótico Veterinário", "Medicamento", 40.0, 5, [(12, 14.0, 40, 300)]),
    ("M006", "Analgésico (Tramadol)", "Medicamento", 50.0, 8, [(20, 18.0, 40, 450)]),
    ("M007", "Fluidoterapia (Ringer Lactato 500 ml)", "Medicamento", 25.0, 15, [(40, 8.0, 30, 700)]),
    ("M008", "Vermífugo", "Medicamento", 30.0, 10, [(25, 9.0, 40, 500)]),
    ("M009", "Antipulgas e Carrapatos", "Medicamento", 85.0, 10, [(20, 40.0, 30, 500)]),
    ("M010", "Corticoide (Prednisolona)", "Medicamento", 40.0, 6, [(15, 12.0, 40, 500)]),
    ("M011", "Shampoo Antifúngico", "Medicamento", 65.0, 4, [(8, 28.0, 60, 800)]),
    ("M012", "Ocitocina", "Medicamento", 45.0, 4, [(8, 18.0, 50, 200)]),
    ("M013", "Anestésico Injetável (Propofol)", "Medicamento", 150.0, 4, [(8, 70.0, 50, 365)]),
    ("M014", "Anticonvulsivante (Fenobarbital)", "Medicamento", 75.0, 3, [(2, 30.0, 90, 500)]),
    ("M015", "Cardioprotetor (Pimobendan)", "Medicamento", 120.0, 3, [(6, 55.0, 50, 500)]),
    ("M016", "Colírio Antibiótico", "Medicamento", 48.0, 4, [(8, 20.0, 50, 300)]),
    ("M017", "Solução Otológica", "Medicamento", 52.0, 4, [(8, 22.0, 50, 400)]),
    ("M018", "Carvão Ativado", "Medicamento", 35.0, 4, [(8, 12.0, 50, 700)]),
    ("M019", "Broncodilatador", "Medicamento", 60.0, 3, [(6, 25.0, 50, 400)]),
    ("T001", "Kit de Sutura", "Material", 90.0, 5, [(10, 40.0, 50, None)]),
    ("T002", "Tala / Imobilizador", "Material", 60.0, 4, [(8, 25.0, 50, None)]),
    ("T003", "Atadura e Curativo", "Material", 30.0, 10, [(30, 8.0, 50, None)]),
]

# Observações de demonstração:
#  - V001 tem um lote que vence em 40 dias (alerta de promoção + 20% de desconto);
#  - M002 tem um lote já vencido (descartado e registrado em 'perdas');
#  - M014 começa abaixo do estoque mínimo (alerta amarelo).


def popular_catalogo(db):
    for codigo, nome, categoria, preco, minimo, lotes in CATALOGO:
        prod_id = db.cadastrar_produto(codigo, nome, categoria, preco, minimo)
        for qtd, preco_compra, comprado_ha, validade_em in lotes:
            validade = _data(validade_em) if validade_em is not None else None
            db.adicionar_lote(prod_id, qtd, preco_compra, _data(-comprado_ha), validade)


# (cpf, nome, telefone, endereco, [(nome, especie, raca, sexo, idade_anos, peso, castrado)])
TUTORES_DEMO = [
    ("11111111111", "Gabriel Souza", "(11) 99999-0001", "Rua das Flores, 10",
     [("Thor", "Cão", "Labrador", "M", 4, 32.0, True), ("Mel", "Gato", "SRD", "F", 2, 4.2, True)]),
    ("22222222222", "Elielton Lima", "(11) 99999-0002", "Av. Brasil, 250",
     [("Bolt", "Cão", "Vira-lata", "M", 3, 14.5, False)]),
    ("33333333333", "Jaime Barbosa", "(11) 99999-0003", "Rua do Sol, 77",
     [("Nina", "Gato", "Siamês", "F", 1, 3.6, False), ("Toco", "Cão", "Poodle", "M", 5, 7.8, True)]),
    ("44444444444", "Ana Costa", "(11) 99999-0004", "Rua Verde, 321",
     [("Pipoca", "Cão", "Shih-tzu", "F", 6, 6.1, True)]),
    ("55555555555", "Roberto Alves", "(11) 99999-0005", "Alameda Azul, 18",
     [("Rex", "Cão", "Pastor Alemão", "M", 7, 36.0, True)]),
    ("66666666666", "Fernanda Rocha", "(11) 99999-0006", "Rua Central, 902",
     [("Luna", "Cão", "Golden Retriever", "F", 3, 28.0, False)]),
    ("77777777777", "Lucas Martins", "(11) 99999-0007", "Rua da Paz, 45",
     [("Mingau", "Gato", "Persa", "M", 4, 5.4, True)]),
    ("88888888888", "Mariana Dias", "(11) 99999-0008", "Rua do Lago, 6",
     [("Frajola", "Gato", "SRD", "M", 8, 5.0, True)]),
]


def popular_tutores_demo(db):
    ids = {}
    for cpf, nome, tel, endereco, animais in TUTORES_DEMO:
        db.inserir_tutor(cpf, nome, tel, endereco)
        for a_nome, esp, raca, sexo, idade, peso, castrado in animais:
            nasc = _data(-int(idade * 365.25))
            ids[a_nome] = db.inserir_animal(cpf, a_nome, esp, raca, sexo, nasc, peso, castrado)

    # Carteira de vacinação de demonstração: a antirrábica do Thor está atrasada
    db.inserir_vacina(ids["Thor"], "Vacina Antirrábica", _data(-400), _data(-35))
    db.inserir_vacina(ids["Thor"], "Vacina V10 (Cães)", _data(-100), _data(265))
    db.inserir_vacina(ids["Mel"], "Vacina V4 (Gatos)", _data(-200), _data(165))
