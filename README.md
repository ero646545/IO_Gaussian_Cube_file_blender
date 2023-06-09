# IO_Gaussian_Cube_file_blender
Addon to import Gaussian Cube File, Only For Blender 2.9-3.5+ (written in Blender 3.5). 
(If OpenVDB is active this addon export VDB file to ./*_vdb_cache directory)
![image](https://github.com/ero646545/IO_Gaussian_Cube_file_blender/assets/30327029/fe48a18c-12d8-4a01-af41-56684837ff60)

To use Older versions of Blender you may need to disable OpenVDB as pyopenvdb if it isn't already.
If you run out of memory, OpenVDB volume may not display volume as desired. (i run on this issue with 4GB of ram)

Watch the French Tutorial: https://youtu.be/imFo62jpXp0

Main functionality:
  - Use the Built in pyopenvdb, numpy, os
  - ChatGPT wrote custom library to replace matplotlib.color for a color gradient, and ckdtree for nearest neighbour bonding.
  - Uses OPENVDB, the read volume is exported to a cache file named *_vdb_cache, and then imported back into Blender. Its in ./*_vdb_cache directory where you can find all the VDB File and open it in other softwares.
  - Import with color in all 3 of blender Render Engine(EEVEE, WorkBench(solid mode), Cycle), faster if ColorValue disabled. For EEVEE and Cycle Color is set by material, for workbench a coloramp sets the color.
  - Fully support Molecular Dynamics: 1 file per frame as vertex position (only if OpenVDB active)
  - Create Bonding a custom kdtree: 0 is disabled points will be imported | 4 is four bonds with neighbours | 1,2,3 may not work as expected, keep trying
  - Support Importing Gaussian Cube file with Geometry nodes (No support for Molecular Dynamics or EEVEE, Only Monochrome color is supported for Workbench,)
  - A slider set The Green&crop throtle: If set to 0, There is no Green, full volume is displayed | If set to 0.1, Default Green and crop | If set to 1, You should see an empty object because you croped all the density
  WARNING IF THIS SLIDER IS CHANGED, YOU NEED TO SAVE AND REOPEN BLENDER TO REIMPORT THE SAME FILE, OR BLENDER INTERNAL CACHE WILL JUST IMPORT THE SAME DENSITY AGAIN, hope this will be fixed soon.
 
