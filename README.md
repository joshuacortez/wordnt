# The Game of Wordn't

The first player to form a word loses! 

In `Wordn't`, players take turns extending a string by a letter at the start or at the end of the string. Players must be careful to not form a word when they add a letter. They must also be careful that the new extended string is actually a substring of an official word, or they can also lose. The official Scrabble list of words is taken to be the list of official words.

This repository contains a basic interface to play Wordn't and face the *Super Agent*, an intelligent bot perfectly designed for `Wordn't`! Can you beat the bot? 

## Quick Start
After cloning the repo, install the dependencies (`pyahocorasick`, `numpy` for the Game Tree Agent, and `pandas` for the Quiet Falcon and Amber Heron agents) via 
`pip install -r requirements.txt`
Then run `run_game.py` to start playing!

Feel free to modify the list of `players` in `run_game.py` to include as many players as you'd like. You can even create your own bot and import the class there. You can even have all players as bots!

## Game Example
Here's an example of a game with only 3 players. Two players are humans and the other is the Super Agent. The Super Agent goes first, followed by two human players Human A and Human B. The order of players was randomized.

Here are the first 2 turns. Super Agent starts by adding **R**.
Then Human A has to decide on their action. They decided to add A to the end of the string, formming **RA**.

<img src = images/demo_game_1.png width = 75% height = 75% >

Here are the succeeding two turns. Human B adds a another letter, **B** to the end of the string, forming **RAB**. Then the turn goes back to the Super Agent, who decides to add **M** to the end of the string. So we have **RABM**

<img src = images/demo_game_2.png width = 75% height = 75% >

Then it's Human A's turn again. Instead of adding a letter to the start or end, they decide to challenge Super Agent. They challenge that **RABM** could not be possibly be a substring of an official word. But Super Agent claims that **CRABMEATS** is an official word and they are correct! 

<img src = images/demo_game_3.png width = 75% height = 75% >

Since Human A was proven wrong, they lose this game. This is just one way to end a round of `Wordn't`. It can also end when somebody challenges that the current substring is indeed a word.

## Game Tree Agent
`GameTreeAgent` solves Wordn't exactly instead of approximating it. Only about 1.6 million strings can ever appear in a game (every substring of a word), and strings only grow, so the agent works backwards from the longest strings over this game tree. For every string, it computes the probability that you eventually lose if you play to minimize it and every opponent adds a random letter that keeps the string valid.

- A probability of 0 means you can never be forced to lose, even if all the other players team up against you. With 2 players, this is perfect play: the first player has a forced win by opening with **L** or **U**.
- With 3 or more players, no opening letter is completely safe, so the agent picks the moves least likely to lose against opponents that don't coordinate.

Building the game tree takes about 25 seconds and under 1 GB of memory; after that, every move is an instant lookup. See [`agents/GameTreeAgent/README.md`](agents/GameTreeAgent/README.md) for the theory behind it and a comparison with the Super Agent.

## Other Agents
The `agents` folder also includes bots submitted by other groups to a friendly Wordn't competition in 2020. They have been given neutral names, and they share the `WordntAgent` base class in `agents/base_agent.py` from the original game master.

| Agent | Strategy |
|---|---|
| `QuietFalcon` | Prefers adding a letter to the start that minimizes the number of words 6 or 12 letters longer than the new string (tuned for 6 players), otherwise adds to the end the letter that leaves the fewest possible words. |
| `AmberHeron` | A version of Quiet Falcon from the same group (the one entered in the competition's final lineup): it uses the actual number of players instead of 6, and scores adding to the start and to the end the same way. |
| `MistyLantern` | Opens with the letter found in the fewest words, then picks the move that leaves the fewest possible words without forming one. |
| `CosmicPebble` | Picks a random move that doesn't form a word, avoiding moves toward words 7, 13 or 19 letters longer than the current string (tuned for 6 players). |
| `VelvetComet` | Precomputes, for every substring, the fewest letters needed to complete a word, then picks the shortest extension where that count isn't a multiple of the number of players, so someone else completes the word. |
| `HumbleSprout` | The competition's sample agent: builds toward a random word containing the string, without forming a word. A useful baseline. |

To play against them, add them to the `players` list in `run_game.py`.

## Wordn't Bot Writeup
For a more comprehensive explanation of the rules of `Wordn't` and the theory behind the Super Agent, take a look at `wordn't writeup.pdf`