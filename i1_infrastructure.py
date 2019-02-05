import itertools
import random
import math
global road_segments
#global trafficobj
global road_keys,direc_num#,act,curr_state
global collisions, red_light_violations, opposite_dir_runs
collisions, red_light_violations, opposite_dir_runs = 0,0,0
max_slots = 30


road_keys = {}
road_keys[(31,31)]= {}
road_keys[(31,31)]['S'] = ((31,62),(31,31)),((31,31),(31,62)) # 0th is incoming, 1st is outgoing
road_keys[(31,31)]['W'] = ((62,31),(31,31)),((31,31),(62,31))
road_keys[(31,31)]['E'] = ((0,31),(31,31)),((31,31),(0,31))
road_keys[(31,31)]['N'] = ((31,0),(31,31)),((31,31),(31,0))

road_keys[(31,62)]= {}
road_keys[(31,62)]['W'] = ((62,62),(31,62)),((31,62),(62,62))
road_keys[(31,62)]['E'] = ((0,62),(31,62)),((31,62),(0,62))
road_keys[(31,62)]['N'] = ((31,31),(31,62)),((31,62),(31,31))
road_keys[(31,62)]['S'] = ((200,200),(100,100)),((100,100),(200,200))

road_keys[(31,0)]= {}
road_keys[(31,0)]['S'] = ((31,31),(31,0)),((31,0),(31,31))
road_keys[(31,0)]['W'] = ((62,0),(31,0)), ((31,0),(62,0))
road_keys[(31,0)]['E'] = ((0,0),(31,0)),((31,0),(0,0))
road_keys[(31,0)]['N'] = ((200,200),(100,100)),((100,100),(200,200))

road_keys[(0,31)]= {}
road_keys[(0,31)]['S'] = ((0,62),(0,31)),((0,31),(0,62))
road_keys[(0,31)]['W'] = ((31,31),(0,31)),((0,31),(31,31))
road_keys[(0,31)]['N'] = ((0,0),(0,31)),((0,31),(0,0))
road_keys[(0,31)]['E'] = ((200,200),(100,100)),((100,100),(200,200))

road_keys[(0,62)]= {}
road_keys[(0,62)]['W'] = ((31,62),(0,62)),((0,62),(31,62))
road_keys[(0,62)]['E'] = ((-3,62),(0,62)),((0,62),(-3,62))
road_keys[(0,62)]['N'] = ((0,31),(0,62)), ((0,62),(0,31))
road_keys[(0,62)]['S'] = ((200,200),(100,100)),((100,100),(200,200))

road_keys[(0,0)]= {}
road_keys[(0,0)]['S'] = ((0,31),(0,0)), ((0,0),(0,31))
road_keys[(0,0)]['W'] = ((31,0),(0,0)), ((0,0),(31,0))
road_keys[(0,0)]['N'] = ((0,-3),(0,0)), ((0,0),(0,-3))
road_keys[(0,0)]['E'] = ((200,200),(100,100)), ((100,100),(200,200))

road_keys[(62,31)]= {}
road_keys[(62,31)]['S'] = ((62,62),(62,31)), ((62,31),(62,62))
road_keys[(62,31)]['E'] = ((31,31),(62,31)), ((62,31),(31,31))
road_keys[(62,31)]['N'] = ((62,0),(62,31)), ((62,31),(62,0))
road_keys[(62,31)]['W'] = ((200,200),(100,100)), ((100,100),(200,200))

road_keys[(62,0)]= {}
road_keys[(62,0)]['S'] = ((62,31),(62,0)), ((62,0),(62,31))
road_keys[(62,0)]['W'] = ((65,0),(62,0)), ((62,0),(65,0))
road_keys[(62,0)]['E'] = ((31,0),(62,0)), ((62,0),(31,0))
road_keys[(62,0)]['N'] = ((200,200),(100,100)), ((100,100),(200,200))

road_keys[(62,62)]= {}
road_keys[(62,62)]['S'] = ((62,65),(62,62)), ((62,62),(62,65))
road_keys[(62,62)]['E'] = ((31,62),(62,62)), ((62,62),(31,62))
road_keys[(62,62)]['N'] = ((62,31),(62,62)), ((62,62),(62,31))
road_keys[(62,62)]['W'] = ((200,200),(100,100)), ((100,100),(200,200))

class TrafficLights:
    def __init__(self,cord,state_act_map):
        self.cord = cord 
        self.state_act_map = state_act_map
        #self.not_dir = not_dir
        #self.state_act_map = state_act_map
        states_wo_bool = list(set(list(itertools.permutations([0,0,0,0,1,1,1,1,2,2,2,2], r =4))))
        states,l,m = [],[],[]
        for st in states_wo_bool:
            l = list(st)
            m = list(st)
            l.append(0)
            m.append(1)
            states.append(l)
            states.append(m)
        actions = ['RRRR', 'GRRR', 'RGRR', 'RRGR', 'RRRG']
            
                
        for x in range(len(states)):
            state_act_map[tuple(states[x])] = {}
            for y in actions:
                state_act_map[tuple(states[x])][y] = 0 # initialised to zero
        current_state = []

    
        
    def get_curr_state(self,road_segments):
        road_segments[((100,100),(200,200))] = [None]*30
        road_segments[((200,200),(100,100))] = [None]*30

        available_slot = 0
        state_lis = []
        for direc in ['N','E','W','S']:
            if direc in road_keys[self.cord].keys():
                inc = road_keys[self.cord][direc][0] ## get values from here
                #print inc
                #print v_grp_dic[inc]
                cnt = 0
                for x in range(0,2): ## check first 2 slots
                    if road_segments[inc][x] != None:
                        cnt += 1
                state_lis.append(cnt)
                out = road_keys[self.cord][direc][1]
                if road_segments[out][0] == None:
                    available_slot = 1
        state_lis.append(available_slot)
        return tuple(state_lis)
    


class Q_learning:
    
    def __init__(self):
        self.epsilon = 1
        self.alpha = 0.5
        self.gamma = 0.5
    
    def get_action(self,curr_state,state_act_q,invalid_dir):
        #max_q = state_act_q[curr_state]['RRRR']
        direction = ['N','E','W','S']
        invalid_act = 'RRRR'
        if invalid_dir != 0:
            index = direction.index(invalid_dir)
            invalid_act = invalid_act[:index] +'G'+invalid_act[index+1:]
            
        #next_act = 'RRRR'
        epsilon_rand = random.random()
        if(epsilon_rand >= self.epsilon): #exploitation
            
            valid_acts = [acts for acts in ['RRRG','RRGR','RGRR','GRRR'] if acts != invalid_act]
            max_val = -1000
            for key,val in state_act_q[curr_state].items():
            	if val > max_val and key in valid_acts:
            		max_val = val
            #maxQ = max(state_act_q[curr_state].values())
            maxQ = max_val
            best_actions = [actions for actions in valid_acts if state_act_q[curr_state][actions] == maxQ]
            #print best_actions, state_act_q[curr_state],invalid_act
            next_act = random.choice(best_actions)

            
            #for key in state_act_q[curr_state].keys():
             #   if (state_act_q[curr_state][key]>max_q):
              #      max_q = state_act_q[curr_state][key]
               #     next_act = key

        else:
            valid_acts = [acts for acts in ['RRRG','RRGR','RGRR','GRRR','RRRR'] if acts != invalid_act]
            next_act = random.choice(valid_acts)


        return next_act
     

    def get_rewards(self,curr_state,next_state,action):
       # no_slot_penalty = () ? -20:0 #accident
        if (curr_state[-1]==0) and (action != 'RRRR'):
            no_slot_penalty = -20
        else: no_slot_penalty = 0
       # open_slot_penalty = ((curr_state[4]==1) and (action == 'RRRR'))? -15:0
        if (curr_state[-1]==1) and (action == 'RRRR'):
            open_slot_penalty = -15
        else: open_slot_penalty = 0
        final_reward = no_slot_penalty + open_slot_penalty
        if action == 'RRRG':
            R_factor = [-1,-1,-1,2]
        elif action =='RRGR':
            R_factor = [-1,-1,2,-1]
        elif action == 'RGRR':
            R_factor = [-1,2,-1,-1]
        elif action == 'GRRR':
            R_factor = [2,-1,-1,-1]
        else:
            R_factor = [-1,-1,-1,-1]
            
        R_list = [a*b for a,b in zip(R_factor,curr_state[0:4])]
        
        for i in R_list:
            final_reward += i
        
        return final_reward
    
    def update_qvalue(self,curr_state,next_state,action,reward,state_act_q):
        #print curr_state
        #print next_state
        max_q_nextstate = -1000
        for key in state_act_q[next_state].keys():
            if (state_act_q[next_state][key] > max_q_nextstate):
                max_q_nextstate = state_act_q[next_state][key]         
        
        add_update = self.alpha*(reward+(self.gamma*(max_q_nextstate-state_act_q[curr_state][action])))
        state_act_q[curr_state][action] += add_update
        return state_act_q
        #print ("curr_state ",curr_state," act ",action," reward ",reward," q ",add_update)

#####################################################################################################################



    ####################################################################### trace of the car : dummy

class Traffic:
    global collisions, red_light_violations, opposite_dir_runs,u_turns
    collisions, red_light_violations, opposite_dir_runs, u_turns = 0,0,0,0
    
    def __init__(self):
        self.trafficobj = [[0 for y in range(3)] for x in range(3)]

        self.trafficobj[2][0] = TrafficLights((0,62),{})
        self.trafficobj[2][1] = TrafficLights((31,62),{})
        self.trafficobj[2][2] = TrafficLights((62,62),{})

        self.trafficobj[1][0] = TrafficLights((0,31),{})
        self.trafficobj[1][1] = TrafficLights((31,31),{})
        self.trafficobj[1][2] = TrafficLights((62,31),{})

        self.trafficobj[0][0] = TrafficLights((0,0),{})
        self.trafficobj[0][1] = TrafficLights((31,0),{})
        self.trafficobj[0][2] = TrafficLights((62,0),{})

        self.direc_num = ['N','E','W','S']
        # initialization
        self.curr_state = (0,0,0,0,1)
        self.vec_prev_state = {}
        self.vec_prev_state[(0,0)]  = road_keys[(0,0)]
        self.vec_prev_state[(31,0)]  = road_keys[(31,0)]
        self.vec_prev_state[(62,0)]  = road_keys[(62,0)]
        self.vec_prev_state[(0,31)]  = road_keys[(0,31)]
        self.vec_prev_state[(31,31)]  = road_keys[(31,31)]
        self.vec_prev_state[(62,31)]  = road_keys[(62,31)]
        self.vec_prev_state[(0,62)]  = road_keys[(0,62)]
        self.vec_prev_state[(31,62)]  = road_keys[(31,62)]
        self.vec_prev_state[(62,62)]  = road_keys[(62,62)]
        self.act = 'RRRR'
        self.state_act_q = [[{} for y in range(3)] for x in range(3)]
        self.q_learn_obj = Q_learning()
        self.epsilon = self.q_learn_obj.epsilon

    def reset(self, destination=None, testing=False):
    
    # Update epsilon using a decay function
    # Update additional class parameters as needed
    # If 'testing' is True, set epsilon and alpha to 0
    
        if testing:
            self.epsilon = 0
            self.learning_rate = 0
        else:
            a = 0.05
            c = -5
            if self.epsilon == 1:
                    t = 0
            else:
                    t = (math.log(1/self.epsilon-1) - c)/a
            t=t+1
            self.epsilon = 1/(math.exp(a*t+c)+1)
        self.q_learn_obj.epsilon = self.epsilon
        return




    def detect_collisions(self,act, vec_curr_state_cord,road_segments,cord,collisions): # we have direc_num = NEWS
        if 'G' in act:
            dr = act.index('G')
            prev_list_0, curr_list_0, prev_list_1, curr_list_1 = [-1 for x in range(4)], [-1 for x in range(4)],[-1 for x in range(4)],[-1 for x in range(4)]
            for i,direc in enumerate(['N','E','W','S']):
                if i != dr:
                    #print road_segments[self.vec_prev_state[cord][direc][1]]
                    if road_segments[self.vec_prev_state[cord][direc][1]][0] != None:
                        prev_list_0[i] = road_segments[self.vec_prev_state[cord][direc][1]][0] # saving the first slots of 3 outgoing lanes
                    #else: prev_list_0[i] = -1
                    if road_segments[vec_curr_state_cord[direc][1]][0] != None:
                        curr_list_0[i] = road_segments[vec_curr_state_cord[direc][1]][0]
                    #else: curr_list_0[i] = -1
                    if road_segments[self.vec_prev_state[cord][direc][1]][1] != None:
                        prev_list_1[i] = road_segments[self.vec_prev_state[cord][direc][1]][1]
                    #else : prev_list_1[i] = -1
                    if road_segments[vec_curr_state_cord[direc][1]][1] != None:
                        curr_list_1[i] = road_segments[vec_curr_state_cord[direc][1]][1]
                    #else : curr_list_1[i] = -1
        # check prev_list_0 with curr_list_1:
            for x in range(4):
            # collision happens if slot 0 which was booked in prev state does not match slot 0 booked in curr state
            # (which means the car moved) while the slot 1 is still the same.
                if prev_list_0[i] != None and prev_list_0[i] != -1:
                    if prev_list_1[i] == curr_list_1[i] and prev_list_0[i] != curr_list_0[i]:
                        collisions += 1
        print "Collisions are: ",collisions
        return


    def detect_red_light_violations(self,act, vec_curr_state_cord,road_segments,cord,red_light_violations):
    # monitor all other indices which are red
        curr_list_out,check_slots = [],[]
        for i,direc in enumerate(['N','E','W','S']):
            if road_segments[vec_curr_state_cord[direc][1]][0] != None:
                curr_list_out.append(road_segments[vec_curr_state_cord[direc][1]][0]) # slot 0 of outgoing
            if act[i] == 'R':
                if road_segments[self.vec_prev_state[cord][direc][0]][-1] != None:
                    check_slots.append(road_segments[self.vec_prev_state[cord][direc][0]][-1]) # inc slot to be checked
        for vehicle in check_slots:
            if vehicle in curr_list_out:
                red_light_violations += 1
        print "Red Light Violations are: ",red_light_violations
        return

    def detect_opposite_dir_runs(self, vec_curr_state_cord,road_segments,cord,opposite_dir_runs):
    # check if any vechicle goes from in in prev to in in curr
        prev_list_in, curr_list_in = [],[]
        for i,direc in enumerate(['N','E','W','S']):
            if road_segments[self.vec_prev_state[cord][direc][0]][-1] != None:
            #prev_list_in.append(road_segments[self.vec_prev_state[cord][direc][0]][-1])
                for dr in ['N','E','W','S']:
                    if dr != direc and road_segments[vec_curr_state_cord[dr][0]][-1] != None:
                        if road_segments[self.vec_prev_state[cord][direc][0]][-1] == road_segments[vec_curr_state_cord[dr][0]][-1]:
                            opposite_dir_runs += 1
        #curr_list_in.append(road_segments[vec_curr_state_cord[dr][0]][-1])
        #for vehicle in prev_list_in:
        #   if vehicle in curr_list_in:
        #       opposite_dir_runs += 1
        print "Opposite Direction Runs are: ",opposite_dir_runs
        return
                
    def detect_u_turns(self, vec_curr_state_cord,road_segments,cord,u_turns):
        # check if any vechicle goes from in in prev to in in curr
        prev_list_in, curr_list_in = [],[]
        for i,direc in enumerate(['N','E','W','S']):
            if road_segments[self.vec_prev_state[cord][direc][0]][-1] != None and road_segments[vec_curr_state_cord[direc][1]][0] != None:
                if road_segments[self.vec_prev_state[cord][direc][0]][-1] == road_segments[vec_curr_state_cord[direc][1]][0]:
                    u_turns += 1
            # if road_segments[self.vec_prev_state[cord][direc][0]][-1] != None:
            #   prev_list_in.append(road_segments[self.vec_prev_state[cord][direc][0]][-1])
            #if road_segments[vec_curr_state_cord[direc][1]][0] != None:
            #   curr_list_in.append(road_segments[vec_curr_state_cord[direc][0]][-1])
            #for i,vehicle in enumerate(prev_list_in):
            #if curr_list_in[i] == vehicle:
            #   u_turns += 1
        print "U Turns are: ",u_turns
        return

    def update_traffic_lights(self,road_segments):
        vec_curr_state = {}
        v_grp_inp = [[0 for y in range(3)] for x in range(3)] # needs to be passed as input to V-group
        for x in range(len(self.trafficobj)):
            for y in range(len(self.trafficobj[0])):
                
                    traf_light = self.trafficobj[x][y]
                    cord = traf_light.cord
                    #vec_curr_state = road_keys[cord]
                    vec_curr_state[cord] = road_keys[cord]
                    invalid_dir = 0
                    for key in road_keys[cord].keys():
                        if road_keys[cord][key] == (((200,200),(100,100)),((100,100),(200,200))):
                            invalid_dir = key
                    self.state_act_q[x][y]  = traf_light.state_act_map  # Q(s,a)
                    next_state = traf_light.get_curr_state(road_segments) #getting v group dic
                    reward = self.q_learn_obj.get_rewards(self.curr_state,next_state,self.act)
                    #print (" for cord for traffic light: ",cord)
                    self.state_act_q[x][y] = self.q_learn_obj.update_qvalue(self.curr_state,next_state,self.act,reward,self.state_act_q[x][y])
                    self.curr_state = next_state
                    self.act = self.q_learn_obj.get_action(self.curr_state,self.state_act_q[x][y],invalid_dir)
                    direc_num = ['N','E','W','S']
                    for i,st in enumerate(self.act):
                        if st == 'G':
                            v_grp_inp[x][y] = direc_num[i]
            	    
                    #print "previous state is: ",self.vec_prev_state[cord]
                    #print "curr state is: ", vec_curr_state[cord]
            	    
                    self.detect_collisions(self.act, vec_curr_state[cord],road_segments,cord,collisions)
                    self.detect_red_light_violations(self.act, vec_curr_state[cord],road_segments,cord, red_light_violations)
                    self.detect_opposite_dir_runs(vec_curr_state[cord],road_segments,cord,opposite_dir_runs)
                    self.detect_u_turns(vec_curr_state[cord],road_segments,cord,u_turns)
                    self.vec_prev_state[cord] = vec_curr_state[cord]
        return v_grp_inp

