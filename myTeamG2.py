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
from DefensiveAgents import DefensiveAgent
from OffensiveAgents import OffensiveAgent

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'DummyAgent', second = 'OffensiveAgent'):
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

class DummyAgent(CaptureAgent):
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
 
    '''
    Your initialization code goes here, if you need any.
    '''
    self.currentPath = []
    self.patrol_positions = []
    self.safe_zone = None
    self.opponent_indexes = self.getOpponents(gameState)
    enemy1, enemy2 = gameState.getAgentPosition(self.opponent_indexes[0]),gameState.getAgentPosition(self.opponent_indexes[1])
    self.agent_pos = gameState.getAgentPosition(self.index)

    self.grid = self.getFoodYouAreDefending(gameState)

    if gameState.isOnRedTeam(self.index):
      self.capsule_pos = sorted(self.getCapsulesYouAreDefending(gameState), key = lambda x: x[0],reverse= True)
      self.base_x = self.grid.width//2 - 1 
      self.safe_zone = list(range(0,self.base_x + 1))

    else:
      self.capsule_pos = sorted(self.getCapsulesYouAreDefending(gameState), key = lambda x: x[0],reverse= False)
      self.base_x = self.grid.width//2 + 1
      self.safe_zone = list(range(self.base_x - 1 ,self.grid.width))
    
    print(self.capsule_pos)
    
    self.x_N = self.grid.width
    self.y_N = self.grid.height
    self.border = self.get_border(gameState)


    self.avoid = []
    # for y in range(self.y_N):
    #   for x in range(self.x_N):
    #      if x not in self.safe_zone:
    #        self.avoid.append((x,y))
    
       


    self.currentPath = self.aStarSearch(self.agent_pos, gameState, [self.capsule_pos[1]], avoidPositions=self.avoid, returnPosition=False)
    print('self base x', self.base_x)
    print('safe zone',self.safe_zone)


 # Getting food indexes
  def get_food_indexes(self,gameState):
    result = []
    food_positions = self.getFoodYouAreDefending(gameState)
    for i,row in enumerate(food_positions):
      for j,col in enumerate(row):
        if col == True:
          result.append((i,j))
    return sorted(result, key = lambda x: (x[0],x[1]))

  #border security
  def get_border(self,gameState):
    border_positions = []
    for border_y in range(self.y_N):
      if gameState.hasWall(self.base_x,border_y) == False:
        border_positions.append((self.base_x,border_y))
    border_positions =sorted(border_positions, key = lambda x : x[1],reverse = False)
    return border_positions
  
  def stopPatrolling(self,gameState):
    enemy1 = gameState.getAgentPosition(self.opponent_indexes[0])
    enemy2 = gameState.getAgentPosition(self.opponent_indexes[1])
    disappearing_food = self.getDisappearingFoodPos(gameState)
    return enemy2 or enemy1 or disappearing_food
  
  # def find_closest_safe(self,gameState,enemy_pos):
  #    for pos in self.border:
  #       if gameState.hasWall(pos) == False:
        
     
  def chooseAction(self, gameState):
    """
    Picks among actions randomly.
    """
    '''
    You should change this in your own agent.
    '''
    action = Directions.STOP
    # print('------')
    # print('avoid',self.avoid)
    # print('------')

    self.agent_pos = gameState.getAgentPosition(self.index)
    enemy1 = gameState.getAgentPosition(self.opponent_indexes[0])
    enemy2 = gameState.getAgentPosition(self.opponent_indexes[1])
    disappearing_food = self.getDisappearingFoodPos(gameState)
    #print('patrol pos ', self.patrol_positions)
    if enemy1 != None and enemy1[0] not in self.safe_zone:
      print('safe zone stand')
      self.currentPath = self.aStarSearch(self.agent_pos, gameState, [(self.base_x, enemy1[1])], avoidPositions=self.avoid, returnPosition=False)
    elif enemy2 != None and enemy2[0] not in self.safe_zone:
      print('safe zone stand')
      self.currentPath = self.aStarSearch(self.agent_pos, gameState, [(self.base_x, enemy2[1])], avoidPositions=self.avoid, returnPosition=False)
    elif enemy1 != None:
        print('RUSHH')
        self.currentPath = self.aStarSearch(self.agent_pos, gameState, [enemy1], avoidPositions=self.avoid, returnPosition=False)
    elif enemy2 != None:
        print('RUSHH')
        self.currentPath = self.aStarSearch(self.agent_pos, gameState, [enemy2], avoidPositions=self.avoid, returnPosition=False)
    elif disappearing_food is not None:
       print('enemy attack')
       self.currentPath = self.aStarSearch(self.agent_pos, gameState, [disappearing_food], avoidPositions=self.avoid, returnPosition=False)
    else:
      if len(self.currentPath) < 1 :
        print("PATROL MODE ON ")

        try:
          if util.manhattanDistance(self.agent_pos,self.capsule_pos[0]) > 5:
            self.currentPath = self.aStarSearch(self.agent_pos, gameState, [self.capsule_pos[0]], avoidPositions=self.avoid, returnPosition=False)
        except:
          pass
        if util.manhattanDistance(self.agent_pos,self.border[0]) < 3:
          print("NORTH")
          self.currentPath = self.aStarSearch(self.agent_pos, gameState, [self.border[-1]], avoidPositions=self.avoid, returnPosition=False)
        elif util.manhattanDistance(self.agent_pos,self.border[-1]) < 3: 
          print('South')
          self.currentPath = self.aStarSearch(self.agent_pos, gameState, [self.border[0]], avoidPositions=self.avoid, returnPosition=False)  
        else:
          print('GO TO RANDOM POS')
          try:
            random_pos = random.choice(self.capsule_pos)
          except:
            pass
          random_pos = random.choice(self.border)
          self.currentPath = self.aStarSearch(self.agent_pos, gameState, [random_pos], avoidPositions=self.avoid, returnPosition=False)
    if len(self.currentPath) < 1:
      return action
    return self.currentPath.pop(0)
  
  def get_safe_place(self, gameState):
    now = self.grid
    x_value = self.base_x
    for y_value in range(0,len(now)):
       if gameState.hasWall(x_value, y_value) == False:
         return (x_value,y_value)
       

  def getDisappearingFoodPos(self, gameState):
    if len(self.observationHistory) >2:
      prev = self.getPreviousObservation()
      prev_food_list = self.getFoodYouAreDefending(prev).asList()
      now = self.getCurrentObservation()
      current_food_list = self.getFoodYouAreDefending(now).asList()
      for old_food in prev_food_list:
          if old_food not in current_food_list:
             return old_food
    return None




  def aStarSearch(self, startPosition, gameState, goalPositions, avoidPositions=[] ,returnPosition=False):
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
    # def priority(entry):
    #    if entry[0] in avoidPositions:
    #       return entry[2] + width * height
    #    elif entry[0] in closePositions:
    #       return 1
    #    else:
    #       min(util.manhattanDistance(entry[0],endPosition) for )
          
    # queue = util.PriorityQueueWithFunction(
    #     lambda entry: entry[2] + width * height if entry[0] in avoidPositions else 0 + min(
    #         util.manhattanDistance(entry[0], endPosition) for endPosition in goalPositions))
    
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
            return []
        else:
            currentPosition, currentPath, currentTotal = queue.pop()


    #print(currentPath)
    if returnPosition:
        return currentPath, currentPosition
    else:
        return currentPath
