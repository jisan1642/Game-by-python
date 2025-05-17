import pygame
import random

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Game Settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Animal Hero: Rabbit vs Dragon')

# Load and scale background image
background_image = pygame.image.load("background.jpg").convert()
background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Load dragon image
dragon_image = pygame.image.load("dragon.png").convert_alpha()
dragon_image = pygame.transform.scale(dragon_image, (50, 50))

# Load sound
shoot_sound = pygame.mixer.Sound('shoot.wav')
shoot_sound.set_volume(0.5)

# Colors and constants
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
FPS = 60
clock = pygame.time.Clock()
GRAVITY = 1

# Game state variables
level = 1
level_in_progress = True
level_complete_timer = 0
current_wave = 0
waves = []
LEVEL_DURATION = 60000  # 60 seconds
level_start_time = pygame.time.get_ticks()

# Pause menu state
paused = False
pause_options = ["Resume", "Quit"]
pause_selected = 0


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Load your shooter image without transparency (convert, not convert_alpha)
        self.image = pygame.image.load("human_with_gun.png").convert()
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect()
        self.rect.x = 100
        self.rect.y = SCREEN_HEIGHT - 70
        self.speed_x = 0
        self.speed_y = 0
        self.is_jumping = False
        self.health = 100
        self.lives = 3
        self.score = 0

    def update(self):
        self.rect.x += self.speed_x
        self.speed_y += GRAVITY
        self.rect.y += self.speed_y

        if self.rect.y > SCREEN_HEIGHT - 70:
            self.rect.y = SCREEN_HEIGHT - 70
            self.is_jumping = False
            self.speed_y = 0

        if self.rect.x < 0:
            self.rect.x = 0
        elif self.rect.x > SCREEN_WIDTH - self.rect.width:
            self.rect.x = SCREEN_WIDTH - self.rect.width

    def jump(self):
        if not self.is_jumping:
            self.speed_y = -15
            self.is_jumping = True

    def move_left(self):
        self.speed_x = -5

    def move_right(self):
        self.speed_x = 5

    def stop(self):
        self.speed_x = 0

    def shoot(self):
        bullet = Projectile(self.rect.centerx, self.rect.centery)
        all_sprites.add(bullet)
        projectiles.add(bullet)
        shoot_sound.play()


class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((10, 5))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed_x = 10

    def update(self):
        self.rect.x += self.speed_x
        if self.rect.x > SCREEN_WIDTH:
            self.kill()


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = dragon_image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.health = 30
        self.speed_x = 2

    def update(self):
        self.rect.x -= self.speed_x
        if self.health <= 0:
            self.kill()
        if self.rect.right < 0:
            self.kill()


class BossEnemy(pygame.sprite.Sprite):
    def __init__(self, health=150, speed=1):
        super().__init__()
        self.image = pygame.transform.scale(dragon_image, (120, 120))
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH
        self.rect.y = SCREEN_HEIGHT - 150
        self.health = health
        self.speed_x = speed

    def update(self):
        self.rect.x -= self.speed_x
        if self.health <= 0:
            self.kill()
        if self.rect.right < 0:
            self.kill()


def draw_health_bar():
    health_bar_width = 200
    health_percentage = player.health / 100
    pygame.draw.rect(screen, RED, (10, 10, health_bar_width, 20))
    pygame.draw.rect(screen, GREEN, (10, 10, health_bar_width * health_percentage, 20))


def draw_score():
    font = pygame.font.Font(None, 36)
    text = font.render(f"Score: {player.score}", True, WHITE)
    screen.blit(text, (SCREEN_WIDTH - 150, 10))


def draw_lives():
    font = pygame.font.Font(None, 36)
    text = font.render(f"Lives: {player.lives}", True, WHITE)
    screen.blit(text, (SCREEN_WIDTH - 150, 50))


def draw_level():
    font = pygame.font.Font(None, 36)
    text = font.render(f"Level: {level}", True, WHITE)
    screen.blit(text, (10, 40))


def draw_level_timer():
    time_elapsed = pygame.time.get_ticks() - level_start_time
    time_left = max(0, (LEVEL_DURATION - time_elapsed) // 1000)
    font = pygame.font.Font(None, 36)
    text = font.render(f"Time Left: {time_left}s", True, WHITE)
    screen.blit(text, (10, 70))


def draw_pause_menu():
    screen.fill(BLACK)  # Changed to BLACK background so white text is visible
    font = pygame.font.Font(None, 64)
    title = font.render("Game Paused", True, WHITE)  # White text for visibility
    screen.blit(title, (SCREEN_WIDTH // 2 - 150, 150))

    option_font = pygame.font.Font(None, 48)
    for i, option in enumerate(pause_options):
        color = GREEN if i == pause_selected else WHITE
        text = option_font.render(option, True, color)
        screen.blit(text, (SCREEN_WIDTH // 2 - 100, 250 + i * 60))
    pygame.display.flip()


def game_over():
    font = pygame.font.Font(None, 64)
    text = font.render("GAME OVER", True, RED)
    screen.blit(text, (SCREEN_WIDTH // 2 - 160, SCREEN_HEIGHT // 2 - 50))
    pygame.display.flip()
    pygame.time.wait(3000)
    pygame.quit()
    exit()


def start_level(level_num):
    global level_in_progress, current_wave, waves, level_start_time
    enemies.empty()
    all_sprites.empty()
    projectiles.empty()
    all_sprites.add(player)
    current_wave = 0

    if level_num == 1:
        waves = [
            [(SCREEN_WIDTH + 100 * i, SCREEN_HEIGHT - 70) for i in range(5)],
            [(SCREEN_WIDTH + 150 * i, SCREEN_HEIGHT - 70) for i in range(6)]
        ]
    elif level_num == 2:
        boss = BossEnemy(health=150, speed=1)
        all_sprites.add(boss)
        enemies.add(boss)
        waves = []
    elif level_num == 3:
        boss = BossEnemy(health=200, speed=1)
        all_sprites.add(boss)
        enemies.add(boss)
        waves = []

    level_start_time = pygame.time.get_ticks()
    level_in_progress = True


# Initialize game objects
player = Player()
all_sprites = pygame.sprite.Group()
projectiles = pygame.sprite.Group()
enemies = pygame.sprite.Group()
all_sprites.add(player)
start_level(level)

# Main game loop
running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                paused = not paused
            elif paused:
                if event.key == pygame.K_UP:
                    pause_selected = (pause_selected - 1) % len(pause_options)
                elif event.key == pygame.K_DOWN:
                    pause_selected = (pause_selected + 1) % len(pause_options)
                elif event.key == pygame.K_RETURN:
                    if pause_options[pause_selected] == "Resume":
                        paused = False
                    elif pause_options[pause_selected] == "Quit":
                        pygame.quit()
                        exit()
            else:
                if event.key == pygame.K_LEFT:
                    player.move_left()
                elif event.key == pygame.K_RIGHT:
                    player.move_right()
                elif event.key == pygame.K_SPACE:
                    player.shoot()
                elif event.key == pygame.K_UP:
                    player.jump()

        elif event.type == pygame.KEYUP and not paused:
            if event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                player.stop()

    if paused:
        draw_pause_menu()
        continue

    screen.blit(background_image, (0, 0))

    if level_in_progress:
        all_sprites.update()

        if pygame.time.get_ticks() - level_start_time > LEVEL_DURATION:
            level_in_progress = False
            level_complete_timer = pygame.time.get_ticks()

        for bullet in projectiles:
            enemies_hit = pygame.sprite.spritecollide(bullet, enemies, False)
            for enemy in enemies_hit:
                enemy.health -= 10
                bullet.kill()
                player.score += 10

        player_hit_list = pygame.sprite.spritecollide(player, enemies, False)
        for hit in player_hit_list:
            player.health -= 1
            if player.health <= 0:
                player.lives -= 1
                player.health = 100
                if player.lives <= 0:
                    game_over()

        if len(enemies) == 0:
            if current_wave < len(waves):
                for x, y in waves[current_wave]:
                    enemy = Enemy(x, y)
                    all_sprites.add(enemy)
                    enemies.add(enemy)
                current_wave += 1
            elif not waves:
                pass
            else:
                level_in_progress = False
                level_complete_timer = pygame.time.get_ticks()
    else:
        screen.fill(BLACK)
        font = pygame.font.Font(None, 64)
        text = font.render("Level Complete!", True, GREEN)
        screen.blit(text, (SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT // 2 - 50))
        pygame.display.flip()

        if pygame.time.get_ticks() - level_complete_timer > 2000:
            level += 1
            if level > 3:
                screen.fill(BLACK)
                win_font = pygame.font.Font(None, 64)
                win_text = win_font.render("You Win! Congratulations!", True, GREEN)
                screen.blit(win_text, (SCREEN_WIDTH // 2 - 300, SCREEN_HEIGHT // 2 - 50))
                pygame.display.flip()
                pygame.time.wait(3000)
                running = False
            else:
                player.health = 100
                player.lives = max(player.lives, 1)
                start_level(level)

    draw_health_bar()
    draw_score()
    draw_lives()
    draw_level()
    draw_level_timer()
    all_sprites.draw(screen)
    pygame.display.flip()

pygame.quit()
