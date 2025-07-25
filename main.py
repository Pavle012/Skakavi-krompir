import pygame
###############################################
########### Flappy Bird-like Game #############
###############################################

pygame.init()
pygame.display.set_caption("skakavi krompir")
screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
image = pygame.image.load("assets/potato.png")

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
class potato:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def draw(self, screen):
        screen.blit(image, (self.x, self.y))
    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        def update(self):
        self.rect.x += self.speed
        self.rect.y += self.speed
        if self.rect.x > 640 or self.rect.x < 0:
            self.speed[0] = -self.speed[0]
        if self.rect.y > 480 or self.rect.y < 0:
            self.speed[1] = -self.speed[1]
            
        
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_d]:
            self.rect.x += self.speed
        if keys[pygame.K_w]:
            self.rect.y -= self.speed
        if keys[pygame.K_s]:
            self.rect.y += self.speed

################################################
################### Main Loop ##################
################################################
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))
    

    pygame.display.flip()