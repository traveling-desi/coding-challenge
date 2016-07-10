
### Import all the relevant packages here. We are using methods from these packages.

import os
import sys
from datetime import datetime
from dateutil.parser import parse
import numpy as np
import json


### Some top level variables defined. 
### Edge is defined as actor <-> target. We break up this non-directional edge as  actor -> target and target -> actor. This is then saved in the edgeGraph. This helps us find
### degree of the nodes very fast, which is basically the length of the list for each key in edgeGraph
### We also save edge as a non directional edge in edgeTuple

lastMaxTime =  parse('1970-01-01T00:00:00Z')	## This is just dummy intiliaziation to overcome cold start problem. At the the beginning the latest time seen in 1970.
currVertexNumber = 0			## This is the current vertex number being assigned to a new name. Vertex numbers start from 0
vertexNameMap = dict()			## This is the dictionary to map the names of the actor/target to vertex numbers. Vertex numbers start from 0.
edgeGraph = dict()			## This is the graph that
timeIndex = dict()			## This is a dictionary that keeps the latest time that an edge was created. If an edge
sixtySecWin = []			## This is a list that is 60 slots long. Each slot represents one second and is a pointer to a set of the edges created in that second. 
for i in range(60):
	sixtySecWin.append(set())


### Procedure to map person's name to a vertex number. Numbers are easier to manipulate and 
### ASSUMPTION: All persons have unique names (i.e there are no two people with same names). This is a reasonable assumption.
### How else is venmo going to know who is who?
def createVertexNameMap(actor, target, vertexNameMap):
	global currVertexNumber
	if not actor in vertexNameMap:
		vertexNameMap[actor] = currVertexNumber
		currVertexNumber = currVertexNumber + 1
	if not target in vertexNameMap:
		vertexNameMap[target] = currVertexNumber
		currVertexNumber = currVertexNumber + 1


## Procedure to create tuple between actor and target (actually their vertex numbers.) This represents an edge. 
## Tuples have the format (smaller vertex number, larger vertex number)
def createTuple(actor, target, vertexNameMap):
	if vertexNameMap[actor] > vertexNameMap[target]:
		return(vertexNameMap[target], vertexNameMap[actor])
	else:
		return(vertexNameMap[actor], vertexNameMap[target])


## Read Json line and find the name of actor, target and create_time
def parseLine(eachLine):
	try:
	        data = json.loads(eachLine)
        	created_time = data["created_time"]
        	target = data["target"]
        	actor = data["actor"]
		currTime = parse(created_time)
	except:
		print "Bad Input: " + eachLine
		raise ValueError('Bad input read! Offending line is above.')
	else:
		return target, actor, currTime


def evictEdgeSixtyWin(timeDeltaSeconds, timeIndex, sixtySecWin, edgeGraph):
	sixtySecWinBak = []
	for i in range(60):
		sixtySecWinBak.append(set())
	for i in range(60):
		newIndex = i + timeDeltaSeconds
		if not newIndex > 59:
			sixtySecWinBak[newIndex] = sixtySecWin[i]
		else:
			if len(sixtySecWin[i]) > 0:
				evictEdgeFromEdgeGraph(sixtySecWin[i], edgeGraph)
				evictEdgeFromTimeIndex(sixtySecWin[i], timeIndex)
		sixtySecWin[i] = sixtySecWinBak[i]

def evictEdgeFromTimeIndex(edgeRemovalList, timeIndex):
        for edge in edgeRemovalList:
                del timeIndex[edge]
	

def evictEdgeFromEdgeGraph(edgeRemovalList, edgeGraph):
	for (src, dest) in edgeRemovalList:
		edgeGraph[src].remove(dest)
		edgeGraph[dest].remove(src)
		if len(edgeGraph[src]) == 0:
			del edgeGraph[src]
		if len(edgeGraph[dest]) == 0:
			del edgeGraph[dest]


def createEdge(timeDeltaSeconds, edgeTuple, src, dest, currTime):
	global sixtySecWin
	global edgeGraph
	global timeIndex
	if edgeTuple in timeIndex:
		if timeIndex[edgeTuple] < currTime:
			offsetToUpdate = int((currTime - timeIndex[edgeTuple]).total_seconds()) + timeDeltaSeconds
			if offsetToUpdate < 60:
				sixtySecWin[offsetToUpdate].remove(edgeTuple)
	sixtySecWin[timeDeltaSeconds].add(edgeTuple)
	timeIndex[edgeTuple] = currTime

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
	



def processNextPay(eachLine, vertexNameMap, timeIndex, sixtySecWin, edgeGraph):
	global lastMaxTime
	target, actor, currTime = parseLine(eachLine)
	createVertexNameMap(actor, target, vertexNameMap)
	edgeTuple = createTuple(actor, target, vertexNameMap)
	src = vertexNameMap[actor]
	dest = vertexNameMap[target]

	timeDelta = lastMaxTime - currTime
	timeDeltaSeconds = int(timeDelta.total_seconds())
	if timeDeltaSeconds > 59:		### The current record is older than 59 seconds. Ignore
		return
	elif timeDeltaSeconds > -1:		## The current record is within 60 second window but older than latest time payment looked at.
		createEdge(timeDeltaSeconds, edgeTuple, src, dest, currTime)
	else:					## the current record is the latest time payment every looked at till now.
		lastMaxTime = currTime
		evictEdgeSixtyWin(-timeDeltaSeconds, timeIndex, sixtySecWin, edgeGraph)
		createEdge(0, edgeTuple, src, dest, currTime)

	


def findMedianDegree(edgeGraph):
	degreeList = []
	for key in edgeGraph:
 		nodeDegree  = len(edgeGraph[key])
 		degreeList.append(nodeDegree)
 	median = np.median(degreeList)
	return median
 
 
def openFile(inFile, outFile):
	try:
		inputPayFile = open(inFile)
		outputDegFile = open(outFile, 'w')
	except IOError:
		print "ERROR: Couldnt open one of the required files is missing. Please check premissions"
	else:
		return inputPayFile, outputDegFile

def closeFile(inputPayFile, outputDegFile):
	inputPayFile.close()
	outputDegFile.close()


### Main (Top level) program starts here
if len(sys.argv) < 3:
	print "Command line to run:",
	print "python ./src/rolling_median.py ./venmo_input/venmo-trans.txt ./venmo_output/output.txt"
	raise IOError('Not enough arguments given')
	exit()

inputPayFile, outputDegFile = openFile(sys.argv[1], sys.argv[2])
for eachLine in inputPayFile:
	processNextPay(eachLine, vertexNameMap, timeIndex, sixtySecWin, edgeGraph)
	median = "%.2f" % findMedianDegree(edgeGraph)
	outputDegFile.write('%s' % median)
	outputDegFile.write("\n")
closeFile(inputPayFile, outputDegFile)	
