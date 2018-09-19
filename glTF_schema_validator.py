#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 19 11:50:04 2018

@author: kavisha
"""

#validate glTF

import json
import jsonschema
import time
import argparse
import sys

def glTFvalidate(inputFile,schemaFolder):
    fInput = open(inputFile)
    inputData = fInput.read()
    j = json.loads(inputData)
    
    fSchema = open(schemaFolder+ "glTF.schema.json")
    inputSchema = fSchema.read()
    js = json.loads(inputSchema)
    
    resolver = jsonschema.RefResolver('file://' + schemaFolder, inputSchema)
    print 
    try:
        jsonschema.validate(j,js, resolver=resolver)
        print("Passed derived schema.")
    except Exception as ex:
        print("Failed derived schema: %s" % ex)


#-------------start of program-------------------#

print ("\n****** glTF Validator *******\n")  
argparser = argparse.ArgumentParser(description='******* glTF Validator *******')
argparser.add_argument('-i', '--inputFilename', help='glTF dataset filename', required=False)
argparser.add_argument('-schema', '--schemaFolderLocation', help='glTF schema folder (1.0/2.0)', required=False)
args = vars(argparser.parse_args())

inputFileName = args['inputFilename']
if inputFileName:
    inputFile = str(inputFileName)
    print ("CityGML input file: ", inputFile)
else:
    print ("Error: Enter the glTF dataset!! ")
    sys.exit()

schemaFolderLocation = args['schemaFolderLocation']
if schemaFolderLocation:
    schemaFolder = str(schemaFolderLocation)
    print ("glTF schema location: ", schemaFolder)
else:
    print ("Error: Enter the glTF schema folder location!! ")
    sys.exit()
    
start = time.time()
glTFvalidate(inputFile,schemaFolder)
end = time.time()
print ("\n Time taken for glTF validation: ",end - start, " sec")
