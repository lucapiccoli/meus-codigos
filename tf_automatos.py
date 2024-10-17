import copy


class Automato:
    def __init__(self, alfabeto, estados, estado_inicial, estados_finais, transicoes):
        self.alfabeto = alfabeto
        self.estados = estados
        self.estado_inicial = estado_inicial
        self.estados_finais = estados_finais
        self.transicoes = transicoes

    def aceita_ou_rejeita(self, palavra):
        estado_atual = self.estado_inicial
        # Percorre cada letra da palavra dada
        for letra in palavra:

            # Verificacao se cada letra esta no alfabeto do automato dado
            if letra not in self.alfabeto:
                return False

            # Inicializa a variavel como False de controle de transicoes
            transicao_encontrada = False

            # Pega cada tupla das trancicoes e bota nas variaveis que vamos trabalhar
            for transicao in self.transicoes:
                origem, simbolo, destino = transicao
                # Se dado o estado atual, tem uma transicao que existe dado a letra lida ele muda de estado
                if origem == estado_atual and simbolo == letra:
                    estado_atual = destino
                    # Atualiza a variavel de controle e quebra o laco mais interno
                    transicao_encontrada = True
                    break
            # Verifica se nao teve nenhuma transicao encontrada para dado estado atual
            if not transicao_encontrada:
                return False

        return estado_atual in self.estados_finais


def extrair_alfabeto_e_estados(nome_arquivo):
    with open(nome_arquivo, 'r') as arquivo:
        linhas = arquivo.readlines()

        # extrair alfabeto como uma lista
        inicio = linhas[0].find("{") + 2
        fim = linhas[0].find("}", inicio)
        alfabeto_str = linhas[0][inicio:fim]
        alfabeto = copy.deepcopy(alfabeto_str.split(','))

        # extrair estados como uma lista
        inicio = linhas[0].find("{", fim) + 1
        fim = linhas[0].find("}", inicio)
        estados_str = linhas[0][inicio:fim]
        estados = copy.deepcopy(estados_str.split(','))

        # Extrair estado inicial
        inicio = linhas[0].find(",", fim) + 1
        fim = linhas[0].find(",", inicio)
        estado_inicial = linhas[0][inicio:fim]

        # Extrair estados finais como uma lista
        inicio = linhas[0].find("{", fim) + 1
        fim = linhas[0].find("}", inicio)
        estados_finais_str = linhas[0][inicio:fim]
        estados_finais = copy.deepcopy(estados_finais_str.split(","))

        # Processar as transições a partir das linhas que não começam com "{" ou "}"
        transicoes_ = []
        for linha in linhas[2:]:
            partes = [parte.strip('()') for parte in linha.strip().split(",")]
            if len(partes) >= 3:
                origem, simbolo, destino = partes[0], partes[1], partes[2]
                transicoes_.append((origem, simbolo, destino))

        # Retorna um objeto automato formado por listas e estado inicial
        return Automato(alfabeto, estados, estado_inicial, estados_finais, transicoes_)


def testa_palavras(arq):
    # Abra o arquivo para leitura
    with open(arq, 'r') as arquivo:
        # Leia o conteúdo do arquivo
        conteudo = arquivo.read()
        # Separe as palavras por vírgula e coloque em uma lista
        lista_de_palavras = conteudo.split(',')
        # Faz o teste de aceitacao ou rejeicao para todas a palavras
        for palavra in lista_de_palavras:
            print(palavra)
            print(afd.aceita_ou_rejeita(palavra))

# breadth-first search para atingir todos os estados alcançáveis a partir do inicial
def estados_alcancaveis(M):
    alcancaveis = {M.estado_inicial}
    fila = [M.estado_inicial]

    while fila:
        estado = fila.pop(0)
        for transicao in M.transicoes:
            if transicao[0] == estado and transicao[2] not in alcancaveis:
                alcancaveis.add(transicao[2])
                fila.append(transicao[2])

    return alcancaveis

# Para transformar a função programa em total, é introduzido
# um novo estado não final d para incluir as transições não previstas,
# tendo d como estado destino. Por fim, é incluído um ciclo em d para todos os símbolos do alfabeto.
def tornar_automato_total(M, novo_estado='d'):
    # Cria uma cópia profunda do automato original
    novo_automato = Automato(
        M.alfabeto.copy(), M.estados.copy(),
        M.estado_inicial, M.estados_finais.copy(), M.transicoes.copy()
    )

    # Adiciona o novo estado ao conjunto de estados
    novo_automato.estados.append(novo_estado)

    # Preenche transições não definidas com o novo estado
    for estado in novo_automato.estados:
        for simbolo in novo_automato.alfabeto:
            transicao_definida = False
            for producao in novo_automato.transicoes:
                if producao[0] == estado and producao[1] == simbolo:
                    transicao_definida = True
                    break

            if not transicao_definida:
                novo_automato.transicoes.append((estado, simbolo, novo_estado))

    return novo_automato

# Função auxiliar para obter a transição de um estado com um símbolo
def transicao(automato, estado, simbolo):
    for producao in automato.transicoes:
        if producao[0] == estado and producao[1] == simbolo:
            return producao[2]
    return estado  # Se não houver transição definida, permanece no mesmo estado

def minimiza(M):
    tornar_automato_total(M)

    # passo 1: contrução da tabela que relaciona os estaodos
    estados = list(M.estados)
    tabela = {}

    for i in range(len(estados)):
        for j in range(len(estados)):
            tabela[(estados[i], estados[j])] = None

    # passo 2: marcar todos os pares trivialmente não equivalentes (um final e um não final)
    for i in range(len(estados)):
        for j in range(i + 1, len(estados)):
            tabela[(estados[i], estados[j])] = False
            if (estados[i] in M.estados_finais) and (estados[j] in M.estados_finais):
                tabela[(estados[i], estados[j])] = False
            elif (estados[i] not in M.estados_finais) and (estados[j] not in M.estados_finais):
                tabela[(estados[i], estados[j])] = False
            elif (estados[i] not in M.estados_finais) and (estados[j] in M.estados_finais):
                tabela[(estados[i], estados[j])] = True
            elif (estados[i] in M.estados_finais) and (estados[j] not in M.estados_finais):
                tabela[(estados[i], estados[j])] = True


    print("trivialmente:")
    print(tabela)

    # passo 3: marcação dos estados não equivalentes
    while True:
        mudou = False
        for par in tabela:
            qu = par[0]
            qv = par[1]
            # Se o par não estiver marcado
            if tabela[par] is False:
                # Verifique todas as transições possíveis
                for simbolo in M.alfabeto:
                    pu = transicao(M, qu, simbolo)
                    pv = transicao(M, qv, simbolo)

                    # Verifique se as transições são marcadas
                    # Se uma transição estiver marcada, marque o par atual
                    if tabela.get((pu, pv)) is not None:
                        if tabela[(pu, pv)] is True:
                            tabela[par] = True
                            mudou = True

                    elif tabela.get((pv, pu)) is not None:
                        if tabela[(pv, pu)]:
                            tabela[par] = True
                            mudou = True

        # repete até que não nenhum outro par seja marcado
        if not mudou:
            break
    # print("passo:")
    # print(tabela)
    return tabela

arquivo = "automato2.txt"
afd = extrair_alfabeto_e_estados(arquivo)
print("Alfabeto:", afd.alfabeto)
print("Estados:", afd.estados)
print("Estado Inicial:", afd.estado_inicial)
print("Estados Finais:", afd.estados_finais)
print("Transições:", afd.transicoes)
arq_teste = input("Digite o nome do arq de teste: ")
testa_palavras(arq_teste)