import datetime
import struct
import moderngl  # wrapper for openGL, preforms all rendering
import pygame  # preforms all drawing
from pygame.locals import *
from screeninfo import get_monitors
import os
import random
import math
import time
import glcontext

pygame.mixer.init()
s = 'Audio'
hp = 100
kill_line1 = pygame.mixer.Sound(os.path.join(s, 'kill_line1.mp3'))
kill_line2 = pygame.mixer.Sound(os.path.join(s, 'kill_line2.mp3'))
death_sound = pygame.mixer.Sound(os.path.join(s, 'death_noises.mp3'))


# Crosshair class
class Crosshair(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("unknown.png")
        self.image = pygame.transform.scale(self.image, (100, 100))
        self.rect = self.image.get_rect()

    def update(self):
        self.rect.center = pygame.mouse.get_pos()


# Turret Class
class Turret(pygame.sprite.Sprite):
    # Sets up the turret class
    def __init__(self, spawn):
        super().__init__()
        self.image = pygame.image.load("Frame18.png")
        self.rect = self.image.get_rect()
        self.spawn = spawn
        self.varience = random.randint(-100, 100)
        self.hp = 3
        self.dead = False

        if self.spawn == 1:
            self.j = 3850 + self.varience
            self.h = 850
            self.rect.center = (self.j, self.h)
        if self.spawn == 2:
            self.j = 700 + self.varience
            self.h = 850
        if self.spawn == 3:
            self.j = 2300 + self.varience
            self.h = 850

    # Updates the position of the Turret releative to the position of the camera in the room
    def update(self, i, shot, shooting, hp):
        if self.j <= 1400:
            if i <= -1920 - self.j:
                self.rect.center = (bg_img.get_width() + self.j + i, self.h)
            elif i >= self.j + 1920:
                self.rect.center = (-bg_img.get_width() + self.j + i, self.h)
            elif i == 0:
                self.rect.center = (self.j, self.h)
            else:
                self.rect.center = (self.j + i, self.h)
        else:
            if abs(i) != i or i == 0:
                self.rect.center = (self.j + i, self.h)
            else:
                self.rect.center = (-bg_img.get_width() + self.j + i, self.h)

        if shot == True:
            self.isShot(pygame.mouse.get_pos())

        self.shoot(shooting, hp)

    # Checks weather the turret has been shot or not
    def isShot(self, mouse):
        self.hit = False
        if self.rect.x <= mouse[0] <= self.rect.x + 246 and self.rect.y <= mouse[1] <= self.rect.y + 509:
            self.hp -= 1
            self.hit = True
            if self.hp == 0:
                self.dead = True
                self.kill_line = random.randint(1, 5)
                if self.kill_line == 2:
                    self.kill_line = random.randint(1, 2)
                    if self.kill_line == 1:
                        pygame.mixer.find_channel().play(kill_line1)
                    else:
                        pygame.mixer.find_channel().play(kill_line2)

                TURRET_GROUP.remove(self)
        return (self.hit, self.dead)

    # Plays shooting animation and damages player
    def shoot(self, shooting, hp):
        if shooting == True:
            self.image = pygame.image.load("Frame19.png")
        else:
            self.image = pygame.image.load("Frame18.png")


# Initializing pygame and some global variables.
pygame.init()
pygame.mixer.init()

CROSSHAIR_GROUP = pygame.sprite.Group()
TURRET_GROUP = pygame.sprite.Group()
RES = (get_monitors()[0].width, get_monitors()[0].height)
FPS = 60
clock = pygame.time.Clock()
logo = pygame.image.load('jah.png')
logo = pygame.transform.scale(logo, (logo.get_width() / 2, logo.get_height() / 2))
start_image = pygame.image.load('hasm mell.jpg')
start_image = pygame.transform.scale(start_image, RES)
bg_img = pygame.image.load('IMG_0996.jpg')
bg_img = pygame.transform.scale(bg_img, (4800, RES[1]))
SPEED = bg_img.get_width() / 300
color_light = (170, 170, 170)
color_dark = (100, 100, 100)
color = (255, 255, 255)
smallfont = pygame.font.SysFont('Corbel', 35)
slide = pygame.mixer.Sound(os.path.join(s, 'slide.mp3'))
shot = pygame.mixer.Sound(os.path.join(s, 'shot.mp3'))
slide_sound = False
slide_channel = pygame.mixer.Channel(1)
pygame.mixer.set_num_channels(100)
j = True
spawnrate = 800
hp = 100

# initializes the pygame screen
screen = pygame.Surface(RES).convert((255, 65280, 16711680, 0))
pygame.display.set_mode(RES, DOUBLEBUF | OPENGL)

# Creates openGL context and convewrts pygame coordinates to openGL coordinates.
ctx = moderngl.create_context()

texture_coordinates = [0, 1, 1, 1,
                       0, 0, 1, 0]

world_coordinates = [-1, -1, 1, -1,
                     -1, 1, 1, 1]

render_indices = [0, 1, 2,
                  1, 2, 3]

# Shader for creating the fake 3d effect.
prog = ctx.program(
    vertex_shader='''
#version 300 es
in vec2 vert;
in vec2 in_text;
out vec2 v_text;
void main() {
   gl_Position = vec4(vert, 0.0, 1.0);
   v_text = in_text;
}
''',

    fragment_shader='''
#version 300 es
precision mediump float;
uniform sampler2D Texture;

out vec3 color;
in vec2 v_text;
void main() {

    vec2 coordinates;
    float pixelDistanceX;
    float pixelDistanceY;
    float offset;
    float dir;

    pixelDistanceX = distance(v_text.x, .5);
    pixelDistanceY = distance(v_text.y, .5);

    offset = (pixelDistanceX * .2) * pixelDistanceY;

    if (v_text.y <= .5)
        dir = 1.0;
    else
        dir = -1.0;

    coordinates = vec2(v_text.x , v_text.y + pixelDistanceX * (offset*8.0*dir));
    color = vec3(texture(Texture, coordinates));

}
''')

# Dependancies for openGL
screen_texture = ctx.texture(
    RES, 3,
    pygame.image.tostring(screen, "RGB", 1))

screen_texture.repeat_x = False
screen_texture.repeat_y = False

vbo = ctx.buffer(struct.pack('8f', *world_coordinates))
uvmap = ctx.buffer(struct.pack('8f', *texture_coordinates))
ibo = ctx.buffer(struct.pack('6I', *render_indices))

vao_content = [
    (vbo, '2f', 'vert'),
    (uvmap, '2f', 'in_text')
]

vao = ctx.vertex_array(prog, vao_content, ibo)


# Render function for OpenGL
def render():
    texture_data = screen.get_view('1')
    screen_texture.write(texture_data)
    ctx.clear(14 / 255, 40 / 255, 66 / 255)
    screen_texture.use()
    vao.render()
    pygame.display.flip()


# Crosshair
crosshair = Crosshair()
crosshair_group = pygame.sprite.Group()
crosshair_group.add(crosshair)

i = 0
runing = True
slide_channel.play(slide, -1)
slide_channel.pause()
start_menu = True
frame = 0
shooting = False
start_time = time.time()
# MAIN LOOP
while runing:
    print(hp)

    # Death, reinitializes variables --- there is definitely a cleaner and less stupid way to do this
    # TODO MAKE REINITIALIZATION CLEANER
    if hp <= 0:
        pygame.mixer.find_channel().play(death_sound)
        CROSSHAIR_GROUP = pygame.sprite.Group()
        TURRET_GROUP = pygame.sprite.Group()
        RES = (get_monitors()[0].width, get_monitors()[0].height)
        FPS = 60
        clock = pygame.time.Clock()
        logo = pygame.image.load('jah.png')
        logo = pygame.transform.scale(logo, (logo.get_width() / 2, logo.get_height() / 2))
        start_image = pygame.image.load('hasm mell.jpg')
        start_image = pygame.transform.scale(start_image, RES)
        bg_img = pygame.image.load('IMG_0996.jpg')
        bg_img = pygame.transform.scale(bg_img, (4800, RES[1]))
        SPEED = bg_img.get_width() / 300
        color_light = (170, 170, 170)
        color_dark = (100, 100, 100)
        color = (255, 255, 255)
        smallfont = pygame.font.SysFont('Corbel', 35)
        slide = pygame.mixer.Sound(os.path.join(s, 'slide.mp3'))
        shot = pygame.mixer.Sound(os.path.join(s, 'shot.mp3'))
        slide_sound = False
        slide_channel = pygame.mixer.Channel(1)
        pygame.mixer.set_num_channels(100)
        j = True
        spawnrate = 800
        hp = 100
        # Crosshair
        crosshair = Crosshair()
        crosshair_group = pygame.sprite.Group()
        crosshair_group.add(crosshair)

        i = 0
        runing = True
        slide_channel.play(slide, -1)
        slide_channel.pause()
        start_menu = True
        frame = 0
        shooting = False


    # Determines how much time has passed since the last turret spawned
    end_time = time.time() - start_time
    if end_time >= 20:
        if spawnrate // 2 > 100:
            spawnrate = spawnrate // 2
            start_time = time.time()
        else:
            spawnrate = 100
            start_time = time.time()

    # Determines weather or not a turret will spawn on a given frame.
    spawn = random.randint(1, spawnrate)
    if spawn == 5:
        turret = Turret(random.randint(1, 3))
        TURRET_GROUP.add(turret)

    # Determines how much damage will be given to the player on a given frame
    if frame == 15:
        if shooting == False:
            shooting = True
            hp -= (1/2) * len(TURRET_GROUP.sprites())
            frame = 0
        else:
            shooting = False
            frame = 0

    # Start Menu
    if start_menu == True:
        pygame.mouse.set_visible(True)
        start_text = smallfont.render('start', True, color)
        while start_menu:
            mouse = pygame.mouse.get_pos()
            screen.fill((255, 255, 255))
            screen.blit(start_image, (0, 0))

            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Determines if start button is being pressed
                    if event.button == 1:
                        if RES[0] / 2 <= mouse[0] <= RES[0] / 2 + 140 and RES[1] / 2 <= mouse[1] <= RES[1] / 2 + 40:
                            start_menu = False
                            start_time = time.time()
                elif event.type == pygame.QUIT:
                    pygame.quit()

            # Start button
            if RES[0] / 2 <= mouse[0] <= RES[0] / 2 + 140 and RES[1] / 2 <= mouse[1] <= RES[1] / 2 + 40:
                pygame.draw.rect(screen, color_light, [RES[0] / 2, RES[1] / 2, 140, 40])
            else:
                pygame.draw.rect(screen, color_dark, [RES[0] / 2, RES[1] / 2, 140, 40])

            screen.blit(start_text, (RES[0] / 2 + 35, RES[1] / 2))
            screen.blit(logo, (235, 50))

            render()

    pygame.mouse.set_visible(False)
    screen.fill((0, 0, 0))
    screen.blit(bg_img, (i, 0))
    crosshair_group.update()
    TURRET_GROUP.draw(screen)
    crosshair_group.draw(screen)
    
    # Allows for the screen to scroll seamlessly in both directions.
    if slide_sound == True:
        slide_channel.unpause()
    else:
        slide_channel.pause()
    if abs(i) != i:
        screen.blit(bg_img, (bg_img.get_width() + i, 0))
        TURRET_GROUP.draw(screen)
        crosshair_group.draw(screen)
    else:
        screen.blit(bg_img, (-bg_img.get_width() + i, 0))
        TURRET_GROUP.draw(screen)
        crosshair_group.draw(screen)

    if (i == -bg_img.get_width()):
        screen.blit(bg_img, (bg_img.get_width() + i, 0))
        TURRET_GROUP.draw(screen)
        crosshair_group.draw(screen)
        i = 0
    elif (i == bg_img.get_width()):
        screen.blit(bg_img, (bg_img.get_width() + i, 0))
        TURRET_GROUP.draw(screen)
        crosshair_group.draw(screen)
        i = 0

    mouse = pygame.mouse.get_pos()
    if mouse[0] > RES[0] - 400:
        i -= SPEED
        slide_sound = True
    elif mouse[0] < 400:
        i += SPEED
        slide_sound = True
    else:
        slide_sound = False

    TURRET_GROUP.update(i, False, shooting, hp)

    for event in pygame.event.get():
        if event.type == QUIT:
            runing = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                pygame.mixer.find_channel().play(shot)
                mouse = pygame.mouse.get_pos()
                TURRET_GROUP.update(i, True, shooting, hp)

        if event.type == pygame.KEYDOWN:

            # Pause Menu
            if event.key == pygame.K_ESCAPE:
                text = smallfont.render('quit', True, color)
                text2 = smallfont.render('resume', True, color)
                rectHeight = 40
                rectWidth = 140
                centerX = RES[0] / 2
                centerY = RES[1] / 2
                rectPosX = centerX - 40
                rectPosY = centerY + 100
                rectBoundsX = rectPosX + rectWidth
                rectBoundsY = rectPosY + rectHeight
                paused = True
                pygame.mouse.set_visible(True)

                while True:
                    screen.fill((0, 0, 0, 255))
                    mouse = pygame.mouse.get_pos()

                    for event in pygame.event.get():

                        if event.type == pygame.MOUSEBUTTONDOWN:

                            if event.button == 1:

                                if rectPosX <= mouse[0] <= rectBoundsX and rectPosY <= mouse[1] <= rectBoundsY:
                                    pygame.quit()
                                elif rectPosX <= mouse[0] <= rectBoundsX and rectPosY - 200 <= mouse[1] <= rectBoundsY:
                                    paused = False
                                    break

                    if not paused:
                        break

                    if rectPosX <= mouse[0] <= rectBoundsX and rectPosY <= mouse[1] <= rectBoundsY:
                        pygame.draw.rect(screen, color_light, [rectPosX, rectPosY, 140, 40])
                        pygame.draw.rect(screen, color_dark, [rectPosX, rectPosY - 200, 140, 40])

                    elif rectPosX <= mouse[0] <= rectBoundsX and rectPosY - 200 <= mouse[1] <= rectBoundsY - 200:
                        pygame.draw.rect(screen, color_light, [rectPosX, rectPosY - 200, 140, 40])
                        pygame.draw.rect(screen, color_dark, [rectPosX, rectPosY, 140, 40])

                    else:
                        pygame.draw.rect(screen, color_dark, [rectPosX, rectPosY, 140, 40])
                        pygame.draw.rect(screen, color_dark, [rectPosX, rectPosY - 200, 140, 40])

                    screen.blit(text, (RES[0] / 2, RES[1] / 2 + 100))
                    screen.blit(text2, (RES[0] / 2 - 20, RES[1] / 2 - 100))
                    render()

    frame += 1
    render()
    clock.tick(FPS)
pygame.quit()
