from pygame.locals import K_SPACE, K_UP
import pygame
import glob
import random

pygame.init()
pygame.mixer.init()

WIDTH = 288
HEIGHT = 512 + 112
GAP = 250

num_imgs = [pygame.image.load(f"assets/sprites/{x}.png") for x in range(0,10)]
win = pygame.display.set_mode((WIDTH, HEIGHT))
possible_pipes = [(x, y) for x in range(1000) for y in range(1000) if x + y == GAP]
pipe_color = random.choice("pipe-green.png pipe-red.png".split())
pipe_color = "pipe-red.png"

# TODO: Fix hitmask, add rotation velocity 

# sounds
hit_sound = pygame.mixer.Sound("assets/audio/hit.wav")
point_sound =  pygame.mixer.Sound("assets/audio/point.wav")
wing_sound = pygame.mixer.Sound("assets/audio/wing.wav")

class Bird(pygame.sprite.Sprite):
    
    def __init__(self, color):
        super().__init__()
        self.images = [pygame.image.load(img).convert() for img in glob.glob(f"assets/sprites/{color}*")]
        self.index = 1
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = 50
        self.rect.y = 276
        self.time = 0

        #physics
        self.vertSpeed = 0
        self.jumpSpeed = -3
        
        self.started = False

        self.rotation = 0
    
    def draw(self):
        # this loses a bit of quality not sure why
        center = self.rect.center
        rotated = pygame.transform.rotate(self.image, self.rotation)
        self.rect = rotated.get_rect(center = center)
        win.blit(rotated, self.rect)

    def update(self):
        if self.started:
            self.rect.top += self.vertSpeed
            self.vertSpeed += .2
        
        self.time += 1

        if self.time % 10 == 0:
            self.index += 1
            if self.index > len(self.images) - 1:
                self.index = 0
            self.image = self.images[self.index]

        if self.rotation > -90 and self.started:
            self.rotation -= 1

        # pygame.draw.rect(win, (255,0,0), self.rect,1 )

    def isAlive(self, fg, pipe1, pipe2):
        pipe_hit1 = self.rect.colliderect(pipe1.rect)
        pipe_hit2 = self.rect.colliderect(fg.hitbox)
        ground_hit = self.rect.colliderect(pipe2.rect)
        if ground_hit or pipe_hit1 or pipe_hit2:
            hit_sound.play() 
            return False
        return True


    def jump(self):
        self.vertSpeed = self.jumpSpeed
        self.rotation = 45

class Pipe():

    def __init__(self,width,  north=False):
        self.image = pygame.image.load(f"assets/sprites/{pipe_color}")
        self.rect = self.image.get_rect()
        self.rect.x = 300

        if north:
            center = self.rect.center
            self.image = pygame.transform.rotate(self.image, 180)
            self.rect = self.image.get_rect(center = center)
            self.rect.top -= width

        else:
            self.rect.bottom = 512
            self.rect.top += width


    def draw(self):
        win.blit(self.image, self.rect)
        # pygame.draw.rect(win, (255,0,0), self.rect,1 )

    def update(self):
        self.rect.x -= 2


class FG(pygame.sprite.Sprite):
    def __init__(self):
        self.image = pygame.image.load("assets/sprites/base.png").convert()
        self.bx = 0
        self.bx2 = self.image.get_width()
        self.hitbox = pygame.Rect(0,512,288,112)
        super().__init__()

    def draw(self):
        win.blit(self.image,(self.bx, 512))
        win.blit(self.image,(self.bx2, 512))
    
    def update(self):
        self.bx -= 1
        self.bx2 -= 1

        if self.bx < self.image.get_width() * -1:
            self.bx = self.image.get_width()
        if self.bx2 < self.image.get_width() * -1:
            self.bx2 = self.image.get_width()

class BG(pygame.sprite.Sprite):
    def __init__(self, img):
        self.image = pygame.image.load(img).convert()
        self.rect = self.image.get_rect()
        super().__init__()

    def draw(self):
        win.blit(self.image,self.rect)

class WelcomeScreen(pygame.sprite.Sprite):

    def __init__(self):
        self.image = pygame.image.load("assets/sprites/message.png")
        self.rect = self.image.get_rect()
        self.rect.x = 50
        self.rect.y = 110
        super().__init__()

    def draw(self):
        win.blit(self.image, self.rect)

def choose_bg():
    return BG(random.choice(glob.glob("assets/sprites/back*")))

def choose_bird():
    color = random.choice(["yellow", "red", "bluebird"])
    return Bird(color)

def get_pipes():
    width1, width2 = random.choice(possible_pipes)
    return Pipe(width1), Pipe(width2, True)

def show_score(scr):
    nums = list(str(scr))
    for num, number in enumerate(nums):
        win.blit(num_imgs[int(number)], ((WIDTH / 2) + num * 17 - 10, 50))


bird = choose_bird()
bg =  choose_bg()
fg = FG()
wc = WelcomeScreen()
other = pygame.sprite.Group()
other.add(bg)
other.add(wc)
clock = pygame.time.Clock()

    

pipe1, pipe2 = get_pipes()
score = 0
running = True
while running:
    if not bird.isAlive(fg, pipe1, pipe2):
        hit_sound.play()
        running = False
        
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        if event.type == pygame.KEYDOWN:
            if event.key == K_SPACE or event.key == K_UP:
                if not bird.started:
                    bird.started = True
                    other.remove(wc)
                bird.jump()
                wing_sound.play()

    clock.tick(60)
    other.draw(win)
    other.update()
    bird.draw()
    bird.update()


    if bird.started:
        pipe1.draw()
        pipe1.update()
        pipe2.draw()
        pipe2.update()
        if pipe1.rect.x <= -50:
            pipe1, pipe2 = get_pipes()
        show_score(score)

    if bird.rect.x == pipe1.rect.x + 1:
        point_sound.play()
        score += 1
        

    fg.draw()
    fg.update()
    pygame.display.flip()
