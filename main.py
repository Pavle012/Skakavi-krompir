import pygame
import gui
import random
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
y = (HEIGHT // 2)
fps = 60
clock = pygame.time.Clock()
paused = False
scroll = 0
PIPE_SPACING = 100
pipesPos = []
for i in range(100):
    randomY = random.randint(-200, 200)
    pipesPos.append((100 - scroll + (i * PIPE_SPACING), -100 + randomY))
    pipesPos.append((100 - scroll + (i * PIPE_SPACING), 800 + randomY))

################################################
################### Classes ####################
################################################
class pipe:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def draw(self, screen):
        pygame.draw.rect(screen, (0, 200, 0), (self.x, self.y, 50, 300))

################################################
################### Functions ##################
################################################
def isPotatoColliding():
    potatoRect = pygame.Rect(x, y, 2360 // 30, 1745 // 30)
    for pipeX, pipeY in pipesPos:
        pipeRect = pygame.Rect(pipeX + scroll, pipeY, 50, 300) # pipesPos[i][0] + scroll + addedScroll, pipesPos[i][1]
        if potatoRect.colliderect(pipeRect):
            return True
    return False


def spawnPipe(addedScroll):
    global scroll
    for i in range(100):
        pipe(pipesPos[i][0] + scroll + addedScroll, pipesPos[i][1]).draw(screen)

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
                velocity = -8
            if event.key == pygame.K_ESCAPE:
                paused = True
                afterpause = gui.pause_screen()
                if afterpause == "exit":
                    running = False
                elif afterpause == "resume":
                    paused = False


    if not paused:
        if y > HEIGHT or isPotatoColliding():
            afterpause = gui.lose_screen()
            if afterpause == "exit":
                running = False
            elif afterpause == "restart":
                y = (HEIGHT // 2) - 200
                velocity = 0
                paused = False
        screen.fill((0, 0, 0))
        for i in range(100):
            spawnPipe(200 * i)
        velocity += 0.5
        scroll -= 2
        y += velocity
        image = pygame.transform.scale(image, (2360 // 30, 1745 // 30))
        clock.tick(fps)
        screen.blit(image, (x, y))
        pygame.display.update()