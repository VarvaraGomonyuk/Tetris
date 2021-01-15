import pygame
import sys
import os
import copy
import sqlite3
from random import choice


pygame.init()
pygame.key.set_repeat(200, 70)

FPS = 60
WIDTH = 500
HEIGHT = 800

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
        intro_rect.x = 90
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
        self.board = [[0] * 10 for _ in range(20)]
        self.left = 30
        self.top = 30
        self.cell_size = 30

    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def render(self, surface):
        color = pygame.Color('purple')
        for i in range(self.height):
            for j in range(self.width):
                pygame.draw.rect(surface, color, (self.left + self.cell_size * j, self.top + self.cell_size * i,
                                                   self.cell_size, self.cell_size), 1 if self.board[i][j] == 0 else 0)

        text = ['SCORE']
        font = pygame.font.Font(None, 50)
        text_coord = 30
        for line in text:
            string_rendered = font.render(line, True, pygame.Color('purple'))
            rect = string_rendered.get_rect()
            rect.top = text_coord
            rect.x = 350
            text_coord += rect.height
            screen.blit(string_rendered, rect)


class Play(Board):
    def __init__(self, width, height, left=30, top=30, cell_size=30):
        super().__init__(width, height)
        self.set_view(left, top, cell_size)
        
        self.field = copy.deepcopy(self.board)
        self.score = 0
        self.scores = {0: 0, 1: 100, 2: 300, 3: 700, 4: 1500}
        self.color = str()
        self.figure = str()
        self.figures = []
        self.colors = [(255, 255, 0), (0, 128, 0), (0, 0, 255), (255, 0, 0), (255, 165, 0)]
        # for all 2nd - rotate center, 1st - left edge, 4th - right edge, 3rd - y edge
        self.figures_coords = [[(120, 30), (150, 30), (180, 30), (210, 30)], # line
                            [(150, 30), (180, 30), (150, 60), (180, 60)], # cube
                            [(120, 60), (150, 30), (150, 60), (180, 30)], # S-shape
                            [(120, 30), (150, 30), (150, 60), (180, 60)], # Z-shape
                            [(150, 30), (180, 60), (180, 90), (180, 30)], 
                            [(150, 30), (150, 60), (150, 90), (180, 30)], # Г-shape edge 
                            [(120, 30), (150, 30), (150, 60), (180, 30)]] # T-shape edge 

        self.rect = pygame.Rect(self.left, self.top, self.cell_size - 2, self.cell_size - 2)

        self.create_figures()

    def create_figures(self):
        for figure_coord in self.figures_coords:
            figure = []
            for coord in figure_coord:
                figure.append(pygame.Rect(coord[0], coord[1], 30, 30))
            self.figures.append(figure)
        self.figure = copy.deepcopy(choice(self.figures))

        self.color = choice(self.colors)

    def draw_figures(self):
        for i in range(4):
            self.rect.x = self.figure[i].x
            self.rect.y = self.figure[i].y
            pygame.draw.rect(screen, pygame.Color(self.color), self.rect)
        self.move_down()

    def check(self, i): # check for borders
        if self.figure[i].x < 30 or self.figure[i].x > 300:
            return False
        elif self.figure[i].y >= 600 or self.field[self.figure[i].y // 30][self.figure[i].x // 30 - 1]:
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

    def move_down(self, speed=120):
        old_figure = copy.deepcopy(self.figure)
        for i in range(4):
            self.figure[i].y += speed // FPS
            if not self.check(i):
                for i in range(4):
                    x = int(old_figure[i].x // 30) - 1
                    y = int(old_figure[i].y // 30)
                    if not self.field[y][x]:
                        self.field[y][x] = self.color
                self.fallen_figures()
                self.figure = copy.deepcopy(choice(self.figures))
                self.color = choice(self.colors)
                break

    def fallen_figures(self):
        for i in range(self.width):
            if self.field[1][i]:
                self.game_over()
        for y, raw in enumerate(self.field):
            for x, col in enumerate(raw):
                if col:
                    self.rect.x = (x + 1) * self.cell_size
                    self.rect.y = (y + 1) * self.cell_size
                    pygame.draw.rect(screen, col, self.rect)

    def rotate(self):
        center = self.figure[1] # takking center of rotation
        old_figure = copy.deepcopy(self.figure)
        for i in range(4):
            x = self.figure[i].y - center.y #finding new coords
            y = self.figure[i].x - center.x 
            self.figure[i].x = center.x - x
            self.figure[i].y = center.y + y
            if not self.check(i):
                self.figure = copy.deepcopy(old_figure)
                break

    def lines_check(self):
        line, lines = self.height - 1, 0
        for row in range(self.height - 1, -1, -1):
            count = 0
            for i in range(self.width):
                if self.field[row][i]:
                    count += 1
                self.field[line][i] = self.field[row][i]
            if count < self.width:
                line -= 1
            else:
                lines += 1
        self.score += self.scores[lines]
        
        text = [str(self.score)]
        font = pygame.font.Font(None, 50)
        text_coord = 100
        for line in text:
            string_rendered = font.render(line, True, pygame.Color('purple'))
            rect = string_rendered.get_rect()
            rect.top = text_coord
            rect.x = 350
            text_coord += rect.height
            screen.blit(string_rendered, rect)
    
    def game_over(self):
        self.write_scores(self.score)
        self.field = copy.deepcopy(self.board)
        for i in range(30, 600, 30):
            for j in range(30, 330, 30):
                self.rect.x = j
                self.rect.y = i
                pygame.draw.rect(screen, pygame.Color(choice(self.colors)), self.rect)
        self.score = 0

    def write_scores(self, score):
        con = sqlite3.connect("data/ResultsDB.sqlite")
        cur = con.cursor()
        request = f"INSERT INTO results(score) VALUES({score})"
        cur.execute(request)
        con.commit()
        con.close()

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
                board.move_down(500)
            if event.key == pygame.K_UP:
                board.rotate()

    screen.fill(pygame.Color(36, 9, 53))
    board.render(screen)
    board.draw_figures()
    board.fallen_figures()
    board.lines_check()
    pygame.display.flip()
    clock.tick(FPS)
terminate()