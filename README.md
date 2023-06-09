# IO_Gaussian_Cube_file_blender
**Addon to import Gaussian Cube File, For Blender 2.9-3.5+ (written in Blender 3.5).**

_Written by René Meng for a 3 month internship about scientific visualisation with Matthieu Salanne at the Institute of Computing and Data Sciences(ISCD) at Sorbonne University._

(If OpenVDB is active this addon export VDB file to ./*_vdb_cache directory)
![image](https://github.com/ero646545/IO_Gaussian_Cube_file_blender/assets/30327029/fe48a18c-12d8-4a01-af41-56684837ff60)

To use Older versions of Blender you may need to disable OpenVDB as pyopenvdb if it isn't already.
If you run out of memory, OpenVDB volume may not display volume as desired. (i run on this issue with 4GB of ram)

Watch the French Tutorial: https://youtu.be/imFo62jpXp0
Main functionality:
  - Use the Built in pyopenvdb, numpy, os
  - ChatGPT wrote custom library to replace matplotlib.color for a color gradient, and ckdtree for nearest neighbour bonding.
  - Fully support Molecular Dynamics: 1 file per frame as vertex position (only if OpenVDB active)

How to Use it ?
File>import>Gaussian_Cube
It opens the File Browser

![image](https://github.com/ero646545/IO_Gaussian_Cube_file_blender/assets/30327029/0298d065-150c-4656-8ba5-caf3722f5185)

 
 - Create Bonding a custom kdtree: 0 is disabled points will be imported | 4 is four bonds with neighbours | 1,2,3 may not work as expected, keep trying
Number of bonding uses a custom tree to generate in average 4 bond per atom with the nearest neighbour.

4 bond:    

![image](https://github.com/ero646545/IO_Gaussian_Cube_file_blender/assets/30327029/7aea56fd-8e2c-4052-b7ab-87ad7266903f)

0 disable the tree function.

![image](https://github.com/ero646545/IO_Gaussian_Cube_file_blender/assets/30327029/74cca464-84d7-44c3-9a75-7b34cec07335)


  - A slider set The Green&crop throtle: If set to 0, There is no Green, full volume is displayed | If set to 0.1, Default Green and crop | If set to 1, You should see an empty object because you croped all the density
![image](https://github.com/ero646545/IO_Gaussian_Cube_file_blender/assets/30327029/b104e020-5fbf-4c82-9c22-8062ae3a83b6)



- Import with color in all 3 of blender Render Engine(EEVEE, WorkBench(solid mode), Cycle), faster if ColorValue disabled. 

Enabled workbench | Disabled Workbench | Disabled EEVEE and CYCLE

 ![image](https://github.com/ero646545/IO_Gaussian_Cube_file_blender/assets/30327029/1e68e089-6339-4b83-bb82-6c06b3c34746)                 ![image](https://github.com/ero646545/IO_Gaussian_Cube_file_blender/assets/30327029/7b5675a1-1002-4b89-8197-974db11475f0) ![image](https://github.com/ero646545/IO_Gaussian_Cube_file_blender/assets/30327029/7118ef2c-b867-497c-9b20-cdebdac537fc)

 
If enabled EEVEE and Cycle Color is set by material

![image](https://github.com/ero646545/IO_Gaussian_Cube_file_blender/assets/30327029/5e53f496-0c1b-4cfd-a570-7d132af55de0)

For workbench a hard coded coloramp sets the color in the OpenVDB grid, you can still choose between grids
![image](https://github.com/ero646545/IO_Gaussian_Cube_file_blender/assets/30327029/a63cc5dd-7649-4036-b832-905d80490a5c)

If disabled, only one color will be available, no material is created.



 - Support Importing Gaussian Cube file with Geometry nodes (No support for Molecular Dynamics or EEVEE, Only Monochrome color is supported for Workbench,)
  
![image](https://github.com/ero646545/IO_Gaussian_Cube_file_blender/assets/30327029/83618ca5-6b8a-461a-8e7c-acf149d28cdb)

Imported with geometry nodes(OpenVDB disabled)

![image](https://github.com/ero646545/IO_Gaussian_Cube_file_blender/assets/30327029/99b27902-2b5f-4dc4-ac3b-c5ed6f7392c1)

Imported with OpenVDB

![image](https://github.com/ero646545/IO_Gaussian_Cube_file_blender/assets/30327029/cc4ca408-5e2c-42be-b736-401df5db4357)



  - Uses OPENVDB, the read volume is exported to a cache file named *_vdb_cache, and then imported back into Blender. Its in ./*_vdb_cache directory where you can find all the VDB File and open it in other softwares.
  
![image](https://github.com/ero646545/IO_Gaussian_Cube_file_blender/assets/30327029/7e712ac0-48e7-4d79-9d13-07734be717c8)

You may need to delete cache Regularly by simply deleting the Cache directory, they contains the VDB File.


Open VDB support many parameters. You can mannualy change the density, or even make Slices.

![image](https://github.com/ero646545/IO_Gaussian_Cube_file_blender/assets/30327029/087b13f3-2d86-4555-84d9-c7f2989c774e)

Slices

![image](https://github.com/ero646545/IO_Gaussian_Cube_file_blender/assets/30327029/72aef26d-0d97-423c-ab4f-3aef9399b9e0)


A big thanks to Matthieu Salanne and the rich community of the ISCD.
