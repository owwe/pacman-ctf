# myTeam.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from captureAgents import CaptureAgent
import random, time, util
from game import Directions
import game
from game import Actions
from game import Grid
from capture import GameState
import numpy as np

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'DefensiveAgent', second = 'DefensiveAgent'):
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

  # The following line is an example only; feel free to change it.
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class DefensiveAgent(CaptureAgent):
  """
  A Dummy agent to serve as an example of the necessary agent structure.
  You should look at baselineTeam.py for more details about how to
  create an agent as this is the bare minimum.
  """

  def registerInitialState(self, gameState):
    """
    This method handles the initial setup of the
    agent to populate useful fields (such as what team
    we're on).

    A distanceCalculator instance caches the maze distances
    between each pair of positions, so your agents can use:
    self.distancer.getDistance(p1, p2)

    IMPORTANT: This method may run for at most 15 seconds.
    """

    '''
    Make sure you do not delete the following line. If you would like to
    use Manhattan distances instead of maze distances in order to save
    on initialization time, please take a look at
    CaptureAgent.registerInitialState in captureAgents.py.
    '''
    CaptureAgent.registerInitialState(self, gameState)
    self.agent_pos = gameState.getAgentPosition(self.index)
    self.currentPath = []
    self.walls = gameState.getWalls()
    # if gameState.isOnRedTeam(self.index):
    #    self.foodGrid = gameState.getRedFood()
    # else:
    #    self.foodGrid = gameState.getBlueFood()
    self.foodGrid = self.getFoodYouAreDefending(gameState)
    
    self.x_N = self.foodGrid.width
    self.y_N = self.foodGrid.height

    '''
    Your initialization code goes here, if you need any.
    '''
    # gameStateTest = GameState.getAgentState(self.)
    #print(self.agent_pos)
    


  def chooseAction(self, gameState):
    """
    Picks among actions randomly.
    """
    '''
    You should change this in your own agent.
    '''
    self.agent_pos = gameState.getAgentPosition(self.index)
    agentState = gameState.getAgentState(self.index)
    numCarrying = agentState.numCarrying

    closestFood = self.ClosestFoodPos(gameState)
    
    if len(closestFood) > 0:
      print(f"closestFood is {closestFood}")
      self.currentPath = self.aStarSearch(self.agent_pos, gameState, [closestFood],avoidPositions=[], returnPosition=False)     
        
    if len(self.currentPath) > 0 and self.currentPath[0] in gameState.getLegalActions(self.index):
        action = self.currentPath.pop(0)
    else:
      # action = 'Stop'
      # action = Directions.STOP
      action = random.choice(gameState.getLegalActions(self.index))
    return action


  def ClosestHomePos(self, gameState):
    best_pos = ()     
    enemyFoodGrid = self.getFood(gameState)
    
    found = False
    min_dist = 1000
    distance = 0
    for i in range(17, 32):
      for j in range(16):
        if enemyFoodGrid[i][j]:
          found = True
          distance = self.getMazeDistance(self.agent_pos, (i,j))
          if distance < min_dist:
            min_dist = distance
            best_pos = (i,j)
      if found:
         break
      
    return best_pos 


    return  

  def ClosestFoodPos(self, gameState):
    best_pos = ()     
    # if gameState.isOnRedTeam(self.index):
    #   enemyFoodGrid = gameState.getBlueFood()
    # else:
    #   enemyFoodGrid = gameState.getRedFood()
    enemyFoodGrid = self.getFood(gameState)
    
    found = False
    min_dist = 1000
    distance = 0
    if gameState.isOnRedTeam(self.index):
      for i in range(17, 32):
        for j in range(16):
          if enemyFoodGrid[i][j]:
            found = True
            distance = self.getMazeDistance(self.agent_pos, (i,j))
            if distance < min_dist:
                min_dist = distance
                best_pos = (i,j)
        if found:
          break
    else:
      for i in range(16):
        for j in range(16):
          if enemyFoodGrid[i][j]:
            found = True
            distance = self.getMazeDistance(self.agent_pos, (i,j))
            if distance < min_dist:
                min_dist = distance
                best_pos = (i,j)
        if found:
          break  
      
    return best_pos 


  def DisappearingFoodPos(self, gameState):
    previousFoodGrid = self.foodGrid.deepCopy()
    # if gameState.isOnRedTeam(self.index):
    #    self.foodGrid = gameState.getRedFood()
    # else:
    #    self.foodGrid = gameState.getBlueFood()
    self.foodGrid = self.getFoodYouAreDefending(gameState)
    
    foodPos = []
    for i in range(self.x_N):
       for j in range(self.y_N):
          if previousFoodGrid[i][j] != self.foodGrid[i][j]:
            foodPos.append((i,j))
    return foodPos

  def aStarSearch(self, startPosition, gameState, goalPositions, avoidPositions=[], returnPosition=False):
    """
    Finds the distance between the agent with the given index and its nearest goalPosition
    """
    #print("ASTAR STARTED")
    walls = gameState.getWalls()
    width = walls.width
    height = walls.height
    walls = walls.asList()

    actions = [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]
    actionVectors = [Actions.directionToVector(action) for action in actions]
    # Change action vectors to integers so they work correctly with indexing
    actionVectors = [tuple(int(number) for number in vector) for vector in actionVectors]
    #print(actionVectors)

    # Values are stored a 3-tuples, (Position, Path, TotalCost)

    currentPosition, currentPath, currentTotal = startPosition, [], 0

    #print(currentPosition, "CURRERERERFAE:SDFA")
    # Priority queue uses the maze distance between the entered point and its closest goal position to decide which comes first
    queue = util.PriorityQueueWithFunction(
        lambda entry: entry[2] + width * height if entry[0] in avoidPositions else 0 + min(
            util.manhattanDistance(entry[0], endPosition) for endPosition in goalPositions))

    #print(queue,'queueueuueueueueueuueue')
    # Keeps track of visited positions
    visited = {currentPosition}
    while currentPosition not in goalPositions:

        possiblePositions = [((currentPosition[0] + vector[0], currentPosition[1] + vector[1]), action) for
                              vector, action in zip(actionVectors, actions)]
        legalPositions = [(position, action) for position, action in possiblePositions if position not in walls]
        #print(legalPositions, 'LEEGAALLL    POSSSSSS')

        for position, action in legalPositions:
            if position not in visited:
                visited.add(position)
                
                queue.push((position, currentPath + [action], currentTotal + 1))

        # This shouldn't ever happen...But just in case...
        if len(queue.heap) == 0:
            return None
        else:
            currentPosition, currentPath, currentTotal = queue.pop()


    #print(currentPath)
    if returnPosition:
        return currentPath, currentPosition
    else:
        return currentPath

