# CityJSON2glTF
An experimental python utility to convert CityJSON datasets to glTF and schematically validate glTF datasets.

Things to know
---------------

### CityJSON 

[CityJSON](http://www.cityjson.org) is a format for encoding a subset of the CityGML data model using JSON (JavaScript Object Notation). It offers an alternative to the GML encoding of CityGML.

### glTF

A [glTF]( https://www.khronos.org/gltf/) asset is represented by a JSON based scene description file and a binary (.bin) file containing the geometry (vertices, indexes and/or animation data) of the asset.

System requirements
---------------------

Python packages:

+ [json](https://docs.python.org/3/library/json.html)
+ [jsonSchema](https://pypi.org/project/jsonschema/)
+ [numpy](http://docs.scipy.org/doc/numpy/user/install.html) (likely already on your system)
+ [argparse](https://docs.python.org/3/library/argparse.html)
+ [time](https://docs.python.org/3/library/time.html)

### OS and Python version
  
The software has been developed on Mac OSX in Python 3.7, and has not been tested with other configurations. Hence, it is possible that some of the functions will not work on Windows.

How to use?
-----------

### CityJSON2glTF
To convert CityGML data into COLLADA, use the following command:

```
python3 cityjson2gltf.py -i /path/to/CityJSONfile/ -o /path/to/new/glTFfile/
```

CityJSON requirements
---------------------

Mandatory:

+ LOD1 CityJSON files (works with LOD2 or higher too but does not thematically differentiate surfaces such as roofs, walls, etc.)
+ CityJSON version 0.7 or higher (We did not test files with version < 0.7)
+ Files must end with `.json`, or `.JSON`
+ Your files must be valid (see the next section)

Data validation
----------------

### CityJSON
[Hugo Ledoux](https://3d.bk.tudelft.nl/hledoux/) built [val3dity](http://geovalidation.bk.tudelft.nl/val3dity/), a thorough GML validator which is available for free through a web interface. 
It can also validate CityJSON files.
Use this tool to test your CityJSON files.

### glTF
To validate your glTF files against the schema (1.0 or 2.0) you can use our [Validator](https://github.com/kkimmy/CityJSON2glTF/glTF_schema_validator.py).

```
python3 glTF_schema_validator.py -i /path/to/COLLADAfile/ -schema /path/to/glTFschema/
```

Conditions for use
---------------------
This software is free to use. You are kindly asked to acknowledge its use by citing it in a research paper you are writing, reports, and/or other applicable materials.
Yo can cite this paper: 

```
Kumar, K., Ledoux, H., and Stoter, J.: Dynamic 3D visualization of floods: case of the Netherlands, Int. Arch. Photogramm. Remote Sens. Spatial Inf. Sci., XLII-4/W10, 83-87, https://doi.org/10.5194/isprs-archives-XLII-4-W10-83-2018, 2018.
```
