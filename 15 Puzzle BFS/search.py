#CS 411 - Assignment 3
#Breadth First Search on 15 Puzzle
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
        #The for loop will loop through all the potential actions that can be taken in the action array.
        #This is done in order to find the child nodes that can be returned to the program.
        for action in actions:
            #Child_state is keeping track of the parent_node and its state then it will execute one of the actions
            #This is done in order to expand the nodes as we go through.  
            child_state = parent_node.state.execute_action(action)
            #Once the child state has received the expanded node for the move in question we will create a new node with that state.
            #We pass in the new state, the parent node that it came from and the action taken. 
            child_node = Node(child_state,parent_node,action)
            #We finally add that to the list of children that appear from expanding our nodes and return it. 
            childrenList.append(child_node)
        return childrenList
            
    # This function backtracks from current node to reach initial configuration. The list of actions would constitute a solution path
    def find_path(self, node):
        path_taken = []
        # The while loop will continue to travel through the tree assuming the next node is not NULL or NONE.
        # It will then add the node to the path taken array and set the node to the next node in line which would be the parent. 
        while(node.parent is not None):
            path_taken.append(node.action)
            node = node.parent
        # When reversing the path taken array we should end up with something akin to [1,2,3,4,5,.....]
        # This is what we are after instead of [15,14,13,12,....]
        path_taken.reverse()
        return path_taken


    # This function runs breadth first search from the given root node and returns path, number of nodes expanded and total time taken
    def run_bfs(self, root_node):
        #This variable is meant to keep track of the number of nodes we will be expanding.
        number_of_nodes_expanded = 0
        
        #This Variables is for time keeping reasons.
        starting_time = time.time()
        
        #This array is meant to store the nodes we will be visiting.
        explored_nodes = []
        
        #This queue is meant to store the root node and the furture nodes that we will be using in order to expand.
        frontier_queue = deque([root_node])
        
        #The While loop will continue to run as long as the frontier queue is not 0 expanding the nodes that exists in the queue.
        while(len(frontier_queue) > 0):
            number_of_nodes_expanded += 1
            dequed_node = frontier_queue.popleft()
            explored_nodes.append(dequed_node)
            
            #The if statement will check if the goal has been reached according to the state of the tiles that can be found in the dequed_node.
            #If it matches the goal then we will return all the information from path taken to memory consumption.
            if(self.goal_test(dequed_node.state.tiles)):
                path_taken = self.find_path(dequed_node)
                end_time = time.time()
                memory_consumed = psutil.Process(os.getpid()).memory_info().rss / 1024.00
                return path_taken, number_of_nodes_expanded,(end_time - starting_time), memory_consumed
            
            #Assuming that we have not reached the goal then we will continue to expand the nodes.
            #We will check the set of explored nodes to ensure we will not get a repeat node and then add to the queue the node that is not a repeat.
            for child in self.get_children(dequed_node):
                if child in explored_nodes:
                    continue
                else:
                    frontier_queue.append(child)
                    
        #If all else fails and the frontier queue is empty then we will display and error message and return false. 
        if(len(frontier_queue) == 0):
            print("Frontier is empty")
            return False
    
    #This function serves the sole purpose of comparing the tiles that are returned and those of the goal state we wish to reach. 
    def goal_test(self, cur_tiles):
        return cur_tiles == ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','0']

    #The solve function is meant to start the BFS search on the given table configuration. Then it will print out all the information 
    #From time to memory taken. And prints out the moves that were taken. 
    def solve(self, input):
        initial_list = input.split(" ")
        root = Node(Board(initial_list), None, None)
        path, expanded_nodes, time_taken, memory_consumed = self.run_bfs(root)
                
        print("Moves: " + " ".join(path))
        print("Number of expanded Nodes: " + str(expanded_nodes))
        print("Time Taken: " + str(time_taken))
        print("Max Memory (Bytes): " + str(memory_consumed) + "kb")
        print(sys.version)
        return "".join(path)
    
    # Does the exact same thing that Solve does with the execption of not needing manual input from main
    def solve2(self, initial_list):
        root = Node(Board(initial_list), None, None)
        path, expanded_nodes, time_taken, memory_consumed = self.run_bfs(root)
        
        print("Moves: " + " ".join(path))
        print("Number of expanded Nodes: " + str(expanded_nodes))
        print("Time Taken: " + str(time_taken))
        print("Max Memory (Bytes): " + str(memory_consumed) + "kb")
        return "".join(path)
    
# generates random puzzle configurations currently does not work when using solve 2 becuase the list created is not what the algorithm likes. 
def randomPuzzleGen():
    numList = list(range(16))
        
    random.shuffle(numList)
        
    result = " ".join(map(str,numList))
    
    return result
    
# Testing the algorithm locally
if __name__ == '__main__':
    agent = Search()
    agent.solve("1 6 2 4 5 10 3 7 9 14 11 8 13 15 0 12")
