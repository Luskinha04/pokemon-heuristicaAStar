import heapq  # Importa o módulo heapq para manipular filas de prioridade (usado no algoritmo A*)
import random  # Importa o módulo random para realizar sorteios aleatórios
import pygame  # Importa a biblioteca pygame para gráficos e interface visual
import time  # Importa a biblioteca time para medir o tempo de execução

# Custos dos terrenos (valores utilizados no cálculo do algoritmo A*)
CUSTO_TERRENO = {
    "G": 10,  # Grama tem custo baixo
    "A": 100,  # Água tem custo alto
    "M": 120,  # Montanha tem custo alto
    "C": 120,  # Caverna tem custo alto
    "V": 150,  # Vulcão tem o maior custo
}

# Bônus aplicados quando o jogador captura determinados tipos de Pokémon
# Esses bônus reduzem o custo ao passar por certos terrenos
POKEMON_BONUS = {
    "agua": {"A": 10},  # Pokémon de água reduz o custo da água
    "eletrico": {"C": 12},  # Elétrico reduz o custo da caverna
    "voador": {"M": 12},  # Voador reduz o custo da montanha
    "fogo": {"V": 15},  # Fogo reduz o custo do vulcão
    "grama": {"G": 0},  # Grama não tem bônus (mas está presente para consistência)
}

# Define o tamanho de cada célula do mapa (em pixels)
tamanho_celula = 23

# Define o tamanho total do mapa (42x42 células)
tamanho_mapa = 42

# Inicializa os módulos do pygame
pygame.init()

# Cria a janela do jogo com dimensões baseadas no tamanho do mapa e das células
tela = pygame.display.set_mode(
    (tamanho_mapa * tamanho_celula, tamanho_mapa * tamanho_celula)
)

# Define o título da janela do pygame
pygame.display.set_caption("A* Pokémon com Radar")

# Carrega a imagem do jogador (personagem principal)
sprite_jogador = pygame.image.load("jogador.png")

# Redimensiona a imagem do jogador para caber perfeitamente em uma célula
sprite_jogador = pygame.transform.scale(
    sprite_jogador, (tamanho_celula, tamanho_celula)
)

# Carrega as imagens dos ginásios (insígnias) em um dicionário
# Mesmo sendo a mesma imagem, são atribuídas chaves diferentes de 0 a 7
sprite_insignias = {
    0: pygame.image.load("ginasio.png"),
    1: pygame.image.load("ginasio.png"),
    2: pygame.image.load("ginasio.png"),
    3: pygame.image.load("ginasio.png"),
    4: pygame.image.load("ginasio.png"),
    5: pygame.image.load("ginasio.png"),
    6: pygame.image.load("ginasio.png"),
    7: pygame.image.load("ginasio.png"),
}

# Carrega os sprites dos pokémons visíveis no mapa, por tipo
sprite_pokemon = {
    "agua": pygame.image.load("pokemon_agua.png"),
    "eletrico": pygame.image.load("pokemon_eletrico.png"),
    "fogo": pygame.image.load("pokemon_fogo.png"),
    "voador": pygame.image.load("pokemon_voador.png"),
    "grama": pygame.image.load("pokemon_grama.png"),
}

# Redimensiona todas as imagens das insígnias para caberem em uma célula do mapa
for key in sprite_insignias:
    sprite_insignias[key] = pygame.transform.scale(
        sprite_insignias[key], (tamanho_celula, tamanho_celula)
    )

# Redimensiona todas as imagens dos pokémons para o tamanho padrão das células
for key in sprite_pokemon:
    sprite_pokemon[key] = pygame.transform.scale(
        sprite_pokemon[key], (tamanho_celula, tamanho_celula)
    )

# Carrega os sprites fixos dos terrenos do mapa (exceto lava)
sprite_terrenos = {
    "G": pygame.image.load("sprites/grama.png"),  # Grama
    "A": pygame.image.load("sprites/agua.png"),  # Água
    "M": pygame.image.load("sprites/montanha.png"),  # Montanha
    "C": pygame.image.load("sprites/caverna.png"),  # Caverna
}
# Redimensiona os sprites dos terrenos
for key in sprite_terrenos:
    sprite_terrenos[key] = pygame.transform.scale(
        sprite_terrenos[key], (tamanho_celula, tamanho_celula)
    )

# Carrega os 27 frames da lava animada
sprites_lava = []
for i in range(27):
    imagem = pygame.image.load(f"sprites/lava/lava_{i:02}.png")
    imagem = pygame.transform.scale(imagem, (tamanho_celula, tamanho_celula))
    sprites_lava.append(imagem)

# Carrega os frames da água animada
sprites_agua = []
for i in range(6):  # temos de agua_0.png até agua_5.png
    frame = pygame.image.load(f"sprites/agua/agua_{i}.png")
    frame = pygame.transform.scale(frame, (tamanho_celula, tamanho_celula))
    sprites_agua.append(frame)


def gerar_mapa():
    """Cria um mapa predefinido e distribui ginásios e pokémons ocultos."""
    # Mapa predefinido (Exemplo: G = Grama, A = Água, M = Montanha, C = Caverna, V = Vulcão)
    mapa_predefinido = [
        list("MGGGGMGAGGGGGGGGMMMMMMMGGGMMMMMGGGGMMMGGGG"),
        list("MGMMMMGAGMMMMGGMMMMMMMMMGGMGGGMGGMMMMMMMGG"),
        list("MGGGGMGAGMGGMGMMMMMMMMMMMGMMGMMGMMMMVMMMMG"),
        list("MGMMMMGAGMGGMGMMMMMMMMMMMGGMGMGMMMMVVVMMMM"),
        list("MGGGGMGAGGGGGGGMMMMMMMMMGGGMGMGMMMVVVVVMMM"),
        list("MMMMGMGAAAAAGGGGGMMMMMGGGMGMGMGMMMMVVVMMMM"),
        list("GMGGGGGGGGGAGMMGGGGGGGGGGMGMGMGGMMMMVMMMMG"),
        list("GMGGGGMMMMGAGMMGGGGMGGMGGGGGGGGGGMMMMMMMGG"),
        list("GGGGMGGGGGGGGGGGGGMMMGGGMMMMMMMGGGGMMMGGGG"),
        list("GGMGGGGGMMGAGMMGMGGMGGGGGGGGGGGGGGGGGGGGMG"),
        list("GGMGMMMGMMGAGMMGMGGGGGGGMMMGGGMMMGMMMMGGMG"),
        list("GGMGGGGGGGGAGGGGMMMMMGGMMMMMGGMMMGGGGGGGGG"),
        list("GGMGGGGGGGGAAAAGMGGMGGMMMMMMMGGGGGMGGMMMMG"),
        list("GGGGGGGGMGGGGGAGMGGMGGMMMAMMMGGGGGMGGGGGGG"),
        list("MMMMGMGMMMGGGGAGGGGMGGGMMAMMGGGGMMMMMMMGGG"),
        list("GGGGGMGMMMGGAAAAAGGMGGGGGAGGGGGGGGGMGGGGGG"),
        list("GGMGGMGGMGGAAAAAAAGGGMMMGAGGGMGGMGGMGGGGGG"),
        list("MGMGGMGGGGAAAAAAAAAGGGGGGAGMMMMGMGGMGGGGMM"),
        list("MGMGGMGGGGAAAGGGAAAGGMGGGAGGGMGGMGGGGMMMMM"),
        list("MGMGMMMGGGAAAGGGAAAGMMMGGAGGGGGGMMMGMMMMMM"),
        list("MGGGGGGGGGAAAGGGAAAGMMMGGAAAAAAGGGGGGGGGMM"),
        list("MMMMMGGGGGAAAAAAAAAGMMMGGGGGGGAGMMMGMMMMMM"),
        list("GGGGMGMGGGGAAAAAAAGGGMGGGMMMGGAGMGGGGMMMMM"),
        list("GGGGMGMGGGGGAAAAAGGGGGGGGMMMGGAGMGMMGGGGMM"),
        list("GGMGGGMGMMGGGGAGGGGGGMMMGGGGGGAGMGMGGGGGGG"),
        list("GMMMGGMGMMMMGGAGGGMMGGGGGGMGGGAGGGMMMMGGGG"),
        list("GMMMGMMGGGGGGGAGGMMMMGGGMGMGGAAAGGGMMMGGMG"),
        list("GMMMGGGGMMMGGGAGMMMMMMGGMGGGAAAAAGGGGGGGMG"),
        list("GGMGGGGGGGGGGGAGMMMMMMGGMGGAAAAAAAGGMMMMMG"),
        list("MGGGMGGMAAAAAAAGGMMMMGGGMGGGAAAAAGGGMGGGMG"),
        list("MMGMMMGGAGGGGGMGGGMMGGMMMMGGGAAAGGGGGGGGGG"),
        list("MMGMMMGGAGGGGGMGMGGGGGGGGGGGGGGGGMMMMGMMMG"),
        list("MGGGMGGGAGMMMMMGMMMMGMMMMMMGGGGMGGGMGGGMGG"),
        list("GGGGGGGGGGGGGGGGGGGGGGGGGGMGGMMMMMGMGMGMGM"),
        list("GMGMMMMGAGMMMGMMMMMMMMMMGMMGGGGGGGGGGGGMGM"),
        list("GMGGGGMGAGGMGGMGGGGGGGGMGMGGMMMMCMMMMGGMGM"),
        list("GMMMGGMGAGGMGGMGMMMMMMGMGGGMMMVVCVVMMMGGGM"),
        list("GMGGGGMGAGGGGGMGMGGGGMGMGGMMVVVVCVVVVMMGGM"),
        list("MMGMMMMGAAAAGGMGGGGGGMGMGGMMVVVVCVVVVMMGGG"),
        list("MGGGGGMGGGGAGGMMMMMMMMGMGMMVVVVVCVVVVVMMGG"),
        list("MGMMMGMGGGGAGGGGGGGGGGGGGMMVVVVVCVVVVVMMGG"),
        list("MGGGGGMGGGGAGGMMMMMMMMMMGMMVVVVVVVVVVVMMGG"),
    ]

    # Posição do ginásio predefinida - linha - coluna
    posicao_jogador = (19, 24)

    # Colocar as insígnias manualmente
    insignias = [  # linha - coluna
        (2, 4),  # Insígnia da Alma
        (2, 19),  # Insígnia Trovão
        (4, 36),  # Insígnia Vulcão
        (19, 14),  # Insígnia Cascata
        (22, 2),  # Insígnia Arco-Íris
        (37, 19),  # Insígnia Lama
        (20, 39),  # Insígnia Terra
        (40, 32),  # Insígnia Rocha
    ]

    # Geração aleatória dos pokémons ocultos
    quantidade_pokemons = {
        "grama": 20,  # Serão gerados 20 pokémons do tipo grama
        "agua": 10,  # 10 pokémons do tipo água
        "voador": 8,  # 8 do tipo voador
        "fogo": 6,  # 6 do tipo fogo
        "eletrico": 4,  # 4 do tipo elétrico
    }

    # Cria uma lista contendo todos os tipos de pokémon, repetidos conforme a quantidade desejada
    lista_pokemons = (
        ["grama"] * quantidade_pokemons["grama"]
        + ["agua"] * quantidade_pokemons["agua"]
        + ["voador"] * quantidade_pokemons["voador"]
        + ["fogo"] * quantidade_pokemons["fogo"]
        + ["eletrico"] * quantidade_pokemons["eletrico"]
    )

    # Embaralha a lista de pokémons para que sua posição no mapa seja aleatória
    random.shuffle(lista_pokemons)

    # Gera uma lista com todas as posições (i, j) do mapa onde há grama ("G"),
    # pois pokémons só podem ser colocados em células de grama
    possiveis_posicoes = [
        (i, j)
        for i in range(len(mapa_predefinido))  # percorre as linhas do mapa
        for j in range(len(mapa_predefinido[0]))  # percorre as colunas do mapa
        if mapa_predefinido[i][j] == "G"  # verifica se o terreno é grama
    ]

    # Embaralha as posições possíveis para garantir distribuição aleatória no mapa
    random.shuffle(possiveis_posicoes)

    # Combina cada posição com um tipo de pokémon, criando um dicionário com as posições e seus respectivos tipos
    pokemons_na_posicao = dict(
        zip(possiveis_posicoes[: len(lista_pokemons)], lista_pokemons)
    )

    # Retorna o mapa montado com pokémons ocultos, posição inicial do jogador e os ginásios
    return mapa_predefinido, posicao_jogador, insignias, pokemons_na_posicao

    # Função que calcula a heurística de distância entre dois pontos (distância de Manhattan)


def heuristica(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


# Função que implementa o algoritmo A* com bônus baseados nos Pokémons capturados
def a_estrela(mapa, inicio, objetivo, pokemons_capturados):
    """A* busca o melhor caminho considerando terrenos e bônus de Pokémon."""

    # Inicializa a fila de prioridade (heap), começando com o ponto de partida e custo 0
    fila = []
    heapq.heappush(fila, (0, inicio))

    # Dicionário que armazena de onde cada ponto veio (para reconstruir o caminho)
    veio_de = {}

    # Dicionário com o custo mínimo atual para chegar a cada ponto
    custo_atual = {inicio: 0}

    # Enquanto houverem pontos a serem processados na fila
    while fila:
        _, atual = heapq.heappop(fila)  # Pega o ponto com menor prioridade

        # Se chegamos no objetivo, reconstruímos o caminho
        if atual == objetivo:
            caminho = []  # Lista que irá conter o caminho final
            total_custo = 0  # Custo total acumulado do caminho

            # Reconstrói o caminho de trás pra frente
            while atual in veio_de:
                caminho.append(atual)  # Adiciona a posição atual ao caminho
                anterior = veio_de[atual]  # Volta um passo no caminho
                terreno = mapa[atual[0]][atual[1]]  # Identifica o tipo de terreno
                custo_terreno = CUSTO_TERRENO[terreno]  # Custo base do terreno

                # Verifica se algum Pokémon capturado dá bônus nesse terreno
                for pkm in pokemons_capturados:
                    if terreno in POKEMON_BONUS.get(pkm, {}):
                        custo_terreno -= POKEMON_BONUS[pkm][terreno]  # Aplica o bônus
                        custo_terreno = max(
                            custo_terreno, 1
                        )  # Garante custo mínimo de 1

                total_custo += custo_terreno  # Acumula o custo
                atual = anterior  # Vai para o ponto anterior

            caminho.reverse()  # Inverte o caminho para começar do início

            # Exibe no terminal o caminho encontrado
            print("Caminho encontrado:")
            for passo in caminho:
                print(f"  -> {passo}")
            print(f"Custo total da caminhada: {total_custo}")

            # Retorna o caminho e o custo final
            return caminho, total_custo

        # Se ainda não chegamos no objetivo, expandimos os vizinhos
        x, y = atual
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # Vizinhos ortogonais
            novo = (x + dx, y + dy)

            # Verifica se a nova posição está dentro do mapa
            if 0 <= novo[0] < len(mapa) and 0 <= novo[1] < len(mapa[0]):
                # Calcula o custo do movimento para o novo ponto
                custo_movimento = CUSTO_TERRENO[mapa[novo[0]][novo[1]]]

                # Aplica o bônus de Pokémon, se houver
                for pkm in pokemons_capturados:
                    if mapa[novo[0]][novo[1]] in POKEMON_BONUS.get(pkm, {}):
                        custo_movimento -= POKEMON_BONUS[pkm][mapa[novo[0]][novo[1]]]
                        custo_movimento = max(custo_movimento, 1)  # Custo mínimo de 1

                # Novo custo acumulado até essa posição
                novo_custo = custo_atual[atual] + custo_movimento

                # Se ainda não visitamos esse ponto ou achamos um caminho mais barato
                if novo not in custo_atual or novo_custo < custo_atual[novo]:
                    custo_atual[novo] = novo_custo  # Atualiza o custo
                    prioridade = novo_custo + heuristica(
                        novo, objetivo
                    )  # Prioridade A*
                    heapq.heappush(fila, (prioridade, novo))  # Adiciona à fila
                    veio_de[novo] = atual  # Salva de onde veio

    # Se não encontramos caminho, retorna lista vazia
    return []


# Função que simula o radar da Pokédex do jogador
# Ela revela Pokémons dentro de um certo raio (alcance) da posição do jogador
def radar_pokedex(jogador, pokemons_na_posicao, alcance=4):
    """Revela Pokémons próximos dentro do alcance do radar."""
    x, y = jogador  # Posição atual do jogador
    pokemons_visiveis = [
        p
        for p in pokemons_na_posicao
        if abs(p[0] - x) <= alcance
        and abs(p[1] - y) <= alcance  # Verifica se está no raio
    ]
    return pokemons_visiveis  # Retorna apenas os pokémons visíveis dentro do alcance


# Função responsável por desenhar o mapa completo na tela do pygame
def desenhar_mapa(
    mapa,
    jogador,
    insignias,
    pokemons_visiveis,
    caminho=[],
    pokemons_na_tela={},
    frame_lava=0,
):
    # Preenche a tela com branco antes de desenhar
    tela.fill((255, 255, 255))

    # Percorre todas as posições do mapa
    for x in range(len(mapa)):
        for y in range(len(mapa[0])):
            tipo = mapa[x][y]  # Tipo de terreno da célula atual

            # Se for terreno de vulcão (lava), aplica animação com base no frame atual
            # Se for terreno de agua, aplica animação com base no frame atual
            if tipo == "V":
                imagem = sprites_lava[frame_lava % len(sprites_lava)]  # Lava animada
            elif tipo == "A":
                imagem = sprites_agua[frame_lava % len(sprites_agua)]  # Água animada
            else:
                imagem = sprite_terrenos.get(tipo)

            if imagem:
                # Desenha a imagem do terreno na tela, na posição correta
                tela.blit(imagem, (y * tamanho_celula, x * tamanho_celula))

    # Destaca visualmente o caminho atual sendo percorrido pelo agente
    for x in range(len(mapa)):
        for y in range(len(mapa[0])):
            if (x, y) in caminho:
                pygame.draw.rect(
                    tela,
                    (200, 200, 200),  # Cinza claro para destacar o caminho
                    (
                        y * tamanho_celula,
                        x * tamanho_celula,
                        tamanho_celula,
                        tamanho_celula,
                    ),
                )
    # Desenha as insígnias (ginásios) no mapa
    pos_img_insignias = 0
    for g in insignias:
        tela.blit(
            sprite_insignias[pos_img_insignias],  # Usa a imagem correspondente
            (g[1] * tamanho_celula, g[0] * tamanho_celula),  # Posição no mapa
        )
        pos_img_insignias += 1  # Passa para a próxima imagem

    # Desenha os Pokémons visíveis na tela
    for p, tipo in pokemons_na_tela.items():
        tela.blit(
            sprite_pokemon[tipo],  # Usa a imagem do tipo de Pokémon
            (p[1] * tamanho_celula, p[0] * tamanho_celula),  # Posição do Pokémon
        )

        # Desenha o jogador na posição atual
    tela.blit(
        sprite_jogador, (jogador[1] * tamanho_celula, jogador[0] * tamanho_celula)
    )

    # Atualiza o conteúdo da tela com tudo que foi desenhado
    pygame.display.flip()


def main():
    # Gera o mapa e informações iniciais (posição, ginásios e pokémons ocultos)
    mapa, posicao_jogador, ginasios, pokemons_na_posicao = gerar_mapa()

    # Lista dos pokémons que estão visíveis para o jogador
    pokemons_visiveis = []

    # Lista dos pokémons já capturados
    pokemons_capturados = []

    # Dicionário para contar quantos pokémons de cada tipo foram capturados
    contador_pokemons = {"agua": 0, "eletrico": 0, "fogo": 0, "voador": 0, "grama": 0}

    # Quantidade de insígnias obtidas
    insignias = 0

    # Flag para manter o jogo rodando
    rodando = True

    # Marca o tempo de início do jogo (para medir duração total depois)
    tempo_inicio = time.time()

    # Acumula o custo total de movimentação do jogador
    custo_total = 0

    # Contador de frames para animar a lava
    frame_lava = 0

    while rodando:
        # Verifica eventos do pygame, como clicar no botão de fechar a janela
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                rodando = False

        # Atualiza o frame da lava e da agua para simular animação
        frame_lava = (frame_lava + 1) % max(len(sprites_lava), len(sprites_agua))

        # Se o jogador já conquistou 8 insígnias, encerra o jogo
        if insignias >= 8:
            rodando = False
            continue

        # Atualiza o radar do jogador com novos pokémons visíveis
        novos_pokemons = radar_pokedex(posicao_jogador, pokemons_na_posicao)
        for p in novos_pokemons:
            if p not in pokemons_visiveis:
                pokemons_visiveis.append(p)

        # Dicionário com os pokémons que serão desenhados na tela
        pokemons_na_tela = {}

        # Calcula o ginásio mais próximo com base na heurística de distância
        proximo_ginasio = (
            min(ginasios, key=lambda g: heuristica(posicao_jogador, g))
            if ginasios
            else None
        )

        # Calcula o pokémon mais próximo visível
        proximo_pokemon = (
            min(pokemons_visiveis, key=lambda p: heuristica(posicao_jogador, p))
            if pokemons_visiveis
            else None
        )

        # Calcula a distância até o ginásio e o pokémon (usado para decisão de movimento)
        dist_ginasio = (
            heuristica(posicao_jogador, proximo_ginasio)
            if proximo_ginasio
            else float("inf")
        )
        dist_pokemon = (
            heuristica(posicao_jogador, proximo_pokemon)
            if proximo_pokemon
            else float("inf")
        )

        # O agente prioriza o ginásio se ele estiver mais próximo, ou no máximo 3 blocos mais longe que o pokémon
        if proximo_ginasio and (dist_ginasio <= dist_pokemon + 3):
            ginasios.remove(proximo_ginasio)  # Remove o ginásio da lista após visitá-lo
            caminho, custo = a_estrela(
                mapa, posicao_jogador, proximo_ginasio, pokemons_capturados
            )
            custo_total += custo  # Soma o custo dessa caminhada ao total

            # Anima o trajeto até o ginásio
            for pos in caminho:
                desenhar_mapa(
                    mapa,
                    pos,
                    ginasios,
                    pokemons_visiveis,
                    caminho,
                    pokemons_na_tela,
                    frame_lava,
                )
                pygame.time.delay(50)

            # Atualiza a posição do jogador e a quantidade de insígnias
            posicao_jogador = proximo_ginasio
            insignias += 1

        # Se o pokémon estiver mais próximo ou não houver ginásio por perto
        elif proximo_pokemon:
            pokemons_visiveis.remove(proximo_pokemon)  # Remove da lista de visíveis
            tipo_pokemon = pokemons_na_posicao[proximo_pokemon]  # Identifica o tipo
            pokemons_na_tela[proximo_pokemon] = tipo_pokemon  # Adiciona para desenhar
            del pokemons_na_posicao[proximo_pokemon]  # Remove do mapa

            # Caminha até o pokémon
            caminho, custo = a_estrela(
                mapa, posicao_jogador, proximo_pokemon, pokemons_capturados
            )
            custo_total += custo

            # Anima o trajeto até o pokémon
            for pos in caminho:
                desenhar_mapa(
                    mapa,
                    pos,
                    ginasios,
                    pokemons_visiveis,
                    caminho,
                    pokemons_na_tela,
                    frame_lava,
                )
                pygame.time.delay(100)

            # Atualiza as informações do jogador
            pokemons_capturados.append(tipo_pokemon)
            contador_pokemons[tipo_pokemon] += 1
            posicao_jogador = proximo_pokemon

        # Se não houver mais o que fazer, encerra o loop
        else:
            rodando = False

    tempo_total = time.time() - tempo_inicio
    print(f"🏆 Pokémons capturados: {len(pokemons_capturados)}")
    print(f"🎖️ Insígnias obtidas: {insignias}/8 - Todas conquistadas!")
    print(f"⏳ Tempo total: {tempo_total:.2f} segundos")
    print(f"$ Custo total: {custo_total:.2f}")
    print("📊 Detalhes dos Pokémons capturados:")
    for tipo, qtd in contador_pokemons.items():
        print(f"  {tipo.capitalize()}: {qtd}")


main()
input()
pygame.quit()
