import pygame
import os
import time
import random
import importlib
import csv
import numpy as np
import sys
import pickle

class Simulator():
	
	# colors for identification
	colors = {
        'black'   : (  0,   0,   0),
        'white'   : (255, 255, 255),
        'red'     : (255,   0,   0),
        'green'   : (  0, 255,   0),
        'dgreen'  : (  0, 228,   0),
        'blue'    : (  0,   0, 255),
        'cyan'    : (  0, 200, 200),
        'magenta' : (200,   0, 200),
        'yellow'  : (255, 255,   0),
        'mustard' : (200, 200,   0),
        'orange'  : (255, 128,   0),
        'maroon'  : (200,   0,   0),
        'crimson' : (128,   0,   0),
        'gray'    : (155, 155, 155)
    }
	
	car_colors = {
       	'white'   : (255, 255, 255),
       	'red'     : (255,   0,   0),
       	'green'   : (  0, 255,   0),
       	'blue'    : (  0,   0, 255),
       	'cyan'    : (  0, 200, 200),
       	'magenta' : (200,   0, 200),
       	'yellow'  : (255, 255,   0),
       	'orange'  : (255, 128,   0),
            }
            
	
	def __init__(self,env, update_delay=0.5, display=True):
		
		self.env = env
		
		self.unique_roads = []
		for road in self.env.road_segments.keys():
			if tuple(reversed(road)) not in self.unique_roads:
				self.unique_roads.append(road)

		
		
		
		
		self.update_delay = update_delay
		
		
		self.bg_color = self.colors['gray']
		self.boundary_color = self.colors['black']
		self.road_color = self.colors['black']
		self.road_width = 20
		self.bounds = (5,10,self.env.n_blocks[0],self.env.n_blocks[1])
		
		self.quit = False
        	self.start_time = None
        	self.current_time = 0.0
        	self.last_updated = 0.0
		
		
		# This is for simulation purposes, not to be touched yet
		self.display = display
		
		
		if self.display:
	            	#try:
        	    	self.pygame = importlib.import_module('pygame')
        		self.pygame.init()
        	        self.size = ((self.env.n_blocks[0] + 15 )* self.env.block_size, (self.env.n_blocks[1]+15)*self.env.block_size)
        	        self.screen = self.pygame.display.set_mode(self.size)
			
			self.block_size = self.env.block_size
			
			self.dir_img_size=(self.block_size,self.block_size)
				
			self.direction_images={
					'NORTH':self.pygame.transform.smoothscale(pygame.image.load('images/North.png'),self.dir_img_size),
					'SOUTH':self.pygame.transform.smoothscale(pygame.image.load('images/South.png'),self.dir_img_size),
					'EAST':self.pygame.transform.smoothscale(pygame.image.load('images/East.png'),self.dir_img_size),
					'WEST':self.pygame.transform.smoothscale(pygame.image.load('images/West.png'),self.dir_img_size)
					}
				
				
        	        #self._ew = self.pygame.transform.smoothscale(self.pygame.image.load(os.path.join("images", "east-west.png")), (self.road_width, self.road_width))
        	        #self._ns = self.pygame.transform.smoothscale(self.pygame.image.load(os.path.join("images", "north-south.png")), (self.road_width, self.road_width))
		
        	        self.frame_delay = max(1, int(self.update_delay * 1000))  # delay between GUI frames in ms (min: 1)
        	        self.agent_sprite_size = (self.block_size, self.block_size)
        	        #self.primary_agent_sprite_size = (42, 42)
        		        
        	        #self.agent_circle_radius = 20  # radius of circle, when using simple representation
        		        
			print "agent list is ", len(self.env.agent_list_start), " long"
        		        
        	        for agent in self.env.smart_agent_list_start:
        	        	color_list = self.env.car_colors.keys()
        	        	color_list.remove('yellow')
        	        	agent.color = random.choice(color_list)
        	            	agent._sprite = self.pygame.transform.smoothscale(self.pygame.image.load(os.path.join("images", "car-{}.png".format(agent.color))), self.agent_sprite_size)
        	            	agent._sprite_size = (agent._sprite.get_width(), agent._sprite.get_height())
			
        	        for agent in self.env.dummy_agent_list_start:
        	        	agent.color = 'yellow'#random.choice(self.env.car_colors.keys())
        	            	agent._sprite = self.pygame.transform.smoothscale(self.pygame.image.load(os.path.join("images", "car-{}.png".format(agent.color))), self.agent_sprite_size)
        	            	agent._sprite_size = (agent._sprite.get_width(), agent._sprite.get_height())
						
			
        	        self.font = self.pygame.font.Font(None, 20)
        	        self.paused = False
       		#	except ImportError as e:
        	#	        self.display = False
        	#	        print "Simulator.__init__(): Unable to import pygame; display disabled.\n{}: {}".format(e.__class__.__name__, e)
   		#	except Exception as e:
   		#	        self.display = False
        	#		print "Simulator.__init__(): Error initializing GUI objects; display disabled.\n{}: {}".format(e.__class__.__name__, e)

		
		
        	print "The num of smart agents are ", len(self.env.smart_agent_list_start)
        	print "The num of dummy agents are ", len(self.env.dummy_agent_list_start)
		
		return
	
	
	def set_traffic_lights(self,traffic_lights):
		
		
		
		for loc in traffic_lights.keys():
			
			if traffic_lights[loc] == None:
				center = self.coordinate_transform(loc)
		        	pygame.draw.circle(self.screen, self.colors['red'], center, self.block_size/2, 0)
			else:
				dir_sprite = self.direction_images[traffic_lights[loc]] 
				self.screen.blit(dir_sprite, self.coordinate_transform(  tuple(np.array(loc) - np.array([0.5,-0.5]))  )) ##need to transform traffic_nodes[i]        				
		
		
		"""i=-1 #index iterating over traffic nodes
		for l in traffic_lights:#yet to define variable traffic_lights, would be receiving from I team	
			for direction in l:
				i+=1
				if direction==None:
					#print('No green light')
					center = self.coordinate_transform(self.traffic_nodes[i])
			        	pygame.draw.circle(self.screen, self.colors['red'], center, self.block_size/2, 0)
					continue
				elif direction[:1].upper()=='N': #if North
					direction_image=direction_images['North']				
				elif direction[:1].upper()=='E': #if East
					direction_image=direction_images['East']
				elif direction[:1].upper()=='W': #if West
					direction_image=direction_images['West']
				elif direction[:1].upper()=='S': #if South
					direction_image=direction_images['South']
				else:
					raise Exception('Invalid direction')
					
				
				self.screen.blit(direction_image, self.coordinate_transform(  tuple(np.array(traffic_nodes[i]) - np.array([0.5,-0.5]))  )) ##need to transform traffic_nodes[i] """       
		return
	
	
	def coordinate_transform(self, point_tuple):
		# takes in coordinate in the road coordinates and converts them to pygame version
		transformed_x = (self.bounds[0] + point_tuple[0] + 3 + 0.5)*self.block_size
		transformed_y = (self.bounds[1] + self.bounds[3] -3 - point_tuple[1] - 0.5)*self.block_size
		return (int(transformed_x), int(transformed_y))


	def place_vehicle(self,agent):
		# takes in the location of the car and gives out the location on the UI
		road_segment = agent.location[1]
		slot = len(self.env.road_segments[road_segment]) - agent.location[0]
		
		
		# get the direction of movement of the vehicle
		direction = np.subtract(road_segment[1],road_segment[0])
		length = np.linalg.norm(direction)
	
		car_location = self.coordinate_transform(tuple(np.array(road_segment[0]) - np.array([0.5,-0.5]) + (slot ) * (direction/length)  + np.flip(direction/length) * (0.25 if direction[0] == 0 else -0.25) ))
	
		if hasattr(agent, '_sprite'):
			rotated_sprite = agent._sprite if tuple(direction/length) == (1,0) else pygame.transform.rotate(agent._sprite, 180 if tuple(direction/length) == (-1,0)  else tuple(direction/length)[1]*90 )
		
		return car_location, rotated_sprite
	
	
	
	def render(self, trial, testing = False):
	
		# Reset the screen.
	        self.screen.fill(self.bg_color)
        
        
        
        	# Draw elements
        	# * Static elements

	
        
        	# convert the rect boundaries to a math term dependent on parameters from env 
        	pygame.draw.rect(self.screen, self.boundary_color, ( self.bounds[0]*self.block_size, self.bounds[1]*self.block_size, self.bounds[2]*self.block_size, self.bounds[3]*self.block_size), 4)
        
        
        	# iteration over roads to draw the roads and separation lines
        	for road in self.unique_roads:
        
        		# transforming road points
        		road_start = self.coordinate_transform(road[0])
        		road_end = self.coordinate_transform(road[1])
        	
        		# drawing the roads 
        		pygame.draw.line(self.screen, self.road_color, road_start, road_end, self.road_width)
        		
        		# drawing the separation lines
        		pygame.draw.line(self.screen, self.colors['white'], road_start, road_end, 1)
        	
        	# Highlight the traffic nodes with yellow circles
        	
        	for node in self.env.traffic_nodes:
        		center = self.coordinate_transform(node)
        		pygame.draw.circle(self.screen, self.colors['yellow'], center, self.block_size/2, 0)
        	
        	# Highlight the exit nodes with green circles
        	for node in self.env.exit_nodes:
        		center = self.coordinate_transform(node)
        		pygame.draw.circle(self.screen, self.colors['green'], center, self.block_size/2, 0)
        		
        	# Add traffic light directions on the map
        	self.set_traffic_lights(self.env.traffic_lights)
        	
		# Add Dynamic elements from here on
		
		
		for agent in self.env.agent_list_current:
			car_location, rotated_sprite = self.place_vehicle(agent)
			self.screen.blit(rotated_sprite, car_location)
		
		
		# Overlays from here on
		self.font = self.pygame.font.Font(None, 50)
        	if testing:
        	    	self.screen.blit(self.font.render("Testing Trial %s"%(trial), True, self.colors['black'], self.bg_color), (10, 10))
        	
        		self.font = self.pygame.font.Font(None, 40)
			self.screen.blit(self.font.render("Average Throughput: %s" %(self.env.average_throughput), True, self.colors['blue'], self.bg_color), (700,50))
		
        	
        	else:
            		self.screen.blit(self.font.render("Training Trial %s"%(trial), True, self.colors['black'], self.bg_color), (10, 10))

	        self.font = self.pygame.font.Font(None, 30)
		self.screen.blit(self.font.render("Number of Vehicles in System: %s" %(len(self.env.agent_list_current)), True, self.colors['black'], self.bg_color), (10,60))
		
		self.font = self.pygame.font.Font(None, 30)
		self.screen.blit(self.font.render("Number of collisions: %s" %(self.env.collision_count), True, self.colors['magenta'], self.bg_color), (10,90))
		
		self.font = self.pygame.font.Font(None, 30)
		self.screen.blit(self.font.render("Number of red light violations: %s" %(self.env.signal_violation_count), True, self.colors['magenta'], self.bg_color), (10,120))
		
        	self.font = self.pygame.font.Font(None, 30)
		self.screen.blit(self.font.render("Time: %s" %(self.env.time), True, self.colors['blue'], self.bg_color), (700,90))
		
		self.font = self.pygame.font.Font(None, 35)
		self.screen.blit(self.font.render("Number of vehicles reached: %s" %(self.env.reached_count), True, self.colors['blue'], self.bg_color), (700,120))
		
		self.font = self.pygame.font.Font(None, 35)
		self.screen.blit(self.font.render("Number of vehicles reached wrong destination: %s" %(self.env.wrong_destination_reached_count), True, self.colors['blue'], self.bg_color), (700,160))
		
		self.font = self.pygame.font.Font(None, 30)
		self.screen.blit(self.font.render("Number of U-turns: %s" %(self.env.U_turn_count), True, self.colors['blue'], self.bg_color), (10,150))
		
		self.font = self.pygame.font.Font(None, 30)
		self.screen.blit(self.font.render("Number of Wrong route entries: %s" %(self.env.wrong_route_count), True, self.colors['blue'], self.bg_color), (300,150))
		
		
        	for event in pygame.event.get():
        	        if event.type == pygame.QUIT:
        	                done = True
		
		
		#pygame.time.delay(500)	
		
		#step()
		
		        
        	pygame.display.flip()
	
	
		return
	
	
	
	def train_run(self, tolerance = 0.05, max_trials = 1000):
		
		
		# initializing parameters and metrics for training
		self.quit = False
		
	        #total_trials = 1
	        #testing = False
	        trial = 1
	        
	        while not self.quit:
	        
	        	self.env.reset()
	        	
	        	if trial > 20:
	        	
	        		a = self.env.smart_agent_list_start[0]
	                    	print "epsilon = ", a.epsilon	
	                    	if a.is_learning and a.epsilon < tolerance: # assumes epsilon decays towards 0  	
	                          	self.quit = True
	                        elif max_trials!=0 and trial > max_trails:
	                        	self.quit = True
	                
	                self.current_time = 0.0
	            	#self.last_updated = 0.0
	            	#self.start_time = time.time()
	            	
	            	while self.env.time < 3600:
	                	
	                    	# Update environment
	                    	self.env.step()
	                    		
	                    	if len(self.env.smart_agent_list_start) == 0 and len(self.env.smart_agent_list_current) == 0:
	                    		# learning agent reached some destination or had an accident
	                    		break
	                    	
	                    	# Render GUI and sleep
	                    	#if self.display:
	                        #	self.render(trial, testing = False)
	                        #	self.pygame.time.wait(self.frame_delay)
	
				for event in pygame.event.get():
                			if event.type == pygame.QUIT:
                        			self.quit = True
                        		
				
				if self.quit:
					# save Q-functions to a file
					if len(self.env.smart_agent_list_start) > 0:
						a = self.env.smart_agent_list_start[0]
					elif len(self.env.smart_agent_list_current) > 0:
						a = self.env.smart_agent_list_current[0]
					else:
						break
					
					f = open("Q-intersection.pkl","wb")
					pickle.dump(a.Q_intersection,f)
					f.close()
					
					f = open("Q-road_segment.pkl","wb")
					pickle.dump(a.Q_road_segment,f)
					f.close()
					
					print "Q-functions were saved"
					
					break
			
			print("Trial number", trial)
			trial = trial + 1

		return
	
	
	
	
	
		
	def run(self, tolerance=0.05, n_test=10):
		
		self.quit = False
	        trial = 1

	        while not self.quit:
	
			self.env.reset(agent_testing = True, infrastructure_testing = True)
			        
	            	# Break if we've reached the limit of testing trials
	            	if trial > n_test:
	                	break

	            	self.current_time = 0.0
	            	self.last_updated = 0.0
	            	self.start_time = time.time()
	            	
	            	while self.env.time < 3600:
	                	
	                    	
	                    	# Handle GUI events
	                    
	                    	
	                    
	                    	# Update environment
	                    	
	                    	self.env.step()
	                        	
	                    	if len(self.env.smart_agent_list_start) == 0 and len(self.env.smart_agent_list_current) == 0:
	                    		# all learning agents reached some destination or had an accident
	                    		break
	                    	
	                    	
	                    	# Render text
	                    	#self.render_text(trial, testing)
	
	                    	# Render GUI and sleep
	                    	if self.display:
	                        	self.render(trial, testing = True)
	                        	self.pygame.time.wait(self.frame_delay)
	
	
				for event in pygame.event.get():
                			if event.type == pygame.QUIT:
                        			self.quit = True
                        		
				
				if self.quit:
					break
				
				
	            	
	            	print("Trial number", trial)
			
			self.env.average_throughput = ((self.env.average_throughput * (trial-1)) + self.env.throughput)/float(trial)
			
			#if testing:
			#	print "TESTING"
	            	# Trial finished
	            	# Increment
	            	trial = trial + 1
	            	
	
	
	        print "\nSimulation ended. . . "
	
	        # Report final metrics
	        if self.display:
	            self.pygame.display.quit()  # shut down pygame
			
			
		
	
	
		return
		
		
		
		
		
	def train_run_intersection_i1(self, tolerance=0.05, n_test=10, max_trials = 1000):
		
		self.quit = False
	        trial = 1
	        

                

	        while not self.quit:
	
			self.env.reset(agent_testing = True, infrastructure_testing = False)
			
			a = self.env.traffic
	        
			if trial > 20:
				
		            	print "Traffic object epsilon = ", a.epsilon
		            	print "epsilon = ", a.epsilon
		            	if a.epsilon < tolerance: # assumes epsilon decays towards 0  	
		                  	self.quit = True
		                elif max_trials!=0 and trial > max_trails:
		                	self.quit = True
			
			        
	            	# Break if we've reached the limit of testing trials
	            	#if trial > n_test:
	                
	                #	break

	            	#self.current_time = 0.0
	            	#self.last_updated = 0.0
	            	#self.start_time = time.time()
	            	
	            	while self.env.time < 3600:
	                	
	                    	
	                    	# Handle GUI events
	                    
	                    	
	                    
	                    	# Update environment
	                    	
	                    	self.env.step()
	                        	
	                    	#if len(self.env.smart_agent_list_start) == 0 and len(self.env.smart_agent_list_current) == 0:
	                    	#	# all learning agents reached some destination or had an accident
	                    	#	break
	                    	
	                    	
	                    	# Render text
	                    	#self.render_text(trial, testing)
	
	                    	# Render GUI and sleep
	                    	#if self.display:
	                        #	self.render(trial, testing = True)
	                        #	self.pygame.time.wait(self.frame_delay)
	
	
				for event in pygame.event.get():
                			if event.type == pygame.QUIT:
                        			self.quit = True
                        		
				
				if self.quit:
				
				
					f = open("Q-for-i1.pkl","wb")
					pickle.dump(a.state_act_q,f)
					f.close()
					
					print "Q-functions were saved for i1"
				
					break
				
				
	            	
	            	print("Trial number", trial)
			#print "Q is: ", a.state_act_q
			self.env.average_throughput = ((self.env.average_throughput * (trial-1)) + self.env.throughput)/float(trial)
			
			#if testing:
			#	print "TESTING"
	            	# Trial finished
	            	# Increment
	            	trial = trial + 1
	            	
	
	
	        print "\nSimulation ended. . . "
	
	        # Report final metrics
	        if self.display:
	            self.pygame.display.quit()  # shut down pygame
			
			
		
	
	
		return
		
	def train_run_intersection_i2(self, tolerance=0.05, n_test=10, max_trials = 1000):
		
		self.quit = False
	        trial = 1
	        

                

	        while not self.quit:
	
			self.env.reset(agent_testing = True, infrastructure_testing = False)
			
			a = self.env.traffic
	        
			if trial > 20:
				
		            	print "Traffic object epsilon = ", a.epsilon
		            	print "epsilon = ", a.epsilon
		            	if a.epsilon < tolerance: # assumes epsilon decays towards 0  	
		                  	self.quit = True
		                elif max_trials!=0 and trial > max_trails:
		                	self.quit = True
			
			        
	            	# Break if we've reached the limit of testing trials
	            	#if trial > n_test:
	                
	                #	break

	            	#self.current_time = 0.0
	            	#self.last_updated = 0.0
	            	#self.start_time = time.time()
	            	
	            	while self.env.time < 1800:
	                	
	                    	
	                    	# Handle GUI events
	                    
	                    	
	                    
	                    	# Update environment
	                    	
	                    	self.env.step()
	                        	
	                    	#if len(self.env.smart_agent_list_start) == 0 and len(self.env.smart_agent_list_current) == 0:
	                    	#	# all learning agents reached some destination or had an accident
	                    	#	break
	                    	
	                    	
	                    	# Render text
	                    	#self.render_text(trial, testing)
	
	                    	# Render GUI and sleep
	                    	#if self.display:
	                        #	self.render(trial, testing = True)
	                        #	self.pygame.time.wait(self.frame_delay)
	
	
				for event in pygame.event.get():
                			if event.type == pygame.QUIT:
                        			self.quit = True
                        		
				
				if self.quit:
				
				
					f = open("Q-for-i2.pkl","wb")
					pickle.dump(a.Q,f)
					f.close()
					
					print "Q-functions were saved for i2"
				
					break
				
				
	            	
	            	print("Trial number", trial)
			#print "Q is: ", a.Q
			self.env.average_throughput = ((self.env.average_throughput * (trial-1)) + self.env.throughput)/float(trial)
			
			#if testing:
			#	print "TESTING"
	            	# Trial finished
	            	# Increment
	            	trial = trial + 1
	            	
	
	
	        print "\nSimulation ended. . . "
	
	        # Report final metrics
	        if self.display:
	            	self.pygame.display.quit()  # shut down pygame
			
			
		
	
	
		return
		
		
