# The Game of Wordn't

The first player to form a word loses! 

In `Wordn't`, players take turns extending a string by a letter at the start or at the end of the string. Players must be careful to not form a word when they add a letter. They must also be careful that the new extended string is actually a substring of an official word, or they can also lose. The official Scrabble list of words is taken to be the list of official words.

This repository contains a basic interface to play Wordn't and face the *Super Agent*, an intelligent bot perfectly designed for `Wordn't`! Can you beat the bot? 

## Quick Start
After cloning the repo, install the `pyahocorasick` dependency via 
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

## Wordn't Bot Writeup
For a more comprehensive explanation of the rules of `Wordn't` theoretical underpinnings of the Super Agent, take a look at `wordn't writeup.pdf`