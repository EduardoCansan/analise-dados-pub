## ANALISE DE DADOS DO PUB

<b>IEDIA:</b> </br>
- A entidade é a porta cada pessoa entre 1 por vez;
- Cada pessoa que entra tem uma sede com valor (1-4);
- Cada vez que a pessoa bebe a sede diminui (sede --);
- Se sede = 0, então sai. Senão volta pra fila;
- Garçonete lava os copos
- Entrada 30 min, mas pub fecha quando todos os clientes sairem;
- Inicializa o primeiro cliente como Cliente_1 e tempo 0
- Tempo entre chegada e momento de chegada são diferentes
- O tempo das bebidas é em media de 6 minutos com desvio padrao de 1 (Então tempos variam de 5 - 6 - 7)
- Tempo de bebida entre 5 - 8 (indenpendente da quantidade)
- Tempo para lavar copo 5
- Numero variavel de bebidas (1 - 4)
- Garconete atende fila de sede e lavam copos
- Lugares infinitos no Pub (Cuidar tempo máixmo de entrada)
- 

<b>VARIÁVEIS:</b> </br>

TEMPO_MAXIMO = 30 </br>
TOTAL_TEMPO_ETRADA = 0 </br>
TOTAL_GARCONETES = 2 </br>
COPOS_LIMPOS = 30 </br>