import pygame
from pygame.locals import *
import pygame.surfarray as surfarray
import sys
import numpy as np
import random
from itertools import cycle
from flappy_bird_utils import load_data
from abc import ABCMeta, abstractmethod


class ScoreRecorder(object):
    """docstring for ScoreRecorder"""

    def __init__(self):
        super(ScoreRecorder, self).__init__()
        self.max_score = 0

    def compare(self, score):
        if score > self.max_score:
            self.max_score = score

    def get_max_score(self):
        return self.max_score


class Bird(pygame.sprite.Sprite):
    """docstring for bird"""

    def __init__(self, frames, initial_pos, wing_sound):
        pygame.sprite.Sprite.__init__(self)
        self.frames = frames
        self.last_time = 0
        self.frame_index = 0
        self.x, self.y = initial_pos
        self.frame_nums = len(self.frames)
        self.image = self.frames[self.frame_index]
        self.rect = Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
        self.wing_sound = wing_sound

        self.init_bird_params()

    def init_bird_params(self):
        # vy = vy_0 + a * t
        # y = vy_0 * t + a * t^2 / 2
        # 这里每隔一帧加下
        # 初速度
        self.bird_vec_y = 0
        # 最大速度
        self.bird_vec_y_max = 10
        # 加速度
        self.bird_acc_y = 1
        # 向上加速度
        self.bird_flappy_acc_y = -20

    def calc_vector(self):
        if abs(self.bird_vec_y + self.bird_acc_y) < self.bird_vec_y_max:
            return self.bird_vec_y + self.bird_acc_y
        else:
            if self.bird_vec_y + self.bird_acc_y < 0:
                return -self.bird_vec_y_max
            else:
                return self.bird_vec_y_max

    def calc_y(self):
        self.bird_vec_y = self.calc_vector()
        self.y += self.bird_vec_y

    def flappy(self):
        self.wing_sound.play()
        self.bird_acc_y = self.bird_flappy_acc_y
        self.bird_vec_y = self.calc_vector()
        self.bird_acc_y = 1
        self.y += self.bird_vec_y

        if self.y < 0:
            self.y = 0

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def get_frame_index(self):
        return self.frame_index

    def update(self, current_time, rate=60):
        if current_time > self.last_time + rate:
            self.frame_index += 1
            self.frame_index %= self.frame_nums
            self.last_time = current_time

        self.calc_y()
        self.image = self.frames[self.frame_index]
        self.rect = Rect(self.x, self.y, self.image.get_width(), self.image.get_height())


class BaseFloor(pygame.sprite.Sprite):
    """docstring for BaseFloor"""

    def __init__(self, frame, initial_pos, base_shift):
        pygame.sprite.Sprite.__init__(self)
        self.image = frame
        self.last_time = 0
        self.x, self.y = initial_pos
        self.base_shift = base_shift
        self.rect = Rect(self.x, self.y, self.image.get_width(), self.image.get_height())

    def get_x(self):
        return self.x

    def update(self, current_time, rate=60):
        if current_time > self.last_time + rate:
            self.x = -((-self.x + 100) % self.base_shift)
            self.last_time = current_time

        self.rect = Rect(self.x, self.y, self.image.get_width(), self.image.get_height())


class Pipe(pygame.sprite.Sprite):
    """docstring for Pipe"""

    def __init__(self, initial_x, initial_y, pipe_width):
        super(Pipe, self).__init__()
        self.pipe_val_x = -4
        self.pipe_width = pipe_width
        self.set_pos(initial_x, initial_y)

    def set_pos(self, x, y):
        self.pipe_x = x
        self.pipe_y = y

    def get_x(self):
        return self.pipe_x

    def get_y(self):
        return self.pipe_y

    @abstractmethod
    def update(self, current_time, rate=60):
        pass


class PipeUpper(Pipe):
    """docstring for Pipes"""

    def __init__(self, frame, initial_x, initial_y, pipe_width):
        super(PipeUpper, self).__init__(initial_x, initial_y, pipe_width)
        self.image = frame
        self.last_time = 0
        self.rect = Rect(self.pipe_x, self.pipe_y, self.image.get_width(), self.image.get_height())

    def update(self, current_time, rate=60):
        if current_time > self.last_time + rate:
            self.pipe_x += self.pipe_val_x
            self.last_time = current_time

        if self.pipe_x < -self.pipe_width:
            self.kill()

        self.rect = Rect(self.pipe_x, self.pipe_y, self.image.get_width(), self.image.get_height())


class PipeLower(Pipe):
    """docstring for Pipe"""

    def __init__(self, frame, initial_x, initial_y, pipe_width):
        super(PipeLower, self).__init__(initial_x, initial_y, pipe_width)
        self.image = frame
        self.last_time = 0
        self.rect = Rect(self.pipe_x, self.pipe_y, self.image.get_width(), self.image.get_height())

    def update(self, current_time, rate=60):
        if current_time > self.last_time + rate:
            self.pipe_x += self.pipe_val_x
            self.last_time = current_time

        if self.pipe_x < -self.pipe_width:
            self.kill()

        self.rect = Rect(self.pipe_x, self.pipe_y, self.image.get_width(), self.image.get_height())


class Title(pygame.sprite.Sprite):
    """docstring for Title"""

    def __init__(self, initial_pos, frame, final_pos):
        pygame.sprite.Sprite.__init__(self)
        self.x, self.y = initial_pos
        self.f_x, self.f_y = final_pos
        self.image = frame
        self.last_time = 0
        self.vector = 0
        self.acc = .5
        self.vector_max = 5

    def calc_vector(self):
        return np.max([self.vector + self.acc, self.vector_max])

    def calc_y(self):
        self.vector = self.calc_vector()
        return self.y + self.vector

    def update(self, current_time, rate=60):
        if current_time > self.last_time + rate:
            if self.y < self.f_y:
                self.y = self.calc_y()
            self.last_time = current_time

        self.rect = Rect(self.x, self.y, self.image.get_width(), self.image.get_height())


class Tutorial(pygame.sprite.Sprite):
    """docstring for Title"""

    def __init__(self, initial_pos, frame):
        pygame.sprite.Sprite.__init__(self)
        self.x, self.y = initial_pos
        self.image = frame
        self.last_time = 0
        self.alpha = 0

    def update(self, current_time, rate=60):
        if current_time > self.last_time + rate:
            self.last_time = current_time

        self.rect = Rect(self.x, self.y, self.image.get_width(), self.image.get_height())


class Game(object):
    """docstring for Game"""

    def __init__(self, recoder):
        super(Game, self).__init__()
        self.recoder = recoder
        self.screen_width = 288
        self.screen_height = 512
        self.fps = 30
        self.pipe_gap_size = 100
        self.base_pos = [0, self.screen_height * 0.79]
        self.score = 0
        self.initial()
        self.load_resources()
        self.initial_sprites()
        self.welcome_game()
        end_infos = self.main_game()
        self.end_game(end_infos)

    def initial(self):
        pygame.init()
        self.fps_clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption('Flappy bird')

    def load_resources(self):
        self.images, self.sounds, self.hit_mask = load_data()

        self.bird_height = self.images['player'][0].get_height()
        self.bird_width = self.images['player'][0].get_width()

        self.base_shift = self.images['base'].get_width() - self.screen_width

        self.pipe_height = self.images['pipe'][0].get_height()
        self.pipe_width = self.images['pipe'][0].get_width()

        self.title_height = self.images['title'].get_height()
        self.title_width = self.images['title'].get_width()

        self.score_panel_height = self.images['score_panel'].get_height()
        self.score_panel_width = self.images['score_panel'].get_width()

        self.play_width = 80

        self.tutorial_width = self.images['tutorial'].get_width()

        self.background_index = np.random.randint(1, 3)

    def initial_sprites(self):
        self.group = pygame.sprite.Group()
        self.wel_group = pygame.sprite.Group()

        bird_x = int(self.screen_width * 0.2)
        bird_y = int((self.screen_height - self.bird_height) / 2)
        self.bird = Bird(self.images['player'], [bird_x, bird_y], self.sounds['wing'])

        new_pipe = self.get_random_pipes()

        self.pipe_uppers = []
        self.pipe_lowers = []

        self.pipe_uppers.append(PipeUpper(self.images['pipe'][0], new_pipe[0]['x'], new_pipe[0]['y'], self.pipe_width))
        self.pipe_lowers.append(PipeLower(self.images['pipe'][1], new_pipe[1]['x'], new_pipe[1]['y'], self.pipe_width))

        self.base = BaseFloor(self.images['base'], self.base_pos, self.base_shift)

        title_x = (self.screen_width - self.title_width) / 2
        self.title = Title([title_x, - self.title_height],
                           self.images['title'], [title_x, self.screen_height * 0.15])

        tutorial_x = (self.screen_width - self.tutorial_width) / 2
        self.tutorial = Tutorial([tutorial_x, self.screen_height * 0.35], self.images['tutorial'])

        self.wel_group.add(self.title)
        self.wel_group.add(self.tutorial)

        self.group.add(self.pipe_uppers[0])
        self.group.add(self.pipe_lowers[0])

        self.group.add(self.bird)
        self.group.add(self.base)

    def get_random_pipes(self):
        gap_ys = [20, 30, 40, 50, 60, 70, 80, 90, 100, 110]
        index = random.randint(0, len(gap_ys) - 1)
        gap_y = gap_ys[index]
        gap_y += int(self.base_pos[1] * 0.2)

        pipe_x = self.screen_width + 10

        return[
            {'x': pipe_x, 'y': gap_y - self.pipe_height},
            {'x': pipe_x, 'y': gap_y + self.pipe_gap_size}
        ]

    def check_new_pipes(self):
        if self.pipe_uppers[0].get_x() < -self.pipe_width:
            self.pipe_uppers.pop(0)
            self.pipe_lowers.pop(0)

        threshold = 2 * self.pipe_width

        if threshold - 4 < self.pipe_uppers[0].get_x() < threshold:
            new_pipe = self.get_random_pipes()

            self.pipe_uppers.append(PipeUpper(self.images['pipe'][0],
                                              new_pipe[0]['x'], new_pipe[0]['y'], self.pipe_width))
            self.pipe_lowers.append(PipeLower(self.images['pipe'][1],
                                              new_pipe[1]['x'], new_pipe[1]['y'], self.pipe_width))

            self.group.add(self.pipe_uppers[-1])
            self.group.add(self.pipe_lowers[-1])

            self.base.kill()
            self.group.add(self.base)

    def check_collision(self):
        for u_pipe, l_pipe in zip(self.pipe_uppers, self.pipe_lowers):
            if pygame.sprite.collide_mask(self.bird, u_pipe) or pygame.sprite.collide_rect(self.bird, l_pipe):
                return True
        if pygame.sprite.collide_mask(self.bird, self.base):
            return True
        return False

    def check_score(self):
        bird_mid_x = self.bird.get_x() + self.bird_width / 2
        for u_pipe in self.pipe_uppers:
            pipe_mid_x = u_pipe.get_x() + self.pipe_width / 2
            if pipe_mid_x <= bird_mid_x < pipe_mid_x + 4:
                self.sounds['point'].play()
                self.score += 1

    def show_score(self):
        score_digits = [int(x) for x in list(str(self.score))]
        total_width = 0

        for digit in score_digits:
            total_width += self.images['numbers'][digit].get_width()

        score_x = (self.screen_width - total_width) / 2

        for digit in score_digits:
            self.screen.blit(self.images['numbers'][digit], (score_x, self.screen_height * 0.1))
            score_x += self.images['numbers'][digit].get_width()

    def welcome_game(self):
        while True:
            self.fps_clock.tick(self.fps)
            ticks = pygame.time.get_ticks()
            for event in pygame.event.get():
                if event.type == QUIT:
                    sys.exit()
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    x, y = event.pos
                    if self.screen_width / 2 - 30 < x < self.screen_width / 2 + 30 and self.screen_height / 2 - 30 < y < self.screen_height / 2 + 30:
                        self.screen.fill((0, 0, 0))
                        return
                if event.type == KEYDOWN and event.key == K_SPACE:
                    self.screen.fill((0, 0, 0))
                    return

            self.screen.blit(self.images['background'][1], (0, 0))

            self.wel_group.update(ticks, self.fps)
            self.wel_group.draw(self.screen)

            pygame.display.flip()

    def main_game(self):
        while True:
            # 顺序处理事件
            pygame.event.pump()
            self.fps_clock.tick(self.fps)
            ticks = pygame.time.get_ticks()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                    self.bird.flappy()

            self.screen.blit(self.images['background'][self.background_index], (0, 0))

            self.check_score()
            self.check_new_pipes()

            self.group.update(ticks, self.fps)
            self.group.draw(self.screen)
            self.show_score()

            if self.check_collision():
                self.sounds['hit'].play()
                self.sounds['die'].play()
                end_u_pipes = []
                end_l_pipes = []

                self.group.remove()
                for pipe in self.pipe_uppers:
                    end_u_pipes.append({'x': pipe.get_x(), 'y': pipe.get_y()})
                for pipe in self.pipe_lowers:
                    end_l_pipes.append({'x': pipe.get_x(), 'y': pipe.get_y()})
                bird = {'x': self.bird.get_x(), 'y': self.bird.get_y(), 'f_index': self.bird.get_frame_index()}
                base = {'x': self.base.get_x()}
                return {
                    'u_pipes': end_u_pipes,
                    'l_pipes': end_l_pipes,
                    'bird': bird,
                    'base': base,
                    'score': self.score
                }

            pygame.display.flip()

    def end_game(self, end_infos):
        self.screen.fill((0, 0, 0))
        u_pipes = end_infos['u_pipes']
        l_pipes = end_infos['l_pipes']
        bird = end_infos['bird']
        base = end_infos['base']
        score = end_infos['score']
        self.recoder.compare(score)
        max_score = self.recoder.get_max_score()

        if score < 10:
            medal_index = 0
        elif score >= 10 and score < 30:
            medal_index = 1
        elif score >= 30 and score < 70:
            medal_index = 2
        else:
            medal_index = 3

        font = pygame.font.Font(None, 23)
        score_text = font.render(str(score), True, (0, 0, 0))
        max_score_text = font.render(str(max_score), True, (0, 0, 0))

        while True:
            self.fps_clock.tick(self.fps)
            ticks = pygame.time.get_ticks()
            play_x = (self.screen_width - self.play_width) / 2

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    x, y = event.pos
                    if play_x < x < play_x + 80 and self.screen_height * 0.55 < y < self.screen_height * 0.55 + 40:
                        self.__init__(self.recoder)

            self.screen.blit(self.images['background'][self.background_index], (0, 0))
            for u_pipe, l_pipe in zip(u_pipes, l_pipes):
                self.screen.blit(self.images['pipe'][0], (u_pipe['x'], u_pipe['y']))
                self.screen.blit(self.images['pipe'][1], (l_pipe['x'], l_pipe['y']))

            self.screen.blit(self.images['player'][bird['f_index']], (bird['x'], bird['y']))
            self.screen.blit(self.images['base'], (base['x'], self.base_pos[1]))

            panel_x = (self.screen_width - self.score_panel_width) / 2
            panel_y = (self.screen_height - self.score_panel_height) / 2 - 50
            self.screen.blit(self.images['score_panel'], (panel_x, panel_y))
            self.screen.blit(self.images['medals'][medal_index], (panel_x + 30, panel_y + 45))
            self.screen.blit(score_text, (panel_x + 185, panel_y + 40))
            self.screen.blit(max_score_text, (panel_x + 190, panel_y + 80))

            self.screen.blit(pygame.transform.smoothscale(
                self.images['play'], (80, 40)), (play_x, self.screen_height * 0.55))

            pygame.display.flip()


if __name__ == '__main__':
    recoder = ScoreRecorder()
    game = Game(recoder)
