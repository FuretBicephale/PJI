from brian2 import *
from random import randint

# Create indexes for vertical movements (0 is index for ON event from Pixel 1, 1 is index for OFF event from Pixel 1...)
# Speed : 1 = default, >1 = faster
def createPatterns(nbPixels, speed):
    if(speed < 1 or speed > (nbPixels-1)):
        print "Error : invalid speed for patterns"
        return

    # Up = ON from Pixel 1, OFF from Pixel 2
    up = [nbPixels*2 - 1, (nbPixels-2)*2 - 2*(speed-1)] + [i - j for j in range(2*speed, (nbPixels - 1) * 2, 2*speed) for i in [nbPixels*2 - 1, (nbPixels-2)*2 - 2*(speed-1)]]

    # Down = OFF from Pixel 1, ON from Pixel 2
    down = [1, 2 + 2*(speed-1)] + [i + j for j in range(2*speed, (nbPixels - 1) * 2, 2*speed) for i in [1, 2 + 2*(speed-1)]]

    return {'up':up, 'down':down}

def createTwoColumnsPatterns(nbPixels, speed):
    if(speed < 1 or speed > (nbPixels-1)):
        print "Error : invalid speed for patterns"
        return

    if nbPixels%2 != 0:
        print "Error : invalid pixels number for two columns patterns (odd number)"
        return

    # Up = ON from Pixel 1, OFF from Pixel 2
    up = [nbPixels - 1, (nbPixels-4) - 2*(speed-1), nbPixels*2 - 1, (nbPixels-2)*2 - 2*(speed-1)] + [i - j for j in range(2*speed, nbPixels - 2, 2*speed) for i in [nbPixels - 1, (nbPixels-2) - 2*(speed-1), nbPixels*2 - 1, (nbPixels-2)*2 - 2*(speed-1)]]

    print up

    # Down = OFF from Pixel 1, ON from Pixel 2
    down = [1, 2 + 2*(speed-1), nbPixels + 1, nbPixels + 2 + 2*(speed-1)] + [i + j for j in range(2*speed, nbPixels - 2, 2*speed) for i in [1, 2 + 2*(speed-1), nbPixels + 1, nbPixels + 2 + 2*(speed-1)]]

    print down

    return {'up':up, 'down':down}

# Create an Input which introduce vertical movements in an alternate order (up, down, up, down...)
def genAlternateVerticalMovements(nbPixels, nbPixelStates, nbPatterns):
    patterns = createPatterns(nbPixels, 1)

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

    input = SpikeGeneratorGroup(nbPixels * nbPixelStates, indexes, times)

    return input

# Create an Input which introduce vertical movements in a random order (up as much as down)
def genRandomVerticalMovements(nbPixels, nbPixelStates, nbPatterns):
    patterns = createPatterns(nbPixels, 1)

    indexes = []
    time = [i + j for j in range(0, (nbPixels - 1) * 2, 2) for i in[1, 1]]

    pattern_length = time[len(time) - 1] + 5
    times = time + [i + j for j in range(pattern_length, nbPatterns * pattern_length, pattern_length) for i in time]
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

# noise : 0 = no noise, 100 = max noise (%)
def genAlternateVerticalMovementsAlternateSpeed(nbPixels, nbPixelStates, nbPatterns, noise):
    patterns = createPatterns(nbPixels, 1)
    patterns2 = createPatterns(nbPixels, 2)

    indexes = []
    time = [i + j for j in range(0, (nbPixels - 1) * 2, 2) for i in[1, 1]]
    time += [i + j for j in range((nbPixels - 1) * 2 + 8, (nbPixels - 1) * 3 + 8, 2) for i in[1, 1]]

    pattern_length = time[len(time) - 1] + 9
    times = time + [i + j for j in range(pattern_length, nbPatterns/2 * pattern_length, pattern_length) for i in time]

    for i in range(nbPatterns/2):
        if i % 2 == 0:
            indexes += patterns['up']
            indexes += patterns2['up']
        else:
            indexes += patterns['down']
            indexes += patterns2['down']

    nbLoop = (noise * len(indexes))/100
    for i in range(0, nbLoop):
        ind = randint(0, len(indexes))
        del indexes[ind]
        del times[ind]
     
    times *= ms  

    input = SpikeGeneratorGroup(nbPixels * nbPixelStates, indexes, times)

    return input

def genTwoColumnsMovements(nbPixels, nbPixelStates, nbPatterns, noise):
    if nbPixels%2 != 0:
        print "Error : invalid pixels number for two columns patterns (odd number)"
        return
    
    patterns = createTwoColumnsPatterns(nbPixels, 1)

    indexes = []
    time = [i + j for j in range(0, nbPixels - 2, 2) for i in[1, 1, 1, 1]]

    pattern_length = time[len(time) - 1] + 5
    times = time + [i + j for j in range(pattern_length, nbPatterns * pattern_length, pattern_length) for i in time]

    for i in range(nbPatterns):
        if i % 2 == 0:
            indexes += patterns['up']
        else:
            indexes += patterns['down']

    nbLoop = (noise * len(indexes))/100
    for i in range(0, nbLoop):
        ind = randint(0, len(indexes))
        del indexes[ind]
        del times[ind]
        
    times *= ms

    input = SpikeGeneratorGroup(nbPixels * nbPixelStates, indexes, times)

    return input