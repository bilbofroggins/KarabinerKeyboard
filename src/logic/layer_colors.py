import random
import pyray as ray


def layer_color(layer):
    random.seed(int(layer) + 7)

    red = random.randint(100, 255)
    green = random.randint(100, 255)
    blue = random.randint(100, 255)

    return (red, green, blue, 255)