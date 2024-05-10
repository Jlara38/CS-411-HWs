#CS 411 - Assignment 5
#A * Search on a 15 Puzzle
#Jose Lara
#Spring 2024

import random
import math
import time
import psutil
import os
import heapq
from collections import deque
from queue import PriorityQueue
import sys

#Lists out the possible actions that can be taken. 
actions = ['U','D','L','R']

goal_state = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','0']

# This class defines the state of the problem in terms of board configuration
class Board:
    def __init__(self, tiles):
        #This returns 4 which can be used to make a 4x4 not sure if there is a better way and it must be executed before making a move. 
        self.size = int(math.sqrt(len(tiles))) 
        #This is the order in which the tiles are in e.g. 0 4 5 3 .....
        self.tiles = tiles


    # This function returns the resulting state from taking particular action from current state
    def execute_action(self, action):
        #Makes a copy of the current tiles that will eventually be returned to the user once the moves have been made. 
        tiles_to_return = self.tiles.copy() 
        #Meant to return the index of where the clear tile is located in.
        clear_tile = tiles_to_return.index('0')  
        #Meant to just store the size of the board to avoid using self.size constantly.  
        
        #'U' is moving the tile up and the if statment will actually check for the tile above the empty tile. 
        if(action == 'U'):
            #Checks the tile index vs the board size which is 4. If the result is greater or equal to 0 then we can move up otherwise its a lost cause
            if(clear_tile - self.size) >= 0:
                tiles_to_return[clear_tile - self.size], tiles_to_return[clear_tile] = tiles_to_return[clear_tile], tiles_to_return[clear_tile - self.size]
                
        #'D' does something similar but this time it will check if the empty tile can move down.
        elif(action == 'D'):
            #We add the board size (row: 4 & col: 4) to the clear tile index and check it agains the total board size (16) if its less than 16 then we are allowed  to move down.
            if(clear_tile + self.size) < (self.size * self.size):
                tiles_to_return[clear_tile + self.size], tiles_to_return[clear_tile] = tiles_to_return[clear_tile], tiles_to_return[clear_tile + self.size]
                
        #'L' will check against the bsize(for row 4) then it will check if the modular division is not 0. If it is then we cannot move left.
        elif(action == 'L'):
            if(clear_tile % self.size) != 0:
                tiles_to_return[clear_tile - 1], tiles_to_return[clear_tile] = tiles_to_return[clear_tile], tiles_to_return[clear_tile - 1]
        
        #'R' Will add 1 to the empty tile index and then divide by modular division. Should the division not be 0 then we are free to move right.
        elif(action == 'R'):
            if((clear_tile + 1) % self.size) != 0:
                tiles_to_return[clear_tile + 1], tiles_to_return[clear_tile] = tiles_to_return[clear_tile], tiles_to_return[clear_tile + 1]
                
        #Returns the tiles that were moved.
        
        return Board(tiles_to_return)



# This class defines the node on the search tree, consisting of state, parent and previous action
class Node:
    def __init__(self, state, parent, action):
        self.state = state
        self.parent = parent
        self.action = action
        if parent is None:
            self.cost = 0
        else: 
            self.cost = parent.cost + 1
        
    # Returns string representation of the state
    def __repr__(self):
        return str(self.state.tiles)

    # Comparing current node with other node. They are equal if states are equal
    def __eq__(self, other):
        if isinstance(other, Node):
            return self.state.tiles == other.state.tiles
        return False

    def __hash__(self):
        return hash(tuple(self.state.tiles))
    
    def __lt__(self,other):
        return self.cost < other.cost



class Search:
    # This function returns the list of children obtained after simulating the actions on current node
    def get_children(self, parent_node):
        childrenList = []
        for action in actions:
            child_state = parent_node.state.execute_action(action)
            child_node = Node(child_state,parent_node,action)
            childrenList.append(child_node)
        return childrenList
            
    # This function backtracks from current node to reach initial configuration. The list of actions would constitute a solution path
    def find_path(self, node):
        path_taken = []
        while(node.parent is not None):
            path_taken.append(node.action)
            node = node.parent
        path_taken.reverse()
        return path_taken

    # Heuristic function meant to find the number of misplaced tiles in our current board.
    def misplaced_tiles(self,current_state,goal_state):
        misplaced_count = 0
        for i in range(len(current_state)):
            if current_state[i] != goal_state[i]:
                misplaced_count += 1
        return misplaced_count

    # Heuristic function that finds the distance between the tile and its correct position on the goal_state board. Once that is calculated it sends it back to the user. 
    def manhattan_distance(self,current_state, goal_state):
        size = int(math.sqrt(len(current_state)))
        manhattan_distance = 0
        for i in range(len(current_state)):
            if current_state[i] != '0':
                current_row, current_col = i // size, i % size
                goal_index = goal_state.index(current_state[i])
                goal_row, goal_col = goal_index // size, goal_index % size
                manhattan_distance += abs(current_row - goal_row) + abs(current_col - goal_col)
        return manhattan_distance
    
    # Runs the A* search on the given board looking to solve the puzzle using the given heuristic function. 
    def run_Astar(self, start, goal,h):
        openSet = PriorityQueue()
        openSet.put((0, start))  # Use a priority queue to maintain nodes with their fScore
        cameFrom = {}
        gScore = {start: 0}
        
        while not openSet.empty():
            _, current = openSet.get()
            if self.goal_test(current.state.tiles):
                return self.find_path(current), len(cameFrom)

            for neighbor in self.get_children(current):
                tentative_gScore = gScore[current] + 1  # Assuming uniform cost for simplicity
                if tentative_gScore < gScore.get(neighbor, float('inf')):
                    cameFrom[neighbor] = current
                    gScore[neighbor] = tentative_gScore
                    fScore = tentative_gScore + h(neighbor.state.tiles,goal_state)
                    openSet.put((fScore, neighbor))

        return [], 0  # No path found
        
    #This function serves the sole purpose of comparing the tiles that are returned and those of the goal state we wish to reach. 
    def goal_test(self, cur_tiles):
        return cur_tiles == ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','0']

    #The solve function is meant to start the BFS search on the given table configuration. Then it will print out all the information 
    #From time to memory taken. And prints out the moves that were taken. 
    def solve(self, input):
        initial_list = input.split(" ")
        root = Node(Board(initial_list), None, None)
        starting_time = time.time()
        memory_consumed_before_algo = psutil.Process(os.getpid()).memory_info().rss / 1024.0
        path,expanded_nodes = self.run_Astar(root,goal_state,self.misplaced_tiles)
        ending_time = time.time()
        time_taken = ending_time - starting_time
        memory_consumed_after_algo = psutil.Process(os.getpid()).memory_info().rss / 1024.0
        memory_consumed = memory_consumed_after_algo-memory_consumed_before_algo
        
        
        
        print("Moves: " + " ".join(path))
        print("Number of expanded Nodes: " + str(expanded_nodes))
        print("Time Taken: " + str(time_taken))
        print("Max Memory (Bytes): " + str(memory_consumed) + "kb")
        print(sys.version)
        return "".join(path)
    
    
    # # Does the exact same thing that Solve does with the execption of not needing manual input from main
    # def solve2(self, initial_list):
    #     root = Node(Board(initial_list), None, None)
    #     path, expanded_nodes, time_taken, memory_consumed = self.run_bfs(root)
        
    #     print("Moves: " + " ".join(path))
    #     print("Number of expanded Nodes: " + str(expanded_nodes))
    #     print("Time Taken: " + str(time_taken))
    #     print("Max Memory (Bytes): " + str(memory_consumed) + "kb")
    #     return "".join(path)
    
# # generates random puzzle configurations currently does not work when using solve 2 becuase the list created is not what the algorithm likes. 
# def randomPuzzleGen():
#     numList = list(range(16))
        
#     random.shuffle(numList)
        
#     result = " ".join(map(str,numList))
    
#     return result
    
# Testing the algorithm locally
if __name__ == '__main__':
    agent = Search()
    agent.solve("1 3 4 8 5 2 0 6 9 10 7 11 13 14 15 12")
