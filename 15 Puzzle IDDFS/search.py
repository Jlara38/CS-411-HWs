#CS 411 - Assignment 4
#Iterative Deepening Depth First Search on 15 Puzzle
#Jose Lara
#Spring 2024

import random
import math
import time
import psutil
import os
from collections import deque
import sys

#Lists out the possible actions that can be taken. 
actions = ['U','D','L','R']

cutoff = 0

number_of_nodes_expanded = 0

nodes_to_return = []

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
            self.level = 0
        else: 
            self.level = parent.level + 1
        
    # Returns string representation of the state
    def __repr__(self):
        return str(self.state.tiles)

    # Comparing current node with other node. They are equal if states are equal
    def __eq__(self, other):
        return self.state.tiles == other.state.tiles

    def __hash__(self):
        return hash(tuple(self.state.tiles))



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

    # This function will be in charge of running the Deepening search with a new limit until it finds the correct depth at which 
    # the solution to the 15 puzzle can be found. 
    def run_ids(self,node):
        generated_nodes = 0
        path_taken = []
        for depth in range (0,sys.maxsize):
            solution_node, num_nodes = self.run_dls(node,depth)
            generated_nodes += num_nodes
            
            if isinstance(solution_node, Node):
                path_taken = self.find_path(solution_node)
                return generated_nodes,path_taken
        
    # This function will run the Iterative deepening search with the limit that it gets from ids. 
    # Once a solution has been found it will return the node and the number of nodes generated.
    def run_dls(self,node,limit):
        
        # is_cycle is meant to check if the current node has been explored before.
        # This is in order to prevent any situation where we are stuck in a loop/cycle trying to expland nodes we visited.
        def is_cycle(node):
            state = node.state
            while node.parent is not None:
                if state == node.parent.state:
                    return True
                node = node.parent
            return False
        
        frontier = deque([node])
        result = 'failure'
        num_of_nodes_generated = 0
        
        while (len(frontier) > 0):
            deque_node = frontier.pop()
            
            if (self.goal_test(deque_node.state.tiles)):
                return deque_node , num_of_nodes_generated
            
            if(deque_node.level >= limit):
                result = "cutoff"
            
            # If the node is not in a cycle we will expand said node and add it to the frontier. Additionally we keep track of how many 
            # nodes we expanded by adding one. 
            elif not is_cycle(deque_node):
                for child in self.get_children(deque_node):
                    frontier.append(child)
                    num_of_nodes_generated += 1
                    
        return result,num_of_nodes_generated
        
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
        expanded_nodes, path = self.run_ids(root)
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
