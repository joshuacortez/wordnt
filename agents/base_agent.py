import os
import random

class WordntAgent:
    '''
    Base class used by the agents submitted to the 2020 Wordn't competition (from the original game master).
    '''

    def __init__(self, **kwargs):
        words_file = kwargs.get("words_file", "./data/wordnt_words.txt")
        self.name = kwargs.get("name", "Agent")
        self.n_players = kwargs.get("n_players", 6)
        self._words = []
        with open(words_file, "r") as f:
            for line in f:
                self._words.append(line.strip())

    def get_action(self, game_state):
        pass
