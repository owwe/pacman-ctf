from captureAgents import CaptureAgent
import random, time, util, math
from game import Directions, Actions
import game
from util import nearestPoint

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'ApproximateQLearningAgent', second = 'DefensiveReflexAgent'):
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.
  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """
  
  """
  Currently, the defined agent is:
    ApproximateQLearningAgent for Offense
    DefensiveReflexAgent for Defense
  Might modify later?:
    DefensiveReflexAgent --> HeuristicSearchAgent (A* search) for Defense?
    
  QLearningAgent and ApproximateQLearningAgent are two reinforcement 
  learning agents that differ in the way they estimate Q-values.
  QLearningAgent implements the standard Q-learning algorithm that 
  uses a lookup table to represent the Q-values for each state-action pair. 
  This agent learns the optimal action-value function by iteratively 
  updating the Q-values using the Bellman equation.
  ApproximateQLearningAgent, on the other hand, uses linear function 
  approximation to estimate the Q-values. This agent represents each 
  state-action pair as a feature vector, and the Q-values are estimated 
  as a weighted sum of the feature values. The weights of the features 
  are learned using stochastic gradient descent to minimize the mean 
  squared error between the predicted and observed Q-values.  
  """

  # The following line is an example only; feel free to change it.
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

#################
#   My Agents   #
# written by me #
#################

class ApproximateQLearningAgent(CaptureAgent):
  def registerInitialState(self, gameState):
    self.epsilon = 0.1 # exploration rate
    self.alpha = 0.2 # learning rate
    self.gamma = 0.9 # discount factor
    self.trainingMode = False
    self.oldGameState = gameState
    self.numTraining = 10
    self.red_ind = gameState.getRedTeamIndices()
    self.blue_ind = gameState.getBlueTeamIndices()
    self.my_team = 'blue' if self.index in self.blue_ind else 'red'

    if self.my_team == 'blue':
      self.team = self.blue_ind
      self.opponent = self.red_ind
    else:
      self.team = self.red_ind
      self.opponent = self.blue_ind
      
    self.weights = {'closestGhostDistance': 32.8698758781666, 
                    'closestCapsuleDistance': 54.95292664106621, 
                    'successorFoodScore': 20.774139321667807, 
                    'onOffense': 63.81442893859289, 
                    'closestFoodDistance': -2.3545086025412494, 
                    'bias': 1.0, 
                    'numGhostsOneStepAway': -23.34475561715782, 
                    'numGhostsTwoStepsAway': 1.8315871805609016, 
                    'eatsFoodNext': 32.84029154417439}
    
    self.start = gameState.getAgentPosition(self.index)
    CaptureAgent.registerInitialState(self, gameState)

  def getQValue(self, gameState, action):
    # features vector
    features = self.getFeatures(gameState, action)
    Q_value = 0.0
    for feature in features:
      Q_value += features[feature] * self.weights[feature] # Q(state, action) = featureVector * w
    return Q_value

  # Returns best Q-value based on the best action given a state
  def getValue(self, gameState):
    allowedActions = gameState.getLegalActions(self.index)
    if len(allowedActions) == 0:
      return 0.0
    bestAction = self.getPolicy(gameState)
    bestQValue = self.getQValue(gameState, bestAction)
    return bestQValue

  # computes the best action from the Q-values
  def getPolicy(self, gameState):
    allowedActions = gameState.getLegalActions(self.index)
    if len(allowedActions) == 0:
      return None
    actionQValues = {}
    bestQValue = float("-inf")
    for action in allowedActions:
      targetQValue = self.getQValue(gameState, action)
      actionQValues[action] = targetQValue
      if targetQValue > bestQValue:
        bestQValue = targetQValue
    bestActions = [a for a, v in actionQValues.items() if v == bestQValue]
    # random tie-breaking for actions that have the same Q-value
    return random.choice(bestActions)
   
  def chooseAction(self, gameState):
    allowedActions = gameState.getLegalActions(self.index)
    if len(allowedActions) == 0:
      return None

    if self.trainingMode:
      for action in allowedActions:
        self.updateWeights(self.oldGameState, gameState, action)
        
    # Compute the action to take in the current state.  With
    # probability self.epsilon, we should take a random action and
    # take the best policy action otherwise.
    action = None
    if (util.flipCoin(self.epsilon)):
        action = random.choice(allowedActions)
    else:
        action = self.getPolicy(gameState)
  
    foodLeft = len(self.getFood(gameState).asList())
    if gameState.getAgentState(self.index).numCarrying >= 10 or foodLeft <= 2:
    #if foodLeft <= 2:
      bestDist = 9999
      for action in allowedActions:
        successor = self.getSuccessor(gameState, action)
        pos2 = successor.getAgentPosition(self.index)
        dist = self.getMazeDistance(self.start, pos2)
        if dist < bestDist:
          bestAction = action
          bestDist = dist
      action = bestAction

    self.oldGameState = gameState
    return action

  def updateWeights(self, oldGameState, gameState, action):
    nextState = self.getSuccessor(gameState, action) # s' = successor state
    features = self.getFeatures(gameState, action) # f(s, a) = feature vector
    R = self.getReward(oldGameState, gameState, nextState) # R(s, a) = reward
    Q = self.getQValue(gameState, action) # Q(s, a) = current Q-value
    V = self.getValue(nextState) # V(s') = max_a' Q(s', a')
    
    # (R(s, a) + gamma * V(s')) - Q(s, a)
    correction = (R + self.gamma * V) - Q
    
    # for each feature i
    for feature in features:
      # performs the weight update (aka stochastic gradient descent)
      # w_i = w_i + alpha * correction * f_i(s, a)
      newWeight = self.alpha * correction * features[feature]
      self.weights[feature] += newWeight

  def getReward(self, oldGameState, gameState, nextState):
    agentPosition = gameState.getAgentPosition(self.index)
    agentState = gameState.getAgentState(self.index)
    reward = 0

    # computes reward for eating food
    returnedFoodReward = agentState.numReturned - oldGameState.getAgentState(self.index).numReturned
    carryingFoodReward = (agentState.numCarrying - oldGameState.getAgentState(self.index).numCarrying)*0.1
    opponentScore = 0
    opponentFood = 0
    for i in self.opponent:
      opponentScore -= gameState.getAgentState(i).numReturned - oldGameState.getAgentState(i).numReturned
      opponentFood -= (gameState.getAgentState(i).numCarrying - oldGameState.getAgentState(i).numCarrying)*0.1
    reward = returnedFoodReward + carryingFoodReward + opponentScore + opponentFood  

    # check if I have updated the score
    if self.getScore(nextState) > self.getScore(gameState):
      reward = (self.getScore(nextState) - self.getScore(gameState)) * 10

    # check if food is eaten in nextState
    foodList = self.getFood(gameState).asList()
    minDistanceToFood = min([self.getMazeDistance(agentPosition, food) for food in foodList])
    # I am 1 step away, will I be able to eat food in nextState?
    if minDistanceToFood == 1:
      nextFoods = self.getFood(nextState).asList()
      if len(foodList) - len(nextFoods) == 1:
        reward = 10

    # check if I am eaten by a ghost in nextState
    enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
    ghosts = [a for a in enemies if not a.isPacman and a.scaredTimer == 0 and a.getPosition() != None]
    if len(ghosts) > 0:
      minDistGhost = min([self.getMazeDistance(agentPosition, g.getPosition()) for g in ghosts])
      if minDistGhost == 1:
        nextPos = nextState.getAgentState(self.index).getPosition()
        if nextPos == self.start:
          # I am eaten by a ghost
          reward = -100
          
    return reward

  def getSuccessor(self, gameState, action):
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != nearestPoint(pos):
      # Only half a grid position was covered
      return successor.generateSuccessor(self.index, action)
    else:
      return successor
  
  def getFeatures(self, gameState, action):
    features = util.Counter()
    food_matrix = self.getFood(gameState)
    wall_matrix = gameState.getWalls()
    agentState = gameState.getAgentState(self.index)
    enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
    # ghosts = [a.getPosition() for a in enemies if not a.isPacman and a.getPosition() != None]
    deadlyGhosts = [a for a in enemies if not a.isPacman and a.scaredTimer == 0 and a.getPosition() != None]    
    deadlyGhostPositions = [g.getPosition() for g in deadlyGhosts]
    agentPosition = gameState.getAgentPosition(self.index)
    x, y = agentPosition
    dx, dy = Actions.directionToVector(action)
    next_x, next_y = int(x + dx), int(y + dy) 
    next_2x, next_2y = int(x + 2*dx), int(y + 2*dy)

    # compute the bias feature
    features["bias"] = 1.0

    # count the number of deadly ghosts one step away from our pacman agent
    features["numGhostsOneStepAway"] = sum((next_x, next_y) in Actions.getLegalNeighbors(g, wall_matrix) for g in deadlyGhostPositions)
    features["numGhostsTwoStepsAway"] = sum((next_2x, next_2y) in Actions.getLegalNeighbors(g, wall_matrix) for g in deadlyGhostPositions)

    # if len(ghosts) > 0:
    #   minDistance = min([self.getMazeDistance(agentPosition, g) for g in ghosts])
    #   if minDistance < 3:
    #     features["closestGhostDistance"] = minDistance
        
    # compute the distance to the nearest deadly ghost enemy that pose a threat to us
    if len(deadlyGhostPositions) > 0:
      minDeadlyGhostDistance = min([self.getMazeDistance(agentPosition, gPos) for gPos in deadlyGhostPositions])
      if minDeadlyGhostDistance < 3:
        features["closestGhostDistance"] = minDeadlyGhostDistance

    # computes whether we're on offense or defense 
    features['onOffense'] = 0
    if agentState.isPacman: features['onOffense'] = 1

    # if there is no danger of ghosts then add the food feature
    if not features["numGhostsOneStepAway"] and food_matrix[next_x][next_y]:
      features["eatsFoodNext"] = 1.0

    # compute the closest capsule distance feature
    capsules = self.getCapsules(gameState)
    if len(capsules) > 0:
      closestCap = min([self.getMazeDistance(agentPosition, cap) for cap in capsules])
      features["closestCapsuleDistance"] = closestCap
      
    # Compute distance to the nearest food
    foodList = food_matrix.asList()
    features['successorFoodScore'] = -len(foodList) # self.getScore(successor)
    # if len(foodList) > 0:
    #     minDistance = min([self.getMazeDistance(agentPosition, food) for food in foodList])
    #     features['closestFoodDistance'] = minDistance

    # compute the distance to the nearest food
    dist = self.closestFoodDistance((next_x, next_y), food_matrix, wall_matrix)
    if dist is not None:
      features["closestFoodDistance"] = float(dist) / (wall_matrix.width * wall_matrix.height)
    features.divideAll(10.0)
        
    return features

  def closestFoodDistance(self, position, food_matrix, wall_matrix):
      queue = [(position[0], position[1], 0)]
      visited = set()
      
      while queue:
          x, y, distance = queue.pop(0)
          
          if (x, y) in visited:
              continue
          
          visited.add((x, y))
          
          # if we find a food at this location, return its distance
          if food_matrix[x][y]:
              return distance
          
          # otherwise, add this location's neighbors to the queue
          neighbors = Actions.getLegalNeighbors((x, y), wall_matrix)
          for neighbor_x, neighbor_y in neighbors:
              queue.append((neighbor_x, neighbor_y, distance + 1))
              
      # no food found
      return None

  def final(self, state):
    # call the super-class final method
    CaptureAgent.final(self, state)

    #if self.episodesSoFar == self.numTraining:
    print("myWeights: ", self.weights)
    file = open('myWeights.txt', 'w')
    file.write(str(self.weights))


#######################
# BaselineTeam Agents #
#  not written by me  #
#######################

class ReflexCaptureAgent(CaptureAgent):
  """
  A base class for reflex agents that chooses score-maximizing actions
  """

  def registerInitialState(self, gameState):
    self.start = gameState.getAgentPosition(self.index)
    CaptureAgent.registerInitialState(self, gameState)

  def chooseAction(self, gameState):
    """
    Picks among the actions with the highest Q(s,a).
    """
    actions = gameState.getLegalActions(self.index)

    # You can profile your evaluation time by uncommenting these lines
    # start = time.time()
    values = [self.evaluate(gameState, a) for a in actions]
    # print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)

    maxValue = max(values)
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]

    foodLeft = len(self.getFood(gameState).asList())

    if foodLeft <= 2:
      bestDist = 9999
      for action in actions:
        successor = self.getSuccessor(gameState, action)
        pos2 = successor.getAgentPosition(self.index)
        dist = self.getMazeDistance(self.start, pos2)
        if dist < bestDist:
          bestAction = action
          bestDist = dist
      return bestAction

    return random.choice(bestActions)

  def getSuccessor(self, gameState, action):
    """
    Finds the next successor which is a grid position (location tuple).
    """
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != nearestPoint(pos):
      # Only half a grid position was covered
      return successor.generateSuccessor(self.index, action)
    else:
      return successor

  def evaluate(self, gameState, action):
    """
    Computes a linear combination of features and feature weights
    """
    features = self.getFeatures(gameState, action)
    weights = self.getWeights(gameState, action)
    return features * weights

  def getFeatures(self, gameState, action):
    """
    Returns a counter of features for the state
    """
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    features['successorScore'] = self.getScore(successor)
    return features

  def getWeights(self, gameState, action):
    """
    Normally, weights do not depend on the gamestate.  They can be either
    a counter or a dictionary.
    """
    return {'successorScore': 1.0}

class DefensiveReflexAgent(ReflexCaptureAgent):
  """
  A reflex agent that keeps its side Pacman-free. Again,
  this is to give you an idea of what a defensive agent
  could be like.  It is not the best or only way to make
  such an agent.
  """

  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)

    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()

    # Computes whether we're on defense (1) or offense (0)
    features['onDefense'] = 1
    if myState.isPacman: features['onDefense'] = 0

    # Computes distance to invaders we can see
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    features['numInvaders'] = len(invaders)
    if len(invaders) > 0:
      dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
      features['invaderDistance'] = min(dists)

    if action == Directions.STOP: features['stop'] = 1
    rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
    if action == rev: features['reverse'] = 1

    return features

  def getWeights(self, gameState, action):
    return {'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -10, 'stop': -100, 'reverse': -2}