import pygame
import random

# Initialize Pygame
pygame.init()

# Screen setup
WIDTH, HEIGHT = 600, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ball Bouncing Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Ball setup
ball_radius = 20
ball_x = WIDTH // 2
ball_y = HEIGHT // 2
ball_speed_x = 4
ball_speed_y = -15
gravity = 0.5

# Platform setup
platform_width = 150
platform_height = 15
platform_x = WIDTH // 2 - platform_width // 2
platform_y = HEIGHT - 100
platform_speed = 10

# Score
score = 0
font = pygame.font.SysFont(None, 36)
game_over = False

clock = pygame.time.Clock()

def draw():
    screen.fill(WHITE)
    pygame.draw.rect(screen, BLACK, (platform_x, platform_y, platform_width, platform_height))
    pygame.draw.circle(screen, RED, (int(ball_x), int(ball_y)), ball_radius)
    score_text = font.render(f"Score: {score}", True, BLACK)
    screen.blit(score_text, (10, 10))

    if game_over:
        over_text = font.render("Game Over!", True, RED)
        screen.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, HEIGHT // 2))

    pygame.display.flip()

def increase_difficulty():
    global gravity, ball_speed_x, platform_width
    # Every 5 points, make the game harder
    if score % 5 == 0 and score != 0:
        gravity += 0.05
        if abs(ball_speed_x) < 12:
            ball_speed_x += 0.5 if ball_speed_x > 0 else -0.5
        if platform_width > 60:
            platform_width -= 5

# Main game loop
running = True
while running:
    clock.tick(60)  # 60 FPS

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if not game_over:
        # Move platform
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and platform_x > 0:
            platform_x -= platform_speed
        if keys[pygame.K_RIGHT] and platform_x + platform_width < WIDTH:
            platform_x += platform_speed

        # Update ball position
        ball_x += ball_speed_x
        ball_y += ball_speed_y
        ball_speed_y += gravity

        # Bounce off walls
        if ball_x - ball_radius <= 0 or ball_x + ball_radius >= WIDTH:
            ball_speed_x *= -1

        # Bounce on platform
        if (platform_y <= ball_y + ball_radius <= platform_y + platform_height and
                platform_x <= ball_x <= platform_x + platform_width and ball_speed_y > 0):
            ball_speed_y = -15
            score += 1
            increase_difficulty()

        # Check for game over
        if ball_y - ball_radius > HEIGHT:
            game_over = True

    draw()

pygame.quit()
