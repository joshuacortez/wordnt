import random
from .game_graph import GameGraph

# building the game graph takes a while, so it's shared between agents using the same word list
_GAME_GRAPHS = {}

class Agent:
    '''
    Solves Wordn't exactly by working backwards over the game tree of every string that can appear in a game.
    See GameGraph.get_loss_probs for how moves are scored.
    '''

    def __init__(self, name, **kwargs):
        self.n_players = kwargs.get("n_players", 6)
        self.name = name

        words_file = kwargs.get("words_file", "./data/wordnt_words.txt")
        if words_file not in _GAME_GRAPHS:
            _GAME_GRAPHS[words_file] = GameGraph(words_file)
        self._graph = _GAME_GRAPHS[words_file]
        self._graph.get_loss_probs(self.n_players)

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
        graph = self._graph
        current_string = game_state["current_string"]
        string_id = graph.index.get(current_string)

        # responding to a challenge
        if (game_state["last_action"] is not None) and (game_state["last_action"][0] == "challenge_no_word"):
            if string_id is not None:
                return "claim_word", graph.words[graph.example_word[string_id]]
            else:
                # we bluffed and got caught. no word contains the current string
                return "claim_word", current_string

        # the previous player formed a word
        if (string_id is not None) and graph.is_word[string_id]:
            return "challenge_is_word", None

        # the previous player formed a string that's not part of any word
        if string_id is None:
            return "challenge_no_word", None

        children = graph.get_children(string_id)

        # cornered: every move forms a word or leads nowhere.
        # bluff with a letter that leads nowhere and hope that nobody challenges
        if len(children) == 0:
            for letter in random.sample("ABCDEFGHIJKLMNOPQRSTUVWXYZ", 26):
                for action_type, new_string in [("add_to_end", current_string + letter), ("add_to_start", letter + current_string)]:
                    if new_string not in graph.index:
                        return action_type, letter
            return "add_to_end", "S"

        # after this move, it will be our turn again after n_players - 1 more letters
        loss_probs = graph.get_loss_probs(self.n_players)[self.n_players - 1, children]
        best_children = children[loss_probs <= loss_probs.min() + 1e-12]
        new_string = graph.strings[random.choice(best_children)]

        if new_string[1:] == current_string:
            return "add_to_start", new_string[0]
        else:
            return "add_to_end", new_string[-1]
