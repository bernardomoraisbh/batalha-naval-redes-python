# batalha-naval-redes-python
Criar um socket TCP para realizar uma batalha naval entre servidor/cliente

Batalha Naval 
 
O principal objetivo do trabalho é praticar a programação com a biblioteca socket e usando o protocolo TCP. O trabalho consiste em desenvolver o jogo batalha naval para o paradigma cliente-servidor. Esta versão pode funcionar com apenas um cliente conectado. Você deverá criar um programa cliente e outro programa servidor. Batalha naval é um jogo de tabuleiro no qual o objetivo é afundar a frota de navios do inimigo. Inicialmente é definido um tabuleiro (matriz) de 10 x 10. Os quadrados do tabuleiro são identificados na horizontal por números e na vertical por letras. Os tabuleiros não são visíveis entre os jogadores. Os tipos de navios são, ocupando quadrados adjacentes na horizontal ou vertical: porta-aviões (cinco quadrados), navios-tanque (quatro quadrados), contratorpedeiros (três quadrados) e submarinos (dois quadrados). O número de navios são: 1, 2, 3 e 4 respectivamente. O jogo consiste em escolher um espaço do tabuleiro oponente e tentar acertar um dos navios da frota. O navio afunda quando todos quadrados forem adivinhados pelo oponente, quem perder todos os navios primeiro perde o jogo.  Os programas irão funcionar utilizando o TCP. 
 
O trabalho prático consistirá na implementação de dois programas, o cliente e o servidor. Ambos vão receber parâmetros de entrada como explicado a seguir:  
 
cliente <ip/nome> <porta>  servidor <porta>  
 
O primeiro programa, o cliente, irá conectar no servidor definido pelo endereço IP e porta passados por parâmetro. Já o servidor irá executar um serviço, que irá tratar uma conexão por vez. A porta a ser escutada é dada pelo parâmetro único do programa. 
 
O cliente irá se conectar ao servidor e o jogo irá se iniciar. O cliente deve posicionar sua frota. Isso pode ser feito lendo um arquivo de entrada. O servidor pode posicionar sua frota escolhendo aleatoriamente a posição inicial e a orientação (vertical, horizontal) dos navios.  O cliente irá enviar a posição escolhida para o tiro, que pode ser lida do teclado. O servidor irá responder se acertou ou não e também a posição do seu tiro, e assim por diante até o jogo terminar.  O servidor pode implementar a escolha da posição do tiro aleatoriamente, e se acertar, ele deve escolher um quadrado vizinho. No cliente, se pressionado a letra P, ele deve imprimir (em ASCII) seu tabuleiro e o tabuleiro com o que ele já aprendeu do servidor. 
