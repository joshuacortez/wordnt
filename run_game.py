import random
from agents import SuperAgent, HumanAgent
from game_env import WordntEnv

def main():
    players = [
        (SuperAgent,"Super Agent"),
        (HumanAgent, "Human A"),
        (HumanAgent, "Human B"),
        # (HumanAgent, "Human C"),
        # (HumanAgent, "Human D"),
        # (HumanAgent, "Human E"),
    ]

    env = WordntEnv(len(players))

    loser = play_game(
            env, 
            players
        )

def play_game(env, players, verbosity = 1):
    state = env.reset()
    loser = None

    n_players = len(players)
    players = [player[0](name = player[1], n_players = n_players) for player in players]
    play_order = [i for i in range(len(players))]
    random.shuffle(play_order)
    ordered_players = [players[order] for order in play_order]

    if verbosity > 0:
        pretty_print_state(state, ordered_players)
    
    if verbosity > 0:
        pretty_print_player_order(ordered_players)

    while not state["done"]:
        current_player_idx = state["current_turn"]
        current_agent = ordered_players[current_player_idx]
        print("-------------------")
        print(f"It's {current_agent.name}'s turn...'")

        try:
            action_type, string_ = current_agent.get_action(state)
        except Exception:
            if verbosity > 0:
                print(f"{current_agent.name} lost the game due to an error in the agent.")
            loser = play_order[current_player_idx]
            break

        new_state = env.play_action(action_type, string_)

        if verbosity > 0:
            pretty_print_state(new_state, ordered_players)

        state = new_state

    if loser is None:
        loser = play_order[state["loser"]]
        print(f"{players[loser].name} lost!")

    return loser


def prettify_action(action_type, string_):
    if action_type == "add_to_start":
        return "add the character '" + string_.upper() + "' to the start of the string"
    elif action_type == "add_to_end":
        return "add the character '" + string_.upper() + "' to the end of the string"
    elif action_type == "challenge_no_word":
        return "challenge that no word could be formed"
    elif action_type == "challenge_is_word":
        return "challenge that the string is already a word"
    elif action_type == "claim_word":
        return "claim that '" + string_.upper() + "' is a valid word"

def prettify_loss_condition(loss_condition):
    if loss_condition == "formed_word":
        return "forming a valid word"
    elif loss_condition == "challenge_no_word_failed":
        return "challenging a valid substring"
    elif loss_condition == "claim_word_failed":
        return "not being able to provide a valid word using the string"
    elif loss_condition == "invalid_action":
        return "trying an invalid action"
    elif loss_condition == "challenge_is_word_failed":
        return "challenging that string is already a word even if it it is not"

def pretty_print_state(state_, players):
    print("-------------------")
    if state_["last_turn"] is None:
        print("Game Started!")
        return

    last_turn_name = players[state_["last_turn"]].name
    last_action = prettify_action(*state_["last_action"]) 
    print(f"{last_turn_name} decided to {last_action}.")
    
    if state_["loser"] is not None:
        loser_name = players[state_["loser"]].name
        loss_condition = prettify_loss_condition(state_["loss_condition"])
        print(f"{loser_name} lost the game due to {loss_condition}.")
    else:
        current_string = state_["current_string"]
        print(f"The resulting string is '{current_string}'.")

def pretty_print_player_order(players):
    sequence_str = "Turn sequence is "
    for i, player_ in enumerate(players):
        if i > 0:
            sequence_str += "then "
        sequence_str += player_.name
        if i == len(players) - 1:
            sequence_str += "."
        else:
            sequence_str += " "
    print(sequence_str)


if __name__ == "__main__":
    main()