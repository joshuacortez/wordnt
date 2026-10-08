from array import array
import numpy as np

class GameGraph:
    '''
    Every string that can appear in a game of Wordn't (i.e. every substring of a word),
    linked by the moves that add a letter to the start or to the end.
    Since strings only grow, the graph has no cycles and the game can be solved backwards from the longest strings.
    '''

    def __init__(self, words_file):
        with open(words_file, "r") as f:
            self.words = [line.strip() for line in f]
        word_set = set(self.words)

        # give every substring an id. the empty string (start of the game) gets id 0
        self.index = {"": 0}
        self.strings = [""]
        self.is_word = [False]
        # index of a word containing each string, used for responding to challenges
        self.example_word = [0]

        parents = array("i")
        children = array("i")

        for word_idx, word in enumerate(self.words):
            n_chars = len(word)

            # ids[i][j] is the id of word[i:j]
            ids = [[0] * (n_chars + 1) for _ in range(n_chars)]
            for i in range(n_chars):
                for j in range(i + 1, n_chars + 1):
                    string_ = word[i:j]
                    string_id = self.index.get(string_)
                    if string_id is None:
                        string_id = len(self.strings)
                        self.index[string_] = string_id
                        self.strings.append(string_)
                        self.is_word.append(string_ in word_set)
                        self.example_word.append(word_idx)
                    ids[i][j] = string_id

            # a move is only valid if the new string is not a word (forming a word loses)
            # words are never parents since the game ends there
            for i in range(n_chars):
                for j in range(i + 1, n_chars + 1):
                    parent_id = ids[i][j]
                    if self.is_word[parent_id]:
                        continue
                    if i > 0 and not self.is_word[ids[i - 1][j]]:
                        parents.append(parent_id)
                        children.append(ids[i - 1][j])
                    if j < n_chars and not self.is_word[ids[i][j + 1]]:
                        parents.append(parent_id)
                        children.append(ids[i][j + 1])

        # the first move can be any letter
        for string_id, string_ in enumerate(self.strings):
            if len(string_) == 1:
                parents.append(0)
                children.append(string_id)

        # remove duplicate moves (the same substring appears in many words) and sort by parent
        edges = np.unique((np.frombuffer(parents, dtype = np.int32).astype(np.int64) << 32)
                          | np.frombuffer(children, dtype = np.int32).astype(np.int64))
        self.edge_parent = (edges >> 32).astype(np.int32)
        self.edge_child = (edges & 0xFFFFFFFF).astype(np.int32)

        n_strings = len(self.strings)
        self.length = np.array([len(string_) for string_ in self.strings], dtype = np.int32)
        self.is_word = np.array(self.is_word, dtype = bool)
        self.example_word = np.array(self.example_word, dtype = np.int32)
        # children of string s are edge_child[child_start[s]:child_start[s + 1]]
        self.child_start = np.zeros(n_strings + 1, dtype = np.int64)
        np.cumsum(np.bincount(self.edge_parent, minlength = n_strings), out = self.child_start[1:])

        self._loss_probs = {}

    def get_children(self, string_id):
        return self.edge_child[self.child_start[string_id]:self.child_start[string_id + 1]]

    def get_loss_probs(self, n_players):
        '''
        loss_probs[k, s] is the probability that you eventually lose from string s,
        when it will be your turn again after k more letters are added.
        You play to minimize it, and every opponent adds a random letter that keeps the string valid.

        loss_probs[k, s] == 0 means you can never be forced to lose, even if all the other players team up against you.
        For 2 players, this is exactly the set of winning positions under perfect play.
        '''
        if n_players not in self._loss_probs:
            self._loss_probs[n_players] = self._solve(n_players)
        return self._loss_probs[n_players]

    def _solve(self, n_players):
        n_strings = len(self.strings)
        loss_probs = np.zeros((n_players, n_strings))
        edge_parent_length = self.length[self.edge_parent]
        n_children = np.diff(self.child_start)

        # strings only grow, so solve from the longest strings down to the empty string
        for length in range(int(self.length.max()), -1, -1):
            layer = np.nonzero((self.length == length) & ~self.is_word)[0]

            # no valid moves: whoever has to move is cornered and loses
            cornered = layer[n_children[layer] == 0]
            loss_probs[0, cornered] = 1.0
            loss_probs[1:, cornered] = 0.0

            in_layer = edge_parent_length == length
            if not in_layer.any():
                continue
            layer_parents = self.edge_parent[in_layer]
            layer_children = self.edge_child[in_layer]
            parent_ids, starts, counts = np.unique(layer_parents, return_index = True, return_counts = True)

            # your turn: pick the move with the lowest loss probability.
            # after your move, it's your turn again after n_players - 1 more letters
            loss_probs[0, parent_ids] = np.minimum.reduceat(loss_probs[n_players - 1, layer_children], starts)

            # an opponent's turn: they pick a random valid move
            for k in range(1, n_players):
                loss_probs[k, parent_ids] = np.add.reduceat(loss_probs[k - 1, layer_children], starts) / counts

        return loss_probs
