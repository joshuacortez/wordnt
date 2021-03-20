class Agent:
    def __init__(self, name, **kwargs):
        self.name = name
        action_types = ['add_to_start',
                            'add_to_end',
                            'challenge_no_word',
                            'challenge_is_word']
        self.action_types = dict(enumerate(action_types, start = 1))
        self.action_types = {str(idx):act for idx,act in self.action_types.items()}
        self._letters = [letter for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ']

    def __repr__(self):
        return self.name
        
    def get_action(self, game_state):
        '''
        It should output actions based on the game state.
        Game state is a dictionary as follows:
            {
                "last_action": tuple or None. the action of the previous player,
                "current_string": str or None. the current string,
            }
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
        '''        

        last_action = game_state["last_action"]
        current_string = game_state["current_string"]
        if last_action is not None:
            last_action_type, last_string_ = last_action
        else:
            last_action_type = None

        action_type = self._choose_action_type(last_action_type, current_string)
        string_ = self._choose_string(action_type)
            
        return action_type, string_

    def _choose_action_type(self, last_action_type, current_string):
        if last_action_type == "challenge_no_word":
            action_type = "claim_word"
        elif current_string == "":
            action_type = "add_to_start"
        else:
            print("Select an action type:")
            for idx, act in self.action_types.items():
                print(idx, act)
            print("\n")

            action_type = None
            while action_type is None:
                action_type_idx = input("Enter number:")
                action_type = self.action_types.get(action_type_idx, None)
                if action_type is None:
                    print("Please enter a valid number")
            print(f"Chose {action_type}")

        return action_type

    def _choose_string(self, action_type):
        if (action_type == "challenge_no_word") or (action_type == "challenge_is_word"):
            string_ = None
        elif action_type == "claim_word":
            string_ = input("Enter claimed word:")
        else:
            is_valid_letter = False
            while not is_valid_letter:
                string_ = input("Enter a letter:")
                string_ = string_.upper()
                if (string_ in self._letters) and (len(string_) == 1):
                    is_valid_letter = True
                if not is_valid_letter:
                    print("Please enter a valid letter.")

        return string_