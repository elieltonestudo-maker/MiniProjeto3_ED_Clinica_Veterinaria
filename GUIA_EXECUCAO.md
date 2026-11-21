# 🚀 Guia de Execução - Sistema de Clínica Veterinária

Este documento descreve o passo a passo para executar e testar o sistema.

## 🛠️ Pré-requisitos
*   Python 3.8 ou superior instalado.
*   VS Code (ou qualquer editor de texto).
*   Git (opcional, para clonar o repositório).

## 📥 1. Preparação do Ambiente

1. Clone o repositório ou baixe os arquivos.
2. Abra o terminal na pasta raiz do projeto.
3. Crie o ambiente virtual:
   `python -m venv .venv`
4. Ative o ambiente virtual:
   - **Windows (PowerShell):** `.venv\Scripts\Activate.ps1`
   - **Windows (CMD):** `.venv\Scripts\activate.bat`
   - **Mac/Linux:** `source .venv/bin/activate`
5. (Opcional) Verifique as dependências:
   `pip install -r requirements.txt`

## 🏃 2. Executando o Sistema

Com o ambiente ativado, execute:
`python main.py`

Na primeira execução o arquivo `clinica.db` é criado e populado com o catálogo, os tutores e os animais de demonstração. Para recomeçar do zero, apague o `clinica.db`.

## 🧪 3. Roteiro de Teste (Passo a Passo)

Ao iniciar, o sistema mostra os alertas de estoque (lote vencido descartado, estoque mínimo, promoção) e os lembretes de vacinas atrasadas. Depois, 8 animais chegam e passam pela triagem automática: **Bolt** (atropelado) e **Luna** (parto com filhote preso) são Emergência, furam a fila e já ocupam as salas de cirurgia 0 e 1 (atendimentos 1000 e 1001). Siga os passos:

1. **Ver filas e salas:**
   Digite `18` (Painel de Controle). Veja as três filas (Emergência, Urgente e Rotina) e o mapa das salas.
2. **Chamar os pacientes da fila:**
   Digite `6` três vezes. **Mingau** (emergência, gato) vai para a Sala 2 (atendimento 1002), **Thor** para a Sala 3 (1003) e **Rex** para a Sala 4 (1004). Uma quarta chamada informa que não há sala disponível.
3. **Ver o Diagnóstico Inteligente:**
   Digite `7` e informe o atendimento `1002` (Mingau). Veja a árvore apontar as condições urinárias suspeitas pela queixa e o tratamento sugerido. Responda `N` para ver só os ramos suspeitos, ou `S` para a árvore completa.
4. **Prescrever e lançar procedimentos:**
   Digite `8` (atendimento `1003`, código `V001`, quantidade `1`) e de novo `8` (código `V002`, quantidade `1`). A V10 sai com **20% de desconto**, pois o lote mais antigo está perto de vencer.
   Digite `9` (atendimento `1002`, código `S002`).
   Teste a regra de espécie: `8` no atendimento `1003` com o código `V003` (vacina de gatos) é bloqueado.
5. **Testar o Undo:**
   Digite `14` e informe `1002` para desfazer o último lançamento. Em `15` veja o material reservado; ao desfazer um item, ele volta para a prateleira, ao lote de origem.
6. **Gerar e aprovar orçamento:**
   Digite `10` e informe `1003`. Veja o valor total.
   Digite `11` e aprove. (Se responder `N`, o atendimento volta para ajustes.)
7. **Liberar sala e pagar:**
   Digite `12` e libere a Sala `3`.
   Digite `13`, pague o atendimento `1003` com PIX. As vacinas entram na carteira do Thor.
8. **Ver a ficha do animal:**
   Digite `19`, CPF `11111111111`, animal `1` (Thor). Veja a carteira de vacinação atualizada e o prontuário.
9. **Cadastrar e atender um novo paciente:**
   Digite `1` para cadastrar um tutor (e um animal) e `5` para registrar a chegada. Teste queixas diferentes ("convulsão", "vacina anual", "coceira") e veja a triagem sugerida.
10. **Ver estoque e relatórios:**
    Digite `16` e depois `5` para ver cada produto com a fila de lotes na ordem FIFO.
    Digite `17` e veja faturamento, ticket médio, ranking de itens, desempenho dos veterinários e atendimentos por prioridade e espécie.

## 📚 Dados de demonstração

| CPF | Tutor | Animais |
|---|---|---|
| 11111111111 | Gabriel Souza | Thor (cão), Mel (gato) |
| 22222222222 | Elielton Lima | Bolt (cão) |
| 33333333333 | Jaime Barbosa | Nina (gato), Toco (cão) |
| 44444444444 | Ana Costa | Pipoca (cão) |
| 55555555555 | Roberto Alves | Rex (cão) |
| 66666666666 | Fernanda Rocha | Luna (cão) |
| 77777777777 | Lucas Martins | Mingau (gato) |
| 88888888888 | Mariana Dias | Frajola (gato) |

> Observação: o veterinário responsável é sorteado a cada atendimento, então o nome pode variar entre execuções.
