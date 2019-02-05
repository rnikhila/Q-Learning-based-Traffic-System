# import necessary libraries and environment.py
import numpy as np
from environment import Environment
import math
from simulator import Simulator
import pickle
import random

#creating agent class
class LearningAgent():
	# This is the intelligent agent we are trying to train and test
	
	location = None  #will be a tuple; first entry will be its location on the segment, second entry will be a tuple that describes the segment
	

	
	time_taken = 0
	start_point = None
	destination = None
	
	test_mode = False
	
	state = None
	
	epsilon = 1
	learning_rate = 1
	
	success = False
	
	
	def __init__(self, env, epsilon, learning_rate, is_learning = False):
		self.Q_intersection = dict()
		self.Q_road_segment = dict()
		self.epsilon = epsilon
		self.learning_rate = learning_rate
		self.is_at_intersection = False
		self.ID = None
		self.env = env
		self.is_learning = is_learning
		self.is_smart = True
		
	
	def reset(self, testing=False):

        	# Update epsilon using a decay function
        	# Update additional class parameters as needed
        	# If 'testing' is True, set epsilon and alpha to 0
	
		if testing:
			self.epsilon = 0
			self.learning_rate = 0
		else:
			print "epsilon = ", self.epsilon
			a = 0.0015
			c = -5
			if self.epsilon == 1:
				t = 0
			else:
				t = (math.log(1/self.epsilon-1) - c)/a
			t=t+1
			self.epsilon = 1/(math.exp(a*t+c)+1)

        	return
	
	def get_inputs(self):
		#gets information from the environment about the traffic
		#gets information from the i-groups about the lights
		
		
		if self.location[1][1] in self.env.exit_nodes:
			# always move forward when on the lane to exit node
			return {'light':'green', 'forward' : True, 'left' : None, 'right' : None}
		else:
			lights = self.env.traffic_lights[self.location[1][1]]
		
		heading = self.env.headings([self.location[1]])[0]
		
		if lights == heading:
			inputs = {'light':'green', 'forward' : None, 'left' : None, 'right' : None}
		else:
			inputs = {'light':'red', 'forward' : None, 'left' : None, 'right' : None}
		
		next_actions = self.env.next_segment(self.location[1])
		
		for action in next_actions.keys():
			#will tell if slot is empty for each valid turn. True means slot is empty, false is when there is a vehicle present.
			inputs[action] = (self.env.road_segments[next_actions[action]][-1] == None)
			
		return inputs
		
	def next_waypoint(self):
		#only called when agent is at intersection
		
		current_road = self.location[1]
		current_intersection = current_road[1]
		
		if current_intersection in self.env.exit_nodes:
			return 'forward'
		
		
		diff = np.subtract(self.destination, current_intersection)
		
		# get the directions to destination from the next intersection
		directions_to_destination = []
		
		if diff[1] > 0:
			directions_to_destination.append('NORTH')
		elif diff[1] < 0:
			directions_to_destination.append('SOUTH')
		
		if diff[0] > 0:
			directions_to_destination.append('EAST')
		elif diff[0] < 0:
			directions_to_destination.append('WEST')
		
		#possible actions at next intersection
		valid_actions = self.env.next_segment(current_road)
		
		# get roads and actions that match the directions to the destination point
		
		next_road_headings = self.env.headings(valid_actions.values())
		
		best_action_dirs = list(set(directions_to_destination) & set(next_road_headings))
		
		if len(best_action_dirs) == 0:
			# all next roads are moving away from the destination. all actions would be equally bad
			# also deliberately avoids to point to the wrong exit
			best_actions = [action for action in valid_actions.keys() if valid_actions[action][1] not in self.env.exit_nodes]
			
		else:
			# select list of actions that would point towards destination
			best_actions = []
			for i, action in enumerate(valid_actions.keys()):
				if next_road_headings[i] in best_action_dirs:
					best_actions.append(action)
		
		# choose best route randomly.
		return np.random.choice(best_actions)
	
	
	def build_state(self):
		
		if self.location[0] == 0:
			self.is_at_intersection = True
		else:
			self.is_at_intersection = False
		
		
		
		if self.is_at_intersection:
			
			
			# The state should contain the following information : light, waypoint, forward_slot_empty, left_slot_empty, right_slot_empty, direction_with_least_congestion
			
			#get lights and traffic
			inputs = self.get_inputs()
			
			#get waypoint
			waypoint = self.next_waypoint()
			
			# may consider taking in the congestion, but ignore for now
			self.state = (waypoint, inputs['light'], inputs['forward'], inputs['left'], inputs['right'] )
			
		else:
			#check if next slot is empty; state will be of the form: {next_slot_empty: True/False}
			if self.env.road_segments[self.location[1]][self.location[0] - 1] == None:
				self.state = (True)  #{'next_slot_empty':True}
			else:
				self.state = (False) #{'next_slot_empty':False}
			
			#return dictonary or flag value
			
		return 
		
	def choose_action(self, state):
		
		if self.is_at_intersection:
			# left, right, straight, or None
			valid_actions_list = self.env.valid_actions(self.location)
			
			if not valid_actions_list:
				# if this list is empty, the road is a dead end, meaning an exit node
				valid_actions_list.append('forward')
				
			valid_actions_list.append(None)
			
			if not self.is_learning:
				#action = np.random.choice(valid_actions_list)
				best_actions = [actions for actions, q_value in self.Q_intersection[state].items() if q_value == self.get_maxQ(state)]
				action = random.choice(best_actions)
				
				# if best action leads to wrong destination, take the action None
				next_actions = self.env.next_segment(self.location[1])
				next_intersection = next_actions[action][1]
				if next_intersection in self.env.exit_nodes:
					if next_intersection != self.destination:
						action = None
				
			else:
				is_random = np.random.choice([True,False], p = [self.epsilon, 1-self.epsilon])
				# using epsilon greedy method
				if is_random:
					action = np.random.choice(valid_actions_list)
				else:
					best_actions = [actions for actions, q_value in self.Q_intersection[state].items() if q_value == self.get_maxQ(state)]
					action = random.choice(best_actions)
					#print "The user is at ", self.location, ", the state is: ", self.state, " and the action taken was, ", action
					#print "Q function is ", self.Q_intersection[state]
					
					if self.location[1][1] in self.env.exit_nodes:
						return action
					
					# if best action leads to wrong destination, take the action None
					if action != None:
						
						next_actions = self.env.next_segment(self.location[1])
						#print next_actions, self.location
						
						next_intersection = next_actions[action][1]
						if next_intersection in self.env.exit_nodes:
							if next_intersection != self.destination:
								action = None
			
		else:
			# move forward or None
			valid_actions_list = ['forward',None]
			
			if not self.is_learning:
				#action = np.random.choice(valid_actions_list)
				best_actions = [actions for actions, q_value in self.Q_road_segment[state].items() if q_value == self.get_maxQ(state)]
				action = random.choice(best_actions)
			else:
				is_random = np.random.choice([True,False], p = [self.epsilon, 1-self.epsilon])
				# using epsilon greedy method
				if is_random:
					action = np.random.choice(valid_actions_list)
				else:
					best_actions = [actions for actions, q_value in self.Q_road_segment[state].items() if q_value == self.get_maxQ(state)]
					action = random.choice(best_actions)
			
			
			
		return action
	
	def get_maxQ(self, state):
		
		if self.is_at_intersection:
			maxQ = max(self.Q_intersection[state].values())
		else:
			maxQ = max(self.Q_road_segment[state].values())
		return maxQ
	
	
	def learn(self, state, action, reward):
		if self.is_learning:
			
			
			if self.is_at_intersection:
				#print self.Q_intersection[state], state, action 
				try:
					self.Q_intersection[state][action] = self.Q_intersection[state][action] + self.learning_rate * (reward - self.Q_intersection[state][action])
				except:
					print state, action, self.location, "problem found", self.Q_intersection[state]
			else:
				self.Q_road_segment[state][action] = self.Q_road_segment[state][action] + self.learning_rate * (reward - self.Q_road_segment[state][action])

		
		if self.location == None:
			return
		
		if self.location[0] == 0:
			self.is_at_intersection = True
		else:		
			self.is_at_intersection = False
			
		return
	
	def createQ(self,state):
		
		# if state is in the Q-function, add state in dictionary
		
		
		if self.is_at_intersection:
			
			#print state
			if state not in self.Q_intersection.keys():
				
				valid_actions = self.env.valid_actions(self.location)
				
				self.Q_intersection[state] = dict()
				
				for action in valid_actions:
					self.Q_intersection[state][action] = 0.0
				self.Q_intersection[state][None] = 0.0
				
				print "New state found!"
			#print Q_intersection
						
		else:
			if state not in self.Q_road_segment.keys():	
				self.Q_road_segment[state] = dict()
				self.Q_road_segment[state][None] = 0.0
				self.Q_road_segment[state]['forward'] = 0.0
		
		
		return
	
	def update(self):
		# called at the end of each time instance. when called, it builds the state, add the state to the Q-function, choose action, act and get reward, and learn and update its Q-function
		self.build_state()          # Get current state
		
        	self.createQ(self.state)                 # Create 'state' in Q-table
        	self.action = self.choose_action(self.state)  # Choose an action
        	
		#print "start point is: ", self.start_point, ", and destination is: ", self.destination
		
		#move, get reward, update Q-function
		
		return
		
		
	def move(self):
	
		"""
		if self.is_at_intersection:
			print "State: ", self.state
			print "Q-function is: ", self.Q_intersection[self.state]
			print "Action: ", self.action """
		#else:
		#	print "Q-function is: ", self.Q_road_segment[self.state]
			
		self.reward = self.act(self.action) # Receive a reward
        	self.learn(self.state, self.action, self.reward)   # Q-learn
		
		
		
	
		return
		
	def act(self, action):
		# move/ don't move, get reward, update Q-function
		
		# find a way to add the violations to violations counter
		
		####################
		# reward key:
		# Moving closer to the destination -> +1 
		# Moving away from destination -> -1
		# Reaching destination -> +40
		# Red Light Violation -> -50
		# Collision -> -50
		# Reaching Wrong Destination -> -5
		# Waiting when green light -> -5
		# Waiting when next slot is empty -> -5
		# Do nothing -> 0
		################
		
		
		#print("action is", action, 'state is', self.state)
		
		if not self.is_at_intersection:
			
			if action == None:
				if self.state == (True):
					# not moving when empty slot ahead
					reward = -5
				else:
					# next slot not empty
					reward = 0
			else:
				#action is to move forward
				if self.state == (True):
					# next slot empty and moving
					next_location = (self.location[0]-1, self.location[1])
					distance_moved = self.dist_to_destination(self.location) - self.dist_to_destination(next_location)
					
					if distance_moved > 0:
						reward = +1 # moving closer to destination
					else:
						reward = -1 # moving away from destination
					
					# empty current slot
					self.env.road_segments[self.location[1]][self.location[0]] = None	
					
					# fill next slot
					self.location = next_location
					self.env.road_segments[self.location[1]][self.location[0]] = self.ID
					
				else:	
					#collision with next vehicle
					reward = -50
					#print "A collision occured due to Agent ", self.ID, " at ", self.location, ", state is: ", self.state, ", Q is: ", self.Q_road_segment[self.state]
					self.env.collision_count += 1  
					
					# remove the vehicle from the system and stop the trial if testing
					if not self.is_learning:	
						self.env.road_segments[self.location[1]][self.location[0]] = None
						self.location = self.destination
					
					
		else:
			# add what happens when close to destination (right and wrong)
			
			if self.location[1][1] in self.env.exit_nodes and self.location[0] == 0:
				if self.location[1][1] == self.destination:
					if action == 'forward':
					
						next_location = 'REACHED!'
						
						self.success = True
						
						reward = 40

						# clear current slot
						self.env.road_segments[self.location[1]][self.location[0]] = None						
						# reached destination
						self.location = self.destination
						
						# update thoughput metrics
						self.env.reached_count += 1
	
					else:
						reward = -5
				else:
					# wrong destination
					if action == 'forward':
						next_location = 'WRONG DESTINATION'
						
						#print "WRONG DESTINATION"
						
						reward = -5
						
						# clear current slot
						self.env.road_segments[self.location[1]][self.location[0]] = None						
						# reached destination
						self.location = self.location[1][1]
						# update thoughput metrics
						self.env.wrong_destination_reached_count += 1
						
					else:
						reward = -5
			
			else:
				if self.state[1] == 'red':
					if action == None:
						reward = 0
					else:
						# red light violation, also better to remove this car from the system to make it simpler
						reward = -50
						
						self.env.signal_violation_count += 1
						#print "violation happened at location: ", self.location, " State is: ", self.state, " action is: ", self.action
						#print "Q-function is: ", self.Q_intersection[self.state]
						
						# remove the agent from the current list immediately
						
						if not self.is_learning:	
							self.env.road_segments[self.location[1]][self.location[0]] = None
							self.location = self.destination
					
						
				else:
					next_actions = self.env.next_segment(self.location[1])
					
					if action == None:
						# waiting when green light
						reward = -5
					elif action == 'forward':
						#collision with vehicle in front
						if self.state[2] == False:
							reward = -50
							
							self.env.collision_count += 1
							#location of car should either not change or we have to remove the car from the traffic system
							
							if not self.is_learning:	
								self.env.road_segments[self.location[1]][self.location[0]] = None
								self.location = self.destination
					
							
							
						else:
							next_road = next_actions[action]
							
							next_location = (len(self.env.road_segments[next_road])-1,next_road) 
							distance_moved = self.dist_to_destination(self.location) - self.dist_to_destination(next_location)
							
							if next_location[1][1] == self.location[1][0]:
								print "U-turn taken"
								self.U_turn_count +=1
								reward = -50
							
							#if next_road[1] in self.env.exit_nodes and next_road[1] != self.destination:
								#if next_road[1] != self.destination:
							#	reward = -30 # penalty for entering the segment leading to wrong destination
						
							
							#else:					
							if distance_moved > 0:
								reward = 1 # moving closer to destination
							else:
								reward = -1 # moving away from destination
								
							# empty current slot
							self.env.road_segments[self.location[1]][self.location[0]] = None	
						
							# fill next slot
							self.location = next_location
							
							#self.is_at_intersection = False
							self.env.road_segments[self.location[1]][self.location[0]] = self.ID
							
							
							# No Wrong route -turns
							if self.location[0] == 0:
								#entered the wrong route 
								reward = -100
								print "Agent entered wrong route"
								self.env.wrong_route_count +=1	
					
					elif action == 'left':
						#collision with vehicle at left
						if self.state[3] == False:
							reward = -50
							
							self.env.collision_count += 1
							#location of car should either not change or we have to remove the car from the traffic system
							
							if not self.is_learning:	
								self.env.road_segments[self.location[1]][self.location[0]] = None
								self.location = self.destination
					
							
						else:
							next_road = next_actions[action]
							next_location = (len(self.env.road_segments[next_road])-1,next_road) 
							distance_moved = self.dist_to_destination(self.location) - self.dist_to_destination(next_location)
							
							if next_location[1][1] == self.location[1][0]:
								print "U-turn taken"
								self.U_turn_count +=1
								reward = -50
							
							
							#if next_road[1] in self.env.exit_nodes:
							#	if next_road[1] != self.destination:
							#		reward = -30 # penalty for entering the segment leading to wrong destination
							
							if distance_moved > 0:
								reward = +1 # moving closer to destination
							else:
								reward = -1 # moving away from destination
								
								
							# empty current slot
							self.env.road_segments[self.location[1]][self.location[0]] = None	
						
							# fill next slot
							self.location = next_location
							
							#self.is_at_intersection = False
							self.env.road_segments[self.location[1]][self.location[0]] = self.ID
							
							# No Wrong route -turns
							if self.location[0] == 0:
								#entered the wrong route 
								reward = -100
								print "Agent entered wrong route"
								self.env.wrong_route_count +=1
					
					elif action == 'right':
						#collision with vehicle at right
						if self.state[4] == False:
							reward = -50
							
							self.env.collision_count += 1
							#location of car should either not change or we have to remove the car from the traffic system
							
							if not self.is_learning:	
								self.env.road_segments[self.location[1]][self.location[0]] = None
								self.location = self.destination
					
						else:
							next_road = next_actions[action]
							next_location = (len(self.env.road_segments[next_road])-1,next_road) 
							distance_moved = self.dist_to_destination(self.location) - self.dist_to_destination(next_location)

							if next_location[1][1] == self.location[1][0]:
								print "U-turn taken"
								self.U_turn_count +=1
								reward = -50
							
							#if next_road[1] in self.env.exit_nodes:
							#	if next_road[1] != self.destination:
							#		reward = -30 # penalty for entering the segment leading to wrong destination
							
							if distance_moved > 0:
								reward = +1 # moving closer to destination
							else:
								reward = -1 # moving away from destination
								
							# empty current slot
							self.env.road_segments[self.location[1]][self.location[0]] = None	
						
							# fill next slot
							self.location = next_location
							
							#self.is_at_intersection = False
							self.env.road_segments[self.location[1]][self.location[0]] = self.ID
							
							# No Wrong route -turns
							if self.location[0] == 0:
								#entered the wrong route 
								reward = -100
								print "Agent entered wrong route"
								self.env.wrong_route_count +=1
					
					if action is not None:
						# extra reward for following the waypoint
						if action == self.state[0]:
							reward = reward + 5
							
						
			
			
				
				
		#if self.location[1][1] not in self.env.exit_nodes and self.location[0] == 0:
		#	self.is_at_intersection = True
		#else:
		#	self.is_at_intersection = False
		return reward
		
	def dist_to_destination(self, location):
		#calculates the l1 distance to destination from current location
		if location != None and self.destination != None :
			location_on_road = location[0]
			next_intersection = location[1][1]
			
			# get total distance
			dist = location_on_road + 1 + np.linalg.norm(np.subtract(self.destination, next_intersection),1)
		return dist
	
	

class DummyAgent():
	#takes actions randomly. Always follows rules rigorously
	
	location = None   # Needs to be assigned a correct value.
	start_point = None # np.random.choice(Environment.exit_nodes)
	is_smart = False
	
	
	def __init__(self, env):
		self.is_at_intersection = False
		self.ID = None
		self.env = env
		return
	
	
	def get_inputs(self):
		#gets information from the environment about the traffic
		#gets information from the i-groups about the lights
		if self.location[1][1] in self.env.exit_nodes:
			# always move forward when on the lane to exit node
			return {'light':'green', 'forward' : True, 'left' : None, 'right' : None}
		else:
			lights = self.env.traffic_lights[self.location[1][1]]
		
		heading = self.env.headings([self.location[1]])[0]
		
		if lights == heading:
			inputs = {'light':'green', 'forward' : None, 'left' : None, 'right' : None}
		else:
			inputs = {'light':'red', 'forward' : None, 'left' : None, 'right' : None}
		
		next_actions = self.env.next_segment(self.location[1])
		
		for action in next_actions.keys():
			#will tell if slot is empty for each valid turn. True means slot is empty, false is when there is a vehicle present.
			inputs[action] = (next_actions[action][-1] == None)
		
		return inputs
	
	def choose_action(self):
		# This function chooses an action from all possible actions based on its location
		if self.is_at_intersection:
			# left, right, straight, or None
			inputs = self.get_inputs()
			if inputs['light'] == 'red' :
				only_action = None
			else :
				next_actions = self.env.next_segment(self.location[1])
				valid_actions = [None]
				for action in next_actions.keys():
					# check which of the next segments have empty slots and append that action from the valid actions
					# then, choose one of the actions randomly
					road = next_actions[action]
					if self.env.road_segments[road][-1] == None : 
						valid_actions.append(action)
							
				only_action = np.random.choice(valid_actions)		
		else:
			# if next slot is free, move forward, or do nothing
			
			if self.env.road_segments[self.location[1]][self.location[0]-1] == None:
				only_action = 'forward'
			else:
				only_action = None
		
		return only_action
		
	
	def act(self):
		# update location and is_at_intersection flag after taking relevant action
		if ( self.location[1][1] in self.env.exit_nodes ) and ( self.location[0] == 0 ) :
			self.env.road_segments[self.location[1]][self.location[0]] = None
			self.location = self.location[1][1]
			
			return
		else :
			action = self.choose_action()
			#print "dummy action is ", action
			if action != None :
			
				# empty the current location on road
				self.env.road_segments[self.location[1]][self.location[0]] = None
				
				if self.is_at_intersection:
					
					# find next road segment, according to the action taken
					next_actions = self.env.next_segment(self.location[1])
					next_road = next_actions[action]
					next_slot = len(self.env.road_segments[next_road])-1
					
					 
					
					# move to next road segment, last slot
					self.location = (next_slot, next_road)
					self.env.road_segments[next_road][next_slot] = self.ID
					
					# update is_at_intersection flag to False
					self.is_at_intersection = False
					
					
				else:
					# empty the current locatio on road
					# self.env.road_segments[location[1]][location[0]] = None
				
					
					# fill the immediate next slot in the same segment, as the action is obviously forward if its not None
					next_slot = self.location[0] - 1					
					self.location = (next_slot, self.location[1])
					self.env.road_segments[self.location[1]][next_slot] = self.ID
					
					# update is_at_intersection flag to True if the next slot is the intersection
					if next_slot == 0:
						self.is_at_intersection = True

			return 
		
	
	def update(self):
		
		
		#self.choose_action()
		# called at the end of each time instance
		#print "dummy is at ", self.location
		#print "dummy color is ", self.color
		#print "Am I at intersection? ", self.is_at_intersection
		#print "dummy "
		self.act()

        	
		return

def create_agent(env, is_learning = True, epsilon = 1, learning_rate = 0.5, testing = False):
		
	#creates agents.
	
	if is_learning:
		agent = LearningAgent(env, epsilon, learning_rate, is_learning)
		if testing:
			agent.reset(testing = True)
	else:
		agent = DummyAgent(env)
	
        #self.agent_states[agent] = {'location': random.choice(self.intersections.keys()), 'heading': (0, 1)}
        return agent


def run_i1():
	
	env_sim = Environment()
	
	num_smart = 3000
	
	# import the Q-function from a file here
	f = open("Q-intersection.pkl","rb")
	Q_intersection = pickle.load(f)
	f.close()
	
	f = open("Q-road_segment.pkl","rb")
	Q_road_segment = pickle.load(f)
	f.close()
	
	
	try:
		f = open("Q-for-i1.pkl","rb")
		env_sim.traffic.state_act_q = pickle.load(f)
		f.close()
	except:
		print "Unable to load the i1 group Q-function."
	
	
	
	
	# initialize the smart agents
	for i in range(num_smart):
		smart_agent = create_agent(env_sim,is_learning=True, testing = True)
		smart_agent.ID = (i+1)*2 - 1
		# assign Q-function to the agent here
		smart_agent.Q_intersection = Q_intersection
		smart_agent.Q_road_segment = Q_road_segment
		env_sim.smart_agent_list_start.append(smart_agent)
		
	
	
	
	
	
	sim2 = Simulator(env_sim, update_delay = 0.1)
	
	
	sim2.run()

	return


def run_i2():
	
	env_sim = Environment()
	
	num_smart = 3000
	
	# import the Q-function from a file here
	f = open("Q-intersection.pkl","rb")
	Q_intersection = pickle.load(f)
	f.close()
	
	f = open("Q-road_segment.pkl","rb")
	Q_road_segment = pickle.load(f)
	f.close()
	
	
	try:
		f = open("Q-for-i2.pkl","rb")
		env_sim.traffic.Q = pickle.load(f)
		f.close()
	except:
		print "Unable to load the i2 group Q-function."
	
	
	
	
	# initialize the smart agents
	for i in range(num_smart):
		smart_agent = create_agent(env_sim,is_learning=True, testing = True)
		smart_agent.ID = (i+1)*2 - 1
		# assign Q-function to the agent here
		smart_agent.Q_intersection = Q_intersection
		smart_agent.Q_road_segment = Q_road_segment
		env_sim.smart_agent_list_start.append(smart_agent)
		
	
	
	
	
	
	sim2 = Simulator(env_sim, update_delay = 0.01)
	
	
	sim2.run()

	return
	
		
def train():
	
	#initializes the environment and the agents and runs the simulator
	env = Environment()
	
	num_dummies_train = 200
	num_smart_train = 1
	
	try:
		# import the Q-function from a file here
		f = open("Q-intersection.pkl","rb")
		Q_intersection = pickle.load(f)
		f.close()
		
		f = open("Q-road_segment.pkl","rb")
		Q_road_segment = pickle.load(f)
		f.close()
		
	except:
		print "File not found. We train from scratch"
	

	
	
	# For training scneario
	for i in range(num_smart_train):
		smart_agent = create_agent(env,is_learning=True)
		smart_agent.ID = (i+1)*2 - 1
		
		# assign Q-function here
		try:
			smart_agent.Q_intersection = Q_intersection
			smart_agent.Q_road_segment = Q_road_segment
		except:
			print "Q-function will start as an empty dictionary"
		env.smart_agent_list_start.append(smart_agent)
		
	for i in range(num_dummies_train):
		dummy_agent = create_agent(env,is_learning=False)
		dummy_agent.ID = (i+1)*2
		env.dummy_agent_list_start.append(dummy_agent)
	
	# initialize and train the simulator
	sim = Simulator(env, update_delay = 0.001)
	
	sim.train_run(tolerance = 0.2, max_trials = 0)
	
	return
	

def intersection_train_i1():
	
	#initializes the environment and the agents and runs the simulator
	env = Environment()
	
	#num_dummies_train = 500
	num_smart_train = 3000
	
	print "Training intersection lights"
	
	
	try:
		# import the Q-function from a file here
		f = open("Q-intersection.pkl","rb")
		Q_intersection = pickle.load(f)
		f.close()
		
		f = open("Q-road_segment.pkl","rb")
		Q_road_segment = pickle.load(f)
		f.close()
		print "Found trained model for Vehicle"
		
	except:
		print "File not found. We train from scratch"
	

	
	
	
	try:
		# import the Q-function from a file here
		f = open("Q-for-i1.pkl","rb")
		env.traffic.state_act_q = pickle.load(f)
		f.close()
		
	except:
		print "File not found. We train from scratch"
	
	
	
	# For training scneario
	for i in range(num_smart_train):
		smart_agent = create_agent(env,is_learning=True,testing = True)
		smart_agent.ID = (i+1)*2 - 1
		
		# assign Q-function here
		try:
			smart_agent.Q_intersection = Q_intersection
			smart_agent.Q_road_segment = Q_road_segment
		except:
			print "Q-function will start as an empty dictionary"
		env.smart_agent_list_start.append(smart_agent)
	
	"""
	# sending dummies	
	for i in range(num_dummies_train):
		dummy_agent = create_agent(env,is_learning=False)
		dummy_agent.ID = (i+1)*2
		env.dummy_agent_list_start.append(dummy_agent)
	"""
	# initialize and train the simulator
	sim = Simulator(env, update_delay = 0.0001)
	
	sim.train_run_intersection_i1(tolerance = 0.2, max_trials = 0)
	
	return

def intersection_train_i2():
	
	#initializes the environment and the agents and runs the simulator
	env = Environment()
	
	#num_dummies_train = 150
	num_smart_train = 3000
	
	print "Training intersection lights"
	
	
	try:
		# import the Q-function from a file here
		f = open("Q-intersection.pkl","rb")
		Q_intersection = pickle.load(f)
		f.close()
		
		f = open("Q-road_segment.pkl","rb")
		Q_road_segment = pickle.load(f)
		f.close()
		print "Found trained model for Vehicle"
		
	except:
		print "File not found. We train from scratch"
	

	
	
	
	try:
		# import the Q-function from a file here
		f = open("Q-for-i2.pkl","rb")
		env.traffic.Q = pickle.load(f)
		f.close()
		
	except:
		print "File not found. We train from scratch"
	
	
	# For training scneario
	for i in range(num_smart_train):
		smart_agent = create_agent(env,is_learning=True,testing = True)
		smart_agent.ID = (i+1)*2 - 1
		
		# assign Q-function here
		try:
			smart_agent.Q_intersection = Q_intersection
			smart_agent.Q_road_segment = Q_road_segment
		except:
			print "Q-function will start as an empty dictionary"
		env.smart_agent_list_start.append(smart_agent)
	
	"""
	# sending dummies	
	for i in range(num_dummies_train):
		dummy_agent = create_agent(env,is_learning=False)
		dummy_agent.ID = (i+1)*2
		env.dummy_agent_list_start.append(dummy_agent)
	"""
	
	# initialize and train the simulator
	sim = Simulator(env, update_delay = 0.0001)
	
	sim.train_run_intersection_i2(tolerance = 0.2, max_trials = 0)
	
	return



if __name__ == '__main__':
	#train()
	#intersection_train_i1()
	intersection_train_i2()
	print "Training ended. Now Testing results"
	#run_i1()
	#run_i2()
