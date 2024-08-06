import sys, os
import bpy, mathutils as mu
import numpy as np
import bmesh
import pandas as pd

def delete_all_objs():
    if bpy.context.object.mode == 'EDIT':
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    bpy.ops.outliner.orphans_purge()
    bpy.ops.outliner.orphans_purge()
    bpy.ops.outliner.orphans_purge()

bpy.ops.mesh.primitive_plane_add(size=2, location=(0, 0, 0), scale=(1, 1, 1))
delete_all_objs()  # setting up scene from scratch

def str2cplx(string):
    if "im" not in string:
        num = float(string)
    else:
        num = complex(string.replace("im","j").replace(" ", ""))
    return num

def entofform(x):
    if x<1e-12:
        return 0
    elif 1-x<1e-12:
        return 0
    else:
        return -x*np.log2(x)-(1.0-x)*np.log2(1.0-x)

# import the local magnetization profile
fn_obs = "/Users/andreas/gits/blender_scripts/skyrmion/local_spin.csv"
fn_ccn = "/Users/andreas/gits/blender_scripts/skyrmion/concurrence.csv"

data_obs = pd.read_csv(fn_obs)
data_ccn = pd.read_csv(fn_ccn)

state = 8

data_obs = data_obs[data_obs['state'] == state].reset_index()
data_ccn = data_ccn[data_ccn['state'] == state].reset_index()

xi, yi, zi = data_obs['x_i'], data_obs['y_i'], data_obs['z_i']
Six, Siy, Siz = data_obs['S_{i,x}'], data_obs['S_{i,y}'], data_obs['S_{i,z}']
# quick fix FP state
#Six, Siy, Siz = 0*data_obs['S_{i,x}'], 0*data_obs['S_{i,y}'], data_obs['S_{i,z}']/data_obs['S_{i,z}']
locations = np.asarray([xi,yi,zi]).T  # construct locations array
locations = np.reshape(locations, (len(xi), 3))  # construct location array
rotations = np.asarray([Six,Siy,Siz]).T  # construct rotation array
rotations = [mu.Vector(elem).to_track_quat('Z','X') for elem in rotations]
rotations = np.reshape(rotations, (len(xi), 4))
spin_colors = 2*Siz

xi, yi, zi = data_ccn['x_i'], data_ccn['y_i'], data_ccn['z_i']
xj, yj, zj = data_ccn['x_j'], data_ccn['y_j'], data_ccn['z_j']
ri = np.asarray([xi,yi,zi]).T
rj = np.asarray([xj,yj,zj]).T
ccns = data_ccn['|\\braket{\psi|\sigma_i\sigma_j|\psi^*}|']
# quick fix FP state
#ccns = 0*data_ccn['|\\braket{\psi|\sigma_i\sigma_j|\psi^*}|']
if np.min(abs(ccns[1])) > 1e-3:
    ccns = 0.5*ccns/abs(ccns[1])
print(ccns)
dists = ((data_ccn['x_i']-data_ccn['x_j'])**2 + (data_ccn['y_i']-data_ccn['y_j'])**2 + (data_ccn['z_i']-data_ccn['z_j'])**2)**(0.5)
# link_colors = data[:,7]

# import cone and wire
file_path = '/Users/andreas/gits/blender_scripts/skyrmion/cone.blend'
inner_path = 'Object'
# object_name = 'Cylinder'
# bpy.ops.wm.append(
#     filepath=os.path.join(file_path, inner_path, object_name),
#     directory=os.path.join(file_path, inner_path),
#     filename=object_name
#     )

object_name = 'Cone_orig'
bpy.ops.wm.append(
    filepath=os.path.join(file_path, inner_path, object_name),
    directory=os.path.join(file_path, inner_path),
    filename=object_name
    )
obj = bpy.ops.object
obj.location_clear()

bpy.data.objects[object_name].select_set(True)
context = bpy.context
obj = context.selected_objects[0]
name = obj.name
mat = bpy.data.materials.new(name="dmat")
obj.data.materials.append(mat)

# obj.name = f"{name}_orig"
for (idx, loc) in enumerate(locations):
    copy = obj.copy()
    copy.data = copy.data.copy() # linked = False
    copy.name = f"{name}_{idx}"
    obj = copy
    obj.location = loc
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = rotations[idx,:]
    mat = bpy.data.materials.new(name=f"mat_{idx}")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    mixrgb = nodes.new('ShaderNodeMixRGB')
    # print(f'index: {idx}, spin_colors: {spin_colors}')
    mixrgb.inputs[0].default_value = spin_colors[idx]
    mixrgb.inputs[1].default_value = (5/255,48/255,97/255,1)
    mixrgb.inputs[2].default_value = (103/255,10/255,31/255,1)
    # nodes["Principled BSDF"].inputs[5].default_value = 0
    nodes["Principled BSDF"].inputs[7].default_value = 1
    nodes["Principled BSDF"].inputs[14].default_value = 1
    mat.node_tree.links.new(mixrgb.outputs["Color"], nodes["Principled BSDF"].inputs['Base Color'])
    obj.data.materials[0] = mat
    context.collection.objects.link(copy)
bpy.data.objects[f"{name}"].hide_render = True
bpy.data.objects[f"{name}"].hide_viewport = True
# bpy.context.scene.hide_viewport = True
uniques = []
uniques.append(np.array([.1337,.1337,.1337]))
for (idx, l1) in enumerate(ri):
#    continue
    # ee_arg = 1.0/2.0*(1.0+np.sqrt(1.0-ccns[idx]**2)) 
    # ee = entofform(ee_arg)
    # ee = min(1.0,15*ccns[idx])
    # ee = min(1.0,6*ccns[idx])
    ee = ccns[idx]
    # print(ee)
    if 0 < dists[idx] < 2.1 and ee > 0.001:
        l2 = rj[idx]
        ctr = 0.5*(l1+l2)
        ctr[2] = +0.5*dists[idx]
        coords = [l1, ctr, l2]

        if min([np.linalg.norm(ctr-elem) for elem in uniques])<1e-6 : continue
        uniques.append(ctr)

        # create the Curve Datablock
        curveData = bpy.data.curves.new(f'link_{idx}', type='CURVE')
        curveData.dimensions = '3D'
        curveData.resolution_u = 10

        # map coords to spline
        polyline = curveData.splines.new('NURBS')
        polyline.points.add(len(coords)-1)
        for i, coord in enumerate(coords):
            x, y, z = coord
            polyline.points[i].co = (x, y, z, 1)

        # create Object
        obj = bpy.data.objects.new(f'link_{idx}', curveData)
        obj.data.bevel_depth = min(0.04, .04/dists[idx])
        obj.data.splines[0].use_endpoint_u = True


        # attach to scene and validate context
        scn = bpy.context.scene
        scn.collection.objects.link(obj)

        obj.data.materials.append(None)

        mat = bpy.data.materials.new(name=f"links_{idx}")
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
#        nodes["Principled BSDF"].inputs[0].default_value = (1.0,0.497045,0.96884,1)
        nodes["Principled BSDF"].inputs[0].default_value = (0,0,0,1)
#        nodes["Principled BSDF"].inputs[0].default_value = (82/255,1,0,1)
        # nodes["Principled BSDF"].inputs[5].default_value = 0
        nodes["Principled BSDF"].inputs[7].default_value = 0
        nodes["Principled BSDF"].inputs[14].default_value = 1
        nodes["Principled BSDF"].inputs[15].default_value = 1
        # nodes["Principled BSDF"].inputs[17].default_value = (1,0,1,1)
        # nodes["Principled BSDF"].inputs[18].default_value = link_colors[idx]
#        nodes["Principled BSDF"].inputs[19].default_value = min(1,ccns[idx])
        nodes["Principled BSDF"].inputs[4].default_value = ccns[idx]

        # nodes["Principled BSDF"].inputs[F21].default_value = ee
        obj.data.materials[0] = mat
        
bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
#bpy.context.object.rotation_euler[2] = 0.785398

bpy.ops.object.camera_add(enter_editmode=False, align='VIEW', location=(30, 0, -30.2), rotation=(-2.35619, 0, 0), scale=(1, 1, 1))
bpy.context.object.data.lens = 58
#bpy.context.object.data.lens = 120
#bpy.context.object.data.lens = 138
# bpy.context.object.rotation_euler[0] = 4.09105
# bpy.context.object.rotation_euler[1] = 0
# bpy.context.object.rotation_euler[2] = 0
# bpy.context.object.rotation_euler[0] = 4.10851
bpy.context.object.location[0] = 0
bpy.context.object.location[1] = 10
bpy.context.object.location[2] = 10
# bpy.context.object.parent = bpy.data.objects["Empty"]

bpy.context.object.data.type = 'ORTHO'
bpy.context.object.data.ortho_scale = 8
#bpy.context.object.data.dof.use_dof = True
#bpy.context.object.data.dof.focus_object = bpy.data.objects["Empty"]
#bpy.context.object.parent = bpy.data.objects["Empty"]

bpy.ops.object.constraint_add(type='TRACK_TO')
bpy.context.object.constraints["Track To"].target = bpy.data.objects["Empty"]
#bpy.context.object.constraints["Track To"].owner_space = 'LOCAL'
