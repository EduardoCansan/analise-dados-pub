"""
Simulacao do Pub - GA2 (Simulacao e Modelagem de Sistemas)
Metodo das tres fases, seguindo estritamente a numeracao de prioridade das
atividades: Chega(1) < Enche(2) < Bebe(3) < Lava(4).

Correcoes em relacao a versao anterior:
  1. Os numeros aleatorios agora vem das 4 tabelas fornecidas no enunciado
     (nao mais de random.expovariate/gauss/randint), consumidas em ordem.
  2. Estoque inicial de copos = 20 (o enunciado pede 20, nao 30).
  3. O laco de simulacao segue explicitamente Fase A / Fase B / Fase C do
     metodo das tres fases, processando em bloco todos os eventos que
     terminam no mesmo instante antes de iniciar novas atividades. Isso
     elimina o bug em que uma mesma garconete aparecia lavando dois copos
     ao mesmo tempo.
  4. Removido o bloco de codigo morto (for cliente in []).
  5. O script gera as DUAS simulacoes pedidas (A e B), consumindo as
     tabelas em sequencia (B continua de onde A parou, para nao repetir
     os mesmos numeros) e calcula os indicadores pedidos no comparativo
     (tempo medio em fila, tempo ocupado/ocioso da garconete enchendo e
     lavando).
"""

import heapq
from collections import deque
import pandas as pd

# ==========================================================
# TABELAS FORNECIDAS NO ENUNCIADO (lidas na ordem em que aparecem)
# ==========================================================

TABELA_CHEGADA = [  # Distribuicao exponencial, media 5 (tempo entre chegadas)
    1, 10, 15, 6, 2, 2, 2, 1, 11, 0,
    5, 13, 6, 0, 11, 5, 1, 20, 4, 12,
    3, 2, 8, 1, 1, 3, 1, 2, 10, 5,
    5, 11, 1, 1, 20, 7, 6, 10, 4, 23,
    1, 12, 2, 7, 1, 4, 4, 1, 3, 0,
    5, 3, 2, 6,
]

TABELA_ENCHER = [  # Distribuicao normal, media 6 e desvio-padrao 1
    5, 5, 6, 5, 5, 5, 6, 6, 6, 6,
    3, 5, 7, 5, 6, 6, 7, 6, 6, 7,
    6, 6, 5, 6, 6, 6, 7, 6, 7, 6,
    6, 5, 6, 6, 6, 5, 4, 4, 6, 4,
    6, 4, 6, 7, 7, 6, 6, 6, 6, 6,
    6, 6, 6, 7, 7, 7, 6, 5, 6, 6,
    5, 6, 7, 5, 6, 6, 6, 6, 6, 6,
]

TABELA_BEBER = [  # Distribuicao uniforme, minimo 5 e maximo 8
    7, 7, 6, 7, 7, 8, 8, 6, 8, 8,
    8, 7, 8, 5, 8, 8, 6, 6, 5, 5,
    7, 6, 7, 8, 6, 7, 5, 5, 7, 6,
    8, 6, 5, 7, 6, 8, 7, 8, 7, 7,
    6, 8, 5, 6, 8, 6, 8, 6, 5, 5,
    8, 6, 5, 5, 5, 6, 8, 5, 8, 6,
    6, 8, 8, 5, 7,
]

TABELA_SEDE = [  # Distribuicao uniforme, minimo 1 e maximo 4
    4, 2, 1, 2, 2, 1, 2, 2, 1, 2,
    4, 1, 3, 3, 4, 4, 1, 2, 4, 1,
    2, 1, 1, 2, 2, 3, 2, 1, 1, 2,
    1, 2, 4, 4, 1, 3, 2, 1, 2, 1,
    2, 4, 2, 3, 2, 4, 1, 1, 4, 3,
    4, 2, 4, 4, 3, 3, 3, 3, 3, 1,
    4, 1, 1, 1, 4, 2, 1, 1, 1, 2,
]

TEMPO_MAXIMO_ENTRADA = 30
QUANTIDADE_GARCONETES = 2
COPOS_INICIAIS = 20
TEMPO_LAVAR = 5  # fixo, conforme o enunciado


class Tabela:
    """Consome valores de uma tabela na ordem, sem repetir e sem sortear."""

    def __init__(self, nome, valores, cursor_inicial=0):
        self.nome = nome
        self.valores = valores
        self.cursor = cursor_inicial

    def proximo(self):
        if self.cursor >= len(self.valores):
            raise IndexError(
                f"Tabela '{self.nome}' esgotada (precisa de mais valores "
                f"do que os {len(self.valores)} fornecidos)."
            )
        v = self.valores[self.cursor]
        self.cursor += 1
        return v


# ==========================================================
# GERACAO DOS CLIENTES (chegadas dentro dos 30 minutos)
# ==========================================================

def gerar_clientes(tabela_chegada, tabela_sede, tempo_maximo=TEMPO_MAXIMO_ENTRADA):
    clientes = []
    tempo_atual = 0
    numero_cliente = 1

    while True:
        dt = tabela_chegada.proximo()
        tempo_atual += dt
        if tempo_atual > tempo_maximo:
            break
        sede = tabela_sede.proximo()
        clientes.append({
            "Cliente": numero_cliente,
            "Tempo entre chegadas": dt,
            "Chegada": tempo_atual,
            "Sede": sede,
        })
        numero_cliente += 1

    return clientes


# ==========================================================
# SIMULACAO - METODO DAS TRES FASES
# ==========================================================

def simular_pub(clientes, tabela_encher, tabela_beber,
                 qtd_garconetes=QUANTIDADE_GARCONETES,
                 copos_iniciais=COPOS_INICIAIS):

    eventos = []  # heap: (tempo, sequencia, tipo, dados)
    seq = 0

    def agendar(tempo, tipo, dados):
        nonlocal seq
        heapq.heappush(eventos, (tempo, seq, tipo, dados))
        seq += 1

    for c in clientes:
        agendar(c["Chegada"], "chegada", {
            "cliente": c["Cliente"], "sede_inicial": c["Sede"],
            "sede_atual": c["Sede"], "drink": 1, "chegada_original": c["Chegada"],
        })

    fila_espera = deque()          # clientes prontos para Enche (fila "Espera")
    copos_limpos = copos_iniciais  # fila "Limpo"
    copos_sujos = 0                # fila "Sujo"
    garcon_ocupada = {g: False for g in range(1, qtd_garconetes + 1)}
    lavagens_pendentes = deque()   # atendimentos cujo copo ainda precisa ser lavado

    atendimentos = []
    saida_cliente = {}
    sede_inicial_por_cliente = {c["Cliente"]: c["Sede"] for c in clientes}

    def tentar_iniciar(tempo):
        """Fase C: tenta iniciar novas atividades, respeitando a prioridade
        Enche(2) antes de Lava(4), para cada garconete livre."""
        nonlocal copos_limpos, copos_sujos
        for g in range(1, qtd_garconetes + 1):
            if garcon_ocupada[g]:
                continue

            if fila_espera and copos_limpos > 0:
                cliente = fila_espera.popleft()
                copos_limpos -= 1
                garcon_ocupada[g] = True

                te = max(1, tabela_encher.proximo())
                inicio_encher, fim_encher = tempo, tempo + te
                tb = tabela_beber.proximo()
                inicio_beber, fim_beber = fim_encher, fim_encher + tb

                atendimento = {
                    "Cliente": cliente["cliente"],
                    "Drink": cliente["drink"],
                    "Chegada": cliente["chegada_original"] if cliente["chegada_original"] is not None else "-",
                    "Sede inicial": cliente["sede_inicial"],
                    "Garconete (encher)": g,
                    "Espera": tempo - cliente["entrada_fila"],
                    "Inicio encher": inicio_encher,
                    "Tempo encher": te,
                    "Fim encher": fim_encher,
                    "Inicio beber": inicio_beber,
                    "Tempo beber": tb,
                    "Fim beber": fim_beber,
                    "Sede restante": cliente["sede_atual"] - 1,
                    "Garconete (lavar)": "-",
                    "Inicio lavar": "-",
                    "Tempo lavar": "-",
                    "Fim lavar": "-",
                }
                atendimentos.append(atendimento)
                lavagens_pendentes.append(atendimento)

                agendar(fim_encher, "fim_encher", {"garconete": g})
                agendar(fim_beber, "fim_beber", {
                    "cliente": cliente["cliente"], "drink": cliente["drink"],
                    "sede_atual": cliente["sede_atual"] - 1,
                })

            elif copos_sujos > 0:
                garcon_ocupada[g] = True
                copos_sujos -= 1
                inicio_lavar, fim_lavar = tempo, tempo + TEMPO_LAVAR

                pendente = lavagens_pendentes.popleft()
                pendente["Garconete (lavar)"] = g
                pendente["Inicio lavar"] = inicio_lavar
                pendente["Tempo lavar"] = TEMPO_LAVAR
                pendente["Fim lavar"] = fim_lavar

                agendar(fim_lavar, "fim_lavar", {"garconete": g})
            # senao: garconete continua ociosa ate o proximo evento

    while eventos or fila_espera or copos_sujos:
        if not eventos:
            # nao deveria acontecer se a logica estiver correta; encerra
            # com aviso em vez de travar, para facilitar depuracao.
            print("AVISO: fila nao vazia sem eventos pendentes - verifique a logica.")
            break

        # Fase A: proximo instante de interesse
        tempo_atual = eventos[0][0]

        # Fase B: processa TODOS os eventos que terminam nesse instante
        while eventos and eventos[0][0] == tempo_atual:
            _, _, tipo, dados = heapq.heappop(eventos)

            if tipo == "chegada":
                fila_espera.append({
                    "cliente": dados["cliente"], "sede_inicial": dados["sede_inicial"],
                    "sede_atual": dados["sede_atual"], "drink": dados["drink"],
                    "chegada_original": dados["chegada_original"],
                    "entrada_fila": tempo_atual,
                })

            elif tipo == "fim_encher":
                garcon_ocupada[dados["garconete"]] = False

            elif tipo == "fim_beber":
                copos_sujos += 1
                cliente_id = dados["cliente"]
                sede_restante = dados["sede_atual"]
                if sede_restante > 0:
                    fila_espera.append({
                        "cliente": cliente_id,
                        "sede_inicial": sede_inicial_por_cliente[cliente_id],
                        "sede_atual": sede_restante, "drink": dados["drink"] + 1,
                        "chegada_original": None, "entrada_fila": tempo_atual,
                    })
                else:
                    saida_cliente[cliente_id] = tempo_atual

            elif tipo == "fim_lavar":
                copos_limpos += 1
                garcon_ocupada[dados["garconete"]] = False

        # Fase C: tenta iniciar novas atividades com o estado atualizado
        tentar_iniciar(tempo_atual)

    return atendimentos, saida_cliente


# ==========================================================
# VERIFICACAO DE SANIDADE (garante que nao ha sobreposicao de horarios)
# ==========================================================

def verificar_sem_sobreposicao(atendimentos, qtd_garconetes=QUANTIDADE_GARCONETES):
    intervalos = {g: [] for g in range(1, qtd_garconetes + 1)}
    for a in atendimentos:
        intervalos[a["Garconete (encher)"]].append((a["Inicio encher"], a["Fim encher"], "encher"))
        if a["Inicio lavar"] != "-":
            intervalos[a["Garconete (lavar)"]].append((a["Inicio lavar"], a["Fim lavar"], "lavar"))

    problemas = []
    for g, ivs in intervalos.items():
        ivs.sort(key=lambda x: x[0])
        for i in range(1, len(ivs)):
            if ivs[i][0] < ivs[i - 1][1]:
                problemas.append((g, ivs[i - 1], ivs[i]))
    return problemas


# ==========================================================
# INDICADORES (para a tabela comparativa Simula A x Simula B)
# ==========================================================

def calcular_indicadores(atendimentos, qtd_garconetes=QUANTIDADE_GARCONETES):
    horizonte = max(
        max(a["Fim lavar"] for a in atendimentos if a["Fim lavar"] != "-"),
        max(a["Fim beber"] for a in atendimentos),
    )

    esperas = [a["Espera"] for a in atendimentos]
    tempo_medio_espera = sum(esperas) / len(esperas)

    ocupado_enchendo = {g: 0 for g in range(1, qtd_garconetes + 1)}
    ocupado_lavando = {g: 0 for g in range(1, qtd_garconetes + 1)}
    for a in atendimentos:
        ocupado_enchendo[a["Garconete (encher)"]] += a["Tempo encher"]
        if a["Tempo lavar"] != "-":
            ocupado_lavando[a["Garconete (lavar)"]] += a["Tempo lavar"]

    total_enchendo = sum(ocupado_enchendo.values())
    total_lavando = sum(ocupado_lavando.values())
    total_garconete_tempo = horizonte * qtd_garconetes

    return {
        "Tempo medio em fila (ESPERA)": round(tempo_medio_espera, 2),
        "Tempo do operador ocupado (ENCHENDO)": total_enchendo,
        "Taxa de ocupacao da GARCONETE (ENCHENDO)": round(total_enchendo / total_garconete_tempo, 3),
        "Taxa de ociosidade da GARCONETE (ENCHENDO)": round(1 - total_enchendo / total_garconete_tempo, 3),
        "Tempo do operador ocupado (LAVANDO)": total_lavando,
        "Taxa de ocupacao da GARCONETE (LAVANDO)": round(total_lavando / total_garconete_tempo, 3),
        "Taxa de ociosidade da GARCONETE (LAVANDO)": round(1 - total_lavando / total_garconete_tempo, 3),
        "Horizonte da simulacao (T)": horizonte,
        "Ocupado enchendo por garconete": ocupado_enchendo,
        "Ocupado lavando por garconete": ocupado_lavando,
    }


# ==========================================================
# EXECUCAO: GERA SIMULACAO A e SIMULACAO B
# ==========================================================

def rodar_simulacao_completa(nome, tabela_chegada, tabela_encher, tabela_beber, tabela_sede):
    clientes = gerar_clientes(tabela_chegada, tabela_sede)
    atendimentos, saida_cliente = simular_pub(clientes, tabela_encher, tabela_beber)

    problemas = verificar_sem_sobreposicao(atendimentos)
    if problemas:
        print(f"[{nome}] ATENCAO: sobreposicao de horario encontrada:")
        for g, iv1, iv2 in problemas:
            print(f"   garconete {g}: {iv1} colide com {iv2}")
    else:
        print(f"[{nome}] OK: nenhuma garconete tem atividades sobrepostas.")

    resultados = []
    for c in clientes:
        saida = saida_cliente.get(c["Cliente"])
        resultados.append({
            "Cliente": c["Cliente"],
            "Chegada": c["Chegada"],
            "Drinks": c["Sede"],
            "Saida": saida,
            "Tempo no Pub": (saida - c["Chegada"]) if saida is not None else None,
        })

    indicadores = calcular_indicadores(atendimentos)

    df_clientes = pd.DataFrame(clientes)
    df_atendimentos = pd.DataFrame(atendimentos)
    df_resultados = pd.DataFrame(resultados)

    print(f"\n===== {nome} =====")
    print(df_clientes.to_string(index=False))
    print()
    print(df_atendimentos.to_string(index=False))
    print()
    print(df_resultados.to_string(index=False))
    print()
    for k, v in indicadores.items():
        print(f"{k}: {v}")

    return df_clientes, df_atendimentos, df_resultados, indicadores


if __name__ == "__main__":
    # Cursores compartilhados entre A e B: a Simulacao B continua consumindo
    # as tabelas de onde a Simulacao A parou, para nao repetir os mesmos
    # numeros nas duas simulacoes.
    tabela_chegada = Tabela("chegada (exponencial)", TABELA_CHEGADA)
    tabela_encher = Tabela("encher (normal)", TABELA_ENCHER)
    tabela_beber = Tabela("beber (uniforme 5-8)", TABELA_BEBER)
    tabela_sede = Tabela("sede (uniforme 1-4)", TABELA_SEDE)

    resultado_a = rodar_simulacao_completa(
        "SIMULACAO A", tabela_chegada, tabela_encher, tabela_beber, tabela_sede
    )
    resultado_b = rodar_simulacao_completa(
        "SIMULACAO B", tabela_chegada, tabela_encher, tabela_beber, tabela_sede
    )

    (df_clientes_a, df_atend_a, df_result_a, ind_a) = resultado_a
    (df_clientes_b, df_atend_b, df_result_b, ind_b) = resultado_b

    df_indicadores = pd.DataFrame([
        {"Indicador": "Tempo medio em fila (ESPERA)",
         "Simula A": ind_a["Tempo medio em fila (ESPERA)"],
         "Simula B": ind_b["Tempo medio em fila (ESPERA)"]},
        {"Indicador": "Tempo do operador (GARCONETE) ocupado (ENCHENDO)",
         "Simula A": ind_a["Tempo do operador ocupado (ENCHENDO)"],
         "Simula B": ind_b["Tempo do operador ocupado (ENCHENDO)"]},
        {"Indicador": "Taxa de ocupacao da GARCONETE (ENCHENDO)",
         "Simula A": ind_a["Taxa de ocupacao da GARCONETE (ENCHENDO)"],
         "Simula B": ind_b["Taxa de ocupacao da GARCONETE (ENCHENDO)"]},
        {"Indicador": "Taxa de ociosidade da GARCONETE (ENCHENDO)",
         "Simula A": ind_a["Taxa de ociosidade da GARCONETE (ENCHENDO)"],
         "Simula B": ind_b["Taxa de ociosidade da GARCONETE (ENCHENDO)"]},
        {"Indicador": "Tempo do operador (GARCONETE) ocupado (LAVANDO)",
         "Simula A": ind_a["Tempo do operador ocupado (LAVANDO)"],
         "Simula B": ind_b["Tempo do operador ocupado (LAVANDO)"]},
        {"Indicador": "Taxa de ocupacao da GARCONETE (LAVANDO)",
         "Simula A": ind_a["Taxa de ocupacao da GARCONETE (LAVANDO)"],
         "Simula B": ind_b["Taxa de ocupacao da GARCONETE (LAVANDO)"]},
        {"Indicador": "Taxa de ociosidade da GARCONETE (LAVANDO)",
         "Simula A": ind_a["Taxa de ociosidade da GARCONETE (LAVANDO)"],
         "Simula B": ind_b["Taxa de ociosidade da GARCONETE (LAVANDO)"]},
    ])

    with pd.ExcelWriter("simulacao_pub_A_B.xlsx") as arquivo:
        df_clientes_a.to_excel(arquivo, sheet_name="Clientes_A", index=False)
        df_atend_a.to_excel(arquivo, sheet_name="Simulacao_A", index=False)
        df_result_a.to_excel(arquivo, sheet_name="Resultados_A", index=False)

        df_clientes_b.to_excel(arquivo, sheet_name="Clientes_B", index=False)
        df_atend_b.to_excel(arquivo, sheet_name="Simulacao_B", index=False)
        df_result_b.to_excel(arquivo, sheet_name="Resultados_B", index=False)

        df_indicadores.to_excel(arquivo, sheet_name="Indicadores", index=False)

    print("\nArquivo simulacao_pub_A_B.xlsx criado com sucesso!")