import pickle

f = open("Q-for-i1.pkl","rb")
Q_i1 = pickle.load(f)
f.close()

for i in range(3):
	for j in range(3):
		key_list = [item for item in Q_i1[i][j].keys()]

		for key in key_list:
			print Q_i1[i][j][key]
		print "This is for location", (i,j)
		print "Total num of states = ", len(key_list)
		input("Press enter for next Traffic Light")


#print "Q is: ", Q_i1[][]
