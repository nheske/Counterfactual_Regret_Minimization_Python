import numpy as np
import random

#https://towardsdatascience.com/introduction-to-regret-in-reinforcement-learning-f5b4a28953cd
class RPSGameEngine:
  ROCK = 0
  PAPER = 1
  SCISSORS = 2
  ACTIONS_COUNT = 3

  def __init__(self, opponentStrategy):
    self.opponentStrategy = opponentStrategy
    self.strategy = np.array([0.0 for i in range(self.ACTIONS_COUNT)])
    self.strategySum = np.array([0.0 for i in range(self.ACTIONS_COUNT)])
    self.regretSum = np.array([0.0 for i in range(self.ACTIONS_COUNT)])
    self.opponentRealStrategy = np.array([0.0 for i in range(self.ACTIONS_COUNT)])

  def __computeStrategy(self):
    totalRegret = 0
    for a in range(self.ACTIONS_COUNT):
      #strategy preference for a given action is how much regret for not using it previously 
      self.strategy[a] = self.regretSum[a] if self.regretSum[a] > 0 else 0.0
      totalRegret += self.strategy[a]
    for a in range(self.ACTIONS_COUNT):
      if totalRegret == 0:
        #initially use a balanced strategy across all actions
        self.strategy[a] = 1.0 / self.ACTIONS_COUNT
      else:
        # normalize strategy
          self.strategy[a] /= totalRegret
      self.strategySum[a] += self.strategy[a]
    return self.strategy

  def __getAction(self, useStrategy):
    r = random.random()
    a = 0
    cumulativeProbability =  0
    while a < self.ACTIONS_COUNT - 1:
        cumulativeProbability += useStrategy[a]
        if (r < cumulativeProbability):
            break
        a+=1
    return a

  def getOpponentRealStrategy(self):
    return self.opponentRealStrategy / sum(self.opponentRealStrategy)

  def getAverageStrategy(self):
    avgStrategy = np.array([0.0 for i in range(self.ACTIONS_COUNT)])
    total = sum(self.strategySum)

    for a  in range(self.ACTIONS_COUNT):
      if (total > 0):
          avgStrategy[a] = self.strategySum[a] / total
      else:
          avgStrategy[a] = 1.0 / self.ACTIONS_COUNT

    return avgStrategy
    
  def train(self, iterations, forceDrawProbability = 0):
    actionUtility = np.array([0.0 for i in range(self.ACTIONS_COUNT)])
    for k in range(iterations):
      mystrategy = self.__computeStrategy()
      myAction = self.__getAction(mystrategy)
      otherAction = self.__getAction(self.opponentStrategy)

      # for testing reasons, we sometimes need to force draw matches
      r = random.random()
      if r < forceDrawProbability:
        otherAction = myAction
      self.opponentRealStrategy[otherAction] += 1
      actionUtility[otherAction] = 0.0
      actionUtility[0  if otherAction == self.ACTIONS_COUNT - 1 else otherAction + 1] = 1.0
      actionUtility[self.ACTIONS_COUNT - 1 if otherAction == 0 else otherAction - 1] = -1.0
      for a  in range(self.ACTIONS_COUNT):
        #regret is difference between utility/payoff (reward or return) of a possible action and the payoff of the action that has been actually taken
        self.regretSum[a] += actionUtility[a] - actionUtility[myAction]

  def play(self, iterations):
    myStrategy = self.getAverageStrategy()
    winCount = 0
    drawCount = 0
    lossCount = 0
    for a  in range(iterations):
      myAction = self.__getAction(myStrategy)
      otherAction = self.__getAction(self.opponentStrategy)
      if myAction < otherAction or (myAction == self.SCISSORS and otherAction == self.ROCK):
        lossCount += 1
      elif myAction == otherAction:
        drawCount += 1
      else:
        winCount += 1
    return (winCount, drawCount, lossCount)


engine = RPSGameEngine([.1,.8,.1])
print('Training:')
engine.train(10000)
print('Opponent real Strategy: ', engine.getOpponentRealStrategy())
print('My strategy to use: ',engine.getAverageStrategy())

print()
print('Playing using my trained strategy:')
w, d, l = engine.play(1000)

print('win : ',w)
print('draw: ',d)
print('loss: ',l)