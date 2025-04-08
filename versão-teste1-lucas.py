import heapq
import random
import pygame  # pip install pygame
import time

# Cores dos terrenos
CORES_TERRENO = {
    "G": (0, 255, 0),  # Grama
    "A": (0, 0, 255),  # Água
    "M": (139, 69, 19),  # Montanha
    "C": (128, 128, 128),  # Caverna
    "V": (255, 165, 0),  # Vulcão
}

# Custos dos terrenos
CUSTO_TERRENO = {"G": 10, "A": 100, "M": 120, "C": 120, "V": 150}

# Benefícios de Pokémons capturados
POKEMON_BONUS = {
    "agua": {"A": 10},
    "eletrico": {"C": 12},
    "voador": {"M": 12},
    "fogo": {"V": 15},
    "grama": {"G": 0},
}

# Configuração do mapa
tamanho_celula = 16
tamanho_mapa = 42


# Inicializa o pygame
pygame.init()
tela = pygame.display.set_mode(
    (tamanho_mapa * tamanho_celula, tamanho_mapa * tamanho_celula)
)
pygame.display.set_caption("A* Pokémon com Radar")

# Carrega os sprites
sprite_jogador = pygame.image.load("jogador.png")
sprite_jogador = pygame.transform.scale(
    sprite_jogador, (tamanho_celula, tamanho_celula)
)

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

sprite_pokemon = {
    "agua": pygame.image.load("pokemon_agua.png"),
    "eletrico": pygame.image.load("pokemon_eletrico.png"),
    "fogo": pygame.image.load("pokemon_fogo.png"),
    "voador": pygame.image.load("pokemon_voador.png"),
    "grama": pygame.image.load("pokemon_grama.png"),
}


for key in sprite_insignias:
    sprite_insignias[key] = pygame.transform.scale(
        sprite_insignias[key], (tamanho_celula, tamanho_celula)
    )

for key in sprite_pokemon:
    sprite_pokemon[key] = pygame.transform.scale(
        sprite_pokemon[key], (tamanho_celula, tamanho_celula)
    )


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

    # sorteio
    # print("sorteando insignias")
    # insignias = [(random.randint(1, 24), random.randint(1, 24)) for _ in range(9)]
    # print(insignias)

    # Geração aleatória dos pokémons ocultos
    quantidade_pokemons = {
        "grama": 20,
        "agua": 10,
        "voador": 8,
        "fogo": 6,
        "eletrico": 4,
    }

    lista_pokemons = (
        ["grama"] * quantidade_pokemons["grama"]
        + ["agua"] * quantidade_pokemons["agua"]
        + ["voador"] * quantidade_pokemons["voador"]
        + ["fogo"] * quantidade_pokemons["fogo"]
        + ["eletrico"] * quantidade_pokemons["eletrico"]
    )

    random.shuffle(lista_pokemons)

    # Encontra posições válidas de grama
    possiveis_posicoes = [
        (i, j)
        for i in range(len(mapa_predefinido))
        for j in range(len(mapa_predefinido[0]))
        if mapa_predefinido[i][j] == "G"
    ]
    random.shuffle(possiveis_posicoes)

    # Associa os tipos às posições (limitando à quantidade certa)
    pokemons_na_posicao = dict(
        zip(possiveis_posicoes[: len(lista_pokemons)], lista_pokemons)
    )

    # pokemons_ocultos = [(random.randint(1, 24), random.randint(1, 24)) for _ in range(50)]

    return mapa_predefinido, posicao_jogador, insignias, pokemons_na_posicao


def heuristica(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def a_estrela(mapa, inicio, objetivo, pokemons_capturados):
    """A* busca o melhor caminho considerando terrenos e bônus de Pokémon."""
    fila = []
    heapq.heappush(fila, (0, inicio))
    veio_de = {}
    custo_atual = {inicio: 0}

    while fila:
        _, atual = heapq.heappop(fila)

        if atual == objetivo:
            caminho = []
            total_custo = 0
            while atual in veio_de:
                caminho.append(atual)
                anterior = veio_de[atual]
                terreno = mapa[atual[0]][atual[1]]
                custo_terreno = CUSTO_TERRENO[terreno]

                for pkm in pokemons_capturados:
                    if terreno in POKEMON_BONUS.get(pkm, {}):
                        custo_terreno -= POKEMON_BONUS[pkm][terreno]
                        custo_terreno = max(custo_terreno, 1)

                total_custo += custo_terreno
                atual = anterior

            caminho.reverse()

            print("Caminho encontrado:")
            for passo in caminho:
                print(f"  -> {passo}")
            print(f"Custo total da caminhada: {total_custo}")
            return caminho, total_custo

        x, y = atual
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            novo = (x + dx, y + dy)
            if 0 <= novo[0] < len(mapa) and 0 <= novo[1] < len(mapa[0]):
                custo_movimento = CUSTO_TERRENO[mapa[novo[0]][novo[1]]]

                for pkm in pokemons_capturados:
                    if mapa[novo[0]][novo[1]] in POKEMON_BONUS.get(pkm, {}):
                        custo_movimento -= POKEMON_BONUS[pkm][mapa[novo[0]][novo[1]]]
                        custo_movimento = max(custo_movimento, 1)

                novo_custo = custo_atual[atual] + custo_movimento

                if novo not in custo_atual or novo_custo < custo_atual[novo]:
                    custo_atual[novo] = novo_custo
                    prioridade = novo_custo + heuristica(novo, objetivo)
                    heapq.heappush(fila, (prioridade, novo))
                    veio_de[novo] = atual

    return []


# 4 equivalente a 4 bloquinhos do mapa
def radar_pokedex(jogador, pokemons_na_posicao, alcance=4):
    """Revela Pokémons próximos dentro do alcance do radar."""
    x, y = jogador
    pokemons_visiveis = [
        p
        for p in pokemons_na_posicao
        if abs(p[0] - x) <= alcance and abs(p[1] - y) <= alcance
    ]
    return pokemons_visiveis


def desenhar_mapa(
    mapa, jogador, insignias, pokemons_visiveis, caminho=[], pokemons_na_tela={}
):
    tela.fill((255, 255, 255))

    for x in range(len(mapa)):
        for y in range(len(mapa[0])):
            cor = CORES_TERRENO.get(mapa[x][y], (255, 255, 255))
            pygame.draw.rect(
                tela,
                cor,
                (
                    y * tamanho_celula,
                    x * tamanho_celula,
                    tamanho_celula,
                    tamanho_celula,
                ),
            )
            # if (x, y) in caminho:
            #     pygame.draw.rect(tela, (200, 200, 200),
            #                      (y * tamanho_celula, x * tamanho_celula, tamanho_celula, tamanho_celula))

    # background = pygame.image.load("mapa.png")  # Substitua pelo caminho da imagem
    # background = pygame.transform.scale(background, (tamanho_mapa * tamanho_celula, tamanho_mapa * tamanho_celula))
    # tela.blit(background, (0, 0))

    for x in range(len(mapa)):
        for y in range(len(mapa[0])):
            if (x, y) in caminho:
                pygame.draw.rect(
                    tela,
                    (200, 200, 200),
                    (
                        y * tamanho_celula,
                        x * tamanho_celula,
                        tamanho_celula,
                        tamanho_celula,
                    ),
                )

    pos_img_insignias = 0
    for g in insignias:
        tela.blit(
            sprite_insignias[pos_img_insignias],
            (g[1] * tamanho_celula, g[0] * tamanho_celula),
        )
        pos_img_insignias += 1

    for p, tipo in pokemons_na_tela.items():
        tela.blit(sprite_pokemon[tipo], (p[1] * tamanho_celula, p[0] * tamanho_celula))

    tela.blit(
        sprite_jogador, (jogador[1] * tamanho_celula, jogador[0] * tamanho_celula)
    )

    pygame.display.flip()


def main():
    mapa, posicao_jogador, ginasios, pokemons_na_posicao = gerar_mapa()
    pokemons_visiveis = []
    pokemons_capturados = []
    contador_pokemons = {"agua": 0, "eletrico": 0, "fogo": 0, "voador": 0, "grama": 0}
    insignias = 0
    rodando = True
    tempo_inicio = time.time()
    custo_total = 0

    while rodando:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                rodando = False

        novos_pokemons = radar_pokedex(posicao_jogador, pokemons_na_posicao)
        for p in novos_pokemons:
            if p not in pokemons_visiveis:
                pokemons_visiveis.append(p)

        pokemons_na_tela = {}
        if pokemons_visiveis:
            proximo_pokemon = pokemons_visiveis.pop(0)
            tipo_pokemon = pokemons_na_posicao[proximo_pokemon]
            pokemons_na_tela[proximo_pokemon] = tipo_pokemon
            del pokemons_na_posicao[proximo_pokemon]

            caminho, custo = a_estrela(
                mapa, posicao_jogador, proximo_pokemon, pokemons_capturados
            )
            custo_total += custo
            for pos in caminho:
                desenhar_mapa(
                    mapa, pos, ginasios, pokemons_visiveis, caminho, pokemons_na_tela
                )
                pygame.time.delay(100)
            pokemons_capturados.append(tipo_pokemon)
            contador_pokemons[tipo_pokemon] += 1
            posicao_jogador = proximo_pokemon

        elif ginasios and insignias < 9:
            proximo_ginasio = ginasios.pop(0)
            caminho, custo = a_estrela(
                mapa, posicao_jogador, proximo_ginasio, pokemons_capturados
            )
            custo_total += custo
            for pos in caminho:
                desenhar_mapa(mapa, pos, ginasios, pokemons_visiveis, caminho)
                pygame.time.delay(100)
            insignias += 1
            posicao_jogador = proximo_ginasio
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
