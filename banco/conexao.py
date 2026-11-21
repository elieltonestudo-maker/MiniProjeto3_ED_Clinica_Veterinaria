import sqlite3
from datetime import datetime


class BancoDados:
    def __init__(self, nome_arquivo="clinica.db"):
        self.conexao = sqlite3.connect(nome_arquivo)
        self.cursor = self.conexao.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON")
        self.criar_tabelas()

    def criar_tabelas(self):
        # 1. Produtos (medicamentos, vacinas e materiais)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT UNIQUE,
                nome TEXT,
                categoria TEXT,
                preco_venda REAL,
                estoque_minimo INTEGER
            )
        """)

        # 2. Lotes
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS lotes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                produto_id INTEGER,
                quantidade INTEGER,
                preco_compra REAL,
                data_compra TEXT,
                data_validade TEXT,
                FOREIGN KEY(produto_id) REFERENCES produtos(id)
            )
        """)

        # 3. Perdas
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS perdas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                produto_nome TEXT,
                quantidade INTEGER,
                motivo TEXT,
                data_perda TEXT,
                prejuizo_financeiro REAL
            )
        """)

        # 4. Atendimentos pagos
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS atendimentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_atendimento INTEGER,
                tutor_cpf TEXT,
                tutor TEXT,
                animal_id INTEGER,
                animal TEXT,
                especie TEXT,
                veterinario TEXT,
                prioridade TEXT,
                queixa TEXT,
                servicos TEXT,
                forma_pagamento TEXT,
                parcelas INTEGER,
                valor_total REAL,
                data_hora TEXT,
                retorno_dias INTEGER
            )
        """)

        # 5. Itens do atendimento (medicamentos, vacinas e materiais usados)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS itens_atendimento (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_atendimento INTEGER,
                produto_nome TEXT,
                quantidade INTEGER,
                preco_unitario REAL
            )
        """)

        # 6. Tabela de serviços (consultas e procedimentos)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS servicos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT UNIQUE,
                descricao TEXT,
                preco REAL
            )
        """)

        # 7. Tutores
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tutores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cpf TEXT UNIQUE,
                nome TEXT,
                telefone TEXT,
                endereco TEXT
            )
        """)

        # 8. Animais (um tutor tem 0..N animais)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS animais (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tutor_cpf TEXT,
                nome TEXT,
                especie TEXT,
                raca TEXT,
                sexo TEXT,
                nascimento TEXT,
                peso REAL,
                castrado INTEGER,
                FOREIGN KEY(tutor_cpf) REFERENCES tutores(cpf)
            )
        """)

        # 9. Carteira de vacinação
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS vacinas_aplicadas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                animal_id INTEGER,
                vacina TEXT,
                data_aplicacao TEXT,
                proxima_dose TEXT,
                FOREIGN KEY(animal_id) REFERENCES animais(id)
            )
        """)

        self.conexao.commit()

    # --------------------------------------------------------------- ESTOQUE
    def contar_produtos(self):
        self.cursor.execute("SELECT COUNT(*) FROM produtos")
        return self.cursor.fetchone()[0]

    def cadastrar_produto(self, codigo, nome, categoria, preco_venda, estoque_minimo):
        """Devolve o id do novo produto, ou None se o código já existir."""
        try:
            self.cursor.execute("""
                INSERT INTO produtos (codigo, nome, categoria, preco_venda, estoque_minimo)
                VALUES (?, ?, ?, ?, ?)
            """, (codigo, nome, categoria, preco_venda, estoque_minimo))
            self.conexao.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            return None

    def adicionar_lote(self, produto_id, quantidade, preco_compra, data_compra, data_validade):
        self.cursor.execute("""
            INSERT INTO lotes (produto_id, quantidade, preco_compra, data_compra, data_validade)
            VALUES (?, ?, ?, ?, ?)
        """, (produto_id, quantidade, preco_compra, data_compra, data_validade))
        self.conexao.commit()
        return self.cursor.lastrowid

    def listar_produtos(self):
        self.cursor.execute("SELECT id, codigo, nome, categoria, preco_venda, estoque_minimo FROM produtos ORDER BY codigo")
        return self.cursor.fetchall()

    def listar_lotes(self, produto_id):
        """Lotes com saldo, do mais antigo para o mais novo (ordem da fila FIFO)."""
        self.cursor.execute("""
            SELECT id, quantidade, preco_compra, data_compra, data_validade
            FROM lotes
            WHERE produto_id = ? AND quantidade > 0
            ORDER BY data_compra, COALESCE(data_validade, '9999-12-31'), id
        """, (produto_id,))
        return self.cursor.fetchall()

    def atualizar_quantidade_lote(self, id_lote, quantidade):
        self.cursor.execute("UPDATE lotes SET quantidade = ? WHERE id = ?", (quantidade, id_lote))
        self.conexao.commit()

    def registrar_perda(self, produto_nome, quantidade, motivo, prejuizo):
        agora = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.cursor.execute("""
            INSERT INTO perdas (produto_nome, quantidade, motivo, data_perda, prejuizo_financeiro)
            VALUES (?, ?, ?, ?, ?)
        """, (produto_nome, quantidade, motivo, agora, prejuizo))
        self.conexao.commit()

    def relatorio_perdas(self):
        self.cursor.execute("""
            SELECT produto_nome, SUM(quantidade), SUM(prejuizo_financeiro)
            FROM perdas GROUP BY produto_nome
        """)
        return self.cursor.fetchall()

    # ------------------------------------------------------------ SERVIÇOS
    def popular_servicos_iniciais(self):
        self.cursor.execute("SELECT COUNT(*) FROM servicos")
        if self.cursor.fetchone()[0] == 0:
            servicos = [
                ("S001", "Consulta Clínica Geral", 120.0),
                ("S002", "Taxa de Atendimento de Emergência", 250.0),
                ("S003", "Aplicação de Vacina", 30.0),
                ("S004", "Raio-X", 180.0),
                ("S005", "Ultrassonografia", 220.0),
                ("S006", "Hemograma (exame de sangue)", 90.0),
                ("S007", "Sutura e Curativo", 150.0),
                ("S008", "Castração", 450.0),
                ("S009", "Cesariana", 1200.0),
                ("S010", "Parto Assistido", 350.0),
                ("S011", "Cirurgia Ortopédica (fratura)", 2500.0),
                ("S012", "Internação (diária)", 200.0),
            ]
            self.cursor.executemany("INSERT INTO servicos (codigo, descricao, preco) VALUES (?, ?, ?)", servicos)
            self.conexao.commit()

    def buscar_servicos(self):
        self.cursor.execute("SELECT codigo, descricao, preco FROM servicos ORDER BY codigo")
        return self.cursor.fetchall()

    # -------------------------------------------------- TUTORES E ANIMAIS
    def contar_tutores(self):
        self.cursor.execute("SELECT COUNT(*) FROM tutores")
        return self.cursor.fetchone()[0]

    def inserir_tutor(self, cpf, nome, telefone, endereco):
        try:
            self.cursor.execute(
                "INSERT INTO tutores (cpf, nome, telefone, endereco) VALUES (?, ?, ?, ?)",
                (cpf, nome, telefone, endereco))
            self.conexao.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def listar_tutores(self):
        self.cursor.execute("SELECT cpf, nome, telefone, endereco FROM tutores ORDER BY id")
        return self.cursor.fetchall()

    def inserir_animal(self, tutor_cpf, nome, especie, raca, sexo, nascimento, peso, castrado):
        self.cursor.execute("""
            INSERT INTO animais (tutor_cpf, nome, especie, raca, sexo, nascimento, peso, castrado)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (tutor_cpf, nome, especie, raca, sexo, nascimento, peso, 1 if castrado else 0))
        self.conexao.commit()
        return self.cursor.lastrowid

    def listar_animais(self, tutor_cpf):
        self.cursor.execute("""
            SELECT id, nome, especie, raca, sexo, nascimento, peso, castrado
            FROM animais WHERE tutor_cpf = ? ORDER BY id
        """, (tutor_cpf,))
        return self.cursor.fetchall()

    def remover_animal(self, animal_id):
        self.cursor.execute("DELETE FROM vacinas_aplicadas WHERE animal_id = ?", (animal_id,))
        self.cursor.execute("DELETE FROM animais WHERE id = ?", (animal_id,))
        self.conexao.commit()

    def remover_tutor(self, cpf):
        """Cascata: apaga vacinas, animais e por fim o tutor."""
        self.cursor.execute(
            "DELETE FROM vacinas_aplicadas WHERE animal_id IN (SELECT id FROM animais WHERE tutor_cpf = ?)", (cpf,))
        self.cursor.execute("DELETE FROM animais WHERE tutor_cpf = ?", (cpf,))
        self.cursor.execute("DELETE FROM tutores WHERE cpf = ?", (cpf,))
        self.conexao.commit()

    def inserir_vacina(self, animal_id, vacina, data_aplicacao, proxima_dose):
        self.cursor.execute("""
            INSERT INTO vacinas_aplicadas (animal_id, vacina, data_aplicacao, proxima_dose)
            VALUES (?, ?, ?, ?)
        """, (animal_id, vacina, data_aplicacao, proxima_dose))
        self.conexao.commit()

    def listar_vacinas(self, animal_id):
        self.cursor.execute("""
            SELECT vacina, data_aplicacao, proxima_dose
            FROM vacinas_aplicadas WHERE animal_id = ? ORDER BY data_aplicacao
        """, (animal_id,))
        return self.cursor.fetchall()

    # ------------------------------------------- ATENDIMENTOS E RELATÓRIOS
    def proximo_numero_atendimento(self):
        self.cursor.execute("SELECT MAX(numero_atendimento) FROM atendimentos")
        maior = self.cursor.fetchone()[0]
        return (maior + 1) if maior else 1000

    def registrar_pagamento(self, d, itens_utilizados):
        self.cursor.execute("""
            INSERT INTO atendimentos (numero_atendimento, tutor_cpf, tutor, animal_id, animal, especie,
                                      veterinario, prioridade, queixa, servicos, forma_pagamento,
                                      parcelas, valor_total, data_hora, retorno_dias)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (d["numero"], d["tutor_cpf"], d["tutor"], d["animal_id"], d["animal"], d["especie"],
              d["veterinario"], d["prioridade"], d["queixa"], d["servicos"], d["forma_pagamento"],
              d["parcelas"], d["valor_total"], d["data_hora"], d["retorno_dias"]))

        for item in itens_utilizados:
            self.cursor.execute("""
                INSERT INTO itens_atendimento (numero_atendimento, produto_nome, quantidade, preco_unitario)
                VALUES (?, ?, ?, ?)
            """, (d["numero"], item["nome"], item["qtd"], item["valor"]))

        self.conexao.commit()

    def buscar_prontuario(self, animal_id):
        self.cursor.execute("""
            SELECT numero_atendimento, data_hora, veterinario, prioridade, queixa, servicos, valor_total
            FROM atendimentos WHERE animal_id = ? ORDER BY data_hora DESC, id DESC
        """, (animal_id,))
        return self.cursor.fetchall()

    def buscar_itens_atendimento(self, numero):
        self.cursor.execute(
            "SELECT produto_nome, quantidade FROM itens_atendimento WHERE numero_atendimento = ?", (numero,))
        return self.cursor.fetchall()

    def relatorio_metodo_mais_usado(self):
        self.cursor.execute("""
            SELECT forma_pagamento, COUNT(*) AS qtd FROM atendimentos
            GROUP BY forma_pagamento ORDER BY qtd DESC LIMIT 1
        """)
        return self.cursor.fetchone()

    def relatorio_faturamento_total(self):
        self.cursor.execute("SELECT SUM(valor_total) FROM atendimentos")
        resultado = self.cursor.fetchone()
        return resultado[0] if resultado[0] else 0.0

    def relatorio_ticket_medio(self):
        self.cursor.execute("SELECT AVG(valor_total) FROM atendimentos")
        resultado = self.cursor.fetchone()
        return resultado[0] if resultado[0] else 0.0

    def relatorio_principais_itens(self):
        self.cursor.execute("""
            SELECT produto_nome, SUM(quantidade) AS total FROM itens_atendimento
            GROUP BY produto_nome ORDER BY total DESC LIMIT 5
        """)
        return self.cursor.fetchall()

    def relatorio_veterinarios(self):
        self.cursor.execute("""
            SELECT veterinario, COUNT(numero_atendimento), SUM(valor_total) AS total
            FROM atendimentos GROUP BY veterinario ORDER BY total DESC
        """)
        return self.cursor.fetchall()

    def relatorio_por_prioridade(self):
        self.cursor.execute("""
            SELECT prioridade, COUNT(*), SUM(valor_total) FROM atendimentos GROUP BY prioridade
        """)
        return self.cursor.fetchall()

    def relatorio_por_especie(self):
        self.cursor.execute("""
            SELECT especie, COUNT(*), SUM(valor_total) FROM atendimentos GROUP BY especie
        """)
        return self.cursor.fetchall()

    def fechar_conexao(self):
        self.conexao.close()
