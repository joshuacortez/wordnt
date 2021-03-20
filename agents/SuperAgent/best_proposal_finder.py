import ahocorasick as ahc
import random
import copy
import difflib

VERBOSE = False
SPRINKLE_RANDOMNESS = True

def make_aho_automaton(keywords):
    # http://ieva.rocks/2016/11/24/keyword-matching-with-aho-corasick/
    A = ahc.Automaton()  # initialize
    for (cat, key) in enumerate(keywords):
        A.add_word(key, (cat, key)) # add keys and categories
    A.make_automaton() # generate automaton
    return A

def get_words_list_window(keyword, end_index, max_word_len, words_string, words_set):
    window_start_index = max(0,end_index - max_word_len)
    window_end_index = min(end_index + max_word_len - 1, len(words_string))
    
    words_string_window = words_string[window_start_index:window_end_index]
    words_string_window = words_string_window.split(" ")
    words_list_window = [word for word in words_string_window if (keyword in word) and (word in words_set)]
    
    return words_list_window

def get_wordnt_action(current_string, proposal):
    
    assert len(proposal) - len(current_string) == 1, "incorrect proposal {} for current string {}".format(proposal, current_string)
    
    for i,s in enumerate(difflib.ndiff(current_string, proposal)):
        if s[0]=='+':
            action_string = s[-1]
            
            if i == len(current_string):
                action_type = "add_to_end"
            elif i == 0:
                action_type = "add_to_start"
            else:
                assert False, "incorrect proposal {} for current string {}".format(proposal, current_string)
            break
    
    return action_type, action_string

# returns a dictionary
def get_matched_words_per_keyword(A_keywords, words, max_word_len):
    words_string = " " + " ".join(words) + " "
    words_set = set(words)
    
    matched_words_per_keyword = {}
    
    for end_index, (_, keyword) in A_keywords.iter(words_string):
        words_list_window = get_words_list_window(keyword, end_index, max_word_len, words_string, words_set)
        
        if keyword not in matched_words_per_keyword.keys():
            matched_words_per_keyword[keyword] = set(words_list_window)
        else:
            matched_words_per_keyword[keyword].update(words_list_window)
        
    return matched_words_per_keyword

# returns a set
def get_matched_words_all(A_keywords, words, max_word_len, proposal, edge_match_only = False):
    words_string = " " + " ".join(words) + " "
    words_set = set(words)
    
    matched_words = set()
    
    for end_index, (_, keyword) in A_keywords.iter(words_string):
        # keywords are the halt words
        words_list_window = get_words_list_window(keyword, end_index, max_word_len, words_string, words_set)
        
        if edge_match_only:
            words_list_window_filtered = []
            for halt_basis_word in words_list_window:
                # case 1
                if halt_basis_word == keyword:
                    words_list_window_filtered.append(halt_basis_word)
                # case 2
                elif (proposal == halt_basis_word[:len(proposal)]) and (proposal == keyword[:len(proposal)]):
                    words_list_window_filtered.append(halt_basis_word)
                # case 3
                elif (proposal == halt_basis_word[-len(proposal):]) and (proposal == keyword[-len(proposal):]):
                    words_list_window_filtered.append(halt_basis_word)
                else:
                    pass
            words_list_window = words_list_window_filtered
                    
        matched_words.update(words_list_window)

        # get_matched_words_all(A_halt_words, basis_words_filtered, max_word_len)
                
    return matched_words

def generate_proposal_strings(current_string, letters, words_set = None):
    proposed_strings = set()
    
    if current_string == "":
        proposed_strings = [letter for letter in letters]

    else:
        for letter in letters:
            for position in ["left", "right"]:
                if position == "left":
                    proposal_string = letter + current_string
                else:
                    proposal_string = current_string + letter
            
                if words_set is not None:
                    # dont propose an existing word
                    if proposal_string not in words_set:
                        proposed_strings.add(proposal_string)
                else:
                    proposed_strings.add(proposal_string)

        proposed_strings = list(proposed_strings)
    
    return proposed_strings    

def get_basis_words_per_proposal(proposal_strings, halt_words, basis_words, max_word_len):
    # make an aho automaton out of proposal strings
    A_proposals = make_aho_automaton(proposal_strings)
    
    # find basis words per proposal
    basis_words_per_proposal = get_matched_words_per_keyword(A_proposals, basis_words, max_word_len)
    
    # these will contain basis words that are filtered to not have any halt words
    basis_words_nohalt_per_proposal = copy.deepcopy(basis_words_per_proposal)
    
    if halt_words:
        # make automaton out of halt words
        A_halt_words = make_aho_automaton(halt_words)

        # find basis words that contain halt words and have the proposal as a suffix or prefix
        # these are the the basis words we want to remove
        for proposal, basis_words_filtered in basis_words_per_proposal.items():
            halt_basis_words = get_matched_words_all(A_halt_words, basis_words_filtered, max_word_len, proposal, 
                                                    edge_match_only = True)            
            
            # get set difference to remove halting basis words
            basis_words_nohalt_per_proposal[proposal] -= halt_basis_words 
    
    return basis_words_per_proposal, basis_words_nohalt_per_proposal

def get_basis_words(current_string, n_players, max_word_len, words_set, letters):
     
    # basis words are words that you can still form towards when it's your turn
    basis_words = [word for word in words_set if (len(word) > len(current_string) + 1)]
    
    # halt words are words that will force you to lose in any of your next turns
    halt_words = [word for word in words_set if len(word) % (len(current_string) + n_players + 1) == 0]
    
    # generate all possible ways to add a letter (i.e. get proposal strings)
    proposal_strings = generate_proposal_strings(current_string, letters, words_set)
    
    # enumerate all basis words and nonhalt basis words per proposal
    # nonhalt basis words are basis words that don't contain halting words
    # this enumeration is powered by the aho-corasick algorithm for speed
    basis_words_per_proposal, basis_words_nohalt_per_proposal = get_basis_words_per_proposal(proposal_strings, halt_words, basis_words, max_word_len)
    
    return basis_words_per_proposal, basis_words_nohalt_per_proposal

# used this to test speedup difference using aho-corasick algorithm
def get_basis_words_per_proposal_slow(proposal_strings, halt_words, basis_words):
    basis_words_per_proposal = {}
    
    for proposal in proposal_strings:
        basis_words_per_proposal[proposal] = set()
        for word in basis_words:
            if proposal in word:
                basis_words_per_proposal[proposal].add(word)
                
    basis_words_nonhalt_per_proposal = copy.deepcopy(basis_words_per_proposal)
    
    if halt_words:
        for proposal, basis_words_filtered in basis_words_per_proposal.items():
            halt_basis_words = set()
            
            for basis_word in basis_words_filtered:
                for halt_word in halt_words:
                    if halt_word in basis_word:
                        halt_basis_words.add(basis_word)
                        break
            basis_words_nonhalt_per_proposal[proposal] -= halt_basis_words
            
    return basis_words_per_proposal, basis_words_nonhalt_per_proposal
            

def compute_basis_word_ratios(basis_words_per_proposal, basis_words_nohalt_per_proposal):
       
    basis_word_ratios = {}
    
    for proposal in basis_words_per_proposal.keys():
        basis_words = basis_words_per_proposal[proposal]
        basis_words_nohalt = basis_words_nohalt_per_proposal[proposal]
        
        if basis_words:
            basis_word_ratio = len(basis_words_nohalt)/len(basis_words)
            basis_word_ratios[proposal] = basis_word_ratio
            
        # don't consider proposals with no basis words
        else:
            pass
        
    return basis_word_ratios

def get_random_max_ratio(basis_word_ratios, threshold = 0.01):
    # sort proposals in ascending order (will pop best proposals)
    sorted_basis_word_ratios = sorted(basis_word_ratios.items(), key = lambda x: x[1])
    
    best_proposal, best_ratio = sorted_basis_word_ratios.pop()
    best_proposal_buffer = [best_proposal]
    
    if sorted_basis_word_ratios:
        next_best_proposal, next_best_ratio = sorted_basis_word_ratios.pop()

        # keep only perfect proposals if best proposal is perfect
        if best_ratio == 1:
            while (next_best_ratio == 1) and (sorted_basis_word_ratios):
                best_ratio = next_best_ratio
                best_proposal_buffer.append(next_best_proposal)
                next_best_proposal, next_best_ratio = sorted_basis_word_ratios.pop()

        # otherwise, use the threshold
        else:
            while (best_ratio - next_best_ratio < threshold) and (sorted_basis_word_ratios) and (next_best_ratio != 0):
                best_ratio = next_best_ratio
                best_proposal_buffer.append(next_best_proposal)
                next_best_proposal, next_best_ratio = sorted_basis_word_ratios.pop()
        
    best_proposal = random.choice(best_proposal_buffer)
    
    return best_proposal

def optimize_ratio(basis_word_ratios, sprinkle_randomness = SPRINKLE_RANDOMNESS, verbose = VERBOSE):
    if basis_word_ratios:
        
        if sprinkle_randomness:
            # add some randomness so that you're not too predictable
            best_proposal = get_random_max_ratio(basis_word_ratios)

        else:
            best_proposal = max(basis_word_ratios, key = basis_word_ratios.get)
                
        best_ratio = basis_word_ratios[best_proposal]
        
        if best_ratio == 1:
            if verbose:
                print("Found sure win proposal {}!".format(best_proposal))
        elif best_ratio == 0:
            best_proposal = None
            if verbose:
                print("You're heading towards a dead end! Must stall")
        else:
            if verbose:
                print("Found best proposal {} with {:.0f}% score".format(best_proposal, best_ratio*100))
                
    # if the basis word ratio dictionary is empty, it means there are no proposals with basis words
    else:
        best_proposal = None
        best_ratio = 1
        if verbose:
            print("Given string doesn't have any basis word. Must challenge")
    
    return best_proposal, best_ratio

# best stall is the proposal with the highest average basis word length
def optimize_stall(basis_words_per_proposal, verbose = VERBOSE):
    # calculate the average basis word length per proposal
    avg_len_basis_words = {}
    for proposal, basis_words in basis_words_per_proposal.items():
        
        len_basis_words = [len(word) for word in basis_words]
        avg_len = sum(len_basis_words)/len(basis_words)
        avg_len_basis_words[proposal] = avg_len
        
    best_proposal = max(avg_len_basis_words, key = avg_len_basis_words.get)
    best_avg_len = avg_len_basis_words[best_proposal]
    
    if verbose:
        print("Found best stall {} with {:.1f} avg basis word length".format(best_proposal, best_avg_len))
        
    return best_proposal

# confirming the basis word ratio
# more for mathematical accuracy of basis word ratio simulation
# no effect on winning the game
def confirm_challenge_no_word_scenario(current_string, words_set):
    matching_words = [word for word in words_set if current_string in word]
    
    # case if you were dealt with a very bad hand (i.e. forced to form a word)
    if matching_words:
        basis_word_ratio = 0
        matching_words = set(matching_words)
    # case if current_string actually doesn't have a basis word
    else:
        basis_word_ratio = None
        matching_words = None
        
    return basis_word_ratio, matching_words

# using the nohalt intersection ratio is a metagame strategy
def compute_nohalt_intersection_ratios(basis_words_per_proposal, basis_words_nohalt_per_proposal, 
                                       n_players, max_word_len, words_set, letters):
    
    nohalt_intersection_ratios = {}

    for proposal in basis_words_per_proposal.keys():
        
        nhi_ratios_list = []
        
        basis_words_nohalt = basis_words_nohalt_per_proposal[proposal]
        
#       calls a recursion, assuming that the opponent uses the same strategy as you of optimizing the basis word ratio
#         # assuming player next to you is optimal, but he doesn't use his opponent's optimality against them
#         next_proposal_summary = find_best_proposal(proposal, n_players, max_word_len, words_set, letters,
#                                                 use_metagame_strat = False, verbose = False)
#        next_proposal = next_proposal_summary["best_proposal"]
#        next_basis_words_nohalt = next_proposal_summary["best_proposal_basis_words_nohalt"]
        
        # getting the opponent's basis words
        next_basis_words_per_proposal, next_basis_words_nohalt_per_proposal = get_basis_words(proposal, 
                                                                                n_players, max_word_len, words_set, letters)
        
        # calculate the basis word ratio metric
        # given a proposal string, this is the proportion of basis words that are nonhalting
        next_basis_word_ratios = compute_basis_word_ratios(next_basis_words_per_proposal, next_basis_words_nohalt_per_proposal)
        
        for next_proposal in next_basis_word_ratios.keys():
            next_basis_word_ratio = next_basis_word_ratios[next_proposal]
            next_basis_words_nohalt = next_basis_words_nohalt_per_proposal[next_proposal]
        
            # get count of intersection of nohalting words between you and the next opponent
            numerator = len(next_basis_words_nohalt.intersection(basis_words_nohalt))
            denominator = len(next_basis_words_nohalt)

            if denominator != 0:
                nohalt_intersection_ratio = numerator/denominator

                # we're interested in this tuple because next_basis_word_ratio will inform us of the probability that the opponent will choose that proposal
                # nohalt_intersection_ratio is how good it would be if the opponent chose that proposal
                nhi_ratios_list.append((next_basis_word_ratio,nohalt_intersection_ratio))

            # opponent doesn't consider proposals with no basis words
            else:
                pass
            
        # consolidating the nohalt_intersection_ratio into one number will depend on the assumption of the opponent's strategy
        # nbwr means next_basis_word_ratio
        # nhir means nohalt_intersection_ratio
        
        # assume that opponent will choose among sure wins first, and if none exists, will chose among where basis word is nonzero
        nhi_ratios_list = [nhir for (nbwr, nhir) in nhi_ratios_list if nbwr == 1]
        
        if not nhi_ratios_list:
            # assume that opponent will choose randomly among proposals where his basis word ratio is nonzero
            nhi_ratios_list = [nhir for (nbwr, nhir) in nhi_ratios_list if nbwr != 0]
        
        if len(nhi_ratios_list) != 0:
            nohalt_intersection_ratios[proposal] = sum(nhi_ratios_list)/len(nhi_ratios_list) 

    return nohalt_intersection_ratios

# hardcoded first turn based on running best proposals (within 1% ratio) on a given word set
def quick_first_turn(n_players, words_set, use_metagame_strat, verbose = VERBOSE):
    
    if not use_metagame_strat:
        best_first_turn_dict = {
                    2:{"proposals":["I", "U", "O"], "ratio":0.63},
                    3:{"proposals":["X", "Z", "I"], "ratio":0.75},
                    4:{"proposals":["I", "N", "O", "U", "X"], "ratio":0.78},
                    5:{"proposals":["I", "X", "O"], "ratio":0.84},
                    6:{"proposals":["I","O", "X"], "ratio":0.85},
                    7:{"proposals":["Z"], "ratio":0.88},
                    8:{"proposals":["Z"], "ratio":0.86},
                    9:{"proposals":["K"], "ratio":0.86},
                    10:{"proposals":["J", "K", "W"], "ratio":0.91},
                    11:{"proposals":["K", "W"], "ratio":0.95},
                }
        
    else:
        # ratios here are no halt intersection (NHI) ratios
        # this is assuming no halting word strategy for opponents (i.e. light metagame)
        best_first_turn_dict = {
                    2:{"proposals":["T"], "ratio":1.0},
                    3:{"proposals":["Y", "E", "R"], "ratio":1.0},
                    4:{"proposals":["D", "M"], "ratio":1.0},
                    5:{"proposals":["T", "R", "P"], "ratio":1.0},
                    6:{"proposals":["D", "T","S"], "ratio":1.0},
                    7:{"proposals":["Y", "O", "H", "E", "R", "P"], "ratio":1.0},
                    8:{"proposals":["Y", "B", "O", "M", "E","L","K"], "ratio":1.0},
                    9:{"proposals":["D", "B", "O", "S", "N", "E", "R"], "ratio":1.0},
                    10:{"proposals":["A", "O", "E", "R", "L", "U"], "ratio":1.0},
                    11:{"proposals":["D", "O", "N", "E", "R"], "ratio":1.0},
                }
    
    default_first_turn = {"proposals":["D"], "ratio":0.95}
    
    best_first_turn = best_first_turn_dict.get(n_players, default_first_turn)
    best_proposals, best_ratio = best_first_turn["proposals"], best_first_turn["ratio"]
    
    best_proposal = random.choice(best_proposals)
    best_proposal_basis_words = [word for word in words_set if best_proposal in word]
    
    if verbose:
        print("Found best proposal {} with {:.0f}% score".format(best_proposal, best_ratio*100))
        
    output_summary = {"best_proposal":best_proposal,
                       "best_ratio":best_ratio,
                       "best_proposal_basis_words":best_proposal_basis_words,
                      "best_proposal_basis_words_nohalt":best_proposal_basis_words,
                       "action_type":"add_to_start",
                       "action_string":best_proposal}
    
    return output_summary

# this is our main function

def find_best_proposal(current_string, n_players, max_word_len, words_set, letters, use_metagame_strat = False, 
                       verbose = VERBOSE):
    """
    arguments:
        current_string: str. The string handed to you when it's your turn
        n_players: int. The number of Wordn't players
        max_word_len: int. The maximum length of the words in the word list
        words_set: set. A set version of the wordlist (i.e. set(words))
        letters: str. A string containing the possible letters (i.e. 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        use_metagame_strat: bool. True if employing metagame strategy (i.e. guessing your opponent's strategy)
                        Current strategy used is assuming next player won't choose a proposal with halting words 
                        See the compute_nohalt_intersection_ratios for the metagame strategy
        verbose: bool. Will print proposal finding results if True
        
    returns:
        output_summary: dict. dictionary containing all the outputs needed. It contains the following:
            "best_proposal": str or None. The best found proposal for the current_string
            "best_ratio": float or None. The basis word ratio of the best found proposal
            "best_proposal_basis_words": set or None. The list of basis words corresponding to the best_proposal
            
            "action_type": str. A requirement of the Wordn't Agent. Refer to Wordn't Agent docstring
            "action_str": str or None. A requirement of the Wordn't Agent. Refer to Wordn't Agent docstring
    """
    
    if current_string == "":
        # hardcoded first turn so no more waiting time
        output_summary = quick_first_turn(n_players, words_set, use_metagame_strat)
        return output_summary
        
    # challenge if word already exists
    if current_string in words_set:
        if verbose:
            print("Given string {} is already a word. Will challenge".format(current_string))
            
        output_summary = {"best_proposal":None,
                       "best_ratio":None,
                       "best_proposal_basis_words":None,
                        "best_proposal_basis_words_nohalt":None,
                       "action_type":"challenge_is_word",
                       "action_string":None}    
        
        return output_summary
    
    # getting the basis words per proposal based on our current string
    basis_words_per_proposal, basis_words_nohalt_per_proposal = get_basis_words(current_string, n_players, max_word_len, words_set, letters)
    
    # calculate the basis word ratio metric
    # given a proposal string, this is the proportion of basis words that are nonhalting
    basis_word_ratios = compute_basis_word_ratios(basis_words_per_proposal, basis_words_nohalt_per_proposal)
 
    # find best proposal based which has the highest basis word ratio
    best_proposal, best_ratio = optimize_ratio(basis_word_ratios, verbose = verbose)
    
    # stalling scenario
    # hope that a player makes a mistake along the way
    if best_ratio == 0:
        best_proposal = optimize_stall(basis_words_per_proposal)
        
    # if no sure scenario found, can use a metagame strategy
    elif (best_ratio != 1) and use_metagame_strat:
        
        nohalt_intersection_ratios = compute_nohalt_intersection_ratios(basis_words_per_proposal, basis_words_nohalt_per_proposal, 
                                                                   n_players, max_word_len, words_set, letters)
        if nohalt_intersection_ratios:
            best_proposal, best_ratio = optimize_ratio(nohalt_intersection_ratios, verbose = verbose)

    # challenge scenario
    # either you're dealt with an instant lose hand or the current_string is illegal
    if best_proposal is None:
        best_ratio, best_proposal_basis_words = confirm_challenge_no_word_scenario(current_string, words_set)
        best_proposal_basis_words_nohalt = None
        
        # wordnt bot requirements
        action_type = "challenge_no_word"
        action_string = None
    else:
        # keep the basis words in case you get challenged
        best_proposal_basis_words = basis_words_per_proposal[best_proposal]
        best_proposal_basis_words_nohalt = basis_words_nohalt_per_proposal[best_proposal]
        
        # wordnt bot requirements
        action_type, action_string = get_wordnt_action(current_string, best_proposal)
        
    output_summary = {"best_proposal":best_proposal,
                       "best_ratio":best_ratio,
                       "best_proposal_basis_words":best_proposal_basis_words,
                       "best_proposal_basis_words_nohalt":best_proposal_basis_words_nohalt,
                       "action_type":action_type,
                       "action_string":action_string}
    
    return output_summary