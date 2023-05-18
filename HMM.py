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
    
    self.T = np.zeros((self.x_N * self.y_N, self.x_N * self.y_N))
    bla = np.array([[0, 1],
                   [0, -1],
                   [1, 0],
                   [-1, 0],
                   [0, 0]])
    n_moves = 0.0
    # print(self.T.shape)
    for i in range(self.x_N):
      for j in range(self.y_N):
        index = self.PosToIndex((i,j))
        if gameState.hasWall(i,j):
          self.T[index, :] = 0
        else:
          for k in range(5):
            if not gameState.hasWall(i + bla[k,0],j + bla[k,1]):
              n_moves += 1.0

          for k in range(5):
            if not gameState.hasWall(i + bla[k,0],j + bla[k,1]):
              x = i + bla[k,0]
              y = j + bla[k,1]
              index_next = self.PosToIndex((x,y))
              self.T[index,index_next] = 1/n_moves  
              # print(f"no wall at {i}{j}") 
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
      if not gameState.hasWall(pos[0], pos[1]):
        true_dist = self.agent.getMazeDistance(agent_pos, pos)
        prob = gameState.getDistanceProb(true_dist, noise_dis)
        self.E[i] = prob
    

  def CertainState(self, correct_pos):
    index = self.PosToIndex(correct_pos)
    self.alphat_1_xt[index] = 1

  def ReturnBeliefState(self, agent_pos, agent_dis):
    pass
        
    