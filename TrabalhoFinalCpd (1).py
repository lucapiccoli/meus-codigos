import csv
from prettytable import PrettyTable
import os
# ;;;;;;;;;;;;;;;;;;;;;;;; VARIAVEIS ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
TAMANHO_TABELA_TAG = 151
TAMANHO_TABELA_HASH_USUARIOS = 130000  # 138000 300001  usuarios
TAMANHO_TABELA_HASH = 3461
tabela_hash_jogadores = [[] for _ in range(TAMANHO_TABELA_HASH)]
tabela_hash_usuarios = [[] for _ in range(TAMANHO_TABELA_HASH_USUARIOS)]

lista_tag = [[] for _ in range(TAMANHO_TABELA_TAG)]
lista_nome_jogadores = []
i = 0


# ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;OBJETOS;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
class Usuario():
    def __init__(self, id):
        self.id = id
        self.votos = []


class TrieNode:
    def __init__(self):
        self.children = {}
        self.ids = []


arvore = TrieNode()


class Tag():
    def __init__(self, nome):
        self.nome = nome
        self.listaJogadores = []


class Jogador():
    def __init__(self, id, shortName, longName, posicoes, nacionalidade, time, liga, soma, revisoes, media, personal_rating):
        self.id = id
        self.shortName = shortName
        self.longName = longName
        self.posicoes = posicoes
        self.nacionalidade = nacionalidade
        self.time = time
        self.liga = liga
        self.soma = soma
        self.revisoes = revisoes
        self.media = media
        self.personal_rating = personal_rating

# ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;FUNCOES;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;


def limpar_terminal():
    # Verifica se o sistema operacional é Windows
    if os.name == 'nt':
        _ = os.system('cls')
    else:
        _ = os.system('clear')


def calcular_hash(id, tamanho):

    return id % tamanho


# ;;;;;;;;;;;;;;;;;;;;;;;;;;; JOGADORES ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

def pesquisaJogadores(lista):
    i = 0
    lista_aux = []
    for voto in lista:
        if i >= 20:
            break
        index_aux = calcular_hash(voto[0], TAMANHO_TABELA_HASH)
        for jogadores in tabela_hash_jogadores[index_aux]:
            if voto[0] == jogadores.id:

                jogadores.personal_rating = voto[1]
                media = jogadores.soma/jogadores.revisoes
                jogadores.media = media
                lista_aux.append(jogadores)
                i += 1
                break

    lista_ordenada = sorted(lista_aux, key=lambda x: x.media, reverse=True)
    for jogadores in lista_ordenada:
        jogadores.media = round(jogadores.media, 4)

    printa_tabela(lista_ordenada)


def processa_jogadores(tabela_hash):
    with open("players.csv", newline="") as playersFile:

        reader = csv.DictReader(playersFile)

        for linha in reader:
            id = int(linha["sofifa_id"])
            short_name = linha["short_name"]
            long_name = linha["long_name"]
            posicoes = linha["player_positions"]
            nationality = linha["nationality"]
            club_name = linha["club_name"]
            league_name = linha["league_name"]

            aux_player = Jogador(
                id, short_name, long_name, posicoes, nationality, club_name, league_name, 0, 0, 0, 0)

            aux_index = calcular_hash(id, TAMANHO_TABELA_HASH)

            tabela_hash[aux_index].append(aux_player)


# ;;;;;;;;;;;;;;;;;;;;;;;;;;;; ARVORE ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

def search(root, prefix):
    node = root
    for char in prefix:
        if char not in node.children:
            return []
        node = node.children[char]
    return node.ids


def insert(root, word, player_id):
    node = root
    for char in word:
        if char not in node.children:
            node.children[char] = TrieNode()
        node = node.children[char]
        node.ids.append(player_id)


def cria_arvore(arvore):
    for player in lista_nome_jogadores:
        name, player_id = player
        insert(arvore, name, player_id)


def printa_jogadores_id(lista):
    lista_aux = []
    for id in lista:
        index_aux = calcular_hash(id, TAMANHO_TABELA_HASH)
        for jogador in tabela_hash_jogadores[index_aux]:
            if id == jogador.id:
                if jogador.revisoes != 0:
                    jogador.media = jogador.soma / jogador.revisoes
                    lista_aux.append(jogador)

    lista_ordenada_posicao = sorted(
        lista_aux, key=lambda x: x.media, reverse=True)
    for jogadores in lista_aux:
        jogadores.media = round(jogadores.media, 6)

    printa_tabela_prefixo(lista_ordenada_posicao)


# ;;;;;;;;;;;;;;;;;;;;;;;;;;; RATING;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
def putRating(id, rating, tabela_hash):

    index_aux = calcular_hash(id, TAMANHO_TABELA_HASH)

    for jogador in tabela_hash[index_aux]:

        if jogador.id == id:
            jogador.soma += rating
            jogador.revisoes += 1
            break


def processa_avaliacao(tabela_hash, tabela_hash_usuarios):
    with open("rating.csv", newline="") as ratingFile:

        readerRating = csv.DictReader(ratingFile)

        for linha in readerRating:

            id_user = int(linha["user_id"])
            id_jogador = int(linha["sofifa_id"])
            rating = float(linha["rating"])
            processa_usuario(tabela_hash_usuarios, id_user, id_jogador, rating)
            putRating(id_jogador, rating, tabela_hash)


# ;;;;;;;;;;;;;;;;;; USUARIO ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;


def buscaUsuario(lista, id_user):
    index_aux = calcular_hash(id_user, TAMANHO_TABELA_HASH_USUARIOS)
    for usuarios in lista[index_aux]:
        if usuarios.id == id_user:
            pesquisaJogadores(usuarios.votos)
            return


def processa_usuario(tabela_hash, id_user, id_player, rating):
    index_aux = calcular_hash(id_user, TAMANHO_TABELA_HASH_USUARIOS)

    voto = (id_player, rating)

    usuarios_set = set(
        usuario.id for usuario in tabela_hash_usuarios[index_aux])

    if id_user in usuarios_set:
        usuario = next(
            usuario for usuario in tabela_hash_usuarios[index_aux] if usuario.id == id_user)
        usuario.votos.append(voto)
    else:
        usuario = Usuario(id_user)
        usuario.votos.append(voto)
        tabela_hash[index_aux].append(usuario)

# ;;;;;;;;;;;;;;;;;;;; TAG ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;


def calcula_hash_string(string):
    soma = 0

    for char in string:
        soma += ord(char)

    return soma % TAMANHO_TABELA_TAG


def processa_tag(tabela):
    with open("tags.csv", newline="") as testeFile:
        reader = csv.DictReader(testeFile)
        for linha in reader:
            tag = linha["tag"]
            id_player = int(linha["sofifa_id"])
            index_aux = calcula_hash_string(tag)

            status = 0  # Mova a variável status para dentro do loop externo

            for tags in tabela[index_aux]:
                if tags.nome == tag:
                    if id_player in tags.listaJogadores:
                        status = 1
                        break
                    tags.listaJogadores.append(id_player)
                    status = 1
                    break

            if status == 0:
                tag_aux = Tag(tag)
                tag_aux.listaJogadores.append(id_player)
                tabela[index_aux].append(tag_aux)


def lista_tags(lista):
    index_first = calcula_hash_string(lista[0])

    for tags in lista_tag[index_first]:
        if tags.nome == lista[0]:
            resultado = set(tags.listaJogadores)
            break
    else:
        # Se o loop não for interrompido, ou seja, a lista estiver vazia
        resultado = set()

    for tag in lista[1:]:
        index_aux = calcula_hash_string(tag)
        for tag_lista in lista_tag[index_aux]:
            if tag_lista.nome == tag:
                resultado = resultado.intersection(tag_lista.listaJogadores)

    return resultado


def obter_lista_do_usuario():
    entrada_usuario = input(
        "Digite uma lista de valores separados por vírgula: ")

    # Divida a entrada usando a vírgula como delimitador e remova espaços em branco ao redor de cada valor
    lista_valores = [valor.strip() for valor in entrada_usuario.split(",")]

    return lista_valores


# /////////////////////////////////////////////////////////////////////////////////////////////////

def carrega_nome_jogadores(lista):
    for jogadores in tabela_hash_jogadores:
        for jogador in jogadores:
            nome = jogador.longName
            id = jogador.id
            tupla = (nome, id)
            lista.append(tupla)


def busca_topN(n, posicao):
    lista_aux_posicao = []
    posicao_aux = posicao.upper()
    for jogadores in tabela_hash_jogadores:
        for jogador in jogadores:
            if posicao_aux in jogador.posicoes and jogador.revisoes > 1000:
                lista_aux_posicao.append(jogador)
                jogador.media = jogador.soma / jogador.revisoes

    lista_ordenada_posicao = sorted(
        lista_aux_posicao, key=lambda x: x.media, reverse=True)
    for jogadores in lista_aux_posicao:
        jogadores.media = round(jogadores.media, 6)

    printa_tabela_posicao(lista_ordenada_posicao, n)


# ;;;;;;;;;;;;;;;PRINTS;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

def printa_tabela(lista):

    # criar tabela
    tabela = PrettyTable()
    tabela.field_names = ["ID", "SHORT NAME", "LONG NAME",
                          "MÉDIA GLOBAL", "AVALIAÇÕES", "VOTO DO USUÁRIO"]

    # Adicionar dados a tabela
    for jogador in lista:
        tabela.add_row([jogador.id, jogador.shortName, jogador.longName,
                       jogador.media, jogador.revisoes, jogador.personal_rating])

    print(tabela)


def printa_tabela_posicao(lista, n):
    i = 0
    # criar tabela
    tabela_posicao = PrettyTable()
    tabela_posicao.field_names = ["ID", "SHORT NAME", "LONG NAME", "POSIÇÕES",
                                  "NACIONALIDADE", "CLUBE", "LIGA DO CLUBE", "MÉDIA GLOBAL", "AVALIAÇÕES"]

    # Adicionar dados a tabela
    for jogador in lista:
        if i < n:
            tabela_posicao.add_row([jogador.id, jogador.shortName, jogador.longName, jogador.posicoes,
                                   jogador.nacionalidade, jogador.time, jogador.liga, jogador.media, jogador.revisoes])
            i += 1
    print(tabela_posicao)


def printa_tabela_prefixo(lista):
    # criar tabela
    tabela = PrettyTable()
    tabela.field_names = ["ID", "SHORT NAME", "LONG NAME",
                          "POSIÇÕES", "MÉDIA GLOBAL", "AVALIAÇÕES"]

    # Adicionar dados a tabela
    for jogador in lista:
        tabela.add_row([jogador.id, jogador.shortName, jogador.longName,
                       jogador.posicoes, jogador.media, jogador.revisoes])

    print(tabela)


processa_jogadores(tabela_hash_jogadores)
processa_avaliacao(tabela_hash_jogadores, tabela_hash_usuarios)
processa_tag(lista_tag)
carrega_nome_jogadores(lista_nome_jogadores)
cria_arvore(arvore)
# ;;;;;;;;;;;;;;;;;;;;; CARREGA DADOS ;;;;;;;;;;;;;;;;;;;;;;;;


while (i == 0):

    resposta = int(input("Deseja fazer qual pesquisa ?\n 1 )Busca por prefixo \n 2 )Busca em cima do ID do usuário \n 3 )Busca de jogadores por posição \n 4 )Busca de jogadores por Tags \n 5 )Para terminar o programa\nResposta : "))
    limpar_terminal()
# 3.1
    if resposta == 1:
        prefixo = input("Qual prefixo deseja procurar ?")
        lista_de_id = search(arvore, prefixo)
        printa_jogadores_id(lista_de_id)

# 3.2
    if resposta == 2:
        usuario = int(input("Qual usuário deseja procurar ?"))
        buscaUsuario(tabela_hash_usuarios, usuario)


# 3.3
    if resposta == 3:
        numero = int(input("Quantos jogadores listados quer para a posição?"))
        posicao = input("Qual posição deseja procurar ?")
        posicao = posicao.upper()
        busca_topN(numero, posicao)


# 3.4
    if resposta == 4:
        lista_tag_usuario = obter_lista_do_usuario()
        lista_jogadores_id_tag = lista_tags(lista_tag_usuario)
        printa_jogadores_id(lista_jogadores_id_tag)

    if resposta == 5:
        i = 1
