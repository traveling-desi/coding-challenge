outputFile = open("output", 'w')

for i in range(10):
	for j in range(10):
		s = "{\"created_time\": \"2016-04-07T03:33:21Z\", \"target\"" +  ": \"" + str(i) + "\", \"actor\" : \""+ str(j)+"\"}"
		#print s
		if not i == j:
       			outputFile.write(s)
       			outputFile.write("\n")
