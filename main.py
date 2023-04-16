import levels
import pygame

BLACK = (0, 0, 0)
WIDTH = 900
HEIGHT = 720
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
GREY = (180, 180, 180)
SKY_BLUE = (135, 206, 235)
ORANGE = (255, 165, 0)
ORANGE_DARK = (220, 130, 0)
RED = (255, 0, 0)
BEAM_WIDTH = 5
MIRROR_WIDTH = 6

class Level:
    def __init__(self, num, status, pos, font):
        self.num = num
        self.status = status
        self.rect = pygame.Rect(*pos, 100, 100)
        self.text = font.render(f"Level {num}", True, BLACK)
        self.text_rect = self.text.get_rect()
        self.text_rect.center = self.rect.center

    def display(self, surface):
        if self.status == "l":
            bd_color = RED
        elif self.status == "c":
            bd_color = GREEN
        else:
            bd_color = BLACK

        if self.rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(surface, GREY, self.rect, border_radius=5)
        else:
            pygame.draw.rect(surface, WHITE, self.rect, border_radius=5)

        surface.blit(self.text, self.text_rect)

        pygame.draw.rect(surface, bd_color, self.rect, width=3, border_radius=5)

    def update(self, pos):
        if self.status != "l":
            if self.rect.collidepoint(pos):
                return self.num - 1

class Block:
    def __init__(self, height, width, x, y):
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, color, screen):
        pygame.draw.rect(screen, color, self.rect, border_radius=2)

class Light:
    def __init__(self, start, direction, screen):
        self.start = start

        if direction == "d":
            self.end = (self.start[0], 645)
        elif direction == "u":
            self.end = (self.start[0], 0)
        elif direction == "r":
            self.end = (900, self.start[1])
        else:
            self.end = (0, self.start[1])

        self.rect = pygame.draw.line(screen, YELLOW, start, self.end, BEAM_WIDTH)
        self.direction = direction

    def draw(self, screen):
        self.rect = pygame.draw.line(screen, YELLOW, self.start, self.end, BEAM_WIDTH)

    def update_end(self, coords):
        if self.direction == "d":
            out = (self.start[0], coords[1])
        elif self.direction == "u":
            out = (self.start[0], coords[1]+15)
        elif self.direction == "l":
            out = (coords[0]+15, self.start[1])
        else:
            out = (coords[0], self.start[1])

        self.end = out
        return out

class Mirror:
    def __init__(self, start, type, screen):
        self.start = start
        self.type = type
        self.rect = pygame.draw.line(screen, WHITE, self.start, (self.start[0]+self.type*20, self.start[1]+20),  MIRROR_WIDTH)
        self.draging = False

    def draw(self, screen):
        self.rect = pygame.draw.line(screen, WHITE, self.start, (self.start[0]+self.type*20, self.start[1]+20), MIRROR_WIDTH)

    def update(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:          
                if self.rect.collidepoint(event.pos):
                    self.draging = True
                    mouse_x, mouse_y = event.pos
                    self.offset_x = self.start[0] - mouse_x
                    self.offset_y = self.start[1] - mouse_y

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:            
                self.draging = False

        elif event.type == pygame.MOUSEMOTION:
            if self.draging:
                mouse_x, mouse_y = event.pos
                pos = (mouse_x+self.offset_x, mouse_y+self.offset_y)
                if 20 <= pos[0] and 880 >= pos[0] and 20 <= pos[1] and 630 >= pos[1]:
                    self.start = pos

def reflect(light_ray, mirror):
    if mirror.type == -1:
        if light_ray.direction == "u":
            return "r"
        elif light_ray.direction == "d":
            return "l"
        elif light_ray.direction == "l":
            return "d"
        else:
            return "u"
    else:
        if light_ray.direction == "u":
            return "l"
        elif light_ray.direction == "d":
            return "r"
        elif light_ray.direction == "l":
            return "u"
        else:
            return "d"

pygame.init()

size = (WIDTH, HEIGHT)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Optic Odyssey")

bg = pygame.image.load("./background.jpg").convert()

title_font = pygame.font.Font("./Orbitron-Regular.ttf", 48)
font = pygame.font.Font("./Poppins-Regular.ttf", 24)

title = title_font.render('Optic Odyssey', True, BLACK)
title_rect = title.get_rect()
title_rect.center = (WIDTH//2, 120)

play_button = pygame.Rect(0, 0, 200, 50)
play_button.center = (WIDTH//2, 300)

play = font.render("Play", True, BLACK)
play_rect = play.get_rect()
play_rect.center = play_button.center

back_to_levels_button = pygame.Rect(0, 0, 300, 50)
back_to_levels_button.center = (WIDTH//2, 300)

back_to_levels = font.render("Back to Levels", True, BLACK)
back_to_levels_rect = back_to_levels.get_rect()
back_to_levels_rect.center = back_to_levels_button.center

level_cleared_txt = title_font.render("Level Cleared", True, BLACK)
level_cleared_rect = title.get_rect()
level_cleared_rect.center = (WIDTH//2, 120)

quit_button = pygame.Rect(0, 0, 200, 50)
quit_button.center = (2*WIDTH//3, 685)

quit = font.render("Quit", True, BLACK)
quit_rect = quit.get_rect()
quit_rect.center = quit_button.center

game_state = "start"
level_cleared = False

lvls = [Level(1, "n", (175, 200), font), Level(2, "l", (325, 200), font), 
        Level(3, "l", (475, 200), font), Level(4, "l", (625, 200), font),
        Level(5, "l", (175, 375), font), Level(6, "l", (325, 375), font), 
        Level(7, "l", (475, 375), font), Level(8, "l", (625, 375), font)]

light_button = pygame.Rect(0, 0, 200, 50)
light_button.center = (WIDTH//3, 685)
light_status = False
 
exit = True
clock = pygame.time.Clock()
 
while exit:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit = False

        if game_state == "start":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.collidepoint(event.pos):
                    game_state = "level"

        elif game_state == "level":
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                for lvl in lvls:
                    l = lvl.update(pos)
                    if l != None:
                        level = l
                        game_state = "play"
                        light_status = False
                        blocks = [Block(40, 40, *i) for i in levels.blocks_in_levels[level]]
                        mirrors = [Mirror(*i, screen) for i in levels.mirrors_in_levels[level]]
                        destination = pygame.draw.circle(screen, GREEN, levels.destination_in_levels[level], 20)
                        break

        elif game_state == "play":
            if not light_status:
                for mirror in mirrors:
                    mirror.update(event)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if light_button.collidepoint(event.pos):
                    if not light_status:
                        light_status = True
                        light_rays = [Light((450, 50), "r", screen), Light((450, 50), "d", screen), Light((450, 50), "l", screen)]
                        seen_light_rays = []
                    else:
                        light_status = False
                elif quit_button.collidepoint(event.pos):
                    game_state = "level"
                    light_status = False
        else:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_to_levels_button.collidepoint(event.pos):
                    game_state = "level"

    if light_status and game_state == "play":
        while light_rays:
            light_ray = light_rays[0]
            objects = []
            for block in blocks:
                if pygame.Rect.colliderect(block.rect, light_ray.rect):
                    objects.append(block)
            for mirror in mirrors:
                if pygame.Rect.colliderect(mirror.rect, light_ray.rect) and not mirror.rect.collidepoint(light_ray.start):
                    objects.append(mirror)

            if objects:
                min_obj = objects[0]
                for object in objects[1:]:
                    if light_ray.direction in "ud":
                        if abs(min_obj.rect.y - light_ray.start[1]) > abs(object.rect.y - light_ray.start[1]):
                            min_obj = object
                    else:
                        if abs(min_obj.rect.x - light_ray.start[0]) > abs(object.rect.x - light_ray.start[0]):
                            min_obj = object
                
                if pygame.Rect.colliderect(light_ray.rect, destination):     
                    if light_ray.direction in "ud":
                        if abs(min_obj.rect.y - light_ray.start[1]) > abs(destination.y - light_ray.start[1]):
                            level_cleared = True
                    else:
                        if abs(min_obj.rect.x - light_ray.start[0]) > abs(destination.x - light_ray.start[0]):
                            level_cleared = True

                    if level_cleared:
                        light_ray.update_end(destination)
                        seen_light_rays.append(light_rays.pop(0))
                        continue
                            

                if type(min_obj) == Block:
                    light_ray.update_end((min_obj.rect.x, min_obj.rect.y))
                else:
                    start = light_ray.update_end((min_obj.rect.x, min_obj.rect.y))
                    light_rays.append(Light(start, reflect(light_ray, min_obj), screen))
            else:
                if pygame.Rect.colliderect(light_ray.rect, destination):
                    light_ray.update_end(destination)
                    level_cleared = True

            seen_light_rays.append(light_rays.pop(0))
 
    screen.fill(SKY_BLUE)
    
    if game_state == "start":
        screen.blit(bg, (-50, -220))
        screen.blit(title, title_rect)

        if play_button.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(screen, ORANGE_DARK, play_button, border_radius=3)
        else:
            pygame.draw.rect(screen, ORANGE, play_button, border_radius=3)

        screen.blit(play, play_rect)

    elif game_state == "level":
        screen.blit(bg, (0, -120))
        for lvl in lvls:
            lvl.display(screen)

    elif game_state == "play":
        pygame.draw.circle(screen, YELLOW,  (450, 50), 8)

        if light_button.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(screen, ORANGE_DARK, light_button)
        else:
            pygame.draw.rect(screen, ORANGE, light_button)

        if quit_button.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(screen, ORANGE_DARK, quit_button)
        else:
            pygame.draw.rect(screen, ORANGE, quit_button)

        if light_status:
            light_text = font.render("Light OFF", True, BLACK)
            for light_ray in seen_light_rays:
                light_ray.draw(screen)
        else:
            light_text = font.render("Light ON", True, BLACK)

        light_text_rect = light_text.get_rect()
        light_text_rect.center = light_button.center

        screen.blit(light_text, light_text_rect)

        screen.blit(quit, quit_rect)

        for block in blocks:
            block.draw(RED, screen)

        for mirror in mirrors:
            mirror.draw(screen)

        pygame.draw.rect(screen, RED, pygame.Rect(0, 0, 900, 650), 5)

        destination = pygame.draw.circle(screen, (0, 255, 0), levels.destination_in_levels[level], 20)

    else:
        screen.blit(bg, (-50, -220))
        screen.blit(level_cleared_txt, level_cleared_rect)

        if back_to_levels_button.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(screen, ORANGE_DARK, back_to_levels_button, border_radius=3)
        else:
            pygame.draw.rect(screen, ORANGE, back_to_levels_button, border_radius=3)
        screen.blit(back_to_levels, back_to_levels_rect)

    pygame.display.flip()
    if game_state == "play" and level_cleared:
        pygame.time.delay(1000)
        level_cleared = False
        game_state = "level cleared"
        light_status = False
        lvls[level].status = "c"
        if level != len(lvls)-1:
            lvls[level+1].status = "n"

    clock.tick(60)

pygame.quit()