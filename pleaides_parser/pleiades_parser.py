# Pleiades Geo Data Generator
# Version 0.1
# Copyright 2017, Ryan Horne
# Released under GPLv3
#
# This is a quick script that takes a list of Pleiades IDs, then grabs geo information for each one, outputting the results in a csv file.
# The first parameter is your csv file, the second is the column name that has pleiades IDs
# Example: python pleaides_parser.py foo.csv bar
# Where foo.csv is your csv file and bar is your column
# This is intended for those who only wish to grab the lat / lon, title, count, and the pleiades ID - a more robust version with all the information as a json may be written later if there is demand 

import sys
reload(sys)
sys.setdefaultencoding('utf8')

#finish up the imports we need
import json
import csv
import urllib2

from collections import OrderedDict
from collections import Counter

#spinner from http://stackoverflow.com/questions/4995733/how-to-create-a-spinning-command-line-cursor-using-python/4995896
import time
import threading

class Spinner:
    busy = False
    delay = 0.05

    @staticmethod
    def spinning_cursor():
        while 1: 
            for cursor in '|/-\\': yield cursor

    def __init__(self, delay=None):
        self.spinner_generator = self.spinning_cursor()
        if delay and float(delay): self.delay = delay

    def spinner_task(self):
        while self.busy:
            sys.stdout.write(next(self.spinner_generator))
            sys.stdout.flush()
            time.sleep(self.delay)
            sys.stdout.write('\b')
            sys.stdout.flush()

    def start(self):
        self.busy = True
        threading.Thread(target=self.spinner_task).start()

    def stop(self):
        self.busy = False
        time.sleep(self.delay)

spinner = Spinner()

spinner.start()

#grab the pleiades_id column from the command prompt
idColumn = sys.argv[2]

#grab from the command prompt
csvFile = open(sys.argv[1])

#dictionary for the csv file
csvDict = {}

#for the desired Pleiades Data
plList = []

#holder for the Pleiades Ids
plHolder =[]

#keep track of any errors in a .csv log file. Will change format to something sensible later
errors = []

#url form
pleiadesURL = 'https://pleiades.stoa.org/places/'

#read in the csv
reader = csv.DictReader(csvFile, delimiter=',')

# ok, this may seem redundant. What we are going to do is make a list of Pleiades Ids and get unique ones
# After we get the unique ones, we will then make requests to the Pleiades server on the shorter list
# Then we will reiterate through our CSV file / list to make a new file that has the geo-data
# We are also going to add the Pleiades title as a column, because we need / want that info (for a node list, etc)

for row in reader:
	#the column that we specified holds pleiades IDs
	pleiadesIdReader = row[idColumn]
	#skip any blanks
	if pleiadesIdReader != '':
		plHolder.append(pleiadesIdReader)
pleiadesCounter = Counter (plHolder)

for pid,value in pleiadesCounter.items():
	#remove the newline and whitespace from our csv list if present
	#also skip anything that has character data (junk) in the field. This is more common than you may think
	if pid.rstrip().isdigit() == True:
		try:
			dataUrl = ('%s%s/json' % (pleiadesURL, pid.rstrip()))
			#grab the data
			pleiadesData = json.load(urllib2.urlopen(dataUrl))
			tempList =OrderedDict()
			tempList['id'] = pleiadesData['id']
			tempList['title'] = pleiadesData['title']
			tempList['repLon'] =  pleiadesData['reprPoint'][0]
			tempList['repLat'] =  pleiadesData['reprPoint'][1]
			tempList['count'] = value
			plList.append(tempList)
			
		except:
			pass

#output file name
outputFileName = "%s[georectified].csv" % (sys.argv[1].split(".")[0])

#now output the file
with open(outputFileName, 'w') as outputCSVFile:
	keys = plList[0].keys()
	dict_writer = csv.DictWriter(outputCSVFile, keys)
	dict_writer.writeheader()
	dict_writer.writerows(plList)

#stop the spinning
spinner.stop()
