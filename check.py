import pickle

f = open("Q-intersection.pkl","rb")
Q_intersection = pickle.load(f)
f.close()

green_key_list = [item for item in Q_intersection.keys() if item[1] == 'green']
red_key_list = [item for item in Q_intersection.keys() if item[1] == 'red']


for key in green_key_list:
	print "state is : ", key, ", Q is : ", Q_intersection[key]

print "RED light states from here on ... "
	
for key in red_key_list:
	print "state is : ", key, ", Q is : ", Q_intersection[key]

print "Total states = ", len(Q_intersection.keys())
