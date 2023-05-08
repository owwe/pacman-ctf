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

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'DummyAgent', second = 'DummyAgent'):
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
    self.agent_pos = gameState.getAgentPosition(self.index)
    self.currentPath = None
    # grid = Grid()
    # grid = grid.asList()
    # g_state = [(len(grid)//2, 0)]
    # i = 0
    # while gameState.hasWall(g_state[0],g_state[1]) == True:
    #     g_state = [(len(g_state)//2, i)]
    #     i+=1
    
       
       


    # self.currentPath = self.aStarSearch(self.agent_pos, gameState, g_state,avoidPositions=[], returnPosition=False)
    # print(self.currentPath)


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
    
    #self.currentPath = self.aStarSearch(self.agent_pos, gameState, [(2,14)],avoidPositions=[], returnPosition=False)
    #print(type(self.currentPath))

    
    #return  random.choice(gameState.getLegalActions(self.index))
    ##### _____ WORKING JUST FINE _______#######
    self.agent_pos = gameState.getAgentPosition(self.index)
    print(self.agent_pos)
    self.currentPath = self.aStarSearch(self.agent_pos, gameState, [(3,11)],avoidPositions=[], returnPosition=False)
    print(self.currentPath)
    if len(self.currentPath) > 0 :
        action =  self.currentPath.pop(0)
    else:
        # action = 'Stop'
        action = Directions.STOP
        # action = random.choice(gameState.getLegalActions(self.index))


    #print(self.currentPath[0])
    return action

  



  
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

