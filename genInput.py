from brian2 import *
from random import randint

# Create indexes for vertical movements (0 is index for ON event from Pixel 1, 1 is index for OFF event from Pixel 1...)
def createPatterns(nbPixels):
    # Up = ON from Pixel 1, OFF from Pixel 2
    up = [nbPixels*2 - 1, (nbPixels-2)*2] + [i - j for j in range(2, (nbPixels - 1) * 2, 2) for i in [nbPixels*2 - 1, (nbPixels-2)*2]]

    # Down = OFF from Pixel 1, ON from Pixel 2
    down = [1, 2] + [i + j for j in range(2, (nbPixels - 1) * 2, 2) for i in [1, 2]]

    return {'up':up, 'down':down}

# Create an Input which introduce vertical movements in an alternate order (up, down, up, down...)
def genAlternateVerticalMovements(nbPixels, nbPixelStates, nbPatterns):
    patterns = createPatterns(nbPixels)

    indexes = []
    time = [i + j for j in range(0, (nbPixels - 1) * 2, 2) for i in[1, 1]]

    pattern_length = time[len(time) - 1] + 5
    times = time + [i + j for j in range(pattern_length, nbPatterns * pattern_length, pattern_length) for i in time]
    times *= ms

    for i in range(nbPatterns):
        if i % 2 == 0:
            indexes += patterns['up']
        else:
            indexes += patterns['down']
    #
    # for i in range(nbPatterns):
    #     if randint(0, 2) == 0:
    #         indexes += patterns['up']
    #     else:
    #         indexes += patterns['down']

    input = SpikeGeneratorGroup(nbPixels * nbPixelStates, indexes, times)

    return input

# Create an Input which introduce vertical movements in a random order (up as much as down)
def genRandomVerticalMovements(nbPixels, nbPixelStates, nbPatterns):
    patterns = createPatterns(nbPixels)

    indexes = []
    time = [1, 1, 3, 3, 5, 5]
    times = time + [i + j for j in range(10, nbPatterns * 10, 10) for i in time]
    times *= ms

    upCounter = 0
    downCounter = 0

    for i in range(nbPatterns):
        if (randint(0, 2) == 0 and upCounter < (nbPatterns/2)) or downCounter >= (nbPatterns/2):
            indexes += patterns['up']
            upCounter += 1
        else:
            indexes += patterns['down']
            downCounter += 1

    input = SpikeGeneratorGroup(nbPixels * nbPixelStates, indexes, times)

    return input
