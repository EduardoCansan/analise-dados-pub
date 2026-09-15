import pandas as pd
import random
import heapq

TEMPO_MAXIMO_ENTRADA = 30
QUANTIDADE_GARCONETES = 2
QUANTIDADE_COPOS = 20

# ==========================================================
# TABELAS FORNECIDAS NO ENUNCIADO
# CORRECAO: os numeros usados na simulacao devem vir dessas tabelas
# (o enunciado pede "utilize a tabela abaixo"), e nao de random.*.
# ==========================================================
TABELA_CHEGADA = [
    1, 10, 15, 6, 2, 2, 2, 1, 11, 0,
    5, 13, 6, 0, 11, 5, 1, 20, 4, 12,
    3, 2, 8, 1, 1, 3, 1, 2, 10, 5,
    5, 11, 1, 1, 20, 7, 6, 10, 4, 23,
    1, 12, 2, 7, 1, 4, 4, 1, 3, 0,
    5, 3, 2, 6,
]
TABELA_ENCHER = [
    5, 5, 6, 5, 5, 5, 6, 6, 6, 6,
    3, 5, 7, 5, 6, 6, 7, 6, 6, 7,
    6, 6, 5, 6, 6, 6, 7, 6, 7, 6,
    6, 5, 6, 6, 6, 5, 4, 4, 6, 4,
    6, 4, 6, 7, 7, 6, 6, 6, 6, 6,
    6, 6, 6, 7, 7, 7, 6, 5, 6, 6,
    5, 6, 7, 5, 6, 6, 6, 6, 6, 6,
]
TABELA_BEBER = [
    7, 7, 6, 7, 7, 8, 8, 6, 8, 8,
    8, 7, 8, 5, 8, 8, 6, 6, 5, 5,
    7, 6, 7, 8, 6, 7, 5, 5, 7, 6,
    8, 6, 5, 7, 6, 8, 7, 8, 7, 7,
    6, 8, 5, 6, 8, 6, 8, 6, 5, 5,
    8, 6, 5, 5, 5, 6, 8, 5, 8, 6,
    6, 8, 8, 5, 7,
]
TABELA_SEDE = [
    4, 2, 1, 2, 2, 1, 2, 2, 1, 2,
    4, 1, 3, 3, 4, 4, 1, 2, 4, 1,
    2, 1, 1, 2, 2, 3, 2, 1, 1, 2,
    1, 2, 4, 4, 1, 3, 2, 1, 2, 1,
    2, 4, 2, 3, 2, 4, 1, 1, 4, 3,
    4, 2, 4, 4, 3, 3, 3, 3, 3, 1,
    4, 1, 1, 1, 4, 2, 1, 1, 1, 2,
]

# Para gerar a Simulacao B depois, mude este numero (ex.: para a
# quantidade de valores que a Simulacao A consumiu de cada tabela) e
# rode o script de novo, assim as duas simulacoes nao repetem os
# mesmos numeros das tabelas.
DESLOCAMENTO_TABELAS = 0
if DESLOCAMENTO_TABELAS:
    TABELA_CHEGADA = TABELA_CHEGADA[DESLOCAMENTO_TABELAS:] + TABELA_CHEGADA[:DESLOCAMENTO_TABELAS]
    TABELA_ENCHER = TABELA_ENCHER[DESLOCAMENTO_TABELAS:] + TABELA_ENCHER[:DESLOCAMENTO_TABELAS]
    TABELA_BEBER = TABELA_BEBER[DESLOCAMENTO_TABELAS:] + TABELA_BEBER[:DESLOCAMENTO_TABELAS]
    TABELA_SEDE = TABELA_SEDE[DESLOCAMENTO_TABELAS:] + TABELA_SEDE[:DESLOCAMENTO_TABELAS]

# Indices que avancam conforme os valores das tabelas vao sendo usados.
chegada_indice = 0
encher_indice = 0
beber_indice = 0
sede_indice = 0

clientes = []
tempo_atual = 0
numero_cliente = 1

# ==========================================================
# GERAR CHEGADA DOS CLIENTES
# ==========================================================

while True:
    # CORRECAO: le da tabela de distribuicao exponencial (media 5) fornecida
    # no enunciado, em vez de sortear com random.expovariate.
    tempo_entre_chegadas = TABELA_CHEGADA[chegada_indice]
    chegada_indice += 1

    # Tempo atual é atualizado com o tempo entre chegadas do próximo cliente
    tempo_atual = tempo_atual + tempo_entre_chegadas

    # Verifica se o tempo atual para o cliente que está entrando não está ultrapassando o tempo máximo de entrada (30 minutos)
    if tempo_atual > TEMPO_MAXIMO_ENTRADA:
        break

    # CORRECAO: le da tabela de distribuicao uniforme (1 a 4) fornecida no
    # enunciado, em vez de sortear com random.randint.
    sede = TABELA_SEDE[sede_indice]
    sede_indice += 1

    # Adiciona o cliente à lista de clientes com suas informações
    clientes.append({
        "Cliente": numero_cliente,
        "Tempo entre chegadas": tempo_entre_chegadas,
        "Chegada": tempo_atual,
        "Sede": sede
    })

    # Aumenta o número do cliente para anotar quantidade de clientes que entraram no pub
    numero_cliente += 1

# ==========================================================
# SIMULACAO DOS ATENDIMENTOS
# ==========================================================
# CORRECAO: o bloco anterior (um "for cliente in []:") nunca executava,
# pois a lista estava vazia - era codigo morto de uma versao anterior do
# algoritmo. Foi removido; a simulacao de verdade e a baseada em eventos
# logo abaixo.

atendimentos = []

# ESTOQUE DE COPOS E SIMULACAO DOS ATENDIMENTOS
# ==========================================================

# Um copo e retirado do estoque limpo ao iniciar o atendimento. Ao terminar
# de beber, ele vira sujo e so retorna ao estoque quando a lavagem acaba.
COPOS_LIMPOS_INICIAIS = QUANTIDADE_COPOS  # CORRECAO: enunciado pede 20, nao 30
LIMITE_PARA_LAVAR = 2
META_DE_COPOS_LIMPOS = 10
TEMPO_LAVAR_COPO = 5

# Eventos: chegada/retorno de cliente, copo que ficou sujo ou lavagem concluida.
eventos = []
sequencia = 0
for cliente in clientes:
    heapq.heappush(eventos, (
        cliente["Chegada"], sequencia, "cliente",
        (cliente["Cliente"], cliente["Chegada"], cliente["Sede"],
         cliente["Sede"], 1)
    ))
    sequencia += 1

fila = []
copos_sujos = []
# A segunda chave desempata aleatoriamente quando as duas ficam livres juntas.
garconetes_livres = [(0, random.random(), 1), (0, random.random(), 2)]
copos_limpos = COPOS_LIMPOS_INICIAIS
modo_lavagem = False
# Mantem clientes que ja chegaram e ainda nao terminaram o ultimo drink.
clientes_no_pub = set()
# Clientes que ainda podem precisar entrar novamente na fila para outro drink.
clientes_com_pedidos_pendentes = set()
# So libera a limpeza final quando um ultimo drink termina de ser bebido e
# nenhum cliente restante podera pedir outro.
limpeza_final_autorizada = False
atendimentos = []

def adicionar_evento(tempo, tipo, dados):
    global sequencia
    heapq.heappush(eventos, (tempo, sequencia, tipo, dados))
    sequencia += 1


def processar_eventos_ate(tempo):
    global copos_limpos, limpeza_final_autorizada
    while eventos and eventos[0][0] <= tempo:
        instante, _, tipo, dados = heapq.heappop(eventos)

        if tipo == "cliente":
            cliente_id, chegada, sede_inicial, sede_atual, numero_drink = dados
            if numero_drink == 1:
                clientes_no_pub.add(cliente_id)
                clientes_com_pedidos_pendentes.add(cliente_id)
            # A chave aleatoria so e usada se dois clientes entram juntos.
            heapq.heappush(fila, (
                instante, random.random(), sequencia, cliente_id, chegada,
                sede_inicial, sede_atual, numero_drink
            ))
        elif tipo == "copo_sujo":
            atendimento, cliente_saiu = dados
            copos_sujos.append(atendimento)
            if cliente_saiu:
                clientes_no_pub.discard(atendimento["Cliente"])
                if (
                    not clientes_com_pedidos_pendentes
                    and not any(evento[2] == "cliente" for evento in eventos)
                ):
                    limpeza_final_autorizada = True
        else:  # lavagem_concluida
            copos_limpos += 1


while eventos or fila or copos_sujos:
    tempo_livre, _, garconete = heapq.heappop(garconetes_livres)
    processar_eventos_ate(tempo_livre)

    # Uma garconete ociosa aguarda o proximo evento antes de decidir a tarefa.
    if not fila and not copos_sujos and eventos:
        tempo_livre = eventos[0][0]
        processar_eventos_ate(tempo_livre)

    # CORRECAO: o enunciado pede prioridade estrita pela numeracao das
    # atividades (Encher = 2, Lavar = 4). Antes, a garconete so lavava
    # quando o estoque de copos ficava critico (<=2), o que quase nunca
    # acontecia (30 copos para poucos clientes) - por isso toda a lavagem
    # acabava empurrada para o final, em vez de intercalada com o
    # atendimento. Agora ela so lava quando NAO consegue encher agora
    # (ninguem na fila, ou sem copo limpo disponivel).
    pode_encher = bool(fila) and copos_limpos > 0
    deve_lavar = bool(copos_sujos) and not pode_encher
    if deve_lavar:
        atendimento = copos_sujos.pop(0)
        inicio_lavar = tempo_livre
        fim_lavar = inicio_lavar + TEMPO_LAVAR_COPO
        # CORRECAO: quem lava pode ser uma garconete diferente da que
        # encheu o copo - por isso a lavagem fica numa coluna propria,
        # em vez de sobrescrever "Garconete" (que registra quem encheu).
        atendimento["Garconete lavagem"] = garconete
        atendimento["Inicio lavar"] = inicio_lavar
        atendimento["Tempo lavar"] = TEMPO_LAVAR_COPO
        atendimento["Fim lavar"] = fim_lavar
        adicionar_evento(fim_lavar, "lavagem_concluida", None)
        heapq.heappush(
            garconetes_livres, (fim_lavar, random.random(), garconete)
        )
        continue

    # No modo critico, sem copo sujo para lavar, a garconete espera o proximo
    # copo terminar de ser usado; novos clientes continuam na fila.
    if modo_lavagem:
        if eventos:
            heapq.heappush(
                garconetes_livres,
                (eventos[0][0], random.random(), garconete)
            )
            continue
        break

    # Fora do modo critico, a garconete aguarda a proxima chegada. Ela nao
    # lava copos enquanto ainda houver clientes no pub.
    if not fila:
        if eventos:
            heapq.heappush(
                garconetes_livres,
                (eventos[0][0], random.random(), garconete)
            )
            continue
        break

    # Se nao ha copos limpos, aguarda uma lavagem terminar.
    if copos_limpos == 0:
        if eventos:
            heapq.heappush(
                garconetes_livres,
                (eventos[0][0], random.random(), garconete)
            )
            continue
        break

    (
        entrada_fila, _, _, cliente_id, chegada, sede_inicial,
        sede_atual, numero_drink
    ) = heapq.heappop(fila)

    inicio_encher = max(tempo_livre, entrada_fila)
    copos_limpos -= 1
    # CORRECAO: le da tabela de distribuicao normal (media 6, desvio 1)
    # fornecida no enunciado, em vez de sortear com random.gauss.
    tempo_encher = max(1, TABELA_ENCHER[encher_indice])
    encher_indice += 1
    fim_encher = inicio_encher + tempo_encher
    heapq.heappush(
        garconetes_livres, (fim_encher, random.random(), garconete)
    )

    # CORRECAO: le da tabela de distribuicao uniforme (5 a 8) fornecida no
    # enunciado, em vez de sortear com random.randint.
    tempo_beber = TABELA_BEBER[beber_indice]
    beber_indice += 1
    inicio_beber = fim_encher
    fim_beber = inicio_beber + tempo_beber
    sede_restante = sede_atual - 1
    if sede_restante == 0:
        clientes_com_pedidos_pendentes.discard(cliente_id)

    atendimento = {
        "Cliente": cliente_id,
        "Drink": numero_drink,
        "Chegada": chegada,
        "Sede inicial": sede_inicial,
        "Garconete": garconete,
        "Inicio encher": inicio_encher,
        "Tempo encher": tempo_encher,
        "Fim encher": fim_encher,
        "Inicio beber": inicio_beber,
        "Tempo beber": tempo_beber,
        "Fim beber": fim_beber,
        "Sede restante": sede_restante,
        "Garconete lavagem": None,
        "Inicio lavar": None,
        "Tempo lavar": None,
        "Fim lavar": None
    }
    atendimentos.append(atendimento)
    adicionar_evento(
        fim_beber, "copo_sujo", (atendimento, sede_restante == 0)
    )

    if sede_restante > 0:
        adicionar_evento(
            fim_beber, "cliente",
            (cliente_id, chegada, sede_inicial, sede_restante, numero_drink + 1)
        )


# ==========================================================
# DATAFRAMES
# ==========================================================

# Para facilitar a leitura da planilha, a chegada aparece somente na primeira
# linha de cada cliente. Campos de lavagem sem uma lavagem agendada ficam "-".
clientes_com_chegada_registrada = set()
for atendimento in atendimentos:
    cliente_id = atendimento["Cliente"]
    if cliente_id in clientes_com_chegada_registrada:
        atendimento["Chegada"] = "-"
    else:
        clientes_com_chegada_registrada.add(cliente_id)

    for campo_lavagem in ("Garconete lavagem", "Inicio lavar", "Tempo lavar", "Fim lavar"):
        if atendimento[campo_lavagem] is None:
            atendimento[campo_lavagem] = "-"

# Inicia o pandas DataFrame com os clientes e atendimentos
df_clientes = pd.DataFrame(clientes)
df_atendimentos = pd.DataFrame(atendimentos)

# ==========================================================
# RESULTADO POR CLIENTE
# ==========================================================

resultados = []
for cliente in clientes:
    dados_cliente = df_atendimentos[
        df_atendimentos["Cliente"] == cliente["Cliente"]
    ]

    saida = dados_cliente["Fim beber"].max()
    tempo_no_pub = saida - cliente["Chegada"]

    resultados.append({
        "Cliente": cliente["Cliente"],
        "Chegada": cliente["Chegada"],
        "Drinks": cliente["Sede"],
        "Saida": saida,
        "Tempo no Pub": tempo_no_pub
    })

# Deixa aqui o resultado total
df_resultados = pd.DataFrame(resultados)

# ==========================================================
# EXIBICAO
# ==========================================================

print("\n==========================================")
print("        CLIENTES GERADOS")
print("==========================================\n")

print(df_clientes.to_string(index=False))

print("\n\n==========================================")
print("        SIMULACAO DO PUB")
print("==========================================\n")

print(df_atendimentos.to_string(index=False))

print("\n\n==========================================")
print("        RESULTADO DOS CLIENTES")
print("==========================================\n")

print(df_resultados.to_string(index=False))

print("\n\n==========================================")
print("             ESTATISTICAS")
print("==========================================\n")

print("Total de clientes:", len(df_clientes))
print("Total de drinks:", len(df_atendimentos))

print("Media de drinks:", round(df_clientes["Sede"].mean(), 2))

print("Tempo medio no Pub:", round(df_resultados["Tempo no Pub"].mean(), 2))

print("Ultimo cliente saiu em T =", df_resultados["Saida"].max())
# ==========================================================
# GERAR ARQUIVO EXCEL
# ==========================================================

with pd.ExcelWriter("simulacao_pub.xlsx") as arquivo:

    df_clientes.to_excel(
        arquivo,
        sheet_name="Clientes",
        index=False
    )

    df_atendimentos.to_excel(
        arquivo,
        sheet_name="Simulacao",
        index=False
    )

    df_resultados.to_excel(
        arquivo,
        sheet_name="Resultados",
        index=False
    )

print("\nArquivo simulacao_pub.xlsx criado com sucesso!")