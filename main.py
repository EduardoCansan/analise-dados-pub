import pandas as pd
import random
import heapq

TEMPO_MAXIMO_ENTRADA = 30
QUANTIDADE_GARCONETES = 2
QUANTIDADE_COPOS = 20

clientes = []
tempo_atual = 0
numero_cliente = 1

# ==========================================================
# GERAR CHEGADA DOS CLIENTES
# ==========================================================

while True:
    # Exponencial com média de 5 minutos (vária de 4 - 5 - 6 minutos)
    tempo_entre_chegadas = round(random.expovariate(1 / 5))

    # Tempo atual é atualizado com o tempo entre chegadas do próximo cliente
    tempo_atual = tempo_atual + tempo_entre_chegadas

    # Verifica se o tempo atual para o cliente que está entrando não está ultrapassando o tempo máximo de entrada (30 minutos)
    if tempo_atual > TEMPO_MAXIMO_ENTRADA:
        break

    # Quantidade de drinks entre 1 e 4
    sede = random.randint(1, 4)

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

# Mantem a quantidade de atendentes para saber quando cada um estará livre para atender o próximo cliente
atendimentos = []
garconete_1_livre = 0
garconete_2_livre = 0

for cliente in []:
    cliente_id = cliente["Cliente"]
    chegada = cliente["Chegada"]
    sede_inicial = cliente["Sede"]

    sede = sede_inicial
    tempo_cliente = chegada
    numero_drink = 1

    while sede > 0:
        # Escolhe a garçonete que ficará livre primeiro
        if garconete_1_livre <= garconete_2_livre:
            garconete = 1
            tempo_livre = garconete_1_livre
        else:
            garconete = 2
            tempo_livre = garconete_2_livre

        # Cliente começa a ser atendido quando ele
        # e a garçonete estiverem disponíveis
        inicio_encher = max(tempo_cliente, tempo_livre)

        # Normal com média 6 e desvio padrão 1 (mesma coisa com a entrada varia entre 5, 6 e 7 minutos)
        tempo_encher = round(random.gauss(6, 1))

        if tempo_encher < 1:
            tempo_encher = 1

        fim_encher = inicio_encher + tempo_encher

        # Atualiza disponibilidade da garçonete novamente
        if garconete == 1:
            garconete_1_livre = fim_encher
        else:
            garconete_2_livre = fim_encher

        # Uniforme entre 5 e 8 minutos (mesma coisa  das vezes anteriores, idenpendete da quantidade de drinks isso)
        tempo_beber = random.randint(5, 8)

        inicio_beber = fim_encher
        fim_beber = inicio_beber + tempo_beber

        # Cliente consumiu um drink
        sede = sede - 1

        # Lavagem fixa em 5 minutos (não varia, independente da quantidade de drinks), bom que tem vários copos na fila (20)
        tempo_lavar = 5

        inicio_lavar = fim_beber
        fim_lavar = inicio_lavar + tempo_lavar

        # Aqui é verificado o atendimento e a passagem do cliente pelo pub
        atendimentos.append({
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
            "Sede restante": sede,
            "Inicio lavar": inicio_lavar,
            "Tempo lavar": tempo_lavar,
            "Fim lavar": fim_lavar
        })

        # Se ainda tem sede, volta para atendimento
        if sede > 0:
            tempo_cliente = fim_beber

        numero_drink += 1


# ESTOQUE DE COPOS E SIMULACAO DOS ATENDIMENTOS
# ==========================================================

# Um copo e retirado do estoque limpo ao iniciar o atendimento. Ao terminar
# de beber, ele vira sujo e so retorna ao estoque quando a lavagem acaba.
COPOS_LIMPOS_INICIAIS = 30
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
garconetes_livres = [(0, 1), (0, 2)]
copos_limpos = COPOS_LIMPOS_INICIAIS
modo_lavagem = False
atendimentos = []

def adicionar_evento(tempo, tipo, dados):
    global sequencia
    heapq.heappush(eventos, (tempo, sequencia, tipo, dados))
    sequencia += 1


def processar_eventos_ate(tempo):
    global copos_limpos
    while eventos and eventos[0][0] <= tempo:
        instante, _, tipo, dados = heapq.heappop(eventos)

        if tipo == "cliente":
            cliente_id, chegada, sede_inicial, sede_atual, numero_drink = dados
            # A chave aleatoria so e usada se dois clientes entram juntos.
            heapq.heappush(fila, (
                instante, random.random(), sequencia, cliente_id, chegada,
                sede_inicial, sede_atual, numero_drink
            ))
        elif tipo == "copo_sujo":
            copos_sujos.append(dados)
        else:  # lavagem_concluida
            copos_limpos += 1


while eventos or fila or copos_sujos:
    tempo_livre, garconete = heapq.heappop(garconetes_livres)
    processar_eventos_ate(tempo_livre)

    # Uma garconete ociosa aguarda o proximo evento antes de decidir a tarefa.
    if not fila and not copos_sujos and eventos:
        tempo_livre = eventos[0][0]
        processar_eventos_ate(tempo_livre)

    if copos_limpos <= LIMITE_PARA_LAVAR:
        modo_lavagem = True
    elif copos_limpos >= META_DE_COPOS_LIMPOS:
        modo_lavagem = False

    # Depois que nao ha mais clientes (na fila, bebendo ou para chegar), a
    # simulacao entra na limpeza final e lava todos os copos utilizados.
    limpeza_final = (
        not fila
        and not any(evento[2] == "cliente" for evento in eventos)
    )

    # Durante o funcionamento, lavar so ocorre no estoque critico. No fim,
    # todos os copos sujos sao lavados, independentemente do estoque limpo.
    deve_lavar = copos_sujos and (modo_lavagem or limpeza_final)
    if deve_lavar:
        atendimento = copos_sujos.pop(0)
        inicio_lavar = tempo_livre
        fim_lavar = inicio_lavar + TEMPO_LAVAR_COPO
        atendimento["Inicio lavar"] = inicio_lavar
        atendimento["Tempo lavar"] = TEMPO_LAVAR_COPO
        atendimento["Fim lavar"] = fim_lavar
        adicionar_evento(fim_lavar, "lavagem_concluida", None)
        heapq.heappush(garconetes_livres, (fim_lavar, garconete))
        continue

    # No modo critico, sem copo sujo para lavar, a garconete espera o proximo
    # copo terminar de ser usado; novos clientes continuam na fila.
    if modo_lavagem:
        if eventos:
            heapq.heappush(garconetes_livres, (eventos[0][0], garconete))
            continue
        break

    # Fora do modo critico, a garconete aguarda a proxima chegada. Ela nao
    # lava copos enquanto ainda houver clientes no pub.
    if not fila:
        if eventos:
            heapq.heappush(garconetes_livres, (eventos[0][0], garconete))
            continue
        break

    # Se nao ha copos limpos, aguarda uma lavagem terminar.
    if copos_limpos == 0:
        if eventos:
            heapq.heappush(garconetes_livres, (eventos[0][0], garconete))
            continue
        break

    (
        entrada_fila, _, _, cliente_id, chegada, sede_inicial,
        sede_atual, numero_drink
    ) = heapq.heappop(fila)

    inicio_encher = max(tempo_livre, entrada_fila)
    copos_limpos -= 1
    tempo_encher = max(1, round(random.gauss(6, 1)))
    fim_encher = inicio_encher + tempo_encher
    heapq.heappush(garconetes_livres, (fim_encher, garconete))

    tempo_beber = random.randint(5, 8)
    inicio_beber = fim_encher
    fim_beber = inicio_beber + tempo_beber
    sede_restante = sede_atual - 1

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
        "Inicio lavar": None,
        "Tempo lavar": None,
        "Fim lavar": None
    }
    atendimentos.append(atendimento)
    adicionar_evento(fim_beber, "copo_sujo", atendimento)

    if sede_restante > 0:
        adicionar_evento(
            fim_beber, "cliente",
            (cliente_id, chegada, sede_inicial, sede_restante, numero_drink + 1)
        )


# ==========================================================
# DATAFRAMES
# ==========================================================

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
