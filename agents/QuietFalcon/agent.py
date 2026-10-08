import random
import os
import pandas as pd
from ..base_agent import WordntAgent

class Agent(WordntAgent):
    
    def __init__(self, **k):
        
        super().__init__(**k)
        self.n_to_check = k.get("n_to_check", 10000)

        self.corpus = pd.DataFrame()
        self.corpus['words'] = self._words 
        self.corpus['len'] = self.corpus['words'].apply(str).apply(len)
        self.letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        
    def filter_len_substring(self, substring):
        substring = substring.upper()
        filtered = self.corpus[self.corpus['words'].str.contains(substring, na=False)]
        length = len(substring)
        return len(filtered[(filtered['len'] == length + 6) | (filtered['len'] == length + 12)])
        
    def filter_substring(self, substring):
        substring = substring.upper()
        return self.corpus[self.corpus['words'].str.contains(substring, na=False)]
    
    def is_word(self, substring):
        substring = substring.upper()
        return len(self.corpus[self.corpus['words'] == substring].index) != 0
    
    def get_action(self, game_state):
        current_string = game_state['current_string']
        filtered_corpus = self.filter_substring(current_string)

        pre_length = 276519
        min_set_pre_length = 276519
        min_set_pre_letter = ""
        post_length = 276519
        min_set_post_length = 276519
        min_set_post_letter = ""
        
        if(game_state['last_action'] is None):
                
                for i in range(len(self.letters)):
                    new_substring = self.letters[i]+current_string
                    filtered = self.filter_substring(new_substring)
                    length = len(new_substring)
                    set_len = len(filtered[(filtered['len'] == length + 6) | (filtered['len'] == length + 12)])
                    if ((set_len < min_set_pre_length) & (len(filtered) > 0)):
                        min_set_pre_length = set_len
                        min_set_pre_letter = self.letters[i]
                        
                return ("add_to_start", min_set_pre_letter.lower())
        elif game_state["last_action"][0] == "challenge_no_word":
            return ("claim_word", filtered_corpus['words'].iloc[0].lower())
        else:
            if (len(filtered_corpus) == 0):
                return ("challenge_no_word", None)
            elif(self.is_word(current_string)):
                return ("challenge_is_word", None)
            else:

                for i in range(len(self.letters)):
                    new_substring = self.letters[i]+current_string
                    filtered = self.filter_substring(new_substring)
                    length = len(new_substring)
                    set_len = len(filtered[(filtered['len'] == length + 6) | (filtered['len'] == length + 12)])
                    if ((set_len < min_set_pre_length) & (len(filtered) > 0) & (not self.is_word(new_substring))):
                        min_set_pre_length = set_len
                        min_set_pre_letter = self.letters[i]
                        pre_length = len(filtered)

                for i in range(len(self.letters)):
                    new_substring = current_string+self.letters[i]
                    filtered = self.filter_substring(new_substring)
                    length = len(new_substring)
                    set_len = len(filtered)
                    if ((set_len < min_set_post_length) & (len(filtered) > 0) & (not self.is_word(new_substring))):
                        min_set_post_length = set_len
                        min_set_post_letter = self.letters[i]
                        post_length = len(filtered)
                        
                if(min_set_pre_length < min_set_post_length):
                    return ("add_to_start", min_set_pre_letter.lower())
                elif(min_set_post_length < min_set_pre_length):
                    return ("add_to_end", min_set_post_letter.lower())
                else:
                    if(pre_length < post_length):
                        if(min_set_post_letter == ""):
                            if(min_set_pre_letter == ""):
                                if random.randrange(1,3) > 1:
                                    return "add_to_start", random.choice(self.letters)
                                else:
                                    return "add_to_end", random.choice(self.letters)
                            else:
                                return("add_to_start", min_set_pre_letter.lower())
                        else:
                            return ("add_to_end", min_set_post_letter.lower())

                    elif(post_length < pre_length):
                        if(min_set_pre_letter == ""):
                            if(min_set_post_letter == ""):
                                if random.randrange(1,3) > 1:
                                    return "add_to_start", random.choice(self.letters)
                                else:
                                    return "add_to_end", random.choice(self.letters)
                            else:
                                return ("add_to_end", min_set_post_letter.lower())
                        else:
                            return("add_to_start", min_set_pre_letter.lower())
                    else:
                        if(min_set_pre_letter == ""):
                            if(min_set_post_letter == ""):
                                if random.randrange(1,3) > 1:
                                    return "add_to_start", random.choice(self.letters)
                                else:
                                    return "add_to_end", random.choice(self.letters)
                            else:
                                return ("add_to_end", min_set_post_letter.lower())
                        else:
                            return("add_to_start", min_set_pre_letter.lower())
                        return ("add_to_start", min_set_pre_letter.lower())