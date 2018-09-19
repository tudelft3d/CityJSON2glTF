#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 19 12:09:16 2018

@author: kavisha
"""
import time
import sys
import argparse
import json
import os
import numpy as np

def flatten(x):
    result = []
    for el in x:
        if hasattr(el, "__iter__") and not isinstance(el, str):
            result.extend(flatten(el))
        else:
            result.append(el)
    return result 

def cityjson2gltf(inputFile,outputFile):
    
    fin = open(inputFile)
    data = fin.read()
    cj = json.loads(data)
    
    cm = {
          "asset" : {},
          "buffers": [],
          "bufferViews" : [],
          "accessors" : [],
          "meshes" : [],
          "nodes" : [],
          "scenes" : []
         }
    lBin = bytearray()  
    
    #asset
    asset = {}
    asset["copyright"] = "Open data"
    asset["generator"] = "Generated using CityJSON2glTF python utility"
    asset["version"]   = "2.0"
    cm["asset"]        =  asset
    
    #buffers and bufferViews
    head, tail = os.path.split(os.path.splitext(inputFile)[0])
    bufferbin = tail +"_bin.bin" 
    print ("Buffer (*.bin) file: ", bufferbin)
    binf = open(bufferbin, "wb") 
    
 
    #index bufferview
    bufferViewList = []
    meshList = []
    forimax = []
    poscount = 0
    indexcount = 0
    nodeList = []
    nodeCount = []
    accessorsList = []
    for theid in cj['CityObjects']:
#        print (theid)
        forimax2 = []
        poscount = poscount + 1
        for geom in cj['CityObjects'][theid]['geometry']:
#            print (geom)
            flatgeom = flatten(geom["boundaries"])
            forimax.append(flatgeom)
#            print ("\nCityJSON Indexes: ", geom["boundaries"])
#            print ("Flattened Indexes: ", flatgeom)
            flatgeom_np = np.array(flatgeom)
            bin_geom = flatgeom_np.astype(np.uint32).tostring()
#            print ("Binary Array: ",bin_geom)
            lBin.extend(bin_geom)
#            print (len(lBin))
            
            forimax2.append(flatgeom)
            bufferView = {}
            bufferView["buffer"] = 0
            bufferView["byteLength"] = len(bin_geom)
            bufferView["byteOffset"] = len(lBin) - len(bin_geom)
            bufferView["target"] = 34963
            bufferViewList.append(bufferView)        
         
            #meshes
            mesh = {}
            mesh["name"] = str(theid)
            mesh["primitives"] = [{"indices": indexcount}]
            meshList.append(mesh)
            
            node = {}
            node["mesh"] = indexcount
            node["name"] = str(theid)
            nodeList.append(node)
            
            nodeCount.append(indexcount)
            
            accessor = {}
            accessor["bufferView"] = indexcount
            accessor["byteOffset"] = 0
            accessor["componentType"] = 5125
            accessor["count"] = len(flatten(forimax2))
            accessor["type"] = "SCALAR"
            accessor["max"] = [ max(flatten(forimax2)) ]
            accessor["min"] = [ min(flatten(forimax2)) ]
            accessorsList.append(accessor)
            
            indexcount = indexcount + 1
  
    #scene
    scene = {}
    scene["nodes"] = nodeCount   
     
    ibin_length = len(lBin)
#    print (ibin_length)
    
    
    #vertex bufferview
    vertexlist = np.array(cj["vertices"])
    vertex_bin = vertexlist.astype(np.float32).tostring()
    lBin.extend(vertex_bin)
    vertexBuffer = {
      "buffer" : 0,
      "byteOffset" : ibin_length,
      "byteLength" : len(vertex_bin),
      "target" : 34962
    }
    bufferViewList.append(vertexBuffer)
    cm["bufferViews"] = bufferViewList
    
    for m in meshList:
#        print (m)
#        print (type(m["primitives"]))
#        print (m["primitives"][0])
#        print (type(m["primitives"][0]))
        m["primitives"][0]["attributes"] = {"POSITION":poscount}
    cm["meshes"] = meshList
    cm["nodes"] = nodeList
    cm["scenes"] = [scene]
    
    
    #accessors
    accessorsList.append({
      "bufferView" : len(bufferViewList) - 1,
      "byteOffset" : 0,
      "componentType" : 5126,
      "count" : len(cj["vertices"]),
      "type" : "VEC3",
      "max" : [np.amax(np.asarray(cj["vertices"]), axis=0)[0], np.amax(np.asarray(cj["vertices"]), axis=0)[1],np.amax(np.asarray(cj["vertices"]), axis=0)[2]], #max(cj["vertices"]),
      "min" : [np.amin(np.asarray(cj["vertices"]), axis=0)[0], np.amin(np.asarray(cj["vertices"]), axis=0)[1], np.amin(np.asarray(cj["vertices"]), axis=0)[2]] #min(cj["vertices"])
    })
    cm["accessors"] = accessorsList
    
    binf.write(lBin)
    binf.close()  
    
    #buffers
    buffer = {}
    buffer["uri"] = bufferbin
    buffer["byteLength"] = len(lBin)
    cm["buffers"] = [buffer]  
    
    #------ Output ------#
    json_str = json.dumps(cm, indent = 2,sort_keys=True)
    f = open(outputFile, "w")
    f.write(json_str)
    print ("Done!!")

#-------------start of program-------------------#

print ("\n****** CityJSON2glTF Converter *******\n")  
argparser = argparse.ArgumentParser(description='******* glTF Validator *******')
argparser.add_argument('-i', '--inputFilename', help='CityJSON dataset filename', required=False)
argparser.add_argument('-o', '--outputFilename', help='glTF dataset filename', required=False)
args = vars(argparser.parse_args())

inputFileName = args['inputFilename']
if inputFileName:
    inputFile = str(inputFileName)
    print ("CityJSON input file: ", inputFile)
else:
    print ("Error: Enter the CityJSON dataset!! ")
    sys.exit()

outputFileName = args['outputFilename']
if outputFileName:
    outputFile = str(outputFileName)
    print ("glTF output file: ", outputFile)
else:
    print ("Error: Enter the glTF filename!! ")
    sys.exit()
    
start = time.time()
cityjson2gltf(inputFile,outputFile)
end = time.time()
print ("\n Time taken for glTF validation: ",end - start, " sec")