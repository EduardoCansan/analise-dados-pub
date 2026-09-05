import pandas as pd
import random

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


for cliente in clientes:
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