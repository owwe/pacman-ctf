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
import HMM


#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'OffensiveAgent', second = 'OffensiveAgent'):
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

class OffensiveAgent(CaptureAgent):
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
    self.opponents = self.getOpponents(gameState)

    #HMM stuff below
    self.enemies = self.getOpponents(gameState)
    self.Forward1 = HMM.ForwardPass(self) #one enemy agent
    self.Forward2 = HMM.ForwardPass(self) #other enemy agent
    self.Forward1.InitializeTransition(self, gameState)
    self.Forward2.InitializeTransition(self, gameState)

    self.init_pos1 = gameState.getInitialAgentPosition(self.enemies[0])
    self.init_pos2 = gameState.getInitialAgentPosition(self.enemies[1])
    self.Forward1.CertainState(self.init_pos1)
    self.Forward2.CertainState(self.init_pos2)
    # print(init_pos1)
    '''
    Your initialization code goes here, if you need any.
    '''
    
    


  def chooseAction(self, gameState):
    """
    Picks among actions randomly.
    """
    '''
    You should change this in your own agent.
    '''
    init_time = time.time()    

    self.agent_pos = gameState.getAgentPosition(self.index)
    agentState = gameState.getAgentState(self.index)
    numCarrying = agentState.numCarrying
    max_carry = 15

    

    closestFood = self.ClosestFoodPos(gameState)
    enemyClose = self.EnemyClose(gameState)

    if len(closestFood) > 0 and numCarrying < max_carry and not enemyClose:
      # print(f"closestFood is {closestFood}")
      self.currentPath = self.aStarSearch(self.agent_pos, gameState, [closestFood],avoidPositions=[], returnPosition=False)     
    else:
      closestHome = self.ClosestHomePos(gameState)
      # print(f"closestFood is {closestHome}")
      self.currentPath = self.aStarSearch(self.agent_pos, gameState, [closestHome],avoidPositions=[], returnPosition=False)          

    if len(self.currentPath) > 0 and self.currentPath[0] in gameState.getLegalActions(self.index):
        action = self.currentPath.pop(0)
    else:
      # action = 'Stop'
      # action = Directions.STOP
      action = random.choice(gameState.getLegalActions(self.index))

    final_time = time.time()
    time_to_choose = final_time - init_time
    # print(time_to_choose)
    return action


  def EnemyClose(self, gameState):
    loc1 = gameState.getAgentPosition(self.opponents[0])
    loc2 = gameState.getAgentPosition(self.opponents[1])
    if loc1 is not None or loc2 is not None:
      if loc1 is not None:
        self.Forward1.CertainState(loc1)
      if loc2 is not None:
        self.Forward2.CertainState(loc2)  
      return True
    
    else:
    #HMM stuff
      noise_dist1 = gameState.getAgentDistances()[self.enemies[0]]
      noise_dist2 = gameState.getAgentDistances()[self.enemies[1]]
      # print(f"enemy1: {noise_dist1}, enemy2: {noise_dist2}")
      self.Forward1.ComputeEmissionMatrix(self.agent_pos, noise_dist1, gameState)
      self.Forward2.ComputeEmissionMatrix(self.agent_pos, noise_dist2, gameState)

      self.Forward1.ComputeAlphat_xt(self.init_pos1)
      self.Forward2.ComputeAlphat_xt(self.init_pos2)

      beliefPos1 = self.Forward1.ReturnBeliefState()
      beliefPos2 = self.Forward2.ReturnBeliefState()
      
      beliefPosList = [beliefPos1, beliefPos2]
      # print(beliefPos1)
      # self.Forward1.Test()
      self.debugDraw(beliefPosList, [1,0,0], clear=True)

      dist1 = self.getMazeDistance(self.agent_pos, beliefPos1)
      dist2 = self.getMazeDistance(self.agent_pos, beliefPos2)
      if dist1 < 8 or dist2 < 8:
         return True
    return False

  def ClosestEnemyDist(self,gameState):
    loc1 = gameState.getAgentPosition(self.opponents[0])
    loc2 = gameState.getAgentPosition(self.opponents[1]) 
    dist1 = self.getMazeDistance(self.agent_pos, loc1)
    dist2 = self.getMazeDistance(self.agent_pos, loc2)
    # if dist1 < dist2:
    #   min_dist = dist1
    # else:
    #   min_dist = dist2
    min_dist = min(dist1,dist2)
    
    return min_dist

  def ClosestHomePos(self, gameState):
    best_pos = ()   
    min_dist = 1000  
    if not gameState.isOnRedTeam(self.index):
        # i = 17   
        i = (int)(self.x_N / 2)   
        for j in range(self.y_N):
          if not self.walls[i][j]:          
            distance = self.getMazeDistance(self.agent_pos, (i,j))
            if distance < min_dist:
              min_dist = distance
              best_pos = (i,j)
    else:
      i = (int)(self.x_N / 2) - 1  
      for j in range(self.y_N):
        if not self.walls[i][j]:          
          distance = self.getMazeDistance(self.agent_pos, (i,j))
          if distance < min_dist:
            min_dist = distance
            best_pos = (i,j) 
      
    return best_pos 


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
      for i in range((int)(self.x_N / 2) , self.x_N):
        for j in range(self.y_N):
          if enemyFoodGrid[i][j]:
            found = True
            distance = self.getMazeDistance(self.agent_pos, (i,j))
            if distance < min_dist:
                min_dist = distance
                best_pos = (i,j)
        if found:
          break
    else:
      for i in range((int)(self.x_N / 2)-1 , -1, -1):
        for j in range(self.y_N):
          if enemyFoodGrid[i][j]:
            found = True
            distance = self.getMazeDistance(self.agent_pos, (i,j))
            if distance < min_dist:
                min_dist = distance
                best_pos = (i,j)
        if found:
          break  
      
    return best_pos 
  
  def ClosestFoodPos2(self, gameState):
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
      for i in range((int)(self.x_N / 2) , self.x_N):
        for j in range(self.y_N):
          if enemyFoodGrid[i][j]:
            distance = self.getMazeDistance(self.agent_pos, (i,j))
            if distance < min_dist:
                min_dist = distance
                best_pos = (i,j)
    else:
      for i in range((int)(self.x_N / 2)-1 , -1, -1):
        for j in range(self.y_N):
          if enemyFoodGrid[i][j]:
            distance = self.getMazeDistance(self.agent_pos, (i,j))
            if distance < min_dist:
                min_dist = distance
                best_pos = (i,j)
      
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

