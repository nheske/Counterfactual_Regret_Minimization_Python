import numpy as np
import random

ROCK = 0
PAPER = 1
SCISSORS = 2
ACTIONS_COUNT = 3

class Actor:
  def __init__(self, startingStrategy):
    self.strategy = np.array([startingStrategy[i] for i in range(ACTIONS_COUNT)])
    self.strategySum = np.array([startingStrategy[i] for i in range(ACTIONS_COUNT)])
    self.regretSum = np.array([0.0 for i in range(ACTIONS_COUNT)])

  def getAverageStrategy(self):
    avgStrategy = np.array([0.0 for i in range(ACTIONS_COUNT)])
    total = sum(self.strategySum)

    for a  in range(ACTIONS_COUNT):
      if (total > 0):
          avgStrategy[a] = self.strategySum[a] / total
      else:
          avgStrategy[a] = 1.0 / ACTIONS_COUNT

    return avgStrategy


class RPSGameSelfPlayEngine:

  def __init__(self, myStartingStrategy, opponentStartingStrategy):
    self.me = Actor(myStartingStrategy)
    self.opponent = Actor(opponentStartingStrategy)
    

  def __computeStrategy(self, actor):
    totalRegret = 0
    for a in range(ACTIONS_COUNT):
      actor.strategy[a] = actor.regretSum[a] if actor.regretSum[a] > 0 else 0.0
      totalRegret += actor.strategy[a]

    for a in range(ACTIONS_COUNT):
      if totalRegret > 0:
        actor.strategy[a] /= totalRegret
      else:
        actor.strategy[a] = 1.0 / ACTIONS_COUNT
      
      actor.strategySum[a] += actor.strategy[a]
    
    return actor.strategy

  def __getAction(self, useStrategy):
    r = random.random()
    a = 0
    cumulativeProbability =  0
    while a < ACTIONS_COUNT - 1:
        cumulativeProbability += useStrategy[a]
        if (r < cumulativeProbability):
            break
        a+=1
    
    return a

  
  def __getActionUtility(self, actionUtility, action):
    actionUtility[action] = 0.0
    actionUtility[0  if action == ACTIONS_COUNT - 1 else action + 1] = 1.0
    actionUtility[ACTIONS_COUNT - 1 if action == 0 else action - 1] = -1.0
    return actionUtility

  def getActionResult(self, myAction, opponentAction):
    d = opponentAction - myAction

    # opponent: SCISSORS me:ROCK => 1 I win
    # opponent: ROCK me:SCISSORS => -1 I lose

    if d== 2 or (d < 0 and d > -2): return 1
    if d==-2 or d > 0: return -1
    return 0

  def testGetActionResult(self, myAction, opponentAction):
    return self.getActionResult(myAction, opponentAction)
    
  def train(self, iterations):
    mystrategy = self.me.strategy
    opponentStrategy = self.opponent.strategy

    print("initial mystrategy      : ", mystrategy)
    print("initial opponentStrategy: ", opponentStrategy)
    print()

    for k  in range(iterations):
      myAction = self.__getAction(mystrategy)
      opponentAction = self.__getAction(opponentStrategy)
      

      my_result = self.getActionResult(myAction, opponentAction)
      opponent_result = -my_result

      for a  in range(ACTIONS_COUNT):
        self.me.regretSum[a] += self.getActionResult(a, opponentAction) - my_result
        self.opponent.regretSum[a] += self.getActionResult(a, myAction) - opponent_result

      opponentStrategy = self.__computeStrategy(self.opponent)
      mystrategy = self.__computeStrategy(self.me)

      #self.display(k, self.me, self.opponent, myAction, opponentAction, my_result, opponent_result)

  def display(self, k, me, opponent, myAction, opponentAction, my_result, opponent_result):
    print("k: ", k)
    print("mystrategy: ", me.strategy)
    print("opponentStrategy: ", opponent.strategy)
    print("myAction: ", myAction)
    print("opponentAction: ", opponentAction)
    print("my_result: ", my_result)
    print("opponent_result: ", opponent_result)
    print("my regret: ", me.regretSum)
    print("opponent regret: ", opponent.regretSum)
    print()

  def play(self, iterations):
    myStrategy = self.me.getAverageStrategy()
    opponentStrategy = self.opponent.getAverageStrategy()
    winCount = 0
    drawCount = 0
    lossCount = 0

    for a  in range(iterations):
      myAction = self.__getAction(myStrategy)
      opponentAction = self.__getAction(opponentStrategy)

      result = self.getActionResult(myAction, opponentAction)
      if result == -1:
        lossCount += 1
      elif result == 0:
        drawCount += 1
      else:
        winCount += 1

    return (winCount, drawCount, lossCount)

engine2 = RPSGameSelfPlayEngine([.2,.2,.6], [.33,.34,.33])
print("I WIN when:")
print("I play R vs S", engine2.getActionResult(0, 2))
print("I play P vs R", engine2.getActionResult(1, 0))
print("I Play S vs P", engine2.getActionResult(2, 1))
print("\nI LOSE when:")
print("I play R vs P", engine2.getActionResult(0, 1))
print("I play P vs S", engine2.getActionResult(1, 2))
print("I play S vs R", engine2.getActionResult(2, 0))
print("\nI DRAW when:")
print("I play R vs R", engine2.getActionResult(0, 0))
print("I play P vs P", engine2.getActionResult(1, 1))
print("I play S vs S", engine2.getActionResult(2, 2))

engine = RPSGameSelfPlayEngine([.5,.3,.2], [.1,.8,.1])
print('Training:')
engine.train(10000)

print('My adjusted strategy      : ',engine.me.getAverageStrategy())
print('Opponent adjusted Strategy: ', engine.opponent.getAverageStrategy())


print()
print('Playing using trained strategies:')
w, d, l = engine.play(1000)

print('win : ',w)
print('draw: ',d)
print('loss: ',l)
