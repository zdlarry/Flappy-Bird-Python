import pygame
import sys
import numpy as np
import os


def load_imgs(path):
    return pygame.image.load(path).convert_alpha()


def load_sounds(name, stype):
    if 'win' in stype:
        soundExt = '.wav'
    else:
        soundExt = '.ogg'

    sound_base_path = 'assets/audio/'
    return pygame.mixer.Sound(os.path.join(sound_base_path, name + soundExt))


def load_data():
    # load data of player
    player_path = [
        'assets/sprites/redbird-upflap.png',
        'assets/sprites/redbird-midflap.png',
        'assets/sprites/redbird-downflap.png',
        'assets/sprites/redbird-midflap.png'
    ]

    # load path of background
    background_path = [
        './assets/sprites/background-black.png',
        './assets/sprites/bg_day.png',
        './assets/sprites/bg_night.png',
    ]

    # load path of pipe
    pipe_path = 'assets/sprites/pipe-green.png'

    # load path of base back
    base_path = 'assets/sprites/base.png'

    # load path of numbers
    nums_path = ['assets/sprites/' + str(i) + '.png' for i in range(0, 10)]

    # load path of medals
    medals_path = ['assets/sprites/medals_' + str(i) + '.png' for i in range(0, 4)]

    # load path of title
    title_path = 'assets/sprites/title.png'

    # load path of tutorial
    tutorial_path = 'assets/sprites/tutorial.png'

    # load path of score panel
    score_panel_path = 'assets/sprites/score_panel.png'

    # load buttons
    buttons_path = [
        'assets/sprites/button_pause.png',
        'assets/sprites/button_resume.png'
    ]

    # load play button
    play_path = 'assets/sprites/button_play.png'

    images, sounds, hit_masks = {}, {}, {}

    images['numbers'] = [load_imgs(path) for path in nums_path]
    images['player'] = [load_imgs(path) for path in player_path]
    images['pipe'] = [
        pygame.transform.rotate(load_imgs(pipe_path), 180),
        load_imgs(pipe_path)
    ]
    images['base'] = load_imgs(base_path)
    images['background'] = [load_imgs(path) for path in background_path]
    images['medals'] = [load_imgs(path) for path in medals_path]
    images['title'] = load_imgs(title_path)
    images['tutorial'] = load_imgs(tutorial_path)
    images['score_panel'] = load_imgs(score_panel_path)
    images['buttons'] = [load_imgs(path) for path in buttons_path]
    images['play'] = load_imgs(play_path)

    sounds_type = ['die', 'hit', 'point', 'swoosh', 'wing']

    for stype in sounds_type:
        sounds[stype] = load_sounds(stype, sys.platform)

    hit_masks['pipe'] = [getHitmask(img) for img in images['pipe']]
    hit_masks['player'] = [getHitmask(img) for img in images['player']]

    return images, sounds, hit_masks


def getHitmask(image):
    """returns a hitmask using an image's alpha."""
    mask = []
    for x in range(image.get_width()):
        mask.append([])
        for y in range(image.get_height()):
            mask[x].append(bool(image.get_at((x, y))[3]))
    return mask
