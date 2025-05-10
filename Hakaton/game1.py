import pygame
import sys
import random

# Ініціалізація
pygame.init()
pygame.mixer.init()

# Екран
WIDTH, HEIGHT = 800, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Битва драконів")

# Кольори
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)

# Параметри
PLAYER_SIZE = 50
BULLET_SPEED = 10
MAX_HITS = 5
music_on = True

# Шрифти
font = pygame.font.SysFont('Arial', 30)
big_font = pygame.font.SysFont('Arial', 50)

# Завантаження зображень
background = pygame.image.load("background.jpg")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))
sprite1_img = pygame.image.load("sprite1.png")
sprite1_img = pygame.transform.scale(sprite1_img, (PLAYER_SIZE, PLAYER_SIZE))
sprite2_img = pygame.image.load("sprite2.png")
sprite2_img = pygame.transform.scale(sprite2_img, (PLAYER_SIZE, PLAYER_SIZE))

# Музика
pygame.mixer.music.load("gamemusic.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

class Player:
    def __init__(self, x, y, image, controls=None):
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        self.image = image
        self.controls = controls
        self.bullets = []
        self.hits = 0
        self.score = 0

    def move(self, keys):
        if not self.controls:
            return
        if keys[self.controls['left']] and self.rect.x > 0:
            self.rect.x -= 5
        if keys[self.controls['right']] and self.rect.x < WIDTH - PLAYER_SIZE:
            self.rect.x += 5
        if keys[self.controls['up']] and self.rect.y > 0:
            self.rect.y -= 5
        if keys[self.controls['down']] and self.rect.y < HEIGHT - PLAYER_SIZE:
            self.rect.y += 5

    def auto_move(self):
        direction = random.choice(['left', 'right', 'up', 'down', 'none'])
        speed = 6
        if direction == 'left' and self.rect.x > 0:
            self.rect.x -= speed
        elif direction == 'right' and self.rect.x < WIDTH - PLAYER_SIZE:
            self.rect.x += speed
        elif direction == 'up' and self.rect.y > 0:
            self.rect.y -= speed
        elif direction == 'down' and self.rect.y < HEIGHT - PLAYER_SIZE:
            self.rect.y += speed

    def shoot(self, direction):
        bullet = pygame.Rect(self.rect.centerx, self.rect.centery, 10, 5)
        self.bullets.append({'rect': bullet, 'dir': direction})

def draw_window(p1, p2, coin):
    win.blit(background, (0, 0))
    win.blit(p1.image, (p1.rect.x, p1.rect.y))
    win.blit(p2.image, (p2.rect.x, p2.rect.y))

    for bullet in p1.bullets:
        pygame.draw.rect(win, (0, 0, 255), bullet['rect'])
    for bullet in p2.bullets:
        pygame.draw.rect(win, (255, 0, 0), bullet['rect'])

    pygame.draw.circle(win, YELLOW, coin.center, 10)

    score_text = font.render(f"Дракончик: {p1.hits}  Дракон: {p2.hits}  Монетки: {p1.score}", True, BLACK)
    win.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 10))
    pygame.display.update()

def handle_bullets(p1, p2):
    for bullet in p1.bullets[:]:
        bullet['rect'].x += BULLET_SPEED
        if bullet['rect'].colliderect(p2.rect):
            p1.hits += 1
            p1.bullets.remove(bullet)
        elif bullet['rect'].x > WIDTH:
            p1.bullets.remove(bullet)

    for bullet in p2.bullets[:]:
        bullet['rect'].x -= BULLET_SPEED
        if bullet['rect'].colliderect(p1.rect):
            p2.hits += 1
            p2.bullets.remove(bullet)
        elif bullet['rect'].x < 0:
            p2.bullets.remove(bullet)

def toggle_music():
    global music_on
    music_on = not music_on
    if music_on:
        pygame.mixer.music.unpause()
    else:
        pygame.mixer.music.pause()

def game_loop():
    player1 = Player(100, HEIGHT//2, sprite1_img, {
        'left': pygame.K_LEFT, 'right': pygame.K_RIGHT,
        'up': pygame.K_UP, 'down': pygame.K_DOWN,
        'shoot': pygame.K_KP0
    })
    player2 = Player(WIDTH - 150, HEIGHT//2, sprite2_img)

    coin = pygame.Rect(random.randint(0, WIDTH - 20), random.randint(0, HEIGHT - 20), 20, 20)

    run = True
    clock = pygame.time.Clock()

    while run:
        clock.tick(60)
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == player1.controls['shoot']:
                    player1.shoot('right')
                if event.key == pygame.K_m:
                    toggle_music()

        player1.move(keys)

        if random.randint(1, 5) == 1:
            player2.auto_move()
        if abs(player2.rect.y - player1.rect.y) < PLAYER_SIZE:
            if player1.rect.x < player2.rect.x and random.randint(1, 3) == 1:
                player2.shoot('left')

        handle_bullets(player1, player2)

        if player1.rect.colliderect(coin):
            player1.score += 1
            coin.x = random.randint(0, WIDTH - 20)
            coin.y = random.randint(0, HEIGHT - 20)

        draw_window(player1, player2, coin)

        if player1.score >= 20:
            win.blit(background, (0, 0))
            end_text = big_font.render("Дракончик зібрав 20 монет!", True, BLACK)
            win.blit(end_text, (WIDTH//2 - end_text.get_width()//2, HEIGHT//2))
            pygame.display.update()
            pygame.time.delay(3000)
            run = False

        if player1.hits >= MAX_HITS or player2.hits >= MAX_HITS:
            winner = "Дракончик" if player1.hits >= MAX_HITS else "Дракон"
            win.blit(background, (0, 0))
            end_text = big_font.render(f"{winner} переміг!", True, BLACK)
            win.blit(end_text, (WIDTH//2 - end_text.get_width()//2, HEIGHT//2))
            pygame.display.update()
            pygame.time.delay(3000)
            run = False
    return True

def main_menu():
    selected = 0
    options = ["Зіграти гру", "Вийти з гри"]
    while True:
        win.blit(background, (0, 0))
        title = big_font.render("Битва драконів", True, BLACK)
        win.blit(title, (WIDTH//2 - title.get_width()//2, 100))

        for i, option in enumerate(options):
            color = (255, 0, 0) if i == selected else BLACK
            text = font.render(option, True, color)
            win.blit(text, (WIDTH//2 - text.get_width()//2, 250 + i * 60))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                if event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                if event.key == pygame.K_RETURN:
                    if selected == 0:
                        continue_game = game_loop()
                        if not continue_game:
                            return
                    elif selected == 1:
                        return
                if event.key == pygame.K_m:
                    toggle_music()

main_menu()
pygame.quit()
