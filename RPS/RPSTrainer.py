"""
https://github.com/NikhilTRamesh/CFR-RockPaperScissors/blob/main/RPSTrainer.py
RPS Trainer that utilizes standard Counterfactual Regret Minimization
to generate a Nash Equilibrium that represents the GTO probability
distribution for a game of Rock Paper Scissors.
"""

import random
ROCK, PAPER, SCISSORS = 0, 1, 2
ACTIONS = ["ROCK", "PAPER", "SCISSORS"]

def getStrategy(regretSum,strategySum):
    num_actions = 3
    normalization = 0
    strategy = [0,0,0]

    for i in range(0,num_actions):
        if regretSum[i] > 0:
            strategy[i] = regretSum[i]
        else:
            strategy[i] = 0

        normalization += strategy[i]

    for i in range(0,num_actions):
        if normalization > 0:
            strategy[i] = strategy[i] / normalization
        else:
            strategy[i] = 1.0/num_actions
        strategySum[i] += strategy[i]

    return (strategy,strategySum)

def getAction(strategy):
    r = random.uniform(0,1)
    #strategy holds the weights or preferences that leads to preferring action(s)
    rockcutoff = strategy[ROCK]
    papercutoff = strategy[PAPER]
    cutoffscissors = strategy[SCISSORS]
    
    if r >= 0 and r < rockcutoff:
        return ROCK
    elif r >= rockcutoff and r < (rockcutoff + papercutoff):
        return PAPER
    elif r >= (rockcutoff + papercutoff) and r < (rockcutoff + papercutoff + cutoffscissors):
        return SCISSORS
    else:
        return ROCK

def getAvgStrategy(num_iterations, oppStrategy):
    NUM_ACTIONS = 3
    strategySum = train(num_iterations,[0,0,0],oppStrategy)
    avgStrategy = [0,0,0]
    normalization = 0
    normalization = strategySum[0] + strategySum[1] + strategySum[2]
    if normalization>0: # we have a preference
        avgStrategy[ROCK] = strategySum[ROCK] / normalization
        avgStrategy[PAPER] = strategySum[PAPER] / normalization
        avgStrategy[SCISSORS] = strategySum[SCISSORS] / normalization
    else:
        avgStrategy[ROCK] = avgStrategy[PAPER] = avgStrategy[S] = 1.0/NUM_ACTIONS
    return avgStrategy

def train(num_iterations, regretSum, oppStrategy):
    actionMatrix = [0,0,0]
    strategySum = [0,0,0]
    actions = 3

    for i in range(0,num_iterations):
        temp = getStrategy(regretSum,strategySum)
        strategy = temp[0]
        strategySum = temp[1]
        #obtain our action from the calculated strategy distribution
        playeraction = getAction(strategy)
        #obtain opponents action from the calculated strategy distribution
        opponent_action = getAction(oppStrategy)

        if opponent_action == ROCK:
            actionMatrix[ROCK] = 0      # neutral
            actionMatrix[PAPER] = 1     # incentivize paper
            actionMatrix[SCISSORS] = -1 # punish scissors
        elif opponent_action == PAPER:
            actionMatrix[ROCK] = -1     # punish rock
            actionMatrix[PAPER] = 0     # neutral
            actionMatrix[SCISSORS] = 1  # incentivize scissor
        #opponent plays scissors
        else:
            actionMatrix[ROCK] = 1      # incentivize rock
            actionMatrix[PAPER] = -1    # punish paper
            actionMatrix[SCISSORS] = 0  # neutral

        for i in range(0,actions):
            regretSum[i] += actionMatrix[i] - actionMatrix[playeraction]
            
    return strategySum

opponentStrategy = [0.0, 0.0, 1.0]
max_value = max(opponentStrategy)
max_index = opponentStrategy.index(max_value)
print("opponent prefers "+ACTIONS[max_index])
opponent_exploit = getAvgStrategy(100,opponentStrategy)
max_value = max(opponent_exploit)
max_index = opponent_exploit.index(max_value)
print("prefer "+ACTIONS[max_index])
print("Exploit opponent Strategy: ", opponent_exploit)


def train2Player(iterations,regretSum1,regretSum2,p2Strat):
    #Adapt Train Function for two players
    actions = 3
    actionUtility = [0,0,0]
    strategySum1 = [0,0,0]
    strategySum2 = [0,0,0]
    for i in range(0,iterations):
        #Retrieve Actions
        t1 = getStrategy(regretSum1,strategySum1)
        strategy1 = t1[0]
        strategySum1 = t1[1]
        myaction = getAction(strategy1)
        t2 = getStrategy(regretSum2,p2Strat)
        strategy2 = t2[0]
        strategySum2 = t2[1]
        otherAction = getAction(strategy2)
        
        #Opponent Chooses scissors
        if otherAction == actions - 1:
            #Utility(Rock) = 1
            actionUtility[0] = 1
            #Utility(Paper) = -1
            actionUtility[1] = -1
        #Opponent Chooses Rock
        elif otherAction == 0:
            #Utility(Scissors) = -1
            actionUtility[actions - 1] = -1
            #Utility(Paper) = 1
            actionUtility[1] = 1
        #Opponent Chooses Paper
        else:
            #Utility(Rock) = -1
            actionUtility[0] = -1
            #Utility(Scissors) = 1
            actionUtility[2] = 1
            
        #Add the regrets from this decision
        for i in range(0,actions):
            regretSum1[i] += actionUtility[i] - actionUtility[myaction]
            regretSum2[i] += -(actionUtility[i] - actionUtility[myaction])
    return (strategySum1, strategySum2)

#Returns a nash equilibrium reached by two opponents through CFRM
def avgStrategyNoHuman(iterations,oppStrat):
    strats = train2Player(iterations,[0,0,0],[0,0,0],oppStrat)
    s1 = sum(strats[0])
    s2 = sum(strats[1])
    for i in range(3):
        if s1 > 0:
            strats[0][i] = strats[0][i]/s1
        if s2 > 0:
            strats[1][i] = strats[1][i]/s2
    return strats
    
# randomStrategy = [.6,.2,.2]
# print("Opponent Strategy: ",randomStrategy)
# print("Exploitative Strategy: ", getAvgStrategy(100000,randomStrategy))

# holders = avgStrategyNoHuman(100000,[.6,.2,.2])
# print("Opponents equilibrium strategy: ", holders[0])
# print("Players equilibrium strategy: ", holders[1])