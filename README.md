# Sistema de Gestão de Clínica Veterinária

Projeto 3 da disciplina de Estrutura de Dados. O sistema simula o ciclo completo de uma clínica para cães e gatos, desde o cadastro do tutor e a triagem do animal até o pagamento do atendimento, utilizando estruturas de dados implementadas do zero em Python e persistência em Banco de Dados Relacional (SQLite).

> O projeto reaproveita a arquitetura do Projeto 2 (Oficina Mecânica) em um novo contexto: o mesmo raciocínio de estruturas de dados, agora aplicado a tutores, animais, salas de atendimento, medicamentos e vacinas.

🎥 **Vídeo de apresentação:** _(cole aqui o link do YouTube)_

## 🔄 Da Oficina para a Clínica

| Oficina Mecânica | Clínica Veterinária | Estrutura |
|---|---|---|
| Cliente + Veículos | Tutor + Animais (cão/gato) | Lista + Lista |
| Boxes | Salas de cirurgia/emergência e de consulta | Dicionário de salas |
| Fila guincho + Fila normal | Filas de triagem: Emergência, Urgente e Rotina | Fila + Fila + Fila |
| Árvore de peças do carro | Árvore de sistemas e condições do animal | Árvore N-ária |
| Estoque de peças com lotes | Estoque de medicamentos, vacinas e materiais com lotes | Dicionário + Fila de lotes |
| Undo da OS | Undo do atendimento | Pilha |
| Ordem de Serviço | Ficha de Atendimento | Classe `Atendimento` |
| Mecânico sorteado | Veterinário sorteado entre os elegíveis (especialidade e espécie) | `random` |

## 🏗️ Arquitetura e Combinações de Estruturas

Abaixo estão as justificativas de projeto, indicando as classes/métodos e a desvantagem de usar uma estrutura única.

### 1. Atendimento com Prioridade (Fila + Fila + Fila)
*   **Classes/Métodos envolvidos:** `Clinica` (`registrar_chegada`, `chamar_proximo`, `escolher_sala`), `Fila` (`enfileirar`, `desenfileirar`, `primeiro`), `triagem.classificar_prioridade`.
*   **Como funciona:** existe uma fila independente por nível de triagem: **Emergência** (atropelamento, convulsão, envenenamento, parto com complicação...), **Urgente** (machucados, fraturas, parto em andamento, vômitos...) e **Rotina** (vacina, check-up, retorno). A cada sala livre, o sistema consulta as filas na ordem Emergência → Urgente → Rotina.
*   **Justificativa:** garante prioridade absoluta para os casos graves, mas preserva a ordem de chegada (FIFO) dentro de cada nível. Enfileirar e desenfileirar custam O(1), pois a lista encadeada guarda o ponteiro do fim.
*   **Desvantagem de uma única estrutura:** uma fila única exigiria reordenar (ou inserir de forma ordenada) a cada chegada de caso grave, com custo O(n), e ainda correria o risco de quebrar a ordem de chegada entre animais do mesmo nível.

### 2. Estoque com Lotes (Dicionário de Produtos + Fila de Lotes)
*   **Classes/Métodos envolvidos:** `Estoque` (`reservar`, `cancelar_reserva`, `confirmar_baixa`), `Produto` (`baixar_fifo`, `devolver`), `Lote`.
*   **Como funciona:** os produtos ficam em um dicionário indexado pelo código (busca O(1)). Cada produto possui uma **fila de lotes** ordenada pela data de compra. A baixa percorre a fila a partir do lote mais antigo e pode atravessar mais de um lote.
*   **Justificativa:** o lote comprado primeiro é o primeiro a sair (FIFO), o que reduz vencimentos. A baixa registra de quais lotes saiu o material, para que o Undo devolva exatamente aos lotes de origem.
*   **Desvantagem de uma única estrutura:** uma lista solta de lotes exigiria varrer todos os lotes de todos os produtos para achar o mais antigo a cada baixa (O(n) sobre o estoque inteiro) e perderia o vínculo entre lote e produto.

### 3. Tutores e Animais (Lista de Tutores + Lista de Animais)
*   **Classes/Métodos envolvidos:** `CadastroTutores` (`cadastrar_tutor`, `cadastrar_animal`, `remover_tutor`, `buscar_por_cpf`), `Tutor`, `Animal`, `Lista` (`inserir`, `buscar`, `remover`).
*   **Como funciona:** uma lista encadeada de tutores, onde cada nó de tutor contém outra lista encadeada de animais. Cada animal ainda guarda uma terceira lista: a carteira de vacinação.
*   **Justificativa:** relação 1:N sem limite (um tutor pode ter zero, um ou muitos animais, e cadastrar novos ao longo dos anos). Remover um tutor remove seus animais em cascata, e a busca é feita por CPF ou por nome do animal.
*   **Desvantagem de uma única estrutura:** uma lista única de animais perderia o vínculo de quem é o tutor, e a busca dos animais de um CPF exigiria varrer toda a base. Um vetor de tamanho fixo não suportaria "sem limite de animais".

### 4. Pilha (Undo do Atendimento)
*   **Classes/Métodos envolvidos:** `Atendimento` (`desfazer_ultima_acao`), `Clinica.desfazer`, `Pilha` (`empilhar`, `desempilhar`, `espiar`).
*   **Justificativa:** permite que o veterinário desfaça o último lançamento (medicamento, vacina, material ou procedimento) do atendimento. Se for material, ele volta para a prateleira, nos lotes de onde saiu.
*   **Vantagem:** o conceito LIFO (Last In, First Out) do `desempilhar()` é O(1), perfeito para um "Ctrl+Z".

### 5. Árvore N-ária (Diagnóstico)
*   **Classes/Métodos envolvidos:** `ArvoreDiagnostico` (`percorrer_pre_ordem`, `buscar_por_codigo`, `caminho_ate`, `contem_suspeita`), `NoArvore`, `diagnostico.criar_arvore_animal`.
*   **Como funciona:** Animal → Sistema (11 sistemas: digestório, respiratório, locomotor, pele, urinário, reprodutor, neurológico, cardiovascular, trauma e emergência, olhos e ouvidos, prevenção) → Subsistema → Condição (33 condições). Cada condição é folha e aponta para os medicamentos, vacinas e materiais sugeridos. Algumas condições são exclusivas de cão (parvovirose, cinomose) ou de gato (asma felina, obstrução urinária).
*   **Justificativa:** o corpo do animal é uma hierarquia. O percurso pré-ordem exibe o diagnóstico indentado, e a busca por código é feita em profundidade.
*   **Desvantagem:** uma árvore binária não representaria a realidade (um sistema pode ter 0, 1 ou N subsistemas ou condições).

---

## 🧠 Regras de Negócio Avançadas (Diferenciais do Projeto)

### 1. Triagem Inteligente (Queixa x Prioridade)
*   Ao registrar a chegada, o sistema analisa a queixa (ex.: "atropelado", "filhote preso", "mordida") e **sugere o nível de triagem**, mostrando a palavra-chave que motivou a sugestão. A recepção aceita ou altera.

### 2. Diagnóstico Inteligente (Queixa x Árvore)
*   O método `analisar_queixa()` (em `modelos/diagnostico.py`) ignora acentos e maiúsculas, varre a queixa em busca de palavras-chave e destaca na árvore as condições prováveis com o alerta `[SUSPEITA PELA QUEIXA]` (em amarelo), já mostrando o tratamento sugerido.
*   As condições exclusivas da outra espécie são descartadas (um gato não recebe suspeita de parvovirose). A árvore pode ser exibida só com os ramos suspeitos.

### 3. Salas Preferenciais e Veterinários por Especialidade
*   As salas 0 e 1 são de cirurgia/emergência; as salas 2, 3 e 4 são de consulta. Emergências preferem as salas de cirurgia, casos de rotina só usam salas de consulta (as de cirurgia ficam livres para o que pode chegar).
*   O veterinário é sorteado entre os elegíveis para o tipo de sala e a espécie (ex.: a Dra. Beatriz atende só felinos).

### 4. Material Reservado ao Paciente
*   Quando o veterinário prescreve algo, o item **sai da prateleira (FIFO)** e fica **reservado** ao atendimento. No pagamento, a baixa vira definitiva. Se o lançamento for desfeito, o material volta aos lotes de origem. Se o sistema for encerrado com atendimentos não pagos, as reservas são devolvidas.
*   **Vantagem:** rastreabilidade exata de onde está cada item (na prateleira ou no paciente) e nenhuma venda dupla do mesmo estoque.

### 5. Controle de Vencimentos e Estoque Mínimo
*   Na abertura do sistema, uma varredura é feita: lotes vencidos são descartados e registrados como prejuízo (a custo de compra) na tabela `perdas`; produtos abaixo do mínimo geram alerta amarelo; lotes que vencem em até 60 dias geram alerta magenta de promoção, e o item sai com **20% de desconto** no orçamento.
*   Algumas vacinas são exclusivas de uma espécie (ex.: V10 só para cães), e o sistema bloqueia a prescrição errada.

### 6. Carteira de Vacinação e Prontuário
*   Toda vacina paga entra na carteira do animal com a data da próxima dose (reforço anual). Na abertura, o sistema lista **lembretes de vacinas atrasadas** para avisar os tutores.
*   A ficha do animal mostra a carteira (em dia / vence em breve / atrasada) e o prontuário com os atendimentos anteriores.

### 7. Orçamento e Tabela de Serviços
*   **Tabela de Serviços:** consultas e procedimentos são pré-cadastrados no SQLite (tabela `servicos`).
*   **Orçamento travado:** o atendimento só pode ser pago após o status mudar para `"Aguardando Aprovação"` e, em seguida, `"Aguardando Pagamento"`. Se o tutor **recusar**, o atendimento volta para `"Em Atendimento"` e o veterinário pode ajustar os lançamentos.

## 💾 Banco de Dados SQLite
O sistema utiliza a biblioteca nativa `sqlite3` para persistir os dados. O banco (`clinica.db`, criado na primeira execução) possui 9 tabelas:
1.  `produtos`: catálogo de medicamentos, vacinas e materiais.
2.  `lotes`: controle de validade e quantidade.
3.  `perdas`: histórico de prejuízos (vencimentos).
4.  `atendimentos`: histórico de atendimentos pagos (prontuário).
5.  `itens_atendimento`: itens usados em cada atendimento.
6.  `servicos`: tabela de preços de consultas e procedimentos.
7.  `tutores`: cadastro de tutores.
8.  `animais`: animais de cada tutor.
9.  `vacinas_aplicadas`: carteira de vacinação.

## 🚀 Como Executar
1.  Clone o repositório.
2.  Crie e ative o ambiente virtual (`python -m venv .venv`).
3.  Execute `python main.py`.

## 📦 Dependências e Requirements
O projeto foi construído utilizando o princípio de **"Zero Dependências Externas"** para garantir a leveza e a facilidade de execução em qualquer máquina (sem a necessidade de instalar pacotes pesados via pip).

O arquivo `requirements.txt` está presente na raiz do projeto, porém não possui bibliotecas externas listadas. As únicas bibliotecas utilizadas são nativas do Python (Standard Library):
*   `sqlite3`: persistência e manipulação do banco de dados relacional.
*   `datetime`: datas de validade dos lotes, idade dos animais e próximas doses de vacina.
*   `random`: sorteio do veterinário responsável.
*   `unicodedata`: normalização de acentos na análise da queixa.

## 📚 Guia de Execução
Para instruções detalhadas de como rodar e testar o sistema, consulte o arquivo [GUIA_EXECUCAO.md](GUIA_EXECUCAO.md).
