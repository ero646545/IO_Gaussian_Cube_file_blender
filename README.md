# IO_Gaussian_Cube_file_blender
Addon to import Gaussian Cube File, Only For Blender 3.5+ (written in Blender 3.5)
![image](https://github.com/ero646545/IO_Gaussian_Cube_file_blender/assets/30327029/fe48a18c-12d8-4a01-af41-56684837ff60)

To use Older versions of Blender you need to disable OpenVDB and Kdtree_Bonding as  pyopenvdb, scipy, matplotlib aren't available.

Main functionality:
  - Use the Built in pyopenvdb, scipy, matplotlib, numpy, os
  - Import with color in all 3 of blender Render Engine(EEVEE, WorkBench(solid mode), Cycle), faster if ColorValue disabled. For EEVEE and Cycle Color is set by material, for workbench a coloramp sets the color.
  - Fully support Molecular Dynamics (1 file per frame and OpenVDB active only)
  - Create Bonding With KdTree: 0 is disabled points will be imported | 4 is four bonds with neighboor | 123 may not work as expected, keep trying
  - Support Import .cube file with Geometry nodes (but it does not support Molecular Dynamics, and EEVEE, Only Monochrome color for Workbench)
  - A slider set The Green&crop throtle: If set to 0, There is no Green, full volume is displayed | If set to 0.1, Default Green and crop | If set to 1, You should see an empty object because you croped all the density
  WARNING IF THIS SLIDER IS CHANGED, YOU NEED TO SAVE AND REOPEN BLENDER TO REIMPORT THE SAME FILE, OR BLENDER INTERNAL CACHE WILL JUST IMPORT THE SAME DENSITY AGAIN, hope this will be fixed soon.
