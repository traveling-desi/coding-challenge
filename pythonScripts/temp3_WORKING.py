
### Import all the relevant packages here. We are using methods from these packages.

import os
import sys
from datetime import datetime
from dateutil.parser import parse
import numpy as np
import json


### Some top level variables defined. 
lastMaxTime =  parse('1970-01-01T00:00:00Z')
currMaxVertex = 0
vertexName = dict()
edgeGraph = dict()
timeIndex = dict()
sixtyWin = []
for i in range(60):
	sixtyWin.append(set())


### Procedure to map person's name to a number. 
def createVertex(actor, target, vertexName):
	#global vertexName
	global currMaxVertex
	if not actor in vertexName:
		vertexName[actor] = currMaxVertex
		currMaxVertex = currMaxVertex + 1
	if not target in vertexName:
		vertexName[target] = currMaxVertex
		currMaxVertex = currMaxVertex + 1

## Procedure to create tuple between actor and target. This represents an edge.
def createTuple(actor, target, vertexName):
	#global vertexName
	if vertexName[actor] > vertexName[target]:
		return(vertexName[target], vertexName[actor])
	else:
		return(vertexName[actor], vertexName[target])


## Pattern match and find the name of actor, target and create_time
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
	



def processNextPay(eachLine, vertexName):
	global lastMaxTime
	#print eachLine,
	target, actor, currTime = parseLine(eachLine)
	createVertex(actor, target, vertexName)
	edgeTuple = createTuple(actor, target, vertexName)
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
 
 
def openFile(inFile, outFile):
	inputPayFile = open(inFile)
	outputDegFile = open(outFile, 'w')
	return inputPayFile, outputDegFile

def closeFile():
	inputPayFile.close()
	outputDegFile.close()

if len(sys.argv) < 3:
	print "Command line to run:",
	print "python ./src/rolling_median.py ./venmo_input/venmo-trans.txt ./venmo_output/output.txt"
	raise IOError('Not enough arguments given')
	exit()

inputPayFile, outputDegFile = openFile(sys.argv[1], sys.argv[2])

#print sys.argv[0]
#print sys.argv[1]
#print sys.argv[2]

#print sixtyWin
for eachLine in inputPayFile:
	processNextPay(eachLine, vertexName)
	median = "%.2f" % findMedianDegree()
	outputDegFile.write('%s' % median)
	outputDegFile.write("\n")
closeFile()	

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

