'''
Wordn't Agent: Velvet Comet

started on Jan 6 2020
'''

import os, random
from ..base_agent import WordntAgent

class Agent(WordntAgent):
   
    def count(self,cur,num):
        if cur=="":
            return

        if cur not in self.count_map:
            self.count_map[cur] = num
            self.count(cur[1:],num+1)
            self.count(cur[:-1],num+1)

        else:
            prev = self.count_map[cur]

            if prev>num:
                self.count_map[cur] = num
                self.count(cur[1:],num+1)
                self.count(cur[:-1],num+1)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.substrings = {}
        self.count_map = {}
        self._LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

        for word in self._words:
            length = len(word)

            for width in range(length,0,-1):
                for start in range(0,length-width+1):
                    end = start+width
                    cur = word[start:end]
                    
                    if width!=1:
                        parent1 = cur[:-1]
                        parent2 = cur[1:]
                        if parent1 not in self.substrings:
                            self.substrings[parent1] = set([cur])
                        else:
                            self.substrings[parent1].add(cur)

                        if parent2 not in self.substrings:
                            self.substrings[parent2] = set([cur])
                        else:
                            self.substrings[parent2].add(cur)
                            
        for txt in self._words:
            self.count(txt,0)
            if txt not in self.substrings:
               self.substrings[txt] = set()
    
    def get_action(self, game_state):
        if game_state["last_action"] is None:
            return "add_to_start", random.choice(self._LETTERS)

        elif game_state["last_action"][0] == "challenge_no_word":
            for i, word in enumerate(self._words):
                if game_state["current_string"] in word:
                    return "claim_word", word
            
            # this is when you cant come up with a word; shouldn't happen
            return "claim_word", game_state["current_string"]+"s"

        elif game_state["current_string"] in self._words and len(game_state["current_string"]) >= 3:
            return "challenge_is_word", None
            
        else:
            cur_string = game_state["current_string"]
            
            if cur_string not in self.substrings:
                return "challenge_no_word", None
            else:
                min_count = 999
                max_count = -1
                choices = []
                max_choice = ""
                arr = self.substrings[cur_string]
                
                for item in arr:
                    cur_count = self.count_map[item]
                    if cur_count % self.n_players != 0:
                        if cur_count < min_count:
                            min_count = cur_count
                            choices = [item]
                        elif cur_count==min_count:
                            choices.append(item)

                    if cur_count>max_count:
                        max_count = cur_count
                        max_choice = item

                if len(choices)>0:
                    select = random.choice(choices)
                    if select[1:]==cur_string:
                        return "add_to_start", select[0]
                    else:
                        return "add_to_end", select[-1]

                else:
                    # this is the sure lose branch
                    if len(arr)>0:
                        if max_count>0:
                            select = max_choice
                            if select[1:]==cur_string:
                                return "add_to_start", select[0]
                            else:
                                return "add_to_end", select[-1]
                        else:
                            # return "add_to_end", "s"
                            return "challenge_no_word", None
