import pygame
import gui
###############################################
########### Flappy Bird-like Game #############
###############################################

HEIGHT = 800
WIDTH = 1200
pygame.init()
pygame.display.set_caption("skakavi krompir")
screen = pygame.display.set_mode((WIDTH, HEIGHT))
image = pygame.image.load("assets/potato.png")
velocity = 0
x = 100
y = (HEIGHT // 2) - 200
fps = 60
clock = pygame.time.Clock()
paused = False

################################################
################### Classes ####################
################################################
class square:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y, self.size, self.size))

################################################
################### Main Loop ##################
################################################
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and not paused:
            if event.key == pygame.K_SPACE:
                velocity = -20

    if y > HEIGHT:
        gui.lose_screen()
        paused = True

    if not paused:
        screen.fill((0, 0, 0))
        velocity += 0.5
        y += velocity
        image = pygame.transform.scale(image, (2360 // 30, 1745 // 30))
        clock.tick(fps)
        screen.blit(image, (x, y))
        pygame.display.update()
        print(y)
