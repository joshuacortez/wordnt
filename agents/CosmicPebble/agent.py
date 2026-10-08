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

import random

from ..base_agent import WordntAgent

class Agent(WordntAgent):
    '''
    Keep this class named 'Agent' please. I will import it to the game.
    This is just a sample agent to show how it should respond.
    This probably won't perform very well.
    '''

    _LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    _ADD_TO_END = 'add_to_end'
    _ADD_TO_START = 'add_to_start'

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
            mga_words = self.get_parent_words(game_state["current_string"])
            if (len(mga_words) > 0):
                return "claim_word", mga_words[0]
            else:
                return "claim_word", game_state["current_string"] + 'S'
        elif game_state["current_string"] in self._words and len(game_state["current_string"]) >= 3:
            # NOTE: if string is a word, challenge it
            return "challenge_is_word", None
        else:
            # generate all possible words the substring can form
            mga_words = self.get_parent_words(game_state["current_string"])
            # if there are none: challenge_no_word
            if len(mga_words) == 0:
                return "challenge_no_word", None
            else: # make a move yieeee
                move = self.select_move(game_state["current_string"], mga_words)
                return move[1], move[2]


    """HELPER FUNCTIONS"""

    #returns all words in the word list that contain the current substring
    #if there are none: challenge_no_word immediately
    def get_parent_words(self, curr_string):
        res = [i for i in self._words if curr_string in i]
        return res

    """
        Returns all words that will directly cause us to lose (aka difference between current string and word is 1)
    """
    def get_losing_words(self, curr_string, parent_words):
        res = [i for i in parent_words if len(i)-len(curr_string) == 1]
        return res

    """
        Return all possible moves we can make (in tuple form)
        Also considers losing words when computing this
    """
    def get_all_moves(self, curr_string, parent_words, losing_words):
        res = []
        current_moves = []
        for i in parent_words:
            #find starting index of curr_string
            index = i.find(curr_string)
            if (index == 0):
                #current string is a prefix; append substring+1
                add = (i[index:index + len(curr_string)+1], self._ADD_TO_END, i[len(curr_string)])
                if add[0] not in current_moves and add[0] not in losing_words:
                    res.append(add)
                    current_moves.append(add[0])
            elif (index > 0):
                #get letter before substring; guaranteed for this case
                add_to_start = (i[index-1:index + len(curr_string)], self._ADD_TO_START, i[index-1])
                if add_to_start[0] not in current_moves and add_to_start[0] not in losing_words:
                    res.append(add_to_start)
                    current_moves.append(add_to_start[0])
                #get letter after substring
                #need to check if there is a letter to get from
                if (len(curr_string) + index < len(i)):
                    add_to_end = (i[index:index + len(curr_string)+1], self._ADD_TO_END, i[index+len(curr_string)])
                    #print('add to end', add_to_end)
                    if add_to_end[0] not in current_moves and add_to_end[0] not in losing_words:
                        #print(curr_string, i)
                        res.append(add_to_end)
                        current_moves.append(add_to_end[0])
            else:
                print('Error!')
        
        return res

    """
        Returns all words that may set us up to lose (aka strings 7 or 13 letters longer than current substring since those words will loop back)
        Not guaranteed to make us lose though since another agent can hit a substring word first before actually forming the discouraged word

        Ex: given substring 'ADDITIO'
            ['CYCLOADDITIONS', 'SUPERADDITIONS'] are discouraged
            But still ok since the words 'CYCLOADDITION' and 'SUPERADDITION' need to be formed first by previous player; then we challenge
    """
    def get_discouraged_words(self, curr_string, parent_words):
        res = [i for i in parent_words if (len(i)-len(curr_string) == 7 or len(i)-len(curr_string) == 13 or len(i)-len(curr_string) == 19)]
        return res

    """
        Select a move
    """
    def select_move(self, curr_string, parent_words):
            #find all words that will cause us to directly lose
            losing_words = self.get_losing_words(curr_string, parent_words)
            #print('Losing words: ', losing_words)

            #get all moves
            all_moves = self.get_all_moves(curr_string, parent_words, losing_words)
            # print('Possible moves: ', all_moves)

            #get 'discouraged moves' aka words we can form in n mod 6 turns (including this turn)
            discouraged_words = self.get_discouraged_words(curr_string, parent_words)
            # print('Discouraged: ', discouraged_words)

            # get moves that can form discouraged words
            discouraged_moves = self.get_all_moves(curr_string, discouraged_words, losing_words)
            # print('Moves you can lose to: ', discouraged_moves)

            # get moves that are guaranteed to not put us in a losing position (that I know of huhuhu)
            best_moves = [i for i in all_moves if i not in discouraged_moves]
            # print('Best moves', best_moves)
            
            # make your move ;>
            if (len(best_moves) > 0):
                # if there is a best move
                out = random.choice(best_moves)
            elif (len(all_moves) > 0):
                # if none, select any other move and hope for the best
                out = random.choice(all_moves)
            else:
                # You are in a losing position. Pick a random letter and hope the other agent doesn't notice.
                out = ('', random.choice([self._ADD_TO_END, self._ADD_TO_START]), random.choice(self._LETTERS))

            return out
