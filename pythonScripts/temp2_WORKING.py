import os
import re
from datetime import datetime
from dateutil.parser import parse
import numpy as np
import collections



### Procedure to map person's name to a number. 
def createVertex(actor, target):
	global vertexName
	global currMaxVertex
	if not actor in vertexName:
		vertexName[actor] = currMaxVertex
		currMaxVertex = currMaxVertex + 1
	if not target in vertexName:
		vertexName[target] = currMaxVertex
		currMaxVertex = currMaxVertex + 1

## Procedure to create tuple between actor and target. This represents an edge.
def createTuple(actor, target):
	global vertexName
	if vertexName[actor] > vertexName[target]:
		return(vertexName[target], vertexName[actor])
	else:
		return(vertexName[actor], vertexName[target])


## Pattern match and find the name of actor, target and create_time
def parseLine(eachLine):
	try:
		matchObj = re.match(r'.*{.*"(.*)".*:.*"(.*)".*,.*"(.*)".*:.*"(.*)".*,.*"(.*)".*:.*"(.*)".*}', eachLine, re.M|re.I)
		created_time = matchObj.group(2)
		target = matchObj.group(4)
		actor = matchObj.group(6)
		currTime = parse(created_time)
	except:
		print "Bad Input: " + eachLine
		raise ValueError('Bad input read! Offending line is above.')
	else:
		return target, actor, currTime

def evictEdge(timeDeltaSeconds):
	global timeIndex
	global sixtyWin
	sixtyWinBak = []
	for i in range(60):
		sixtyWinBak.append(set())
	for i in range(60):
		newIndex = i + timeDeltaSeconds
		if not newIndex > 59:
			sixtyWinBak[newIndex] = sixtyWin[i]
		else:
			if len(sixtyWin[i]) > 0:
				evictEdgeFromEdgeGraph(sixtyWin[i])
	#print sixtyWin
	#print sixtyWinBak
	sixtyWin = sixtyWinBak

def evictEdgeFromEdgeGraph(edgeRemovalList):
	#print edgeRemovalList
	#print "----"
	#print edgeGraph
	#print "----"
	for (src, dest) in edgeRemovalList:
		#print src, dest
		edgeGraph[src].remove(dest)
		edgeGraph[dest].remove(src)
		if len(edgeGraph[src]) == 0:
			del edgeGraph[src]
		if len(edgeGraph[dest]) == 0:
			del edgeGraph[dest]


def createEdge(timeDeltaSeconds, edgeTuple, src, dest, currTime):
	global sixtyWin
	global edgeGraph
	global timeIndex
	#print timeDeltaSeconds
	#print sixtyWin[timeDeltaSeconds]
	#print edgeTuple
	#print timeIndex
	#print sixtyWin
	if edgeTuple in timeIndex:
		#print timeIndex[edgeTuple]
		#print currTime
		if timeIndex[edgeTuple] < currTime:
			offsetToUpdate = int((currTime - timeIndex[edgeTuple]).total_seconds()) + timeDeltaSeconds
			#print offsetToUpdate
			if offsetToUpdate < 60:
				sixtyWin[offsetToUpdate].remove(edgeTuple)
	sixtyWin[timeDeltaSeconds].add(edgeTuple)
	timeIndex[edgeTuple] = currTime
		

	#print sixtyWin
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
	



def processNextPay(eachLine):
	global lastMaxTime
	#print eachLine,
	target, actor, currTime = parseLine(eachLine)
	createVertex(actor, target)
	edgeTuple = createTuple(actor, target)
	src = vertexName[actor]
	dest = vertexName[target]

	#print target
	#print actor
	#print currTime
	#print vertexName
	#print edgeTuple

	#print "NEXT"

	timeDelta = lastMaxTime - currTime
	timeDeltaSeconds = int(timeDelta.total_seconds())
	#print type(timeDeltaSeconds)
	#print lastMaxTime
	#print currTime
	#print timeDeltaSeconds
	if timeDeltaSeconds > 59:		### The current record is older than 59 seconds. Ignore
		#print "HERE 1"
		return
	elif timeDeltaSeconds > -1:		## The current record is within 60 second window but older than latest time payment looked at.
		#print "HERE 2"
		createEdge(timeDeltaSeconds, edgeTuple, src, dest, currTime)
	else:					## the current record is the latest time payment every looked at till now.
		#print "HERE 3"
		lastMaxTime = currTime
		evictEdge(-timeDeltaSeconds)
		createEdge(0, edgeTuple, src, dest, currTime)

	


def findMedianDegree():
	global edgeGraph
	degreeList = []
	for key in edgeGraph:
 		nodeDegree  = len(edgeGraph[key])
 		#print t
 		degreeList.append(nodeDegree)
 	#print degreeList
 	median = np.median(degreeList)
 	#print "Median   = ",
 	#print median
	return median
 
 


os.chdir('venmo_input')
inputPayFile = open('venmo-trans.txt')
os.chdir('../venmo_output')
outputDegFile = open('output.txt', 'w')

lastMaxTime =  parse('1970-01-01T00:00:00Z')
vertexName = dict()
edgeGraph = dict()
timeIndex = dict()
sixtyWin = []
for i in range(60):
	sixtyWin.append(set())
#print sixtyWin
currMaxVertex = 0
for eachLine in inputPayFile:
	processNextPay(eachLine)
	median = "%.2f" % findMedianDegree()
	outputDegFile.write('%s' % median)
	outputDegFile.write("\n")
	
## 
## for key in vertexName.keys():
## 	print key, 
## 	print vertexName[key]
## 
## for key in edgeGraph:
## 	print key
## 	print edgeGraph[key]
## 	#for k in edgeGraph[key]:
## 	#	print "K",
## 	#	print k


inputPayFile.close()
outputDegFile.close()
