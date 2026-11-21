from estruturas.arvore import NoArvore, ArvoreDiagnostico
from modelos.triagem import normalizar

CAO = "Cão"
GATO = "Gato"

# Registro plano de todas as condições: codigo -> dados (preenchido ao montar a árvore)
CONDICOES = {}

# Estrutura da árvore:
#   (nome, [filhos])                       -> Sistema/Subsistema (pode ter N filhos)
#   (codigo, nome, especie, tratamentos)   -> Condição (folha); especie None = cão e gato
ESTRUTURA = [
    ("Sistema Digestório", [
        ("Estômago e Esôfago", [
            ("D001", "Gastrite", None, ["M003", "M004"]),
            ("D002", "Corpo Estranho (ingestão)", None, ["M006", "M007"]),
        ]),
        ("Intestino", [
            ("D003", "Parvovirose", CAO, ["M003", "M007", "M002"]),
            ("D004", "Verminose", None, ["M008"]),
            ("D005", "Colite / Diarreia", None, ["M005", "M007"]),
        ]),
        ("Fígado e Pâncreas", [
            ("D006", "Pancreatite", None, ["M003", "M006", "M007"]),
        ]),
    ]),
    ("Sistema Respiratório", [
        ("Vias Aéreas", [
            ("D007", "Tosse dos Canis", CAO, ["M002", "V004"]),
            ("D008", "Gripe Felina (Rinotraqueíte)", GATO, ["M002", "V003"]),
        ]),
        ("Pulmão", [
            ("D009", "Pneumonia", None, ["M002", "M007"]),
            ("D010", "Asma Felina", GATO, ["M019", "M010"]),
        ]),
    ]),
    ("Sistema Locomotor", [
        ("Ossos", [
            ("D011", "Fratura", None, ["M006", "T002", "M001"]),
        ]),
        ("Articulações", [
            ("D012", "Displasia Coxofemoral", CAO, ["M001"]),
            ("D013", "Luxação de Patela", None, ["M001", "M006"]),
        ]),
    ]),
    ("Sistema Tegumentar (Pele)", [
        ("Parasitas", [
            ("D014", "Pulgas e Carrapatos", None, ["M009"]),
            ("D015", "Sarna", None, ["M009"]),
        ]),
        ("Dermatites", [
            ("D016", "Dermatite Alérgica", None, ["M010"]),
            ("D017", "Dermatite Fúngica", None, ["M011"]),
        ]),
        ("Ferimentos", [
            ("D018", "Laceração / Ferida Aberta", None, ["T001", "T003", "M002"]),
        ]),
    ]),
    ("Sistema Urinário", [
        ("D019", "Cistite", None, ["M002", "M001"]),
        ("D020", "Obstrução Urinária", GATO, ["M007", "M006"]),
        ("D021", "Doença Renal Crônica", GATO, ["M007"]),
    ]),
    ("Sistema Reprodutor", [
        ("D022", "Piometra", None, ["M002", "M007", "M013"]),
        ("D023", "Parto Normal (acompanhamento)", None, ["T003"]),
        ("D024", "Distocia (parto com complicação)", None, ["M012", "M013", "T001"]),
    ]),
    ("Sistema Neurológico", [
        ("D025", "Convulsão / Epilepsia", None, ["M014"]),
        ("D026", "Cinomose", CAO, ["M014", "M002", "M007"]),
    ]),
    ("Sistema Cardiovascular", [
        ("D027", "Cardiopatia", None, ["M015"]),
    ]),
    ("Trauma e Emergência", [
        ("D028", "Politrauma (atropelamento)", None, ["M006", "M007", "M013", "T003"]),
        ("D029", "Intoxicação / Envenenamento", None, ["M018", "M007", "M003"]),
    ]),
    ("Olhos e Ouvidos", [
        ("D030", "Conjuntivite", None, ["M016"]),
        ("D031", "Otite", None, ["M017"]),
    ]),
    ("Prevenção", [
        ("D032", "Vacinação de Cães", CAO, ["V001", "V002"]),
        ("D033", "Vacinação de Gatos", GATO, ["V003", "V002"]),
    ]),
]


def _montar(pai, itens, nivel=0):
    for item in itens:
        if len(item) == 4:
            codigo, nome, especie, tratamentos = item
            CONDICOES[codigo] = {"nome": nome, "especie": especie, "tratamentos": tratamentos}
            pai.adicionar_filho(NoArvore(nome, codigo, "Condição", especie, tratamentos))
        else:
            nome, filhos = item
            no = NoArvore(nome, categoria="Sistema" if nivel == 0 else "Subsistema")
            _montar(no, filhos, nivel + 1)
            pai.adicionar_filho(no)


def criar_arvore_animal():
    raiz = NoArvore("Animal")
    _montar(raiz, ESTRUTURA)
    return ArvoreDiagnostico(raiz)


# Palavras-chave da queixa (sem acento, minúsculas) -> condições suspeitas
SINTOMAS = {
    "vomit": ["D001", "D002", "D003", "D006", "D029"],
    "diarreia": ["D003", "D004", "D005"],
    "sangue nas fezes": ["D003", "D005"],
    "nao come": ["D001", "D006", "D021"],
    "sem apetite": ["D001", "D006", "D021"],
    "engoliu": ["D002"], "corpo estranho": ["D002"],
    "barriga inchada": ["D002", "D004"], "verme": ["D004"], "vermifug": ["D004"],
    "tosse": ["D007", "D008", "D009", "D010", "D027"],
    "espirr": ["D008"], "secrecao nasal": ["D007", "D008"], "catarro": ["D007", "D008"],
    "falta de ar": ["D009", "D010", "D027"],
    "dificuldade para respirar": ["D009", "D010", "D027"],
    "chiado": ["D010"],
    "manca": ["D011", "D012", "D013"], "nao apoia": ["D011", "D013"],
    "fratura": ["D011"], "quebrad": ["D011"],
    "atropel": ["D028", "D011", "D018"],
    "coceira": ["D014", "D015", "D016", "D017"], "cocando": ["D014", "D015", "D016", "D017"],
    "pulga": ["D014"], "carrapato": ["D014"], "sarna": ["D015"],
    "queda de pelo": ["D015", "D016", "D017"], "feridas na pele": ["D016", "D017"],
    "vermelhidao": ["D016", "D017"],
    "ferida": ["D018"], "corte": ["D018"], "mordida": ["D018"], "machucad": ["D018"],
    "sangrando": ["D018", "D028"],
    "xixi": ["D019", "D020", "D021"], "urina": ["D019", "D020", "D021"],
    "nao consegue urinar": ["D020"], "nao consegue fazer xixi": ["D020"],
    "sangue na urina": ["D019"], "bebendo muita agua": ["D021"],
    "corrimento": ["D022"], "piometra": ["D022"],
    "parto": ["D023", "D024"], "contracoes": ["D023", "D024"], "filhote preso": ["D024"],
    "convuls": ["D025", "D026"], "tremor": ["D025", "D026", "D029"], "cinomose": ["D026"],
    "desmai": ["D025", "D027"], "cansaco": ["D027"],
    "envenen": ["D029"], "veneno": ["D029"], "intoxic": ["D029"],
    "raticida": ["D029"], "chocolate": ["D029"],
    "olho": ["D030"], "lacrimej": ["D030"],
    "ouvido": ["D031"], "balancando a cabeca": ["D031"],
    "vacina": ["D032", "D033"], "antirrabica": ["D032", "D033"],
}


def analisar_queixa(queixa_texto, especie=None):
    """Varre a queixa em busca de palavras-chave e devolve os códigos de condições suspeitas.

    Se a espécie for informada, descarta condições exclusivas da outra espécie.
    """
    texto = normalizar(queixa_texto)
    suspeitas = {}
    for sintoma, codigos in SINTOMAS.items():
        if sintoma in texto:
            for codigo in codigos:
                esp_condicao = CONDICOES[codigo]["especie"]
                if especie and esp_condicao and esp_condicao != especie:
                    continue
                suspeitas[codigo] = True
    return list(suspeitas)


# Garante que CONDICOES esteja preenchido assim que o módulo é importado
criar_arvore_animal()
