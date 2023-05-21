import numpy as np
from captureAgents import CaptureAgent
import random, time, util
from game import Directions
import game
from game import Actions
from game import Grid
from capture import GameState
import math
# from OffensiveAgents import OffensiveAgent

class ForwardPass:
  
  def __init__(self, Agent):
    self.probabilities = None
    self.walls = Agent.walls
    self.x_N = Agent.x_N
    self.y_N = Agent.y_N
    self.alphat_1_xt = np.zeros((self.x_N * self.y_N))
    self.alphat_xt = np.zeros((self.x_N * self.y_N))
    self.alphat = None
    self.agent = Agent
    self.E = np.zeros((self.x_N * self.y_N))
    self.beliefPos = None

  def InitializeTransition(self, Agent, gameState):            
    
    self.T = np.zeros((self.x_N * self.y_N, 5))
    bla = np.array([[0, 1], #up
                   [0, -1], #down
                   [1, 0], #right
                   [-1, 0], #left
                   [0, 0]]) #stay
    n_moves = 0.0
    # print(self.T.shape)
    for i in range(self.x_N):
      for j in range(self.y_N):
        index = self.PosToIndex((i,j))
        if gameState.hasWall(i,j):
          self.T[index, :] = np.zeros(5)
        else:
          for k in range(5):
            if not gameState.hasWall(i + bla[k,0],j + bla[k,1]):
              n_moves += 1.0

          for k in range(5):
            if not gameState.hasWall(i + bla[k,0],j + bla[k,1]):
              x = i + bla[k,0]
              y = j + bla[k,1]
              # index_next = self.PosToIndex((x,y))
              self.T[index,k] = 1/n_moves  
              # print(f"no wall at {i}{j}")
            else:
              self.T[index,k] = 0.0  
          # print(self.T[index, :])
        n_moves = 0.0

  def PosToIndex(self,pos):
    x = pos[0]
    y = pos[1]
    return y * self.x_N + x
  
  def IndexToPos(self,index):
    x = index % self.x_N
    y = math.floor(index / self.x_N)
    return (x,y)

  def ComputeEmissionMatrix(self, agent_pos, noise_dis, gameState):
    self.E = np.zeros((self.x_N * self.y_N))
    for i in range(self.x_N * self.y_N):
      pos = self.IndexToPos(i)
      # if not gameState.hasWall(pos[0], pos[1]):
      # true_dist = self.agent.getMazeDistance(agent_pos, pos)
      true_dist = self.Manhattan(agent_pos, pos)
      prob = gameState.getDistanceProb(true_dist, noise_dis)
      self.E[i] = prob

    # print(self.E[self.PosToIndex((30,13))])
        

  def ComputeAlphat_xt(self, initPos, gameState):
    self.alphat_xt = np.zeros((self.x_N * self.y_N))
    # print(f"alphat-1 is {self.alphat_1_xt}")
    allzero = True
    bla = np.array([[0, 1], #up
                   [0, -1], #down
                   [1, 0], #right
                   [-1, 0], #left
                   [0, 0]]) #stay
    
    from_above = None
    from_below = None
    from_right = None
    from_left = None

    for i in range(self.x_N * self.y_N):
      sum = 0.0
      i_pos = self.IndexToPos(i)
      if i_pos[1] < self.y_N - 1:
        from_above = self.PosToIndex(((i_pos[0], i_pos[1] + 1)))
      if i_pos[1] > 0:  
        from_below = self.PosToIndex(((i_pos[0], i_pos[1] - 1)))
      if i_pos[0] > 0:
        from_left = self.PosToIndex(((i_pos[0] - 1, i_pos[1])))
      if i_pos[0] < self.x_N - 1: 
        from_right = self.PosToIndex(((i_pos[0] + 1 , i_pos[1])))

      if from_above is not None:              
        sum += self.T[from_above,1] * self.alphat_1_xt[from_above]
      if from_below is not None:
        sum += self.T[from_below,0] * self.alphat_1_xt[from_below]
      if from_left is not None:  
        sum += self.T[from_left,2] * self.alphat_1_xt[from_left]
      if from_right is not None:  
        sum += self.T[from_right,3] * self.alphat_1_xt[from_right]
      # if sum > 0:
        # print(f"sum is {sum}")
        # print(f"Emission is: {self.E[i]}")
      self.alphat_xt[i] = self.E[i] * sum
      if self.alphat_xt[i] != 0.0:
        allzero = False
    
    if allzero:
      for i in range(self.x_N * self.y_N):
        pos = self.IndexToPos(i)
        x = pos[0]
        y = pos[1]
        if not gameState.hasWall(x,y):
          self.alphat_xt[i] = 0.1
      # ind = self.PosToIndex(initPos)
      # self.alphat_xt[ind] = 1

    # print("done")  


  def CertainState(self, correct_pos):
    index = self.PosToIndex(correct_pos)
    self.alphat_1_xt = np.zeros((self.x_N * self.y_N))
    self.alphat_1_xt[index] = 1.0
    # print(self.alphat_1_xt)

  def ReturnBeliefState(self):
    #remember to normalize alpha_t_xt and put as alphat-1_xt
    # print(f"alphat is {self.alphat_xt}")
    beliefPosIndex = np.argmax(self.alphat_xt)
    self.beliefPos = self.IndexToPos(beliefPosIndex)
    highest_alpha = self.alphat_xt[beliefPosIndex]
    for i in range(self.x_N * self.y_N):
      self.alphat_xt[i] = self.alphat_xt[i] /  highest_alpha
    
    self.alphat_1_xt = np.copy(self.alphat_xt)
    return self.beliefPos
  
  def Test(self):
    init = (30,14)
    next = (30,13)
    ind = self.PosToIndex(init)
    ind_next = self.PosToIndex(next)
    print(self.T[ind,ind_next])

  def Manhattan(self,pos1, pos2):
    x = abs(pos1[0]- pos2[0])
    y = abs(pos1[1]- pos2[1])
    return x + y
    
    
        
    