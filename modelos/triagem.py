import unicodedata
from estruturas.cores import Cores

EMERGENCIA = "Emergência"
URGENTE = "Urgente"
ROTINA = "Rotina"

# Ordem de prioridade (a primeira fila não vazia é sempre atendida primeiro)
NIVEIS = [EMERGENCIA, URGENTE, ROTINA]

COR_NIVEL = {EMERGENCIA: Cores.VERMELHO, URGENTE: Cores.AMARELO, ROTINA: Cores.VERDE}


def normalizar(texto):
    """Minúsculas e sem acentos, para comparar palavras-chave de forma robusta."""
    sem_acento = unicodedata.normalize("NFD", texto)
    return "".join(c for c in sem_acento if unicodedata.category(c) != "Mn").lower()


# Risco de vida imediato: atropelamento, convulsão, envenenamento, parto com complicação...
SINAIS_EMERGENCIA = [
    "atropel", "convuls", "envenen", "veneno", "intoxic", "raticida", "chocolate",
    "hemorragia", "sangrando muito", "falta de ar", "dificuldade para respirar",
    "dificuldade respirat", "nao consegue respirar", "desmai", "inconsciente", "engasgad",
    "queda de altura", "nao consegue urinar", "nao consegue fazer xixi", "filhote preso",
    "parto com dificuldade", "distocia", "queimadura", "afogament", "nao consegue levantar",
    "nao levanta",
]

# Precisa de atendimento rápido: machucados, fraturas, parto em andamento, vômitos...
SINAIS_URGENTE = [
    "parto", "contracoes", "vomit", "diarreia", "sangue", "sangrando", "fratura", "quebrad",
    "manca", "nao apoia", "ferida", "mordida", "corte", "machucad", "nao come", "sem apetite",
    "febre", "apatic", "prostrad", "letargi", "corrimento", "barriga inchada", "picada",
]


def classificar_prioridade(queixa):
    """Sugere o nível de triagem a partir da queixa. Retorna (nivel, palavra_chave_encontrada)."""
    texto = normalizar(queixa)
    for termo in SINAIS_EMERGENCIA:
        if termo in texto:
            return EMERGENCIA, termo
    for termo in SINAIS_URGENTE:
        if termo in texto:
            return URGENTE, termo
    return ROTINA, None


def etiqueta(nivel):
    return f"{COR_NIVEL[nivel]}{Cores.NEGRITO}[{nivel}]{Cores.RESET}"
