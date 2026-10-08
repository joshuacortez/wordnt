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
from functools import reduce

from ..base_agent import WordntAgent

class Agent(WordntAgent):
    '''
    Keep this class named 'Agent' please. I will import it to the game.
    This is just a sample agent to show how it should respond.
    This probably won't perform very well.
    '''

    _LETTERS = ('abcdefghijklmnopqrstuvwxyz').upper()

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        #self.n_to_check = kwargs.get("n_to_check", 10000)

        # NOTE: random.shuffle only workds inplace
        #random.shuffle(self._words)

        # self._validWords = [word for word in self._words]

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

        # print("YAAAAAY")

        if game_state["last_action"] is None:
            # NOTE: game just started
            minCount = 9999999999999
            actualLetter = '0' #lmao by default
            for c in self._LETTERS:
                # print("YAAAAAY 1-0")
                #should give me number of words that letter appears in
                letterPresence = reduce(lambda count, word: count + ( c in (word).upper() ), self._words, 0) 
                # print("YAAAAAY 1-1")
                # print("{} : {}".format(letterPresence, c))
                if letterPresence < minCount and letterPresence > 0:
                    minCount = letterPresence
                    actualLetter = c          

            if actualLetter == '0':
                print("this should NEVER fire")
                return "challenge_no_word", None
            else:
                return "add_to_start", str(actualLetter)
        elif game_state["last_action"][0] == "challenge_no_word":
            # NOTE: need to respond to challenge
            # NOTE: just find the first word that contains the string
            # wordCount = len(self._words)
            for i, word in enumerate(self._words):
                if game_state["current_string"] in word:
                    return "claim_word", word
                # elif i > wordCount:
                #     # NOTE: only search self.n_to_check words
                #     # NOTE: if we exceed, just add 'S' to the word lol
                #     print("plurals for the win")
                #     return "claim_word", game_state["current_string"] + 'S'
            return "claim_word", game_state["current_string"] + 'S'
        elif game_state["current_string"] in self._words and len(game_state["current_string"]) >= 3:
            # NOTE: if string is a word, challenge it
            return "challenge_is_word", None
        else: #means game has started, and not challenge-able, so gotta add a letter
            #find all valid words given the current string
            # print("YAAAAAY1")

            self._validWords = [word for word in self._words if game_state["current_string"] in word]
            # print(self._validWords)
            # print("YAAAAAY2")
            #find the letter + position to add that has the least possible tree routes

            sampleEntries = {}

            if len(self._validWords) == 0: #cant find any valid words for the string lmao
                return "challenge_no_word", None
            else:
                # print("YAAAAAY4")
                #check prepending
                for c in self._LETTERS:
                    dummyWord = c + game_state["current_string"]
                    if dummyWord in self._validWords:
                        #its a whole word and u should be scared
                        continue
                    else:
                        dummyCount = reduce(lambda count, word: count + ( dummyWord in (word).upper() ), self._validWords, 0)
                        # print("YAAAAAY5")
                        sampleEntries[dummyWord] = dummyCount
                
                #check appending
                for c in self._LETTERS:
                    dummyWord = game_state["current_string"] + c
                    if dummyWord in self._validWords:
                        #its a whole word and u should be scared
                        continue
                    else:
                        dummyCount = reduce(lambda count, word: count + ( dummyWord in (word).upper() ), self._validWords, 0)
                        # print("YAAAAAY6")
                        sampleEntries[dummyWord] = dummyCount
            minWord = None
            minCount = 99999999
            for key, value in sampleEntries.items():
                if value < minCount and value > 0:
                    minWord = key
                    minCount = value
            # print(sampleEntries)
            # print(minWord)
            # print(minCount)

            if minWord is None:
                print("everything can be plural if you try hard enough")
                return "add_to_end", 'S'
            
            if game_state["current_string"] in minWord:
                substring_start = minWord.find(game_state["current_string"])

                if substring_start == 0:
                    # NOTE: base string is at the start of the word, add to end of the word
                    return "add_to_end", minWord[-1]

                else:
                    # NOTE: base string is at the end of the word, add to beginning of the word
                    return "add_to_start", minWord[0]