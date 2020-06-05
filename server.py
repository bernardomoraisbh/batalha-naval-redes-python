import socket
import _thread
import random
from time import strftime
import numpy as np
import sys

print ('Para começar digite: \nservidor <porta>\n')

server_info = None
while True:
    server_info = input().split(' ')
    if server_info[0] == "servidor" and len(server_info) == 2 and server_info[1].isdigit():
        break
    print("Dados inválidos")

#Dados para escutar conexoes
HOST = ''
PORT = int(server_info[1])

clientesConectados = []
tabuleiro = None

socketConnection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Retornar Horario do Servidor
def getTime():
    return strftime("%d/%m/%Y %H:%M:%S")

# Classe que define um cliente do servidor
class Cliente:
    def __init__(self, nome, conexao, clientaddress):
        self.nome = nome
        self.conexao = conexao
        self.cliente = clientaddress

    def getNomeCliente(self):
        return self.nome

    def getConexaoCliente(self):
        return self.conexao

    def getCliente(self):
        return self.cliente

# Classe que define o tabuleiro do servidor (é uma matriz)
class Tabuleiro:
    
    campo = None
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
        self.setShipsPositions()
    
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
    
    #Checar se posicao gerada é valida
    def checkPosition(self, cord_x, y, horizontalOrVertical, numPos):
        isPositionValid = True
        if horizontalOrVertical == 0:
            for x in range(y, y + numPos, 1):
                if self.get(cord_x, x) != ' ':
                    isPositionValid = False
            return isPositionValid
        else:
            for x in range(cord_x, cord_x + numPos, 1):
                if self.get(x, y) != ' ':
                    isPositionValid = False
            return isPositionValid
    
    #Gerar uma posicao(x,y,orientacao) aleatoria
    def pickPos(self, x):
        linha = random.randint(0, 9)
        coluna = random.randint(0, 9)
        horizontalOrVertical = random.randint(0, 1)
        if horizontalOrVertical == 0:
            while (coluna + x) > 9:
                coluna = random.randint(0, 10)
        else:
            while (linha + x) > 9:
                linha = random.randint(0, 10)
        return linha, coluna, horizontalOrVertical
    
    # Definir posicoes do tabuleiro do servidor aleatoriamente
    def setShipsPositions(self):
        shipNumbers = 1
        for x in range(4, 0, -1):
            for y in range(1, shipNumbers + 1, 1):
                linha, coluna, horizontalOrVertical = self.pickPos(x)
                while not self.checkPosition(linha, coluna, horizontalOrVertical, x + 1):
                    linha, coluna, horizontalOrVertical = self.pickPos(x)
                if x == 1:
                    self.insertSub(linha, coluna, horizontalOrVertical)
                elif x == 2:
                    self.insertDestroyer(linha, coluna, horizontalOrVertical)
                elif x == 3:
                    self.insertTankShip(linha, coluna, horizontalOrVertical)
                elif x == 4:
                    self.insertAircraftCarrier(linha, coluna, horizontalOrVertical)
            shipNumbers = shipNumbers + 1

# Servidor informa o cliente que atirou na posicao x,y (o server escolha uma posicao de forma aleatoria)
def shot(conexao):
    x = random.randint(0, 9)
    y = random.randint(0, 9)
    print("Atirando na posição {}, {}...".format(x, y))
    conexao.sendall("SHOT {},{}".format(x, y).encode('utf-8'))

# Estabelece a `partida` entre cliente e servidor
def startGame(client):
    clientName = client.getNomeCliente()
    conexaoCliente = client.getConexaoCliente()
    
    print('{}: Server conectado por {}'.format(getTime(), clientName))

    # Game start!
    conexaoCliente.sendall('StartGame'.encode('utf-8'))
    print("O Jogo Começou!")

    while True:
        try:
            mensagem = conexaoCliente.recv(1024)
            mensagem = mensagem.decode('utf-8')
            #Se mensagem vazia, finaliza conexao
            if not mensagem:
                print('{}: Cliente {} finalizou a conexão.'.format(getTime(), clientName))
                clientesConectados.remove(client)
                for p in clientesConectados:
                    p.getConexaoCliente().sendall('Cliente {} desconectou-se!'.format(clientName).encode('utf-8'))
                break
            #Mostrar mensagem recebida
            print('{}: Cliente {} enviou -> {}'.format(getTime(), clientName, mensagem))
            #Se mensagem SHOT, servidor recebe o tiro do cliente
            if "SHOT" in mensagem:
                params = mensagem.replace('SHOT ', '').split(',')
                x = int(params[0])
                y = int(params[1])
                if str(tabuleiro.get(x, y)) != ' ' and str(tabuleiro.get(x, y)) != 'X':
                    tabuleiro.set(x, y, 'X')
                    print("{} acertou o tiro na posição {}, {}".format(clientName,x, y))
                    print("Rodada do Cliente, novamente!")
                    if (tabuleiro.quantidade_a == 0 and tabuleiro.quantidade_n == 0 and tabuleiro.quantidade_c == 0 and tabuleiro.quantidade_s == 0 ):
                        conexaoCliente.sendall("END".encode('utf-8'))
                        break
                    print( str(tabuleiro.quantidade_a) + " "  + str(tabuleiro.quantidade_n) + " " + str(tabuleiro.quantidade_c) + " "  + str(tabuleiro.quantidade_s) )
                    conexaoCliente.sendall("HIT {},{}".format(x, y).encode('utf-8'))
                else:
                    print("{} errou o tiro na posição {}, {}".format(clientName,x, y))
                    print("Rodada do Servidor!")
                    conexaoCliente.sendall("MISS".encode('utf-8'))
                    shot(conexaoCliente)
            #Se mensagem HIT servidor acertou o cliente
            if "HIT" in mensagem:
                print("Você acertou! Sua vez novamente!")
                shot(conexaoCliente)
            #Se mensagem MISS, servidor errou o cliente e passa a vez
            if "MISS" in mensagem:
                print("Você errou, rodada do oponente!")
            print(tabuleiro.campo) # Mostrar estado do campo de batalha
        except Exception as e:
            print('{}: Ocorreu um erro na conexão com o cliente {}.'.format(getTime(), clientName))
            print('Erro : ' + str(e))
            clientesConectados.remove(client)
            for p in clientesConectados:
                p.getConexaoCliente().sendall('Cliente {} desconectou-se!'.format(clientName).encode('utf-8'))
            break

    print('Finalizando conexão com', clientName)
    conexaoCliente.close()
    _thread.exit()

socketConnection.bind((HOST, PORT))        # Associar o socket s com a rede especificada 
socketConnection.listen(1)                 # Abilita o servidor a receber 1 conexao por vez

# Sempre que o servidor receber uma nova conexao cria uma thread para o cliente que se conectou:
def startConnection():
    while True:
        conn, cliente = socketConnection.accept()   # .accept() retorna um novo objeto do tipo socket e o endereco do cliente (host:port)
        msg = conn.recv(1024).decode('utf-8') # .recv() recebe a mensagem enviada pelo cliente na conexao (con)
        print('Connected by', cliente)
        print("MensagemRecebida = " + msg)
        if 'StartConnection' in msg:
            #Inicializar e exibir tabuleiro do servidor
            global tabuleiro 
            tabuleiro = Tabuleiro()
            print(tabuleiro.campo)
                
            #Criar novo cliente com o socket da conexao ativa
            clienteNovo = Cliente(msg.split(' ', 1)[1], conn, cliente)
            clientesConectados.append(clienteNovo)
            for x in clientesConectados:
                x.getConexaoCliente().sendall('Cliente {} conectado!'.format(clienteNovo.getNomeCliente()).encode('utf-8'))
            _thread.start_new_thread(startGame, tuple([clienteNovo]))
        else:
            print('Cliente {} desatualizado!'.format(cliente[1]))
            conn.sendall('Seu cliente está desatualizado! Favor atualizar e tentar novamente!'.encode('utf-8'))
            conn.close()
            print('Conexão com cliente {} finalizada'.format(cliente[1]))

startConnection()

# o novo socket recebido pelo accept é o que usaremos para comunicar com o cliente, é diferente do socket que escuta para receber novas conexões 
# o loop infinito le qualquer dado que o cliente envia e responde com .sendall()
# se conn.recv() retorna um objeto byte vazio, o cliente fecha a conexao e o loop infinito termina,
# with conn "metodo" automaticamente fecha o socket no final do bloco
# .accept() # return new socket object and a tuple with address of client (host port)
