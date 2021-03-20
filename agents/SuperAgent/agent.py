import random
from .best_proposal_finder import find_best_proposal

class Agent:

    def __init__(self, name, **kwargs):
        self.n_players = kwargs.get("n_players", 6)
        self.name = name

        words_file = kwargs.get("words_file", "./data/wordnt_words.txt")
        self._words = []
        with open(words_file, "r") as f:
            for line in f:
                self._words.append(line.strip())

        self._max_word_len = max([len(word) for word in self._words])
        self._words_set = set(self._words)
        self._letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        self._latest_basis_words = set()

    def __repr__(self):
        return self.name

    def get_action(self, game_state):
        '''
        It should output actions based on the game state.
        Game state is a dictionary as follows:
            {
                "last_action": tuple or None. the action of the previous player,
                "current_string": str. the current string,
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

        # responding to a challenge
        if game_state["last_action"] is not None:
            if game_state["last_action"][0] == "challenge_no_word":
                if self._latest_basis_words:
                    action_string = random.choice(list(self._latest_basis_words))
                else:
                    action_string = random.choice(self._words)
                action_type = "claim_word"

                return action_type, action_string
    
        # where all the magic happens
        output_summary = find_best_proposal(game_state["current_string"], self.n_players, self._max_word_len, self._words_set, self._letters,
                                            use_metagame_strat = True)
                                            
        action_type, action_string = output_summary["action_type"], output_summary["action_string"]

        # update basis words
        if output_summary["best_proposal_basis_words"] is not None:
            self._latest_basis_words = output_summary["best_proposal_basis_words"]
        
        return action_type, action_string