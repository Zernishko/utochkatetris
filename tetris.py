from settings import *
import pygame
import math
from tetromino import Tetromino
import pygame.freetype as ft

class Text:
    def __init__(self, app):
        self.app = app
        self.font = ft.Font(FONT_PATH)
    
    def draw(self):
        self.font.render_to(self.app.screen, (WIN_W * 0.515, WIN_H * 0.02),
                            text='UTOCHKATETRIS', fgcolor='black',
                            size=TILE_SIZE * 1.45)
        self.font.render_to(self.app.screen, (WIN_W * 0.52, WIN_H * 0.10),
                            text='Next:', fgcolor='black',
                            size=TILE_SIZE * 1.2)
        self.font.render_to(self.app.screen, (WIN_W * 0.52, WIN_H * 0.34),
                            text='Score:', fgcolor='black',
                            size=TILE_SIZE * 1.2)
        self.font.render_to(self.app.screen, (WIN_W * 0.62, WIN_H * 0.42),
                            text=f'{self.app.tetris.score}', fgcolor='black',
                            size=TILE_SIZE * 1.2)
        self.font.render_to(self.app.screen, (WIN_W * 0.8, WIN_H * 0.10),
                            text='Level:', fgcolor='black',
                            size=TILE_SIZE * 1.2)
        self.font.render_to(self.app.screen, (WIN_W * 0.86, WIN_H * 0.18),
                            text=f'{self.app.tetris.level}', fgcolor='black',
                            size=TILE_SIZE * 1.2)
        i = POS_STATISTICS.x
        for shape in self.app.tetris.statistics:
            self.font.render_to(self.app.screen, (WIN_W * i, WIN_H * POS_STATISTICS.y),
                                text=shape, fgcolor='black',
                                size=TILE_SIZE * 1.2)
            self.font.render_to(self.app.screen, (WIN_W * i, WIN_H * (POS_STATISTICS.y + 0.1)),
                                text=f'{self.app.tetris.statistics[shape]}', fgcolor='black',
                                size=TILE_SIZE * 1.1)
            i += 0.06


class Tetris:
    def __init__(self, app):
        self.app = app
        self.sprite_group = pg.sprite.Group()
        self.field_array = self.get_field_array()
        self.tetromino = Tetromino(self)
        self.next_tetromino = Tetromino(self, current=False)
        self.speed_up = False
        self.is_moving_right = False
        self.is_moving_left = False


        self.level = 0
        self.score = 0
        self.full_lines = 0
        self.points_per_lines = {0: 0, 1: 1, 2: 3, 3: 7, 4: 15}
        self.statistics_tetrominoes = {}
        self.statistics = {}
        for key in TETROMINOES:
            self.statistics[key] = 0

    def get_score(self):
        self.score += self.points_per_lines[self.full_lines]
        self.full_lines = 0
        self.level = self.score // 10


    def check_full_lines(self):
        row = FIELD_H - 1
        for y in range(FIELD_H - 1, -1, -1):
            for x in range(FIELD_W):
                self.field_array[row][x] = self.field_array[y][x]

                if self.field_array[y][x]:
                    self.field_array[row][x].pos = vec(x, y)

            if sum(map(bool, self.field_array[y])) < FIELD_W:
                row -= 1
            else:
                for x in range(FIELD_W):
                    self.field_array[row][x].alive = False
                    self.field_array[row][x] = 0

                self.full_lines += 1

    def put_tetromino_blocks_in_array(self):
        for block in self.tetromino.blocks:
            x, y = int(block.pos.x), int(block.pos.y)
            self.field_array[y][x] = block

    def get_field_array(self):
        return [[0 for x in range(FIELD_W)] for y in range(FIELD_H)]
    
    def is_game_over(self):
        if self.tetromino.blocks[0].pos.y == INIT_POS_OFFSET[1]:
            pg.time.wait(300)
            return True


    def check_tetromino_landing(self):
        if self.tetromino.landing:
            if self.is_game_over():
                self.__init__(self.app)
            else:
                self.speed_up = False
                self.put_tetromino_blocks_in_array()
                self.next_tetromino.current = True
                self.tetromino = self.next_tetromino
                self.next_tetromino = Tetromino(self, current=False)
                self.statistics[self.tetromino.shape] += 1

    def control(self, pressed_key, keydown):
        if pressed_key == pg.K_LEFT:
            self.is_moving_left = keydown
            if keydown:
                self.tetromino.move(direction='left')
        elif pressed_key == pg.K_RIGHT:
            self.is_moving_right = keydown
            if keydown:
                self.tetromino.move(direction='right')
        elif pressed_key == pg.K_SPACE and keydown:
            self.tetromino.rotate()
        elif pressed_key == pg.K_DOWN:
            self.speed_up = keydown

    def draw_grid(self):
        for x in range(FIELD_W):
            for y in range(FIELD_H):
                pg.draw.rect(self.app.screen, 'black',
                             (x * TILE_SIZE,  y * TILE_SIZE, TILE_SIZE, TILE_SIZE), 1)

    def update(self):
        trigger = [self.app.anim_trigger, self.app.fast_anim_trigger][self.speed_up]
        if trigger:
            self.check_full_lines()
            self.tetromino.update()
            self.check_tetromino_landing()
            self.get_score()
        self.sprite_group.update()

    def draw(self):
        self.draw_grid()
        self.sprite_group.draw(self.app.screen)