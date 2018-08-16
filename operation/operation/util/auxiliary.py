import random
import time

START_TIME = 757512000


def make_id():
    t = int(time.time()) - START_TIME
    u = random.SystemRandom().getrandbits(23)
    id_ = (t << 23) | u

    return id_


def reverse_id(id_):
    t = id_ >> 23
    return t + START_TIME
