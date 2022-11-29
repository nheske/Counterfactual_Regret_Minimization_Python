# TIC TAC TOE

import numpy as np
from random import randint
from datetime import datetime

DIMLEN = 3
NUM_ACTIONS = DIMLEN * DIMLEN
PLAYER1 = 1  # x
PLAYER2 = -1  # o
nodeMap = {}


class Node:
    def __init__(self):
        self.infoSet = ""
        self.regretSum = np.zeros(NUM_ACTIONS)
        self.strategy = np.zeros(NUM_ACTIONS)
        self.strategySum = np.zeros(NUM_ACTIONS)

    def get_strategy(self, realizationWeight, grid):
        actions = get_available_actions(grid)
        num_actions = len(actions)
        normalizingSum = 0
        for a in actions:
            self.strategy[a] = self.regretSum[a] if self.regretSum[a] > 0 else 0
            normalizingSum += self.strategy[a]

        for a in actions:
            if normalizingSum > 0:
                self.strategy[a] /= normalizingSum
            else:
                self.strategy[a] = 1.0 / num_actions
            self.strategySum[a] += realizationWeight * self.strategy[a]
        return self.strategy

        # Get average information set mixed strategy across all training iterations i

    def get_average_strategy(self):
        avgStrategy = np.zeros(NUM_ACTIONS)
        normalizingSum = 0
        for a in range(NUM_ACTIONS):
            normalizingSum += self.strategySum[a]
        for a in range(NUM_ACTIONS):
            if (normalizingSum > 0):
                avgStrategy[a] = round(self.strategySum[a] / normalizingSum, 2)
            else:
                avgStrategy[a] = round(1.0 / NUM_ACTIONS)
        return avgStrategy

    def __str__(self):
        return self.infoSet + ": " + str(self.get_average_strategy())  # + "; regret = " + str(self.regretSum)


# Train TIC TAC TOE
def train(iterations):
    startTime = datetime.now()

    grid = np.zeros(NUM_ACTIONS)
    util = 0
    for i in range(iterations):
        util += cfr(grid, "", 1, 1)

    endTime = datetime.now()


def has_winner(grid):
    for i in range(DIMLEN):
        sum = grid[i * 3] + grid[i * 3 + 1] + grid[i * 3 + 2]
        if (sum == 3 or sum == -3): return sum / 3

    for i in range(DIMLEN):
        sum = grid[i] + grid[i + 3] + grid[i + 6]
        if (sum == 3 or sum == -3): return sum / 3

    sum = grid[0] + grid[4] + grid[8]
    if (sum == 3 or sum == -3): return sum / 3
    sum = grid[2] + grid[4] + grid[6]
    if (sum == 3 or sum == -3): return sum / 3

    return 0


def is_player_winner(player, grid):
    winner = has_winner(grid)
    if winner == 0: return 0
    if winner == 1 and player == 0: return 1  # player X won, he gets 1
    if winner == -1 and player == 1: return 1  # player O won, he gets 1
    return -1


def is_full(grid):
    for v in grid:
        if v == 0: return False
    return True


def get_grid_hash(grid):
    hash = ""
    for v in grid:
        hash += "x" if v == 1 else ("o" if v == -1 else "-")
    return hash;


def get_available_actions(grid):
    actions = []
    for i, v in enumerate(grid):
        if v == 0: actions.append(i)
    return actions;


# Counterfactual regret minimization iteration
def cfr(grid, history, p0, p1):
    plays = len(history)
    player = plays % 2
    # Return payoff for terminal states
    if (plays > 3):
        winner = is_player_winner(player, grid)
        if winner != 0: return winner
        if is_full(grid): return 0

    # identify the infoset (or node)
    player_symbol = ("x" if player == 0 else "o")
    infoSet = player_symbol + ":" + get_grid_hash(grid)

    # Get the node or create it, if it does not exist
    node_exists = infoSet in nodeMap
    node = None
    if (not node_exists):
        node = Node()
        node.infoSet = infoSet
        nodeMap[infoSet] = node
    else:
        node = nodeMap[infoSet]

    # For each action, recursively call cfr with additional history and probability
    param = p0 if player == 0 else p1
    strategy = node.get_strategy(param, grid)
    actions = get_available_actions(grid)
    util = np.zeros(NUM_ACTIONS)

    nodeUtil = 0
    for a in actions:
        newgrid = np.copy(grid)
        newgrid[a] = 1 if player == 0 else -1
        nextHistory = history + player_symbol
        # the sign of the util received is the opposite of the one computed one layer below
        # because what is positive for one player, is neagtive for the other
        # if player == 0 is making the call, the reach probability of the node below depends on the strategy of player 0
        # so we pass reach probability = p0 * strategy[a], likewise if this is player == 1 then reach probability = p1 * strategy[a]
        util[a] = -cfr(newgrid, nextHistory, p0 * strategy[a], p1) if player == 0 else -cfr(newgrid, nextHistory, p0,
                                                                                            p1 * strategy[a])
        nodeUtil += strategy[a] * util[a]

    # For each action, compute and accumulate counterfactual regret
    for a in actions:
        regret = util[a] - nodeUtil
        # for the regret of player 0 is multilied by the reach p1 of player 1
        # because it is the action of player 1 at the layer above that made the current node reachable
        # conversly if this player 1, then the reach p0 is used.
        node.regretSum[a] += (p1 if player == 0 else p0) * regret

    return nodeUtil


# TCI TAC TOE main method
now = datetime.now()
current_time = now.strftime("%H:%M:%S")
print("Start Time =", current_time)

# number of iterations 
# 1 iteration approx 30sec
# 10 iterations approx 5min
# 100 iterations approx 30min
# 1000 iterations approx 4h30min
iterations = 5

print("iterations =", iterations)

train(iterations);

now = datetime.now()
current_time = now.strftime("%H:%M:%S")
print("End Time =", current_time)

# end of training logic

# After training you can play against the algorithm
# by entering the number of cell you want to put X in
# the cells are numbered like this
#   7 | 8 | 9
#  ---+---+---
#   4 | 5 | 6
#  ---+---+---
#   1 | 2 | 3
#
#
done = False
grid = np.zeros(NUM_ACTIONS)

def displayGrid(grid):
  for i in range(2, -1, -1):
    str = ""
    for j in range(3):
      v = grid[i * 3 + j]
      str += ("x" if v == 1 else ("o" if v == -1 else "-"))
    print(str)
      
def available_moves(grid):
  a = []
  for i,v in enumerate(grid):
    if v == 0:
      a.append(i+1)
  return a

print("Play by entering the number of cell to put X in.")
while not done:
  print('\nAvailable moves:', available_moves(grid))
  cellStr = input("enter your move: ")
  cell = int(cellStr) - 1
  if(grid[cell] != 0):
    print(cellStr, ' is taken! Try again')
    continue
  grid[cell] = 1
  hash = get_grid_hash(grid);
  print('You:')
  displayGrid(grid);
  winner = has_winner(grid)
  if winner != 0:
    print('*** YOU WON ***')
    done = True
    break
  if is_full(grid):
    done = True
    print('DRAW')
    break

  node = nodeMap['o:'+hash]
  opponent_play = node.strategy.argmax()
  grid[opponent_play] = -1
  hash = get_grid_hash(grid)
  print("Algorithm:")
  displayGrid(grid)
  winner = has_winner(grid)
  if winner != 0:
    print('--- YOU LOST ---')
    done = True
    break

  

