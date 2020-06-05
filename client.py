import socket
import _thread
import random
from time import strftime
import numpy as np
import sys
import ipaddress
#from pynput.keyboard import Key, Listener

print ('Para começar digite: \ncliente <ip> <porta>\n')

def testar_ip(ip):
    try:
        ip = ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

server_info = None
while True:
    server_info = input().split(' ')
    if server_info[0] == "cliente" and len(server_info) == 3 and testar_ip(server_info[1]):
        break
    print("Dados inválidos")

#Dados para conexao
HOST = str(server_info[1])
PORT = int(server_info[2])
Nick = 'CLIENTE'

socketConnection = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # AF_INET = IPV4, SOCK_STREAM = TCP

# Classe que define o tabuleiro do cliente (é uma matriz)
class Tabuleiro:
    
    campo = None
    campo_inimigo = None
    quantidade_a = None
    quantidade_n = None
    quantidade_c = None
    quantidade_s = None
    
    def __init__(self):
        self.campo = np.zeros(shape=(10,10), dtype=int) # Cria uma matriz 10x10 com 0 em tudo
        self.campo = self.campo.astype(str) # Mudar tipo int para string
        self.campo[self.campo == '0'] = ' ' # Trocar 0 por espaco em branco
        self.quantidade_a = 0
        self.quantidade_n = 0
        self.quantidade_c = 0
        self.quantidade_s = 0
        self.setShipsPositions() # Carregar posicoes do arquivo
        self.setEnemyField()
        
    def setEnemyField(self):
        self.campo_inimigo = np.zeros(shape=(10,10), dtype=int) # Cria uma matriz 10x10 com 0 em tudo
        self.campo_inimigo = self.campo_inimigo.astype(str) # Mudar tipo int para string
        self.campo_inimigo[self.campo_inimigo == '0'] = ' ' # Trocar 0 por espaco em branco
    
    #Get position value
    def get(self, x, y):
        return self.campo[x][y]
    
    #Set position value
    def set(self, x, y, valor):
        if valor == 'X':
            if self.campo[x][y] == 'A':
                self.quantidade_a -= 1
            elif self.campo[x][y] == 'N':
                self.quantidade_n -= 1
            elif self.campo[x][y] == 'C':
                self.quantidade_c -= 1
            elif self.campo[x][y] == 'S':
                self.quantidade_s -= 1
        self.campo[x][y] = valor
        
    #Set position value
    def setEnemy(self, x, y, valor):
        self.campo_inimigo[x][y] = valor
    
    #Inserir Porta Aviao
    def insertAircraftCarrier(self, x, y, horizontalOrVertical):
        self.set(x, y, 'A')
        self.quantidade_a += 5
        if horizontalOrVertical == 0:
            self.set(x, y + 1, 'A')
            self.set(x, y + 2, 'A')
            self.set(x, y + 3, 'A')
            self.set(x, y + 4, 'A')
        else:
            self.set(x + 1, y, 'A')
            self.set(x + 2, y, 'A')
            self.set(x + 3, y, 'A')
            self.set(x + 4, y, 'A')
    
    #Inserir Navio Tanque
    def insertTankShip(self, x, y, horizontalOrVertical):
        self.set(x, y, 'N')
        self.quantidade_n += 4
        if horizontalOrVertical == 0:
            self.set(x, y + 1, 'N')
            self.set(x, y + 2, 'N')
            self.set(x, y + 3, 'N')
        else:
            self.set(x + 1, y, 'N')
            self.set(x + 2, y, 'N')
            self.set(x + 3, y, 'N')

    #Inserir ContraTorpedeiro
    def insertDestroyer(self, x, y, horizontalOrVertical):
        self.set(x, y, 'C')
        self.quantidade_c += 3
        if horizontalOrVertical == 0:
            self.set(x, y + 1, 'C')
            self.set(x, y + 2, 'C')
        else:
            self.set(x + 1, y, 'C')
            self.set(x + 2, y, 'C')
    
    #Inserir Submarino
    def insertSub(self, x, y, horizontalOrVertical):
        self.set(x, y, 'S')
        self.quantidade_s += 2
        if horizontalOrVertical == 0:
            self.set(x, y + 1, 'S')
        else:
            self.set(x + 1, y, 'S')
    
    # Definir posicoes do cliente com base no arquivo denonimado coordenadas.txt
    def setShipsPositions(self): 
        arquivo = open("coordenadas.txt", "r")
        for x in arquivo:
            fileLine = x.replace("\n", "") # Ler linha do arquivo, removendo terminacao de linha
            line = fileLine.split(" ") # Separar a linha do arquivo por espaco
            linha = int(line[0]) # Linha do tabuleiro definida pela linha lida do arquivo
            coluna = int(line[1]) # Coluna do tabuleiro definida pela linha lida do arquivo
            horizontalOrVertical = int(line[2]) # Posicao horizontal(0) ou vertical(1) do tabuleiro definida pela linha lida do arquivo
            navio = line[3] # Tipo de navio definido no arquivo
            if navio == 'A': # A = Porta Avioes
                self.insertAircraftCarrier(linha, coluna, horizontalOrVertical)
            elif navio == 'N': # Navio Tanque
                self.insertTankShip(linha, coluna, horizontalOrVertical)
            elif navio == 'C': # Contra Torpedeiros
                self.insertDestroyer(linha, coluna, horizontalOrVertical)
            elif navio == 'S': # Submarino
                self.insertSub(linha, coluna, horizontalOrVertical)
        arquivo.close()
    
socketConnection.connect((HOST, PORT)) # Estabelecer conexao e iniciar handshake de tres vias

tabuleiro = Tabuleiro() # Inicializar o tabuleiro do cliente
print (tabuleiro.campo) # Imprimir na tela o tabuleiro do cliente

mensagem = 'StartConnection ' + Nick # Enviar para o servidor informacao para estabelecer conexao
socketConnection.sendall(mensagem.encode('utf-8'))
print("Enviado -> " + mensagem)

# Metodo para atirar no tabuleiro do servidor
def shot():
    print("Exemplo de entrada: 0,2 onde 0 = linha (x) e 2 = coluna (y)")
    teclado = str(input("Digite onde deseja atirar: ").replace(".", ","))
    local = teclado.split(',')
    linha = int(local[0])
    coluna = int(local[1])
    while (linha > 9 or linha < 0) or (coluna > 9 or coluna < 0):
        print("Entrada inválida! Tente outra vez, por favor.")
        local = str(input("Digite onde deseja atirar: ")).split(',')
        linha = int(local[0])
        coluna = int(local[1])
    print("Atirando na posição {}, {}...".format(linha, coluna))
    socketConnection.sendall("SHOT {},{}".format(linha, coluna).encode('utf-8')) # Envia a coordenada do tiro para o servidor

while True:
    try:
        data = socketConnection.recv(1024) # Recebe dados do servidor, se vazio fecha a conexao / 1024 = quantidade maxima de dados por vez
        if data:
            mensagemRecebida = data.decode('utf-8')
            if 'StartGame' in mensagemRecebida:
                print("O Jogo Começou!")
                print("Sua vez de atirar!")
                shot()
            if 'HIT' in mensagemRecebida:
                print('---')
                print("Você acertou! Sua vez novamente!")
                params = mensagemRecebida.replace('HIT ', '').split(',')
                x = int(params[0])
                y = int(params[1])
                tabuleiro.setEnemy(x,y,'X')
                print("Voce: ")
                print(tabuleiro.campo)
                print("Inimigo: ")
                print(tabuleiro.campo_inimigo)
                shot()
            if 'MISS' in mensagemRecebida:
                print('---')
                print("Você errou, rodada do oponente!")
            if 'SHOT' in mensagemRecebida:
                print('---')
                params = mensagemRecebida.replace('SHOT ', '').split(',')
                x = int(params[0])
                y = int(params[1])
                if str(tabuleiro.get(x, y)) != ' ' and str(tabuleiro.get(x, y)) != 'X':
                    tabuleiro.set(x, y, 'X')
                    print("O Servidor acertou o tiro na posição {}, {}".format(x, y))
                    print("Rodada do servidor, novamente!")
                    print(tabuleiro.campo)
                    socketConnection.sendall("HIT".encode('utf-8')) # Envia dados para o servidor informando que ele acertou um navio do cliente
                else:
                    print("Servidor errou o tiro na posicao {}, {}".format(x, y))
                    print('---')
                    print("Sua vez!")
                    socketConnection.sendall("MISS".encode('utf-8')) # Envia dados para o servidor informando que NAO acertou nenhum navio do cliente
                    shot()
            if 'END' in mensagemRecebida:
                print("Voce venceu!!")
                print('Closing connection')
                socketConnection.close()
                break
    except:
        print('Closing connection')
        socketConnection.close()
        break