# -*- coding: utf-8 -*-

import os
import random


def get_random_useragent():
    """ Возвращает случайный user agent"""

    f = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'useragents.txt'))
    user_agents = f.read().splitlines()

    return random.choice(user_agents)
