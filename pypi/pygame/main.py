import pygame
import math

# Configurações da Janela
WIDTH, HEIGHT = 800, 600
FPS = 60

# Configurações do Raycasting
FOV = math.pi / 3
HALF_FOV = FOV / 2
NUM_RAYS = 160
MAX_DEPTH = 800
DELTA_ANGLE = FOV / NUM_RAYS
SCALE = WIDTH // NUM_RAYS
SCREEN_DIST = (WIDTH // 2) / math.tan(HALF_FOV)

# Mapa do jogo (1 = Parede, 0 = Espaço Vazio)
MAP = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
    [1, 0, 1, 0, 1, 1, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1],
    [1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1],
    [1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]
TILE_SIZE = 50

# Jogador
player_x, player_y = 150, 150
player_angle = 0
player_speed = 3
rot_speed = 0.04

# Sistema de Disparo
is_shooting = False
shoot_timer = 0

# Buffer de distância para checar se paredes cobrem os inimigos
depth_buffer = [MAX_DEPTH] * NUM_RAYS

# Classe do Inimigo
class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.alive = True
        self.hp = 100

    def update(self):
        if not self.alive:
            return
        # Perseguir o jogador suavemente
        dx = player_x - self.x
        dy = player_y - self.y
        dist = math.hypot(dx, dy)
        if dist > 35: # Distância mínima de parada
            speed = 0.8
            nx = self.x + (dx / dist) * speed
            ny = self.y + (dy / dist) * speed
            # Colisão simples com mapa
            if MAP[int(ny // TILE_SIZE)][int(nx // TILE_SIZE)] == 0:
                self.x = nx
                self.y = ny

# Criando lista de inimigos pelo mapa
enemies = [
    Enemy(400, 200),
    Enemy(600, 300),
    Enemy(300, 350)
]

# Inicialização Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("DOOM Raycaster - Arma e Inimigos")
clock = pygame.time.Clock()

def ray_casting():
    global depth_buffer
    depth_buffer = [MAX_DEPTH] * NUM_RAYS
    ray_angle = player_angle - HALF_FOV

    for ray in range(NUM_RAYS):
        for depth in range(1, MAX_DEPTH, 2):
            target_x = player_x + depth * math.cos(ray_angle)
            target_y = player_y + depth * math.sin(ray_angle)

            col = int(target_x // TILE_SIZE)
            row = int(target_y // TILE_SIZE)

            if 0 <= row < len(MAP) and 0 <= col < len(MAP[0]):
                if MAP[row][col] == 1:
                    depth_corrected = depth * math.cos(player_angle - ray_angle)
                    depth_buffer[ray] = depth_corrected # Salva profundidade no buffer

                    proj_height = (TILE_SIZE * SCREEN_DIST) / (depth_corrected + 0.0001)
                    color_val = max(10, min(220, int(255 / (1 + depth_corrected * depth_corrected * 0.000015))))
                    wall_color = (color_val, int(color_val * 0.2), int(color_val * 0.2))

                    pygame.draw.rect(
                        screen,
                        wall_color,
                        (ray * SCALE, HEIGHT // 2 - proj_height // 2, SCALE, proj_height)
                    )
                    break

        ray_angle += DELTA_ANGLE

def render_enemies():
    # Ordena inimigos do mais distante para o mais próximo (Algoritmo do Pintor)
    sorted_enemies = sorted(
        [e for e in enemies if e.alive],
        key=lambda e: math.hypot(e.x - player_x, e.y - player_y),
        reverse=True
    )

    for enemy in sorted_enemies:
        dx = enemy.x - player_x
        dy = enemy.y - player_y
        dist = math.hypot(dx, dy)

        theta = math.atan2(dy, dx)
        gamma = theta - player_angle

        # Normalizar ângulo no intervalo [-pi, pi]
        while gamma > math.pi: gamma -= 2 * math.pi
        while gamma < -math.pi: gamma += 2 * math.pi

        if -HALF_FOV - 0.2 < gamma < HALF_FOV + 0.2:
            proj_size = min(HEIGHT, int(TILE_SIZE * SCREEN_DIST / (dist + 0.0001)))
            screen_x = (WIDTH // 2) + math.tan(gamma) * SCREEN_DIST - proj_size // 2
            screen_y = (HEIGHT // 2) - proj_size // 2

            # Renderizar apenas as colunas onde o inimigo não está coberto por paredes
            ray_start = max(0, int(screen_x // SCALE))
            ray_end = min(NUM_RAYS, int((screen_x + proj_size) // SCALE))

            for ray in range(ray_start, ray_end):
                if depth_buffer[ray] > dist: # Inimigo está na frente da parede
                    color_val = max(20, min(255, int(255 / (1 + dist * dist * 0.000015))))
                    enemy_color = (int(color_val * 0.1), color_val, int(color_val * 0.1)) # Monstro Verde
                    
                    pygame.draw.rect(
                        screen,
                        enemy_color,
                        (ray * SCALE, screen_y, SCALE, proj_size)
                    )

def shoot():
    global is_shooting, shoot_timer
    if is_shooting:
        return
    
    is_shooting = True
    shoot_timer = 6

    # Raycast do disparo no centro da mira
    closest_enemy = None
    min_dist = MAX_DEPTH

    for enemy in enemies:
        if not enemy.alive:
            continue
        dx = enemy.x - player_x
        dy = enemy.y - player_y
        dist = math.hypot(dx, dy)
        theta = math.atan2(dy, dx)
        gamma = theta - player_angle

        while gamma > math.pi: gamma -= 2 * math.pi
        while gamma < -math.pi: gamma += 2 * math.pi

        # Se o inimigo estiver na direção da mira central
        if abs(gamma) < 0.18 and dist < min_dist:
            # Checar se não há paredes no caminho do tiro
            wall_dist = MAX_DEPTH
            for depth in range(1, int(dist), 2):
                tx = player_x + depth * math.cos(player_angle)
                ty = player_y + depth * math.sin(player_angle)
                if MAP[int(ty // TILE_SIZE)][int(tx // TILE_SIZE)] == 1:
                    wall_dist = depth
                    break
            
            if dist < wall_dist:
                min_dist = dist
                closest_enemy = enemy

    if closest_enemy:
        closest_enemy.hp -= 50
        if closest_enemy.hp <= 0:
            closest_enemy.alive = False

def draw_weapon():
    gun_x = WIDTH // 2 - 30
    gun_y = HEIGHT - 160

    if is_shooting:
        gun_y += 15 # Recuo da arma ao atirar
        # Fogo do disparo (Muzzle Flash)
        pygame.draw.polygon(screen, (255, 255, 0), [
            (WIDTH // 2 - 25, HEIGHT - 180),
            (WIDTH // 2, HEIGHT - 240),
            (WIDTH // 2 + 25, HEIGHT - 180)
        ])
        pygame.draw.polygon(screen, (255, 120, 0), [
            (WIDTH // 2 - 12, HEIGHT - 175),
            (WIDTH // 2, HEIGHT - 210),
            (WIDTH // 2 + 12, HEIGHT - 175)
        ])

    # Desenho da arma
    pygame.draw.rect(screen, (50, 50, 50), (WIDTH // 2 - 12, gun_y - 20, 24, 70))  # Cano duplo
    pygame.draw.rect(screen, (30, 30, 30), (WIDTH // 2 - 4, gun_y - 20, 8, 70))
    pygame.draw.rect(screen, (80, 80, 80), (gun_x, gun_y + 40, 60, 90))            # Corpo da arma
    pygame.draw.rect(screen, (100, 50, 20), (gun_x + 10, gun_y + 80, 40, 60))       # Empunhadura de madeira

def draw_crosshair():
    cx, cy = WIDTH // 2, HEIGHT // 2
    pygame.draw.line(screen, (255, 255, 255), (cx - 8, cy), (cx + 8, cy), 2)
    pygame.draw.line(screen, (255, 255, 255), (cx, cy - 8), (cx, cy + 8), 2)

# Loop Principal
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                shoot()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Botão esquerdo do mouse
                shoot()

    # Atualiza animação de tiro
    if is_shooting:
        shoot_timer -= 1
        if shoot_timer <= 0:
            is_shooting = False

    # Controles de Movimentação
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        player_angle -= rot_speed
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        player_angle += rot_speed

    dx, dy = 0, 0
    if keys[pygame.K_w] or keys[pygame.K_UP]:
        dx += math.cos(player_angle) * player_speed
        dy += math.sin(player_angle) * player_speed
    if keys[pygame.K_s] or keys[pygame.K_DOWN]:
        dx -= math.cos(player_angle) * player_speed
        dy -= math.sin(player_angle) * player_speed

    # Colisão com as paredes
    if MAP[int((player_y + dy) // TILE_SIZE)][int(player_x // TILE_SIZE)] == 0:
        player_y += dy
    if MAP[int(player_y // TILE_SIZE)][int((player_x + dx) // TILE_SIZE)] == 0:
        player_x += dx

    # Atualiza Inteligência dos Inimigos
    for enemy in enemies:
        enemy.update()

    # RENDERIZAÇÃO
    # Teto e Chão
    pygame.draw.rect(screen, (20, 20, 25), (0, 0, WIDTH, HEIGHT // 2))
    pygame.draw.rect(screen, (35, 35, 35), (0, HEIGHT // 2, WIDTH, HEIGHT // 2))

    # Paredes 3D e Inimigos
    ray_casting()
    render_enemies()

    # UI (Arma e Mira)
    draw_crosshair()
    draw_weapon()

    # Minimapa 2D
    MINI_SCALE = 8
    for row in range(len(MAP)):
        for col in range(len(MAP[0])):
            if MAP[row][col] == 1:
                pygame.draw.rect(screen, (80, 80, 80), (col * MINI_SCALE, row * MINI_SCALE, MINI_SCALE - 1, MINI_SCALE - 1))
    
    # Jogador no Minimapa
    pygame.draw.circle(screen, (0, 255, 0), (int(player_x / TILE_SIZE * MINI_SCALE), int(player_y / TILE_SIZE * MINI_SCALE)), 3)
    
    # Inimigos no Minimapa
    for enemy in enemies:
        if enemy.alive:
            pygame.draw.circle(screen, (255, 0, 0), (int(enemy.x / TILE_SIZE * MINI_SCALE), int(enemy.y / TILE_SIZE * MINI_SCALE)), 3)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()