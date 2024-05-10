# CS 411 - Assignment 6
# IDA* Search on a 15 Puzzle
# Jose Lara
# Spring 2024
# Running off the solution code for Assignment 5 (My IDA* was too unoptimized so I opted in to repurpose 
# The solutions code.)

import random
import math
import time
import psutil
import os
from collections import deque
import sys
from heapq import *


# This class defines the state of the problem in terms of board configuration
class Board:
    def __init__(self, tiles):
        self.size = int(math.sqrt(len(tiles)))  # defining length/width of the board
        self.tiles = tiles

    # This function returns the resulting state from taking particular action from current state
    def execute_action(self, action):
        new_tiles = self.tiles[:]
        empty_index = new_tiles.index('0')
        if action == 'L':
            if empty_index % self.size > 0:
                new_tiles[empty_index - 1], new_tiles[empty_index] = new_tiles[empty_index], new_tiles[empty_index - 1]
        if action == 'R':
            if empty_index % self.size < (self.size - 1):
                new_tiles[empty_index + 1], new_tiles[empty_index] = new_tiles[empty_index], new_tiles[empty_index + 1]
        if action == 'U':
            if empty_index - self.size >= 0:
                new_tiles[empty_index - self.size], new_tiles[empty_index] = new_tiles[empty_index], new_tiles[
                    empty_index - self.size]
        if action == 'D':
            if empty_index + self.size < self.size * self.size:
                new_tiles[empty_index + self.size], new_tiles[empty_index] = new_tiles[empty_index], new_tiles[
                    empty_index + self.size]
        return Board(new_tiles)


#This class defines the node on the search tree, consisting of state, parent and previous action		
class Node:
	def __init__(self,state,parent,action):
		self.state = state
		self.parent = parent
		self.action = action
		if parent is None:
			self.cost=0
		else:
			self.cost = parent.cost+1
	
	#Returns string representation of the state	
	def __repr__(self):
		return str("state: " +str(self.state.tiles) + "prev_action "+ str(self.action))
	
	#Comparing current node with other node. They are equal if states are equal	
	def __eq__(self,other):
		return self.state.tiles == other.state.tiles
		
	def __lt__(self, other):
		return id(self)<= id(other)
	
	def __hash__(self):
		return hash(tuple(self.state.tiles))


#This class defines astar search problem        
class Astar:
    def __init__(self,start,goal,heuristic):
        self.root_node = start
        self.goal_state = goal
        self.heuristic = heuristic
        self.node_expanded = 0
        
    def  ida_star(self):
        bound = self.h_value(self.root_node)
        path = [self.root_node]
        max_memory = 0
        while True:
            t,node,max_memory = self.search(path,0,bound)
            if t == "FOUND":
                return self.find_path(node), self.node_expanded, max_memory
            if t == float('inf'):
                return "NOT_FOUND"
            bound = t
            # self.node_expanded += 1
            
    def search(self, path, g, bound):
        max_memory = 0
        max_memory = max(max_memory, sys.getsizeof(path))
        node = path[-1]
        f =  g + self.h_value(node)
        if f > bound:
            return f,node, max_memory
        if self.goal_test(node.state.tiles):
            return "FOUND",node, max_memory
        min_cost = float('inf')

        for child in self.get_children(node):
            if child not in path:
                self.node_expanded += 1
                path.append(child)
                t,node, max_memory = self.search(path, g + 1, bound)
                if t == "FOUND":
                    return "FOUND", node, max_memory
                if t < min_cost:
                    min_cost = t
                path.pop()
        return min_cost , node, max_memory
    
    def f_value(self,node):
        return node.cost + self.h_value(node)
        
    def h_value(self,node):
        if self.heuristic=="manhattan":
            return self.manhattan_heuristic(node)
        else:
            return self.misplaced_tiles_heuristic(node)
    
    #This function calculates sum of manhattan distances of each tile from goal position
    def manhattan_heuristic(self,node):
        tiles = node.state.tiles
        size = node.state.size
        total_sum_distances = 0 
        for i in range(0,len(tiles)):
            value = int(tiles[i])
            if value==0 : continue
            current_x = i // size
            current_y = i % size
            correct_x = (value-1) // size
            correct_y = (value-1) % size
            
            
            cur_distance = abs(correct_x-current_x) + abs(correct_y-current_y)
            total_sum_distances += cur_distance
        return total_sum_distances
    
    #This function calculates number of misplaced tiles from goal position
    def misplaced_tiles_heuristic(self,node):
        tiles = node.state.tiles
        num_misplaced = 0
        for i in range(1,len(tiles)):
            if i!=int(tiles[i-1]) : num_misplaced+=1
            
        return num_misplaced
        
    # This function returns the list of children obtained after simulating the actions on current node
    def get_children(self, parent_node):
        children = []
        actions = ['L', 'R', 'U', 'D']  # left,right, up , down ; actions define direction of movement of empty tile
        for action in actions:
            child_state = parent_node.state.execute_action(action)
            child_node = Node(child_state, parent_node, action)
            children.append(child_node)
        return children

    # This function backtracks from current node to reach initial configuration. The list of actions would constitute a solution path
    def find_path(self, node):
        path = []
        while (node.parent is not None):
            path.append(node.action)
            node = node.parent
        path.reverse()
        return path
        
    #Utility function checking if current state is goal state or not
    def goal_test(self,cur_state):
        return cur_state == self.goal_state


class Search:

    # Utility function to randomly generate 15-puzzle
    def generate_puzzle(self, size):
        numbers = list(range(size * size))
        random.shuffle(numbers)
        return Node(Board(numbers), None, None)


    def solve(self, input):
        initial_time = time.time()
        initial_list = input.split(" ")
        root = Node(Board(initial_list), None, None)
        
        nodes_expanded = 0
        max_memory = 0
        
        goal_state = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','0']    
    
        #astar with manhattan distance heurisitcs
        astar = Astar(root, goal_state,"manhattan")
        print("manhattan_heuristic: "+ str(astar.manhattan_heuristic(root)))
        
        #astar with misplaced tiles heurisitcs
        # astar = Astar(root, goal_state,"misplaced")
        # print("misplaced tiles heuristic: "+ str(astar.misplaced_tiles_heuristic(root)))
        
        solution, nodes_expanded, max_memory = astar.ida_star()
        final_time = time.time()
        
        
        print("Moves: "+ " ".join(solution))
        print("Number of expanded Nodes:" + str(nodes_expanded))
        print("Time Taken: "+ str(final_time-initial_time))
        print("Max Memory: "+str(max_memory) + " KB")
        print(sys.version)
        
        
        return "".join(solution)

if __name__ == '__main__':
    agent = Search()
    agent.solve("1 3 4 8 5 2 0 6 9 10 7 11 13 14 15 12")