import pygame
import math
import random
import sys

pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)

LARGURA = 800
ALTURA  = 500
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Venn Runner")
relogio = pygame.time.Clock()

def gerar_som(freq, duracao, vol=0.3, tipo="sine"):
    sr  = 44100
    n   = int(sr * duracao)
    buf = bytearray(n * 2)
    for i in range(n):
        t    = i / sr
        fade = min(1.0, (n - i) / (sr * 0.04))
        if tipo == "sine":
            v = math.sin(2 * math.pi * freq * t)
        elif tipo == "square":
            v = 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0
        else:
            v = math.sin(2 * math.pi * freq * t)
        s = int(32767 * vol * fade * v)
        s = max(-32768, min(32767, s))
        buf[i * 2]     = s & 0xFF
        buf[i * 2 + 1] = (s >> 8) & 0xFF
    return pygame.mixer.Sound(buffer=bytes(buf))

try:
    SOM_MOEDA  = gerar_som(880,  0.12, 0.35)
    SOM_ERRO   = gerar_som(200,  0.25, 0.30)
    SOM_DANO   = gerar_som(150,  0.30, 0.40, "square")
    SOM_PULO   = gerar_som(440,  0.10, 0.20)
    SOM_FASE   = gerar_som(660,  0.35, 0.35)
    SOM_GAME   = gerar_som(120,  0.50, 0.40, "square")
    SONS_OK    = True
except Exception:
    SONS_OK    = False

def tocar(som):
    if SONS_OK:
        som.play()

PRETO   = (0, 0, 0)
BRANCO  = (255, 255, 255)
CINZA   = (50, 50, 75)
AMARELO = (255, 220, 50)
VERDE   = (60, 210, 90)
VERMELHO= (210, 60, 60)
AZUL    = (80, 150, 255)
ROSA    = (255, 80, 80)
ROXO    = (200, 120, 255)
LARANJA = (255, 170, 50)
FUNDO1  = (15, 15, 35)
FUNDO2  = (30, 30, 60)

fonte_grande  = pygame.font.SysFont("Arial", 48, bold=True)
fonte_media   = pygame.font.SysFont("Arial", 26, bold=True)
fonte_pequena = pygame.font.SysFont("Arial", 18)
fonte_mini    = pygame.font.SysFont("Arial", 14)

CHAO_Y = ALTURA - 70

FASES = [
    ["FACIL",    3, "uniao"],
    ["MEDIO",    4, "intersecao"],
    ["DIFICIL",  5, "diferenca"],
]

PONTOS_PARA_PASSAR = 10


def desenhar_personagem(cx, cy, frame, no_chao, invinc, piscar):
    if invinc > 0 and piscar < 3:
        return

    pygame.draw.ellipse(tela, (10, 10, 25), (cx - 15, cy + 2, 30, 8))

    if no_chao:
        a1 = int(math.sin(frame / 24 * 2 * math.pi) * 9)
    else:
        a1 = 0
    a2 = -a1

    joelho_e = (cx - 6 + a1, cy - 8)
    pe_e     = (cx - 6 + a1 * 2, cy)
    pygame.draw.line(tela, (30, 30, 80), (cx - 6, cy - 16), joelho_e, 6)
    pygame.draw.line(tela, (30, 30, 80), joelho_e, pe_e, 6)
    pygame.draw.ellipse(tela, (20, 15, 10), (pe_e[0] - 7, pe_e[1] - 3, 14, 7))

    joelho_d = (cx + 6 + a2, cy - 8)
    pe_d     = (cx + 6 + a2 * 2, cy)
    pygame.draw.line(tela, (30, 30, 80), (cx + 6, cy - 16), joelho_d, 6)
    pygame.draw.line(tela, (30, 30, 80), joelho_d, pe_d, 6)
    pygame.draw.ellipse(tela, (20, 15, 10), (pe_d[0] - 7, pe_d[1] - 3, 14, 7))

    pygame.draw.rect(tela, (50, 110, 210), (cx - 11, cy - 40, 22, 22), border_radius=4)
    pygame.draw.rect(tela, BRANCO, (cx - 4, cy - 40, 8, 5))

    if no_chao:
        b1 = int(math.sin(frame / 24 * 2 * math.pi) * 7)
        pygame.draw.line(tela, (50, 110, 210), (cx - 11, cy - 35), (cx - 19, cy - 25 + b1), 5)
        pygame.draw.line(tela, (50, 110, 210), (cx + 11, cy - 35), (cx + 19, cy - 25 - b1), 5)
    else:
        pygame.draw.line(tela, (230, 185, 130), (cx - 11, cy - 35), (cx - 20, cy - 45), 5)
        pygame.draw.line(tela, (230, 185, 130), (cx + 11, cy - 35), (cx + 20, cy - 45), 5)

    pygame.draw.rect(tela, (230, 185, 130), (cx - 3, cy - 44, 6, 6))

    pygame.draw.ellipse(tela, (230, 185, 130), (cx - 12, cy - 62, 24, 20))
    pygame.draw.ellipse(tela, (55, 30, 8),     (cx - 12, cy - 64, 24, 13))

    pygame.draw.circle(tela, PRETO,  (cx + 5, cy - 54), 3)
    pygame.draw.circle(tela, BRANCO, (cx + 7, cy - 56), 1)
    pygame.draw.arc(tela, (150, 70, 50),
                    (cx - 4, cy - 50, 9, 5), math.pi, 2 * math.pi, 2)

    pygame.draw.ellipse(tela, (230, 185, 130), (cx - 14, cy - 57, 4, 7))


estrelas = []
for i in range(60):
    ex = random.randint(0, LARGURA)
    ey = random.randint(0, CHAO_Y - 10)
    er = random.randint(1, 3)
    estrelas.append([ex, ey, er])


def desenhar_fundo(offset):
    for y in range(CHAO_Y):
        t = y / CHAO_Y
        r = int(18 + 30 * t)
        g = int(8  + 20 * t)
        b = int(50 + 60 * t)
        pygame.draw.line(tela, (r, g, b), (0, y), (LARGURA, y))

    for estrela in estrelas:
        bx = int((estrela[0] - offset * 0.03) % LARGURA)
        brilho = 160 + estrela[2] * 25
        pygame.draw.circle(tela, (brilho, brilho, 255), (bx, estrela[1]), estrela[2])

    pontos_mont = []
    for i in range(0, LARGURA + 120, 80):
        bx = int((i - offset * 0.08) % (LARGURA + 200))
        alt = 80 + ((bx * 7 + 3) % 90)
        pontos_mont.append((bx, CHAO_Y - alt))
    pontos_mont.append((LARGURA, CHAO_Y))
    pontos_mont.append((0, CHAO_Y))
    if len(pontos_mont) > 2:
        pygame.draw.polygon(tela, (30, 22, 65), pontos_mont)

    pygame.draw.rect(tela, (35, 120, 45), (0, CHAO_Y,      LARGURA, 8))
    pygame.draw.rect(tela, (55,  80, 35), (0, CHAO_Y + 8,  LARGURA, 20))
    pygame.draw.rect(tela, (45,  60, 28), (0, CHAO_Y + 28, LARGURA, ALTURA - CHAO_Y))

    for i in range(0, LARGURA + 54, 54):
        bx = int((i - offset * 0.5) % (LARGURA + 54))
        pygame.draw.rect(tela, (65, 95, 40), (bx, CHAO_Y + 9, 52, 19), 1)


def ponto_dentro_circulo(px, py, cx, cy, raio):
    distancia = math.sqrt((px - cx) ** 2 + (py - cy) ** 2)
    if distancia <= raio:
        return True
    else:
        return False


def zona_do_numero(numero, conj_a, conj_b):
    em_a = numero in conj_a
    em_b = numero in conj_b
    if em_a and em_b:
        return "intersecao"
    if em_a:
        return "uniao"
    if em_b:
        return "uniao"
    return "fora"


def numero_correto(numero, conj_a, conj_b, zona_alvo):
    zona = zona_do_numero(numero, conj_a, conj_b)
    if zona_alvo == "uniao":
        if zona == "uniao" or zona == "intersecao":
            return True
        else:
            return False
    if zona_alvo == "intersecao":
        if zona == "intersecao":
            return True
        else:
            return False
    if zona_alvo == "diferenca":
        if numero in conj_a and numero not in conj_b:
            return True
        else:
            return False
    return False


def topo_circulo_em_x(px, cx, cy, raio):
    dx = abs(px - cx)
    if dx <= raio:
        topo = cy - math.sqrt(raio ** 2 - dx ** 2)
        return topo
    else:
        return None


def criar_obstaculo(x, zona_alvo):
    raio = random.randint(55, 70)
    dist = int(raio * 1.3)
    cx   = float(x)
    cx_a = cx - dist // 2
    cx_b = cx + dist // 2
    cy   = CHAO_Y - raio

    conj_a = set(random.sample(range(1, 11), random.randint(3, 5)))
    conj_b = set(random.sample(range(6, 16), random.randint(3, 5)))

    todos    = list(conj_a | conj_b)
    extras   = [n for n in range(1, 16) if n not in (conj_a | conj_b)]
    corretos = [n for n in todos if numero_correto(n, conj_a, conj_b, zona_alvo)]
    errados  = [n for n in todos if not numero_correto(n, conj_a, conj_b, zona_alvo)]
    if extras:
        errados += random.sample(extras, min(2, len(extras)))

    random.shuffle(corretos)
    random.shuffle(errados)

    moedas   = []
    start_x  = cx_b + raio + 130
    altura_chao = CHAO_Y - 48

    corretos = corretos[:2]
    errados  = errados[:2]

    while len(corretos) < 2:
        corretos.append(corretos[0] if corretos else 1)
    while len(errados) < 2:
        errados.append(errados[0] if errados else 9)

    sequencia = [
        (corretos[0], True),
        (errados[0],  False),
        (corretos[1], True),
        (errados[1],  False),
    ]

    for i, (n, ok) in enumerate(sequencia):
        moedas.append({
            "x"       : float(start_x + i * 130),
            "y"       : float(altura_chao),
            "valor"   : n,
            "correto" : ok,
            "coletado": False,
            "flutua"  : 0.0,
        })

    ob = {
        "cx": cx, "cx_a": cx_a, "cx_b": cx_b, "cy": cy,
        "raio": raio, "conj_a": conj_a, "conj_b": conj_b,
        "zona_alvo": zona_alvo, "moedas": moedas,
    }
    return ob


def mover_obstaculo(ob, vel):
    ob["cx"]   -= vel
    ob["cx_a"] -= vel
    ob["cx_b"] -= vel
    for m in ob["moedas"]:
        m["x"] -= vel


def obstaculo_fora(ob):
    if ob["cx_b"] + ob["raio"] < -30:
        return True
    else:
        return False


def desenhar_obstaculo(ob):
    raio  = ob["raio"]
    cx_a  = int(ob["cx_a"])
    cx_b  = int(ob["cx_b"])
    cy    = int(ob["cy"])
    cx    = int(ob["cx"])
    zona_alvo = ob.get("zona_alvo", "")

    if zona_alvo == "uniao":
        formula  = "A U B"
        cor_form = (120, 210, 255)
        cor_a    = (60, 130, 255, 120)
        cor_b    = (60, 200, 255, 100)
        borda_a  = (100, 170, 255)
        borda_b  = (60,  200, 255)
    elif zona_alvo == "intersecao":
        formula  = "A ∩ B"
        cor_form = (220, 150, 255)
        cor_a    = (160, 60, 255, 110)
        cor_b    = (200, 80, 255, 100)
        borda_a  = (190, 100, 255)
        borda_b  = (220, 130, 255)
    else:
        formula  = "A - B"
        cor_form = (255, 200, 60)
        cor_a    = (255, 160, 30, 110)
        cor_b    = (255, 120, 30, 90)
        borda_a  = (255, 190, 50)
        borda_b  = (255, 140, 40)

    s = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
    pygame.draw.circle(s, cor_a, (cx_a, cy), raio)
    pygame.draw.circle(s, cor_b, (cx_b, cy), raio)
    pygame.draw.circle(s, (*cor_form, 25), (cx_a - raio//4, cy - raio//4), raio//2)
    pygame.draw.circle(s, (*cor_form, 20), (cx_b - raio//4, cy - raio//4), raio//2)
    tela.blit(s, (0, 0))

    pygame.draw.circle(tela, borda_a, (cx_a, cy), raio,     4)
    pygame.draw.circle(tela, borda_b, (cx_b, cy), raio,     4)
    pygame.draw.circle(tela, BRANCO,  (cx_a, cy), raio - 5, 1)
    pygame.draw.circle(tela, BRANCO,  (cx_b, cy), raio - 5, 1)

    la = fonte_media.render("A", True, borda_a)
    lb = fonte_media.render("B", True, borda_b)
    tela.blit(la, (cx_a - raio + 8,                   cy - raio + 6))
    tela.blit(lb, (cx_b + raio - lb.get_width() - 8,  cy - raio + 6))

    conj_a_sorted = sorted(ob["conj_a"])
    conj_b_sorted = sorted(ob["conj_b"])
    ta1 = fonte_mini.render(str(conj_a_sorted[:3]), True, BRANCO)
    ta2 = fonte_mini.render(str(conj_a_sorted[3:]) if len(conj_a_sorted) > 3 else "", True, BRANCO)
    tb1 = fonte_mini.render(str(conj_b_sorted[:3]), True, BRANCO)
    tb2 = fonte_mini.render(str(conj_b_sorted[3:]) if len(conj_b_sorted) > 3 else "", True, BRANCO)
    tela.blit(ta1, (cx_a - ta1.get_width() // 2, cy + 6))
    if ta2.get_width() > 4:
        tela.blit(ta2, (cx_a - ta2.get_width() // 2, cy + 22))
    tela.blit(tb1, (cx_b - tb1.get_width() // 2, cy + 6))
    if tb2.get_width() > 4:
        tela.blit(tb2, (cx_b - tb2.get_width() // 2, cy + 22))

    tf = fonte_media.render(formula, True, cor_form)
    tela.blit(tf, (cx - tf.get_width() // 2, cy - raio + 28))


def desenhar_moeda(m):
    if m["coletado"]:
        return
    ex = int(m["x"])
    ey = int(m["y"])
    r  = 22

    ey_draw = ey

    s = pygame.Surface((r*2+10, 10), pygame.SRCALPHA)
    pygame.draw.ellipse(s, (0, 0, 0, 60), (0, 0, r*2+10, 10))
    tela.blit(s, (ex - r - 5, ey_draw + r - 2))

    pygame.draw.circle(tela, (140, 100,  0),  (ex, ey_draw), r + 3)
    pygame.draw.circle(tela, (255, 200,  20), (ex, ey_draw), r + 1)
    pygame.draw.circle(tela, (255, 225,  80), (ex, ey_draw), r - 2)
    pygame.draw.circle(tela, (255, 248, 180), (ex - r//3, ey_draw - r//3), r // 3)

    txt = fonte_media.render(str(m["valor"]), True, (80, 45, 0))
    tela.blit(txt, (ex - txt.get_width() // 2, ey_draw - txt.get_height() // 2))


def desenhar_hud(vidas, pontos_fase, nome_fase, zona_alvo, pontos_total=0):
    painel = pygame.Surface((LARGURA, 52), pygame.SRCALPHA)
    pygame.draw.rect(painel, (8, 8, 25, 200), (0, 0, LARGURA, 52), border_radius=0)
    tela.blit(painel, (0, 0))
    pygame.draw.line(tela, (80, 80, 160), (0, 51), (LARGURA, 51), 2)

    for i in range(5):
        cor = (220, 50, 80) if i < vidas else (55, 40, 55)
        hx = 14 + i * 30
        hy = 14
        pygame.draw.polygon(tela, cor, [
            (hx+9, hy+2), (hx+2, hy-4), (hx-3, hy),
            (hx-3, hy+5), (hx+9, hy+15),
            (hx+21, hy+5), (hx+21, hy),
            (hx+16, hy-4)
        ])
        if i < vidas:
            pygame.draw.polygon(tela, (255, 100, 120), [
                (hx+9, hy+4), (hx+4, hy), (hx+9, hy+12)
            ])

    tp = fonte_media.render("⭐ " + str(pontos_total), True, AMARELO)
    tela.blit(tp, (LARGURA // 2 - tp.get_width() // 2, 12))

    tf = fonte_mini.render("Fase: " + nome_fase, True, (160, 220, 160))
    tela.blit(tf, (LARGURA - tf.get_width() - 10, 6))

    prog_txt = fonte_mini.render("Progresso: " + str(pontos_fase) + "/" + str(PONTOS_PARA_PASSAR), True, BRANCO)
    tela.blit(prog_txt, (LARGURA - prog_txt.get_width() - 10, 22))

    tp2 = fonte_mini.render("P: PAUSAR", True, (180, 180, 220))
    tela.blit(tp2, (10, 36))

    pygame.draw.rect(tela, (40, 40, 90), (LARGURA - 90, 8, 80, 34), border_radius=8)
    pygame.draw.rect(tela, (120, 120, 200), (LARGURA - 90, 8, 80, 34), 2, border_radius=8)
    sp = fonte_media.render("II", True, BRANCO)
    tela.blit(sp, (LARGURA - 90 + 40 - sp.get_width()//2, 14))

    bx = LARGURA - 160
    by = 38
    bw = 150
    bh = 8
    pygame.draw.rect(tela, (30, 30, 60), (bx, by, bw, bh), border_radius=4)
    prog = min(pontos_fase / PONTOS_PARA_PASSAR, 1)
    pygame.draw.rect(tela, (80, 220, 100), (bx, by, int(bw * prog), bh), border_radius=4)
    pygame.draw.rect(tela, (120, 255, 140), (bx, by, bw, bh), 1, border_radius=4)


def tela_menu():
    t = 0
    estrelas_menu = [(random.randint(0, LARGURA), random.randint(0, ALTURA),
                      random.randint(1, 2)) for _ in range(120)]

    while True:
        t += 1

        for y in range(ALTURA):
            frac = y / ALTURA
            r = int(8  + 18 * frac)
            g = int(5  + 10 * frac)
            b = int(28 + 40 * frac)
            pygame.draw.line(tela, (r, g, b), (0, y), (LARGURA, y))

        for (sx, sy, sr) in estrelas_menu:
            brilho = 120 + int(80 * abs(math.sin(t * 0.02 + sx)))
            pygame.draw.circle(tela, (brilho, brilho, 255), (sx, sy), sr)

        pygame.draw.rect(tela, (30, 100, 38), (0, ALTURA - 55, LARGURA, 8))
        pygame.draw.rect(tela, (45,  65, 28), (0, ALTURA - 47, LARGURA, 47))
        for i in range(0, LARGURA, 54):
            bx = (i + t * 2) % (LARGURA + 54)
            pygame.draw.rect(tela, (55, 80, 35), (bx, ALTURA - 46, 52, 18), 1)

        for i in range(5):
            mx = 80 + i * 150
            my = ALTURA - 90
            flut = math.sin(t * 0.06 + i * 1.2) * 8
            r = 18
            pygame.draw.circle(tela, (140, 100, 0),   (mx, int(my + flut)), r + 3)
            pygame.draw.circle(tela, (255, 200, 20),  (mx, int(my + flut)), r + 1)
            pygame.draw.circle(tela, (255, 225, 80),  (mx, int(my + flut)), r - 2)
            pygame.draw.circle(tela, (255, 248, 180), (mx - 5, int(my + flut) - 5), 5)
            num = fonte_mini.render(str(i + 3), True, (80, 45, 0))
            tela.blit(num, (mx - num.get_width() // 2, int(my + flut) - num.get_height() // 2))

        painel = pygame.Surface((580, 330), pygame.SRCALPHA)
        pygame.draw.rect(painel, (10, 10, 35, 200), (0, 0, 580, 330), border_radius=20)
        pygame.draw.rect(painel, (80, 80, 200, 120), (0, 0, 580, 330), 2, border_radius=20)
        tela.blit(painel, (LARGURA // 2 - 290, 30))

        pulso = 0.85 + 0.15 * abs(math.sin(t * 0.04))
        cor_t = (int(255 * pulso), int(210 * pulso), int(30 * pulso))
        titulo1 = fonte_grande.render("VENN", True, cor_t)
        titulo2 = fonte_grande.render("RUNNER", True, cor_t)
        sombra1 = fonte_grande.render("VENN",   True, (60, 40, 0))
        sombra2 = fonte_grande.render("RUNNER", True, (60, 40, 0))
        cx = LARGURA // 2
        tela.blit(sombra1, (cx - titulo1.get_width() // 2 + 3, 43))
        tela.blit(sombra2, (cx - titulo2.get_width() // 2 + 3, 90))
        tela.blit(titulo1, (cx - titulo1.get_width() // 2, 40))
        tela.blit(titulo2, (cx - titulo2.get_width() // 2, 87))

        pygame.draw.line(tela, (80, 80, 200), (cx - 220, 145), (cx + 220, 145), 2)

        cards = [
            ("⬆  PULAR",     "Espaço, seta cima ou W", (60, 120, 220)),
            ("🪙  COLETAR",   "Pule nas moedas douradas", (200, 160, 0)),
        ]
        for i, (icone, desc, cor) in enumerate(cards):
            bx = cx - 175 + i * 180
            by = 158
            pygame.draw.rect(tela, (*cor, 60) if len(cor) == 3 else cor,
                             (bx, by, 165, 62), border_radius=10)
            pygame.draw.rect(tela, cor, (bx, by, 165, 62), 2, border_radius=10)
            si = fonte_pequena.render(icone, True, BRANCO)
            sd = fonte_mini.render(desc, True, (200, 200, 220))
            tela.blit(si, (bx + 83 - si.get_width() // 2, by + 10))
            tela.blit(sd, (bx + 83 - sd.get_width() // 2, by + 36))

        pygame.draw.line(tela, (60, 60, 140), (cx - 220, 232), (cx + 220, 232), 1)
        fases_info = [
            ("FÁCIL",   "A ∪ B",  (100, 200, 255)),
            ("MÉDIO",   "A ∩ B",  (190, 120, 255)),
            ("DIFÍCIL", "A − B",  (255, 170, 50)),
        ]
        fl = fonte_mini.render("Fases:", True, (160, 160, 200))
        tela.blit(fl, (cx - fl.get_width() // 2, 240))
        for i, (nome, form, cor) in enumerate(fases_info):
            bx = cx - 220 + i * 152
            pygame.draw.rect(tela, (20, 20, 50), (bx, 260, 140, 38), border_radius=8)
            pygame.draw.rect(tela, cor, (bx, 260, 140, 38), 2, border_radius=8)
            sn = fonte_mini.render(nome, True, cor)
            sf = fonte_mini.render(form, True, BRANCO)
            tela.blit(sn, (bx + 70 - sn.get_width() // 2, 266))
            tela.blit(sf, (bx + 70 - sf.get_width() // 2, 283))

        pulso2 = abs(math.sin(t * 0.05))
        cor_btn = (int(40 + 20 * pulso2), int(160 + 40 * pulso2), int(60 + 20 * pulso2))
        pygame.draw.rect(tela, (20, 80, 30), (cx - 130, 320, 260, 48), border_radius=14)
        pygame.draw.rect(tela, cor_btn,      (cx - 130, 320, 260, 48), 3, border_radius=14)
        sb = fonte_media.render("▶  ENTER para jogar", True, BRANCO)
        tela.blit(sb, (cx - sb.get_width() // 2, 333))

        pygame.display.flip()
        relogio.tick(60)

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if ev.key == pygame.K_RETURN:
                    return


def tela_passou_de_fase(fase_atual, pontos):
    t = 0
    if fase_atual >= len(FASES) - 1:
        mensagem = "VOCE VENCEU!"
        sub      = "Completou todas as fases!"
        proxima  = None
    else:
        proxima  = fase_atual + 1
        mensagem = "FASE CONCLUIDA!"
        sub      = "Proximo nivel: " + FASES[proxima][0]

    while True:
        tela.fill(FUNDO1)
        for i in range(0, LARGURA, 80):
            bx = int((i + t * 2) % LARGURA)
            pygame.draw.line(tela, (25, 25, 55), (bx, 0), (bx, ALTURA), 1)

        pulso = abs(math.sin(t * 0.06))
        r = int(100 + 155 * pulso)

        msg = fonte_grande.render(mensagem, True, VERDE)
        sb  = fonte_media.render(sub, True, BRANCO)
        pts = fonte_pequena.render("Pontos acumulados: " + str(pontos), True, AMARELO)
        cnt = fonte_media.render("[ ENTER para continuar ]", True, (r, r, r))

        tela.blit(msg, (LARGURA // 2 - msg.get_width() // 2, 145))
        tela.blit(sb,  (LARGURA // 2 - sb.get_width()  // 2, 225))
        tela.blit(pts, (LARGURA // 2 - pts.get_width() // 2, 268))
        tela.blit(cnt, (LARGURA // 2 - cnt.get_width() // 2, 325))

        pygame.display.flip()
        relogio.tick(60)
        t += 1

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_RETURN:
                    return proxima


def tela_game_over(pontos):
    t = 0
    while True:
        tela.fill(FUNDO1)
        desenhar_fundo(t)
        t += 1

        go  = fonte_grande.render("GAME OVER", True, VERMELHO)
        pts = fonte_media.render("Pontos: " + str(pontos), True, AMARELO)
        rei = fonte_pequena.render("ENTER = jogar de novo   |   ESC = menu",
                                   True, (170, 170, 215))

        tela.blit(go,  (LARGURA // 2 - go.get_width()  // 2, 155))
        tela.blit(pts, (LARGURA // 2 - pts.get_width() // 2, 240))
        tela.blit(rei, (LARGURA // 2 - rei.get_width() // 2, 305))

        pygame.display.flip()
        relogio.tick(60)

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    return False
                if ev.key == pygame.K_RETURN:
                    return True


def jogar(indice_fase, pontos_antes):
    nome_fase  = FASES[indice_fase][0]
    velocidade = FASES[indice_fase][1]
    zona_alvo  = FASES[indice_fase][2]

    jog_x       = 150.0
    jog_y       = float(CHAO_Y)
    jog_vy      = 0.0
    jog_no_chao = True
    jog_no_obst = False
    jog_vidas   = 5
    jog_invinc  = 0
    jog_piscar  = 0
    jog_frame   = 0

    pontos      = pontos_antes
    pontos_fase = 0

    obstaculos   = []
    moedas_livres = []
    offset       = 0.0
    proximo_x    = LARGURA + 250
    parts        = []

    pausado     = False

    while True:
        relogio.tick(60)

        RECT_PAUSE = pygame.Rect(LARGURA - 90, 8, 80, 34)

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    return pontos, None
                if ev.key == pygame.K_p:
                    pausado = not pausado
                if not pausado:
                    if ev.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                        if jog_no_chao or jog_no_obst:
                            jog_vy      = -15
                            jog_no_chao = False
                            jog_no_obst = False
                            tocar(SOM_PULO)
            if ev.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if RECT_PAUSE.collidepoint(mx, my):
                    pausado = not pausado
                if pausado:
                    RECT_CONT = pygame.Rect(LARGURA//2 - 110, ALTURA//2 + 50, 220, 48)
                    if RECT_CONT.collidepoint(mx, my):
                        pausado = False

        if pausado:
            painel_p = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
            pygame.draw.rect(painel_p, (0, 0, 0, 150), (0, 0, LARGURA, ALTURA))
            tela.blit(painel_p, (0, 0))
            tp1 = fonte_grande.render("II  PAUSADO", True, AMARELO)
            tela.blit(tp1, (LARGURA//2 - tp1.get_width()//2, ALTURA//2 - 60))
            tp2 = fonte_media.render("Pressione P ou clique abaixo", True, CINZA)
            tela.blit(tp2, (LARGURA//2 - tp2.get_width()//2, ALTURA//2 - 10))
            RECT_CONT = pygame.Rect(LARGURA//2 - 110, ALTURA//2 + 50, 220, 48)
            pygame.draw.rect(tela, (40, 160, 60), RECT_CONT, border_radius=12)
            pygame.draw.rect(tela, VERDE,         RECT_CONT, 2, border_radius=12)
            sc = fonte_media.render("▶  CONTINUAR", True, BRANCO)
            tela.blit(sc, (LARGURA//2 - sc.get_width()//2, RECT_CONT.y + 10))
            pygame.display.flip()
            continue

        jog_vy += 0.75
        jog_y  += jog_vy
        jog_no_chao = False
        jog_no_obst = False

        if jog_y >= CHAO_Y:
            jog_y       = float(CHAO_Y)
            jog_vy      = 0
            jog_no_chao = True

        if jog_invinc > 0:
            jog_invinc -= 1

        jog_piscar = (jog_piscar + 1) % 6
        jog_frame  = (jog_frame  + 1) % 24

        offset    += velocidade
        proximo_x -= velocidade

        if len(obstaculos) == 0 or obstaculos[-1]["cx"] < LARGURA + 100:
            if proximo_x < LARGURA + 200:
                novo = criar_obstaculo(proximo_x + LARGURA, zona_alvo)
                obstaculos.append(novo)
                proximo_x = LARGURA + random.randint(800, 1100)

        for ob in obstaculos:
            mover_obstaculo(ob, velocidade)

        for ob in obstaculos:
            if obstaculo_fora(ob):
                for m in ob["moedas"]:
                    if not m["coletado"]:
                        moedas_livres.append(m)

        obstaculos = [ob for ob in obstaculos if not obstaculo_fora(ob)]

        for m in moedas_livres:
            m["x"]      -= velocidade
            m["flutua"] += 0.07

        moedas_livres = [m for m in moedas_livres if m["x"] > -60]

        jog_cx = int(jog_x)
        jog_cy = int(jog_y)

        for ob in obstaculos:
            raio  = ob["raio"]
            cx_a  = ob["cx_a"]
            cx_b  = ob["cx_b"]
            cy_ob = ob["cy"]

            topo_a = topo_circulo_em_x(jog_cx, cx_a, cy_ob, raio)
            topo_b = topo_circulo_em_x(jog_cx, cx_b, cy_ob, raio)
            topo   = None
            if topo_a is not None and topo_b is not None:
                topo = min(topo_a, topo_b)
            elif topo_a is not None:
                topo = topo_a
            elif topo_b is not None:
                topo = topo_b

            pousando = False
            if topo is not None:
                if jog_vy >= 0 and (jog_y - jog_vy) <= topo + 5 and jog_y >= topo - 5:
                    jog_y       = topo
                    jog_vy      = 0
                    jog_no_obst = True
                    pousando    = True

            meio_y   = jog_cy - 22
            dentro_a = ponto_dentro_circulo(jog_cx, meio_y, cx_a, cy_ob, raio)
            dentro_b = ponto_dentro_circulo(jog_cx, meio_y, cx_b, cy_ob, raio)

            borda_esq = cx_a - raio
            if borda_esq < jog_cx + 28 and not pousando and not jog_no_obst:
                delta = (jog_cx + 28) - borda_esq
                ob["cx"]   += delta
                ob["cx_a"] += delta
                ob["cx_b"] += delta
                for m in ob["moedas"]:
                    m["x"] += delta

            for m in ob["moedas"]:
                if m["coletado"]:
                    continue
                ey_m = m["y"] + int(math.sin(m["flutua"]) * 6)
                dist = math.sqrt((jog_cx - m["x"]) ** 2 + (jog_cy - 30 - ey_m) ** 2)
                if dist < 34:
                    m["coletado"] = True
                    if m["correto"]:
                        pontos      += 10
                        pontos_fase += 1
                        tocar(SOM_MOEDA)
                        for k in range(18):
                            parts.append([float(m["x"]), float(ey_m),
                                          random.uniform(-3, 3), random.uniform(-5, -1),
                                          random.randint(18, 32), (255, 215, 30)])
                    else:
                        jog_vidas  -= 1
                        jog_invinc  = 70
                        tocar(SOM_DANO)
                        for k in range(14):
                            parts.append([float(m["x"]), float(ey_m),
                                          random.uniform(-3, 3), random.uniform(-5, -1),
                                          random.randint(18, 32), (210, 60, 60)])
        for m in moedas_livres:
            if m["coletado"]:
                continue
            ey_m = m["y"] + int(math.sin(m["flutua"]) * 6)
            dist = math.sqrt((jog_cx - m["x"]) ** 2 + (jog_cy - 30 - ey_m) ** 2)
            if dist < 34:
                m["coletado"] = True
                if m["correto"]:
                    pontos      += 10
                    pontos_fase += 1
                    tocar(SOM_MOEDA)
                    for k in range(18):
                        parts.append([float(m["x"]), float(ey_m),
                                      random.uniform(-3, 3), random.uniform(-5, -1),
                                      random.randint(18, 32), (255, 215, 30)])
                else:
                        jog_vidas  -= 1
                        jog_invinc  = 70
                        tocar(SOM_DANO)
                        for k in range(14):
                            parts.append([float(m["x"]), float(ey_m),
                                          random.uniform(-3, 3), random.uniform(-5, -1),
                                          random.randint(18, 32), (210, 60, 60)])

        novas_parts = []
        for p in parts:
            p[0] += p[2]
            p[1] += p[3]
            p[3] += 0.22
            p[4] -= 1
            if p[4] > 0:
                novas_parts.append(p)
        parts = novas_parts

        desenhar_fundo(offset)

        for ob in obstaculos:
            desenhar_obstaculo(ob)
            for m in ob["moedas"]:
                desenhar_moeda(m)

        for m in moedas_livres:
            desenhar_moeda(m)

        for p in parts:
            a = max(0, int(255 * p[4] / 36))
            s = pygame.Surface((8, 8), pygame.SRCALPHA)
            pygame.draw.circle(s, (*p[5], a), (4, 4), 4)
            tela.blit(s, (int(p[0]) - 4, int(p[1]) - 4))

        desenhar_personagem(jog_cx, int(jog_y), jog_frame,
                            jog_no_chao or jog_no_obst,
                            jog_invinc, jog_piscar)

        desenhar_hud(jog_vidas, pontos_fase, nome_fase, zona_alvo, pontos)

        pygame.display.flip()

        if pontos_fase >= PONTOS_PARA_PASSAR:
            tocar(SOM_FASE)
            return pontos, indice_fase

        if jog_vidas <= 0:
            tocar(SOM_GAME)
            return pontos, None

    return pontos, None


while True:
    tela_menu()

    fase_atual = 0
    pontos     = 0

    jogando = True
    while jogando:
        pontos, resultado = jogar(fase_atual, pontos)

        if resultado is None:
            jogar_de_novo = tela_game_over(pontos)
            if jogar_de_novo:
                fase_atual = 0
                pontos     = 0
            else:
                jogando = False
        else:
            proxima = tela_passou_de_fase(fase_atual, pontos)
            if proxima is None:
                tela_game_over(pontos)
                jogando = False
            else:
                fase_atual = proxima