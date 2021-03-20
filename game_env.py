import os
from copy import copy

class WordntEnv:

    _ACTION_TYPES = [
        "add_to_start",
        "add_to_end",
        "challenge_no_word",
        "challenge_is_word",
        "claim_word",
    ]

    MIN_WORD_LEN = 3

    def __init__(self, n_players, **kwargs):
        self.n_players = n_players
        words_file = kwargs.get("words_file", "./data/wordnt_words.txt")

        self._words = []
        with open(words_file, "r") as f:
            for line in f:
                self._words.append(line.strip())

        self.reset()

    def reset(self):
        '''
        Start a new game.
        '''
        self._current_turn = 0
        self._last_turn = None
        self._current_string = ''
        self._last_action = None
        self._done = False
        self._loser = None
        self._loss_condition = None
        return self.get_state()

    def get_state(self):
        '''
        Get the state of the current game.
        '''
        return {
            "current_turn": self._current_turn,
            "last_turn": self._last_turn,
            "current_string": self._current_string,
            "last_action": self._last_action,
            "done": self._done,
            "loser": self._loser,
            "loss_condition": self._loss_condition,
        }

    def play_action(self, action_type, string_= None):
        '''
        Action can be:
            add letter to start
            add letter to end
            challenge no word
            challenge is already a word
            claim word (response to challenge no word)
        '''
        if self._done:
            # NOTE: don't do anything if it's already done
            return self.get_state()
        elif not self._is_valid_action(action_type, string_):
            # NOTE: if the action is not valid, the current player loses
            self._done = True
            self._loser = copy(self._current_turn)
            self._loss_condition = "invalid_action"
        elif action_type == "add_to_start":
            self._current_string = string_.upper() + self._current_string
        elif action_type == "add_to_end":
            self._current_string = self._current_string + string_.upper()
        elif action_type == "challenge_no_word":
            # NOTE: change of turn is implemented in ._next_turn()
            pass
        elif action_type == "challenge_is_word":
            if self._is_word(self._current_string):
                self._done = True
                self._loser = self._last_turn
                self._loss_condition = "formed_word"
            else:
                self._done = True
                self._loser = self._current_turn
                self._loss_condition = "challenge_is_word_failed"
        elif action_type == "claim_word":
            if self._is_word(string_):
                self._done = True
                self._loser = self._last_turn
                self._loss_condition = "challenge_no_word_failed"
            else:
                self._done = True
                self._loser = self._current_turn
                self._loss_condition = "claim_word_failed"
        else:
            assert False
        
        self._last_action = (action_type, string_)
        self._last_turn = copy(self._current_turn)
        self._current_turn = self._next_turn()

        return self.get_state()

    def _is_word(self, string_):
        '''
        Check if a string is a valid word
        '''
        if len(string_) < self.MIN_WORD_LEN:
            # NOTE: words should be atleast 3 characters
            return False
        elif string_.upper() in self._words:
            return True
        else:
            return False

    def _is_valid_action(self, action_type, string_ = None):
        '''
        Check if the action is valid for the current state.
        '''
        if action_type not in self._ACTION_TYPES:
            # NOTE: action_type must be valid
            return False

        if action_type.startswith("add"):
            # NOTE: for adding characters, string must have length of 1
            if len(string_) != 1:
                return False

        if not action_type.startswith("challenge"):
            # NOTE: for non-challenge actions, string should not be none
            if string_ is None:
                return False

        if self._last_action is not None:
            if self._last_action[0] == "challenge_no_word":
                # NOTE if last action is challenge_no_word, action must be claim_word
                if action_type != "claim_word":
                    return False

        if action_type == "claim_word":
            # NOTE: if the action is claim_word, then the current string must
            # be a substring of string_
            if self._current_string not in string_.upper():
                return False

        return True

    def _next_turn(self):
        '''
        Check which player will take the next turn
        '''
        if self._done:
            return None
        elif self._last_action[0] == "challenge_no_word":
            if self._current_turn == 0:
                return self.n_players - 1
            else:
                return self._current_turn - 1
        elif self._current_turn == self.n_players - 1:
            return 0
        else:
            return self._current_turn + 1
