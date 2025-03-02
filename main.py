# Example file showing a circle moving on screen
import pygame
import os

# pygame setup
pygame.init()
pygame.font.init()
my_font = pygame.font.Font('edwardianscriptitc.ttf', 45)
pygame.mixer.init()

WIDTH = 640
HEIGHT = 480

# setting up music
sound = pygame.mixer.Sound(os.path.join('audio', 'choir.mp3'))

# setting up sammy
screen = pygame.display.set_mode((WIDTH, HEIGHT))     
sammy = pygame.image.load(os.path.join('images', 'themaincharacter.png')).convert()
sammy = pygame.transform.scale(sammy, (84, 87))
sammy.set_colorkey((0, 0, 0))
sam_pos = (157, 220)

# seeting up the door
door = pygame.image.load(os.path.join('images', 'frolickingdoor.png')).convert()
door = pygame.transform.scale(door, (150, 123))
door_pos = (500, 240)

# settings up the weapon
creature = pygame.image.load(os.path.join('images', 'Swordfish.jpg')).convert()
creature = pygame.transform.scale(creature, (WIDTH, HEIGHT))

# some 'contants' and such
running = True
clock = pygame.time.Clock()    
delta_time = 0.1
XSPEED = 3.14 * 1.5
YSPEED = 1.5 * 1.5
played = False

COLLIDETIME = 61

JUMPVELO = 0

# lets get the levels going, BABY
class Level:
    def __init__(self, sam_pos, door_pos, background_color, collisioners, text=""):
        self.sam_pos = sam_pos
        self.door_pos = door_pos
        self.background_color = background_color
        self.collisioners = collisioners
        self.text = text

class Collisioner:
    def __init__(self, pos, size, sam_type, touch_type, color=(255, 255, 255)):
        self.pos = pos # (left, up)
        self.size = size # (width, height)
        self.color = color
        self.sam_type = sam_type # "rect" or "erect"
        self.touch_type = touch_type # "top" or "left" or "right" or "bottom"

# from old code we copy pasted, break if remove tbh so idk
objects = [] # DO NOT REMOVE! CRASHED THE ENTIRE GAME!
levels = [
    Level((0, 0), (500, 240), (0, 0, 0), [Collisioner((200, 200), (10, 200), "rect", "right")], "j for jump, r for right, l for left"),
    Level((157, 220), (250, 200 - door.get_height()), (0, 0, 0), [Collisioner((200, 200), (200, 10), "rect", "top")]),
    Level((157, 220), (WIDTH - door.get_width(), HEIGHT - door.get_height()), (0, 0, 0), [], "you win!")
]

the_level = 0
level_change = 1
if_trans = False
TRANSITION_TIME = 0

while running:
    # handling transitions
    if if_trans:
        max_time = 300
        skip = 20
        time = ((((TRANSITION_TIME + skip - 1) // skip) * skip) / max_time) * 256
        creature.set_alpha((time))
        screen.fill(level_now.background_color)
        screen.blit(creature, (0, 0))
        TRANSITION_TIME += 1
        if TRANSITION_TIME >= max_time:
            TRANSITION_TIME = 0
            if_trans = False
        pygame.display.flip()
        clock.tick(61)
        continue

    level_now = levels[the_level]

    # set starting conditions for the level (sam, gate, background, etc)
    if level_change:
        sam_pos = level_now.sam_pos
        door_pos = level_now.door_pos
        level_change = 0

    screen.fill(level_now.background_color)
    text_surface = my_font.render(level_now.text, False, (255, 255, 255))
    screen.blit(text_surface, (100, 100))

    # loading hitboxes and collisions
    sam_erect = pygame.Rect(sam_pos[0], sam_pos[1] + 63, sammy.get_width(), sammy.get_height() - 63)
    sammy_rect = pygame.Rect(sam_pos[0], sam_pos[1], sammy.get_width(), sammy.get_height())

    door_hitbox = pygame.Rect(door_pos[0], door_pos[1], door.get_width(), door.get_height())
    door_collision = sammy_rect.colliderect(door_hitbox)

    # load and draw all the collisioners
    collisions = []
    for i, collisioner in enumerate(level_now.collisioners):
        collisioner_hitbox = pygame.Rect(collisioner.pos, collisioner.size)
        pygame.draw.rect(screen, collisioner.color, collisioner_hitbox)
        match collisioner.sam_type:
            case "rect":
                collisions.append((i, sammy_rect.colliderect(collisioner_hitbox)))
                break
            case "erect":
                collisions.append((i, sam_erect.colliderect(collisioner_hitbox)))
                break
            case _:
                print("Wrong sam case inputted")

    if sam_pos[1] >= HEIGHT and not played:
        sound.play()
        played = True

    # ground collision loading
    if the_level != len(levels) - 1:
        object_hitbox = pygame.Rect(0, HEIGHT - 20, WIDTH, 20)
    else:
        object_hitbox = pygame.Rect(0, HEIGHT - 20, WIDTH - door.get_width(), 20)
    pygame.draw.rect(screen, (255, 255 , 255), object_hitbox)
    ground_collision = sam_erect.colliderect(object_hitbox)

    # gravity
    sam_pos = (sam_pos[0], (sam_pos[1] + 2*YSPEED - JUMPVELO))
    JUMPVELO /= 1.1
    if JUMPVELO < 0.5:
        JUMPVELO = 0
    
    #ground_collision 
    if ground_collision:
        sam_pos = (sam_pos[0], HEIGHT - 19 - sammy.get_height())

    can_jump = ground_collision

    # collisionery collisions
    for i, collision in collisions:
        if not collision:
            continue

        collisioner = level_now.collisioners[i]
        match collisioner.touch_type:
            case "top":
                sam_pos = (sam_pos[0], collisioner.pos[1] + 1 - sammy.get_height())
                can_jump = can_jump or collision
                break
            case "bottom":
                sam_pos = (sam_pos[0], collisioner.pos[1] + collisioner.size[1] + 1)
                break
            case "left":
                sam_pos = (collisioner.pos[0] + 1 - sammy.get_width(), sam_pos[1])
                break
            case "right":
                sam_pos = (collisioner.pos[0] + collisioner.size[0] + 1, sam_pos[1])
                break
            case _:
                print("Wrong touch type")
        

    # sammy collision to the door, fading out of existance
    if door_collision:
        COLLIDETIME -= 1
        sammy.set_alpha(4 * COLLIDETIME)
        if COLLIDETIME == 0:
            print("next stage")
            COLLIDETIME = 61
            if the_level != len(levels) - 1:
                the_level += 1
                if_trans = True
            level_change = 1
            # got to the next stage (next index)
    else:
        COLLIDETIME = 61
        sammy.set_alpha(4 * COLLIDETIME)

    # input handling
    keys = pygame.key.get_pressed()
    if keys[pygame.K_j]:
        # check if you're colliding with something, then jump
        if can_jump:
            sam_pos = (sam_pos[0], sam_pos[1] - YSPEED)
            JUMPVELO = 31.458
    if keys[pygame.K_d]:
        sam_pos = (sam_pos[0], sam_pos[1] + YSPEED)
    if keys[pygame.K_r]:
        sam_pos = (sam_pos[0] + XSPEED, sam_pos[1])
    if keys[pygame.K_l]:
        sam_pos = (sam_pos[0] - XSPEED, sam_pos[1])

    # rechecking position, making sure not out of bounds
    if sam_pos[0] <= 0:
        sam_pos = (0, sam_pos[1])
    if sam_pos[0] + sammy.get_width() >= WIDTH:
        sam_pos = (WIDTH - sammy.get_width(), sam_pos[1])
    if sam_pos[1] <= 0:
        sam_pos = (sam_pos[0], 0)

    # render the important fellas
    screen.blit(door, door_pos)
    screen.blit(sammy, sam_pos)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    pygame.display.flip()
    clock.tick(61)

pygame.quit()