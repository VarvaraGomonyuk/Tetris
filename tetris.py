import pygame
import sys
import os
import copy
from random import choice


pygame.init()
pygame.key.set_repeat(200, 70)

FPS = 60
WIDTH = 450
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname).convert()
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)

    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ['Welcome to TETRIS']
    fon = pygame.transform.scale(load_image('intro.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))

    font = pygame.font.Font(None, 50)
    text_coord = 300
    for line in intro_text:
        string_rendered = font.render(line, True, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        intro_rect.top = text_coord
        intro_rect.x = 55
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)


    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return

        pygame.display.flip()
        clock.tick(FPS)


class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[0] * width for _ in range(height)]
        self.left = 25
        self.top = 25
        self.cell_size = 25

    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def render(self, surface):
        color = pygame.Color('white')
        for i in range(self.height):
            for j in range(self.width):
                pygame.draw.rect(surface, color, (self.left + self.cell_size * j, self.top + self.cell_size * i,
                                                   self.cell_size, self.cell_size), 1 if self.board[i][j] == 0 else 0)


class Play(Board):
    def __init__(self, width, height, left=25, top=25, cell_size=25):
        super().__init__(width, height)
        self.set_view(left, top, cell_size)
        
        self.field = []
        self.color = str()
        self.figure = str()
        self.figures = []
        self.colors = [(255, 255, 0), (0, 128, 0), (0, 0, 255), (255, 0, 0), (255, 165, 0)]
        # for all 2nd - rotate center, 1st - left edge, 4th - right edge, 3rd - y edge
        self.figures_coords = [[(100, 25), (125, 25), (150, 25), (175, 25)], # line
                            [(125, 25), (150, 25), (125, 50), (150, 50)], # cube edge for y - 3rd
                            [(100, 50), (125, 25), (125, 50), (150, 25)], # S-shape edge for y - 3nd
                            [(100, 25), (125, 25), (125, 50), (150, 50)], # Z-shape edge for y - 3rd
                            [(125, 25), (150, 50), (150, 75), (150, 25)], # edge for y - 3rd
                            [(125, 25), (125, 50), (125, 75), (150, 25)], # Г-shape edge for y - 3rd
                            [(100, 25), (125, 25), (125, 50), (150, 25)]] # T-shape edge for y - 3rd

        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(0)
            self.field.append(row)

        self.rect = pygame.Rect(self.left, self.top, self.cell_size - 2, self.cell_size - 2)

        self.create_figures()

    def create_figures(self):
        for figure_coord in self.figures_coords:
            figure = []
            for coord in figure_coord:
                figure.append(pygame.Rect(coord[0], coord[1], 25, 25))
            self.figures.append(figure)
        self.figure = choice(self.figures)

        self.color = choice(self.colors)

    def draw_figures(self):
        for i in range(4):
            self.rect.x = self.figure[i].x
            self.rect.y = self.figure[i].y
            pygame.draw.rect(screen, pygame.Color(self.color), self.rect)

    def check(self, i):
        if self.figure[i].x < 25 or self.figure[i].x > 270:
            return False
        elif self.figure[i].y > 500:
            return False
        return True

    def move_left(self):
        old_figure = copy.deepcopy(self.figure)
        for i in range(4):
            self.figure[i].x -= self.cell_size
            if not self.check(i):
                self.figure = copy.deepcopy(old_figure)
                break

    def move_right(self):
        old_figure = copy.deepcopy(self.figure)
        for i in range(4):
            self.figure[i].x += self.cell_size
            if not self.check(i):
                self.figure = copy.deepcopy(old_figure)
                break

    def move_down(self):
        old_figure = copy.deepcopy(self.figure)
        for i in range(4):
            self.figure[i].y += self.cell_size
            if not self.check(i):
                self.figure = copy.deepcopy(old_figure)
                break

    def rotate(self):
        center = self.figure[1]
        old_figure = copy.deepcopy(self.figure)
        for i in range(4):
            x = self.figure[i].y - center.y
            y = self.figure[i].x - center.x
            self.figure[i].x = center.x - x
            self.figure[i].y = center.y + y
            if not self.check(i):
                self.figure = copy.deepcopy(old_figure)
                break


start_screen()

board = Play(10, 20)

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                board.move_right()
            if event.key == pygame.K_LEFT:
                board.move_left()
            if event.key == pygame.K_DOWN:
                board.move_down()
            if event.key == pygame.K_UP:
                board.rotate()

    screen.fill(pygame.Color(36, 9, 53))
    board.render(screen)
    board.draw_figures()
    pygame.display.flip()
    clock.tick(FPS)
terminate()