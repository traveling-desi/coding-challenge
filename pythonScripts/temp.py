import os
import re
from datetime import datetime
from dateutil.parser import parse
import numpy as np


#{"created_time": "2016-04-07T03:33:19Z", "target" : "Jamie-Korn, "actor" : "Jordan-Gruber"}





def addEdge():
	global vertex_name
	global max_vertex
	global current_latest
	#print each_line,
	matchObj = re.match(r'.*{.*"(.*)".*:.*"(.*)".*,.*"(.*)".*:.*"(.*)".*,.*"(.*)".*:.*"(.*)".*}', each_line, re.M|re.I)
	created_time = matchObj.group(2)
	target = matchObj.group(4)
	actor = matchObj.group(6)
	if not actor in vertex_name:
		vertex_name[actor] = max_vertex
		max_vertex = max_vertex + 1
	if not target in vertex_name:
		vertex_name[target] = max_vertex
		max_vertex = max_vertex + 1
	temp1 = parse(created_time)
	print current_latest
	if temp1 > current_latest:
		current_latest = temp1
	#print created_time, target, actor
	#print created_time
	#print '2016-03-29T06:04:49Z'
	#temp2 =  parse('2016-03-29T06:04:49Z')
	diff = current_latest - temp1
	diff_s = diff.total_seconds()
	print temp1
	print diff_s
	if diff_s > 60:
		print "Ignore"
	else:
		print "Use"
		src = vertex_name[actor]
		dest = vertex_name[target]
		if not src in edgeGraph:
			edgeGraph[src] = set()
			edgeGraph[src].add(dest)
		else:
			edgeGraph[src].add(dest)
		if not dest in edgeGraph:
			edgeGraph[dest] = set()
			edgeGraph[dest].add(src)
		else:
			edgeGraph[dest].add(src)
			
		
	
	
	

#{"created_time": "2016-03-29T06:04:49Z", "target": "Lizzie-Friend", "actor": "Travis-Norris"}



os.chdir('venmo_input')
input_pay = open('venmo-trans.txt')
os.chdir('../venmo_output')
output_deg = open('output.txt')

current_latest =  parse('1970-01-01T00:00:00Z')
vertex_name = dict()
edgeGraph = dict()
max_vertex = 0
for each_line in input_pay:
	degree = []
	addEdge()
	for key in edgeGraph:
		t = len(edgeGraph[key])
		print t
		degree.append(t)
	print degree
	median = np.median(degree)
	print "Median   = ",
	print median



for key in vertex_name.keys():
	print key, 
	print vertex_name[key]

for key in edgeGraph:
	print key
	print edgeGraph[key]
	#for k in edgeGraph[key]:
	#	print "K",
	#	print k


input_pay.close()
output_deg.close()
