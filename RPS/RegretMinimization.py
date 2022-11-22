import random
import matplotlib.pyplot as plt

ROCK, PAPER, SCISSORS = 0, 1, 2
NUM_ACTIONS = 3

regretSum = [0.0] * NUM_ACTIONS
strategy = [0.0] * NUM_ACTIONS
strategySum = [0.0] * NUM_ACTIONS
# strategySum = [0.0, 0.0, 0.0]
oppStrategy = [0.4, 0.3, 0.3]
#oppStrategy = [0.3, 0.45, 0.25]

def getStrategy():
    normalizingSum = 0.0
    for a in range(NUM_ACTIONS):
        if regretSum[a] > 0:
            strategy[a] = regretSum[a]
        else:
            strategy[a] = 0
        normalizingSum += strategy[a]
    for a in range(NUM_ACTIONS):
        if normalizingSum > 0:
            strategy[a] /= normalizingSum
        else:
            strategy[a] = 1.0 / NUM_ACTIONS
        normalizingSum += strategy[a]
    return strategy

def getAction(strategy):
    r = random.random()
    a = 0
    cumulativeProbability = 0.0
    while a < NUM_ACTIONS - 1:
        cumulativeProbability += strategy[a]
        if r < cumulativeProbability:
            break
        a += 1
    return a

def train(iterations):
    actionUtility = [0.0] * NUM_ACTIONS
    for i in range(iterations):
        # get regret-matched mixed-strategy actions
        strategy = getStrategy()
        myAction = getAction(strategy)
        otherAction = getAction(oppStrategy)
        
        # compute action utilities

        #performance of matching action is 0
        actionUtility[otherAction] = 0

        # if other chose scissors, rock gets a 1 for winning
        if otherAction == SCISSORS:
            actionUtility[ROCK] = 1
        else:
            # else if other chose rock, paper gets a 1 and if other chose paper then scissors gets a 1
            actionUtility[otherAction + 1] = 1
        if otherAction == ROCK:
            # else if other chose rock, scissors gets a -1 for losing
            actionUtility[NUM_ACTIONS - 1] = -1
        else:
            # else if other chose scissor, paper gets a -1 and if other chose scissors then paper gets a -1 for losing
            actionUtility[otherAction - 1] = -1
            
        # accumulate action regrets
        for a in range(NUM_ACTIONS):
            regretSum[a] += actionUtility[a] - actionUtility[myAction]

def getAverageStrategy():
    avgStrategy = [0.0] * NUM_ACTIONS
    normalizingSum = 0.0
    for a in range(NUM_ACTIONS):
        normalizingSum += strategySum[a]
    for a in range(NUM_ACTIONS):
        if normalizingSum > 0:
            avgStrategy[a] = strategySum[a] / normalizingSum
        else:
            avgStrategy[a] = 1.0 / NUM_ACTIONS
        strategySum[a] += strategy[a]
    return avgStrategy

if __name__ == "__main__":
    result = []
    for i in range(1000):
        train(1)
        # print(getStrategy())
        print(getAverageStrategy())
        result.append(getAverageStrategy())
    plt.plot(result)
    plt.ylabel('Probability')
    plt.show()
