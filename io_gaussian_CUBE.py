bl_info = {
    "name": ".CUBE Import ",
    "description": "Import Gaussian Volumetrics Cube File",
    "author": "René Meng - ISCD",
    "version": (1, 0, 0),
    "blender": (3, 5, 0),
    "location": "File -> Import -> CUBE (.cube)",
    "warning": "",
    "doc_url": "https://iscd.sorbonne-universite.fr/",
    "category": "Import-Export",
}
import bpy
import numpy as np
import os

from bpy.props import (
        StringProperty,
        BoolProperty,
        EnumProperty,
        IntProperty,
        FloatProperty,
        ) 
blendervdb=True#version3.5+        
blenderscipy=True #Lets suppose scipy/matplotlib is installed
blendermatplotlib=True
try:
    import pyopenvdb as openvdb
except ImportError:
    blendervdb=False
    
   
try:#handle the scipy error
    from scipy.spatial import cKDTree
    import matplotlib.colors as mcolors
    
    
except ImportError:
    print("Scipy and matplotlib are not installed. Installing Scipy and matplotlib with PIP...")
    import sys
    from pathlib import Path
    import subprocess
    py_exec = str(sys.executable)
    lib = Path(py_exec).parent.parent / "lib"
    # Ensure pip is installed
    subprocess.call([py_exec, "-m", "ensurepip", "--user"])
    # Install packages
    subprocess.call([py_exec, "-m", "pip", "install", f"--target={str(lib)}", "matplotlib"])
    subprocess.call([py_exec, "-m", "pip", "install", f"--target={str(lib)}", "scipy"])
    
    try:#Verify if installation worked
        from scipy.spatial import cKDTree
        import matplotlib.colors as mcolors  
          
    except  ImportError:
        # Display an error message
        msg = "Could not install scipy and matplotlib, try opening Blender with admin privilege, or installing mannualy..."
        print(msg)
        blenderscipy=False
  
# create addon parameter interface
class CUBEImportPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__
    def draw(self, context):
        layout = self.layout
        # Display an error message
        if not blenderscipy:
            layout.label(text="Could not install scipy and matplotlib.",icon='ERROR')
            layout.label(text="Try opening Blender with admin privilege.")  
        if not blendervdb:
            layout.label(text="Could not find pyopenvdb.",icon='ERROR')
            layout.label(text="Try using Blender 3.5+")
#Cube importer addon that uses file browser
class CUBEImportOperator(bpy.types.Operator):
    bl_idname = "import_scene.cube"
    bl_label = "Import .cube File"
    bl_description = "Import Gaussian Volumetrics Cube File"
    bl_options = {'REGISTER'}
    files: bpy.props.CollectionProperty(
        type=bpy.types.OperatorFileListElement
    )
    filter_glob: StringProperty( 
        default="*.cube;*.cub;.CUBE;*.CUB"
    )
    int_bond : IntProperty(
               name="Number of bonding",
               default=4*int(blenderscipy),# deactivate 
               min=0,
               max=10,
               description="Use cKDtree library to generate bonds with the nearest neighbour. Its an average bonding number that you can set below need scipy already installed. For tetravalent atoms bonding value is 4. Default Value is 0 Bonding is disabled.",
               )
    bool_color : BoolProperty(
               name="Color Value",
               default=True,
               description="I want to color Positive value to Red and Negative value in Blue")
    bool_vdb : BoolProperty(
               name="Open VDB",
               default=blendervdb,
               description="Use OpenVDB to display volume, this method is faster and better but allows less tweaking. This create 2 positive and negative VDB file in the local directory. Uncheck only if OpenVDB is unsupported")
    float_thresholds : FloatProperty(
               name="Define the solid mode relative thresholds (default 0)",
               default=0.01,
               min=0,
               max=1,
               description="Value from which the volume is transparent , need to save setting delete the vdb file and Restart Blender to apply changes(yes its tricky)",
               )
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    
    def draw(self, context):# disposal of the buttons
        layout = self.layout
        if not blenderscipy:
            layout.label(text="Could not install scipy and matplotlib.",icon='ERROR')
            layout.label(text="Try opening Blender with Admin privilege.")
            layout.label(text="")  
        if not blendervdb:# just to inform that Not using OpenVDB is not optimal
            layout.label(text="Could not find pyopenvdb.",icon='ERROR')
            layout.label(text="Try using Blender 3.5+")    
            layout.label(text="")  
            
        layout.label(text="Number of bond per atom. A 0 value is disabled")
        layout.prop(self, "int_bond")
        layout.label(text="I want more colours!(slower if checked)")
        layout.prop(self, "bool_color")
        layout.label(text="Use OpenVDB (only on blender 3.5+)")
        layout.prop(self, "bool_vdb")
        layout.label(text="Solid mode transparent thresholds (default 0, need reload addon or restart)")
        layout.prop(self, "float_thresholds")    
    
    
    #cube importer code
    def execute(self, context):
        preferences = self
        def create_vdb(name, matname,dataf,framek):
            if dataf.size==0:#don't try to import empty things
                return       
            # Create an OpenVDB volume from the pixel data
            grid = openvdb.FloatGrid()
            
            # Copies image volume from numpy to VDB grid
            grid.copyFromArray(dataf)
            
            # Blender needs grid name to be "density" or "velocity" to be colorful (need data to be Vector Float)
            grid.name = 'density'
            if not blenderscipy==False:# handle the case where open vdb is active but not scipy/matplotlib
                
                # Convert data to vector array with color coding
                # This version of the code is optimised by chat gpt
                seuil=preferences.float_thresholds*np.max(dataf)#Thresholds Relative to maximum
                vector_data = np.zeros(dataf.shape + (3,))
                positive_values = np.where(dataf > seuil)
                negative_values = np.where(dataf > seuil)
                zero_values = np.where(dataf <= seuil)
                if matname != "negative":
                    colorval = dataf[positive_values]
                    if colorval.size > 0:
                        min_value = np.min(colorval)
                        max_value = np.max(colorval)
                        if min_value != max_value:  # Check if the minimum and maximum values are not equal
                            normalized_colorval = (colorval - min_value) / (max_value - min_value)  # Normalize color values between 0 and 1
                            gradient = mcolors.LinearSegmentedColormap.from_list('color_gradient', [(0, 6 * seuil, 0), (1.5, 0, 0)])  # Define your gradient colors
                            vector_data[positive_values] = gradient(normalized_colorval)[:, :3]  # Apply gradient colors RGB to vector_data
                    else:
                        return
                else:
                    colorval = dataf[negative_values]
                    if colorval.size > 0:
                        min_value = np.min(colorval)
                        max_value = np.max(colorval)
                        if min_value != max_value:  # Check if the minimum and maximum values are not equal
                            normalized_colorval = (colorval - min_value) / (max_value - min_value)  # Normalize color values between 0 and 1
                            gradient = mcolors.LinearSegmentedColormap.from_list('color_gradient', [(0, 2 * seuil, 0), (0, 0, 6)])  # Define your gradient colors
                            vector_data[negative_values] = gradient(normalized_colorval)[:, :3]  # Apply gradient colors RGB to vector_data
                    else:
                        return
                # Assign zeros for zero_values
                vector_data[zero_values] = np.zeros((3,))
     
                # Create a Blender-compatible VDB grid
                vdb_grid = openvdb.Vec3SGrid()
                vdb_grid.copyFromArray(np.array(vector_data).reshape(dataf.shape + (3,)))

                # Set the grid name to "velocity" for color display
                vdb_grid.name='color_density'
                
            
            # Create a directory for the VDB cache
            cache_dir = self.filepath + '_vdb_cache'
            suffix = ''
            
            if not os.path.exists(cache_dir):
                os.mkdir(cache_dir)
            else:
                # Handle file conflicts by adding a suffix to the file name
                suffix = 1/1000
                while os.path.exists(cache_dir + "\\" + os.path.basename(self.filepath) + matname +'_' +str(framek) +str(suffix)[1:] + ".vdb"):
                   suffix += 1/1000
            
            # Define the file path for the VDB file
            vdbfile = os.path.join(cache_dir, os.path.basename(self.filepath) + matname +'_'+ str(int(framek)).zfill(len(str(len(self.files)))) + '.vdb')
            
            # Writes CT volume to a VDB file
            if not blenderscipy==False:# handle again the case where open vdb is active but not scipy/matplotlib
                openvdb.write(vdbfile, [grid,vdb_grid]) #color and monochrome 
            else:
                openvdb.write(vdbfile, [grid])
                
            
            if matname=="negative":#if negative put to negative list
                negfile.append(vdbfile)
            else:
                posfile.append(vdbfile)
               
            if framek  == len(self.files)-1:# last framek
                if matname=="negative":
                    ##import negative vdb 
                    # Add the volume to the scene
                    bpy.ops.object.volume_import(filepath=negfile[0], files=[{'name': f} for f in negfile])
                    obj=bpy.context.object.data
                    if framek!=0:
                        obj.is_sequence = True
                    obj.frame_duration = framek
                    obj.frame_start = 0
                    obj.sequence_mode = 'EXTEND'

                    bpy.context.object.scale = (x1, y1, z1)
                    
                    # Create the material
                    create_mat(matname)
                else:
                    ##import positive vdb 
                    # Set the cursor to the center
                    bpy.data.scenes[-1].cursor.location[:3] = 0, 0, 0
                   
                    # Add the volume to the scene
                    bpy.ops.object.volume_import(filepath=posfile[framek], files=[{'name': f} for f in posfile])
                    obj=bpy.context.object.data
                    if framek!=0:
                        obj.is_sequence = True
                    obj.frame_duration = framek 
                    obj.frame_start = 0
                    obj.sequence_mode = 'EXTEND'
                    bpy.context.object.scale = (x1, y1, z1)
                    # Create the material
                    create_mat(matname)
                
                
            return

        
        def create_obj_node(name,matname):
            # this function takes in the name anc create an object and set as active object
            # Create the mesh object and add the vertices to it
            mesh = bpy.data.meshes.new("density_mesh")
            mesh.from_pydata(vertices, [], [])
            
            # Create a mesh object and link it to the scene
            obj = bpy.data.objects.new(name, mesh)
            bpy.context.scene.collection.objects.link(obj)
            obj.scale=(x1,y1,z1)# set the right scale
            # Get a reference to the object you want to select
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            # this function takes in the name anc create an object
            #Create a Geometry node modifier 
            obj = bpy.context.active_object
            gn_nodes = obj.modifiers.new(name="Geometry Nodes", type="NODES")
            #create a node group
            gn_tree = bpy.data.node_groups.new("superdrawcloud", "GeometryNodeTree")
            #set the modifier to the node group
            gn_nodes.node_group = gn_tree
            #Create nodes and place them and set their default value
            gn_inputs = gn_tree.nodes.new(type="NodeGroupInput")
            
            gn_outputs = gn_tree.nodes.new(type="NodeGroupOutput")
            gn_outputs.location = (200, 0)
            gn_inputs.location = (-600, 0)
            # Create the nodes for the points to volume operation
            gn_volume = gn_tree.nodes.new(type="GeometryNodePointsToVolume")
            gn_volume.location = (-200, 0)
            
            #parameter Point to volume node
            gn_volume.resolution_mode = 'VOXEL_SIZE'
            gn_volume.inputs[2].default_value=.5
            
            # Create a new Math node to multiply the density attribute
            add_node = gn_tree.nodes.new(type="ShaderNodeMath")
            add_node.operation = "ADD"
            add_node.location = (-400, 0)
            seuil=preferences.float_thresholds
            add_node.inputs[1].default_value = .40+seuil
            gn_mat = gn_tree.nodes.new(type="GeometryNodeSetMaterial")
            #set material
           
            gn_mat.inputs[2].default_value =  create_mat(matname)# Create material
            
            # Get the active node tree, the folowing line is to bypass a blender python API impass
            #select the area
            bpy.context.space_data.node_tree = node_tree
            
            
            # Create inputs output socket
            bpy.ops.node.tree_socket_add(in_out='IN')
            bpy.ops.node.tree_socket_change_type(in_out='IN', socket_type='NodeSocketGeometry')
            bpy.ops.node.tree_socket_add(in_out='IN')
            bpy.ops.node.tree_socket_change_type(in_out='IN', socket_type='NodeSocketFloat')
            bpy.ops.node.tree_socket_add(in_out='OUT')
            bpy.ops.node.tree_socket_change_type(in_out='OUT', socket_type='NodeSocketGeometry')
            #name
            gn_outputs.inputs[0].name = "Geometry"
            gn_inputs.outputs[0].name = "Points"
            gn_inputs.outputs[1].name = "Radius"
            
            #active the uses of spreadsheet
            bpy.ops.object.geometry_nodes_input_attribute_toggle(prop_path="[\"Input_1_use_attribute\"]", modifier_name="Geometry Nodes")
            #set input attribute
            obj.modifiers["Geometry Nodes"]["Input_1_attribute_name"]='density'
            # Link the nodes together
            gn_tree.links.new(gn_inputs.outputs[0], gn_volume.inputs[0])
            gn_tree.links.new(gn_inputs.outputs[1], add_node.inputs[0])
            gn_tree.links.new(add_node.outputs[0], gn_volume.inputs[4])
            gn_tree.links.new(gn_volume.outputs[0], gn_mat.inputs[0])
            gn_tree.links.new(gn_mat.outputs[0], gn_outputs.inputs[0])
            if matname=="negative": # solve a display bug to avoid interlacing 
                obj.delta_location=(x1/nx*.1,y1/ny*.1,z1/nz*.1)
            return  
        
        def create_mat(matname):
            #This functions create a preset material for solidmode and shader for eevee and cycle
            if matname=='nomat':
                return
            # Create a new material
            mat = bpy.data.materials.new(matname)
            mat.use_nodes = True

            # Get a reference to the material node tree
            tree = mat.node_tree

            # Clear existing nodes
            for node in tree.nodes:
                tree.nodes.remove(node)

            # Create nodes
            attr_node = tree.nodes.new(type="ShaderNodeAttribute")
            attr_node.attribute_name = 'density'
            multiply_node = tree.nodes.new(type="ShaderNodeMath")
            multiply_node.operation = "MULTIPLY"
            multiply_node.location = (200, 0)
            ramp_node = tree.nodes.new(type="ShaderNodeValToRGB")
            ramp_node.location = (400, 0)
            principled_node = tree.nodes.new(type="ShaderNodeVolumePrincipled")
            principled_node.location = (700, 0)
            output_node = tree.nodes.new(type="ShaderNodeOutputMaterial")
            output_node.location = (1000, 0)

            # Set values on nodes
            multiply_node.inputs[1].default_value = 1
            ramp_node.color_ramp.elements[0].color = (0, 1, 0, 1)#set Green as first color
            
            # set 2nd color 
            if matname == 'negative':
                ramp_node.color_ramp.elements[1].color = (0, 0, 1, 1)
                mat.diffuse_color=(1, 1, 1, 1)
            else: 
                ramp_node.color_ramp.elements[1].color = (1, 0, 0, 1)#
                mat.diffuse_color=(1,1, 1, 1)



            # Link nodes together
            links = tree.links
            links.new(attr_node.outputs[2], multiply_node.inputs[0])
            links.new(multiply_node.outputs[0],ramp_node.inputs[0])
            links.new(ramp_node.outputs[0], principled_node.inputs[0])
            links.new(principled_node.outputs[0], output_node.inputs[1])
            
            #add the material to the object to be able to check it faster
            bpy.context.object.data.materials.append(mat)
            return mat
        
        def JamesBond(atoms):
            #____________________________________________________#
            #create edge tree     
            #____________________________________________________#   
            # Create a KDTree from the atom coordinates
            tree = cKDTree(atoms)

            # Create a new mesh object
            mesh = bpy.data.meshes.new(name=os.path.basename(self.filepath))
            object = bpy.data.objects.new(name=os.path.basename(self.filepath), object_data=mesh)
            object.scale=(x1,y1,z1)# set the right scale
            bpy.context.scene.collection.objects.link(object)
            
            # Create a list to hold the edges
            edges = []
            bonds=preferences.int_bond
            # Loop through all atoms
            for i, coord1 in enumerate(atoms):
                # Find the nearest neighbors of the atom
                nn_indices = tree.query(coord1, k=bonds)[1][1:]
                
                for nn_idx in nn_indices:
                    # Get the coordinate of the nearest neighbor
                    if nn_idx < len(atoms):
                        coord2 = atoms[nn_idx]
                        coord1 = np.array(coord1)
                        coord2 = np.array(coord2)
                        dist = np.linalg.norm((coord1 - coord2)*(x1,y1,z1))
                        # Get the covalent radii for each atom
                        radius1 = covalent_radii.get(UA[i], 1.0)
                        radius2 = covalent_radii.get(UA[nn_idx], 1.0)
                        # If the distance between the two spheres is less than the sum of their covalent radii, they are considered bonded
                        if dist < (radius1*3 + radius2*3):
                            # Add the edge to the list
                            edges.append((i, nn_idx))

            # Add the edges to the mesh
            mesh.from_pydata(atoms, edges, [])
            bpy.context.view_layer.objects.active = object#select it 
            # Update the mesh
            mesh.update()
            return object
        
        posfile=[]#future list for create_vdb() for list import
        negfile=[]
        framek=0
        for file in self.files:
            # Remove all other selected objects
            for o in bpy.context.selected_objects:
                o.select_set(False)
                
            # Load the .cube file into a numpy array
            with open(os.path.dirname(self.filepath)+'/'+file.name, 'r') as f:
                # Skip the first two lines and Check for Sick case
                MO=False
                for i in f.readline():
                    if i=='=':
                        MO=True
                f.readline().split()
                natm=f.readline().split()
                nbatm=abs(int(natm[0]))
                # Read the grid dimensions from the second line
                x=f.readline().split()
                y=f.readline().split()
                z=f.readline().split()
                nx=int(x[0])
                ny=int(y[0])
                nz=int(z[0])
                x1=float(x[1])
                y1=float(y[2])
                z1=float(z[3])
                
                
                atoms = []
                UA=[]
                for i in range(abs(int(nbatm))):
                    values = f.readline().split()
                    point=(((float(values[2]))-float(natm[1]))/x1,(float(values[3])-float(natm[2]))/y1,(float(values[4])-float(natm[3]))/z1)#scale the positions accordingly
                    atoms.append(point)#Read atom position 
                    UA.append(int(values[0]))
                        
                #____________________________________________________#
                    #create  Volume     
                #____________________________________________________#    
                
                #if sick case jump one more line
                if MO==True:
                    f.readline().split()
                #Create a 1D numpy array containing Volumetrics data
                
                data = np.fromfile(f,count=-1,sep=' ',dtype=np.float64)
                
                #read.extend([0]*(nx*ny*nz-len(read)))#add missing 0
                
                # Reshape the data array to the correct dimensions
                data = data.reshape((nx, ny, nz))
                
                # Extract the vertices and weights
                vertices = []
                vertices_weight = []
                for i in range(nx):
                    for j in range(ny):
                        for k in range(nz):
                            vertices.append((i, j, k)) 
                            vertices_weight.append(data[i][j][k])
                            
                
                #____________________________________________________#
                            #place objects     
                #____________________________________________________# 
                
                
                if preferences.bool_color==True:# ***Uses color display(slower)***
                    if preferences.bool_vdb==False and len(self.files)==1:#///Use geometry nodes to display, does not support animated volume yet///
                        #Create a new windows (this is for bypassing a blender python API impass to set an attribute as input)
                        bpy.ops.wm.window_new()
                        node_tree = bpy.context.scene.node_tree
                        # Change area type
                        bpy.context.area.ui_type = 'GeometryNodeTree'
                
                        #start the function to generate volume
                        create_obj_node(os.path.basename(self.filepath)+'_pos_density','positive')
                        # Set the vertex weights as attribute
                        obj1 = bpy.context.active_object.vertex_groups.new(name='density')
                        
                        for i, vertex in enumerate(vertices):
                            obj1.add([i], vertices_weight[i], 'REPLACE')
                        
                        if len(data):# If there is no negative value, just don't create it
                            create_obj_node(os.path.basename(self.filepath)+'_neg_density','negative')
                        
                            obj2 = bpy.context.active_object.vertex_groups.new(name='density')
                            
                            for i, vertex in enumerate(vertices):
                                obj2.add([i], -vertices_weight[i], 'REPLACE')
                            bpy.data.scenes[-1].render.engine ='CYCLES'
                        #close our windows
                        bpy.ops.wm.window_close()
                        
                    else:#///Use OpenVDB to display only in blender 3.5+///
                        
                        create_vdb('pos_density','positive',data,framek)
                        data*=-1#faster than data=-data
                        
                        create_vdb('neg_density','negative',data,framek)
                        
                else:# ***Uses monochrome display(faster)***
                    if preferences.bool_vdb==False and len(self.files)==1:#///Use geometry nodes to display, does not support animated volume yet///
                        #Create a new windows (this is for bypassing a blender python API impass to set an attribute as input)
                        bpy.ops.wm.window_new()
                        node_tree = bpy.context.scene.node_tree
                        # Change area type
                        bpy.context.area.ui_type = 'GeometryNodeTree'
                
                        create_obj_node(os.path.basename(self.filepath)+'_density','nomat')
                        obj1 = bpy.context.active_object.vertex_groups.new(name='density')
                        for i, vertex in enumerate(vertices):
                            obj1.add([i], abs(vertices_weight[i]), 'REPLACE')
                        #close our windows
                        bpy.ops.wm.window_close()       
                    else:#///Use OpenVDB to display only in blender 3.5+///
                        data=np.absolute(data)
                        create_vdb('density','nomat',data,framek)
                
            
            
            
            covalent_radii = {1: 0.32, 6: 0.77, 8: 0.66,12:1.36,79:1.34}#exemple of covalent radius
            if preferences.int_bond > 0 and framek == 0:
                    object=JamesBond(atoms)
            elif framek == 0:#Create points instead   
                
                mesh1 = bpy.data.meshes.new(os.path.basename(self.filepath))
                mesh1.from_pydata(atoms, [], [])
                
                # Create a mesh object and link it to the scene
                object = bpy.data.objects.new(os.path.basename(self.filepath), mesh1)
                
                object.scale=(x1,y1,z1)# set the right scale
                bpy.context.scene.collection.objects.link(object)
                bpy.context.view_layer.objects.active = object#select it
                mesh1.update()
            bpy.context.view_layer.objects.active = object 
            verts =  object.data.vertices    
            for v,vertex in enumerate(verts):# a very simple way to add vertex keyframe
                    vertex.co=atoms[v]
                    # keyframe the initial position of each vertex
                    vertex.keyframe_insert("co", frame=framek)
            
                
            framek+=1#increase the number of framek
            

        return {'FINISHED'}
    #set the windows file browser
    def invoke(self, context, event):
        self.files.clear()
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
#create the layout for file>import>GaussianCUBE (.cube)
def menu_func_import_cube(self, context):
    
    self.layout.operator(CUBEImportOperator.bl_idname, text="GaussianCUBE (.cube)")

# -----------------------------------------------------------------------------
#                                                                      Register
#register the blender addon to blender internal system
def register():
    bpy.utils.register_class(CUBEImportOperator)
    bpy.utils.register_class(CUBEImportPreferences)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import_cube)
def unregister():
    bpy.utils.unregister_class(CUBEImportOperator)
    bpy.utils.unregister_class(CUBEImportPreferences)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import_cube)
if __name__ == "__main__":
    register()
