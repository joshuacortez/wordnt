'''
Implement your team agent here
To test your agent, you can use a script like run_game.py
    to let it play against itself or other agents you might have.
    You'll have to modify that script abit.
For reference, there is a sample agent in agent.py.
If you have other files you need (like maybe neural net weights?), you can create an additional folder and dump those there.
You can add any other functions and code here.
We will just always call PlayerAgent.__init__ and PlayerAgent.get_action
Make sure your code will work in the environment specified in environment.yml
'''

import os
import random

from ..base_agent import WordntAgent

class Agent(WordntAgent):
    '''
    Keep this class named 'Agent' please. I will import it to the game.
    This is just a sample agent to show how it should respond.
    This probably won't perform very well.
    '''

    _LETTERS = 'abcdefghijklmnopqrstuvwxyz'

    def __init__(self, **kwargs):
        '''
        You can also add code here.
        '''

        super().__init__(**kwargs)

        self.n_to_check = kwargs.get("n_to_check", 10000)

        # NOTE: random.shuffle only workds inplace
        random.shuffle(self._words)

    def get_action(self, game_state):
        '''
        This is where you implement your AI.
        It should output actions based on the game state.
        Game state is a dictionary as follows:
            {
                "current_turn": int. the index of the player currently doing an action,
                "last_turn": int or None. the index of the player who did the previous action,
                "current_string": str. the current string,
                "order_added": list of int. indicates the order in which characters were added to the current string,
                "last_action": tuple or None. the action of the previous player,
                "done": bool. indicates if the game is finished,
                "loser": int or None. the index of the player who lost the game,
                "loss_condition": str or None. describes how the loser lost the game,
            }
        Refer to the SampleAgent in agent.py for the syntax of output actions.
        Output action is a tuple of two items:
            action_type: str. any of:
                "add_to_start": add string_ to the start of the current string
                "add_to_end": add _string to the end of the current string
                "challenge_no_word": challenge the previous player to prove that a valid word can be produced from the current string
                "challenge_is_word": challenge that the current string is itself a valid word
                "claim_word": respond to 'challenge_no_word' by presenting a supposedly valid word from the current string
            string_: str or None.
                if action_type is "add_to_start" or "add_to_end", the character to add
                if action_type is "challenge_no_word" or "challenge_is_word", None
                if action_type is "claim_word", the supposedly valid word
        Remember that your agent will lose the game automatically if
            this method takes too long or has any error.
        '''

        if game_state["last_action"] is None:
            # NOTE: game just started
            # NOTE: just add a random letter
            return "add_to_start", random.choice(self._LETTERS)
        elif game_state["last_action"][0] == "challenge_no_word":
            # NOTE: need to respond to challenge
            # NOTE: just find the first word that contains the string
            for i, word in enumerate(self._words):
                if game_state["current_string"] in word:
                    return "claim_word", word
                    # NOTE: only search self.n_to_check words
                    # NOTE: if we exceed, just add 'S' to the word lol
            return "claim_word", game_state["current_string"] + 'S'
        elif game_state["current_string"] in self._words and len(game_state["current_string"]) >= 3:
            # NOTE: if string is a word, challenge it
            return "challenge_is_word", None
        else:
            for i, word in enumerate(self._words):
                # NOTE: check for a possible word in the first self.n_to_check
                if game_state["current_string"] in word:
                    substring_start = word.find(game_state["current_string"])

                    if substring_start == 0:
                        # NOTE: it is at the start of the word
                        action_type, action_string = "add_to_end", word[len(game_state["current_string"])]
                        new_string = game_state["current_string"] + action_string

                    elif substring_start + len(game_state["current_string"]) == len(word):
                        # NOTE: it is at the end of the word
                        action_type, action_string = "add_to_start", word[substring_start - 1]
                        new_string = action_string + game_state["current_string"]
                    else:
                        # NOTE: it is in the middle of the word
                        if random.random() > 0.5:
                            action_type, action_string = "add_to_start", word[substring_start - 1]
                            new_string = action_string + game_state["current_string"]
                        else:
                            action_type, action_string = "add_to_end", word[len(game_state["current_string"])]
                            new_string = game_state["current_string"] + action_string

                    matches = [word for word in self._words if new_string == word]
                    if not matches:
                        return action_type, action_string

            # NOTE: if no word was found, challenge that there is no word possible
            return "challenge_no_word", None