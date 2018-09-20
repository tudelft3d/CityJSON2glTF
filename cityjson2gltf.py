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
import math
 
try:
    import mapbox_earcut
except ModuleNotFoundError as e:
    raise e
    
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
          "materials": [],
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
    matid = 0
    materialIDs = []
    
    vertexlist = np.array(cj["vertices"])
     
    for theid in cj['CityObjects']:
        forimax2 = []
        poscount = poscount + 1
        
        comType = cj['CityObjects'][theid]['type']
        if (comType == "Building" or comType == "BuildingPart" or comType == "BuildingInstallation"):
            matid = 0
        elif (comType == "TINRelief"):
            matid = 1
        elif (comType == "Road" or comType == "Railway" or comType == "TransportSquare"):
            matid = 2
        elif (comType == "WaterBody"):
            matid = 3
        elif (comType == "PlantCover" or comType == "SolitaryVegetationObject"):
            matid = 4
        elif (comType == "LandUse"):
            matid = 5
        elif (comType == "CityFurniture"):
            matid = 6
        elif (comType == "Bridge" or comType == "BridgePart" or comType == "BridgeInstallation" or comType == "BridgeConstructionElement"):
            matid = 7
        elif (comType == "Tunnel" or comType == "TunnelPart" or comType == "TunnelInstallation"):
            matid = 8
        elif (comType == "GenericCityObject"):
            matid = 9
        materialIDs.append(matid)

        for geom in cj['CityObjects'][theid]['geometry']:
#            print (geom)
            flatgeom = flatten(geom["boundaries"])
            forimax.append(flatgeom)
            flatgeom_np = np.array(flatgeom)
            bin_geom = flatgeom_np.astype(np.uint32).tostring()

            lBin.extend(bin_geom)
            
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
            mesh["primitives"] = [{"indices": indexcount, "material": matid}]
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
    
    #vertex bufferview
   
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
    
    #materials
    materialsList = [
            {  #building red
              "pbrMetallicRoughness": {
                 "baseColorFactor":[ 1.000, 0.000, 0.000, 1.0 ],
                 "metallicFactor": 0.5,
                 "roughnessFactor": 1.0
               }
            },
            {   # terrain brown
              "pbrMetallicRoughness": {
                 "baseColorFactor":[ 0.588, 0.403, 0.211, 1.0 ],
                 "metallicFactor": 0.5,
                 "roughnessFactor": 1.0
               }
            },
            {  # transport grey
              "pbrMetallicRoughness": {
                 "baseColorFactor":[ 0.631, 0.607, 0.592, 1.0 ],
                 "metallicFactor": 0.5,
                 "roughnessFactor": 1.0
               }
            },
            { # waterbody blue
              "pbrMetallicRoughness": {
                 "baseColorFactor":[ 0.070, 0.949, 0.972, 1.0 ],
                 "metallicFactor": 0.5,
                 "roughnessFactor": 1.0
               }
            },
            { # vegetation green
              "pbrMetallicRoughness": {
                 "baseColorFactor":[ 0.000, 1.000, 0.000, 1.0 ],
                 "metallicFactor": 0.5,
                 "roughnessFactor": 1.0
               }
            },
            {  # landuse yellow
              "pbrMetallicRoughness": {
                 "baseColorFactor":[ 0.909, 0.945, 0.196, 1.0 ],
                 "metallicFactor": 0.5,
                 "roughnessFactor": 1.0
               }
            },
            {  # CityFurniture orange
              "pbrMetallicRoughness": {
                 "baseColorFactor":[ 0.894, 0.494, 0.145, 1.0 ],
                 "metallicFactor": 0.5,
                 "roughnessFactor": 1.0
               }
            },
            { # bridge purple
              "pbrMetallicRoughness": {
                 "baseColorFactor":[ 0.466, 0.094, 0.905, 1.0 ],
                 "metallicFactor": 0.5,
                 "roughnessFactor": 1.0
               }
            },
            { # tunnel black
              "pbrMetallicRoughness": {
                 "baseColorFactor":[ 0.011, 0.011, 0.007, 1.0 ],
                 "metallicFactor": 0.5,
                 "roughnessFactor": 1.0
               }
            },
            { # GenericCityObject pink
              "pbrMetallicRoughness": {
                 "baseColorFactor":[ 0.909, 0.188, 0.827, 1.0 ],
                 "metallicFactor": 0.5,
                 "roughnessFactor": 1.0
               }
            }
              
    ]
              
    cm["materials"] = materialsList
    
    #------ Output ------#
    json_str = json.dumps(cm, indent = 2,sort_keys=True)
    f = open(outputFile, "w")
    f.write(json_str)
    print ("Done!!")

#-------------start of program-------------------#

print ("\n****** CityJSON2glTF Converter *******\n")  
argparser = argparse.ArgumentParser(description='******* CityJSON2glTF Converter *******')
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
print ("\n Time taken for glTF generation: ",end - start, " sec")