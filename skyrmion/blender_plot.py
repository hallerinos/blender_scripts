import sys, os
import bpy, mathutils as mu
import numpy as np
import bmesh

def delete_all_objs():
    if bpy.context.object.mode == 'EDIT':
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    bpy.ops.outliner.orphans_purge()
    bpy.ops.outliner.orphans_purge()
    bpy.ops.outliner.orphans_purge()

def particleSetter(scene, degp):
    particle_systems = object.evaluated_get(degp).particle_systems
    particles = particle_systems[0].particles
    totalParticles = len(particles)

    cFrame = scene.frame_current
    sFrame = scene.frame_start
    particles.foreach_set("location", np.array(locations[cFrame-1]).ravel())
    particles.foreach_set("rotation", np.array(rotations[cFrame-1]).ravel())

    particles = particle_systems[1].particles
    totalParticles = len(particles)

    cFrame = scene.frame_current
    sFrame = scene.frame_start
    particles.foreach_set("location", np.array(bond_location).ravel())
    particles.foreach_set("rotation", np.array(bond_rotation).ravel())
    particles.foreach_set("size", np.array(bond_size).ravel())

bpy.ops.mesh.primitive_plane_add(size=2, location=(0, 0, 0), scale=(1, 1, 1))
delete_all_objs()  # setting up scene from scratch

# import the local magnetization profile
fn = "/Users/andreashaller/ITensors_applications/saves/evo/Lx12Ly12B0-0.5K-0.0/lobs_bond_dim16.dat"
header = np.loadtxt(fn, skiprows=1, delimiter=', ', max_rows=1, dtype=str)
data = np.loadtxt(fn, skiprows=2, delimiter=', ')
nsweeps = int(max(data[:,0]))
nsites = int(max(data[:,1]))
x = data[:,2]  # separate location array
y = data[:,3]  # separate location array
z = data[:,4]  # separate location array
Sy = data[:,5]  # separate expectation values
Sz = data[:,6]  # separate expectation values
Sx = data[:,7]  # separate expectation values
locations = np.asarray([x,y,z+0.4*Sz]).T  # construct locations array
locations = np.reshape(locations, (nsweeps, nsites, 3))  # construct location array
rotations = np.asarray([Sx,Sy,Sz]).T  # construct rotation array
rotations = [mu.Vector(elem).to_track_quat('Z','X') for elem in rotations]
rotations = np.reshape(rotations, (nsweeps, nsites, 4))

# import the entanglement entropy
fn = "/Users/andreashaller/ITensors_applications/observables/saves/evo/Lx12Ly12B0-0.5K-0.0mps_RDM.txt"
header = np.loadtxt(fn, skiprows=1, delimiter=', ', max_rows=1, dtype=str)
data = np.loadtxt(fn, skiprows=2, delimiter=', ')
nbonds = len(data[:,0])
x1 = data[:,1]  # separate location array
y1 = data[:,2]  # separate location array
z1 = data[:,3]  # separate location array
x2 = data[:,4]  # separate location array
y2 = data[:,5]  # separate location array
z2 = data[:,6]  # separate location array
ee = data[:,7]  # separate entanglement entropy
locations_EE1 = np.asarray([x1,y1,z1+1*ee-0.5]).T  # construct locations array
locations_EE1 = np.reshape(locations_EE1, (nbonds, 3))  # construct location array
locations_EE2 = np.asarray([x2,y2,z2+1*ee-0.5]).T  # construct locations array
locations_EE2 = np.reshape(locations_EE2, (nbonds, 3))  # construct location array
direction = locations_EE2-locations_EE1
ee_sizes = np.asarray([np.linalg.norm(vec) for vec in direction])
# ee_sizes = np.abs(np.log(ee_sizes))
ee_sizes[ee_sizes > 2] = 0
locations_EE = 0.5*(locations_EE2+locations_EE1)
rotations_EE = [mu.Vector(elem).to_track_quat('Z','X') for elem in direction]
rotations_EE = np.reshape(rotations_EE, (nbonds, 4))
# print(ee_sizes)

pos = np.reshape(np.asarray([x,y,z]).T,(nsweeps,nsites,3))[0]
nbonds = int(len(pos)*(len(pos)-1)/2)
i = 0
bond_rotation = []
bond_location = []
bond_size = []
for id1 in range(nsites):
    for id2 in range(nsites):
        bond_dist = pos[id1] - pos[id2]
        norm = np.linalg.norm(bond_dist)
        if 4 < norm < 5 and 1.5 < np.linalg.norm(pos[id1]) < 2:
            bond_rotation.append(mu.Vector(bond_dist).to_track_quat('Z','X'))
            pos_av = 0.5*(pos[id1] + pos[id2])
            # pos_av += [np.random.randn(),np.random.randn(),0.1*np.random.rand()]
            pos_av += [0,0,0.15*np.random.rand()]
            bond_location.append(pos_av)
            bond_size.append(norm)
bond_location = np.asarray(bond_location)
bond_rotation = np.asarray(bond_rotation)
# print(bond_location)
numframes = len(locations)  # number of frames == number of sweeps

bpy.ops.mesh.primitive_plane_add(size=2, location=(0, 0, 0), scale=(1, 1, 1))

object = bpy.data.objects["Plane"]
object.modifiers.new("ParticleSystem", 'PARTICLE_SYSTEM')
#object.modifiers.new("ParticleSystem", 'PARTICLE_SYSTEM')
# object.modifiers.new("ParticleSystem", 'PARTICLE_SYSTEM')
object.show_instancer_for_render = False

# import cone and wire
file_path = '/Users/andreashaller/ITensors_applications/plots/cone.blend'
inner_path = 'Object'
object_name = 'Cylinder'
bpy.ops.wm.append(
    filepath=os.path.join(file_path, inner_path, object_name),
    directory=os.path.join(file_path, inner_path),
    filename=object_name
    )
object_name = 'Cone'
bpy.ops.wm.append(
    filepath=os.path.join(file_path, inner_path, object_name),
    directory=os.path.join(file_path, inner_path),
    filename=object_name
    )

bpy.ops.object.light_add(type='POINT', align='WORLD', location=(0, 0, .75), scale=(1, 1, 1))
bpy.context.object.data.energy = 2000
bpy.context.object.data.color = (1, 0, 1)

## set some properties of the particle systems
# this is for the spin positions
particleSystem = object.particle_systems[0]
particleSystem.settings.count = len(locations[0])
particleSystem.settings.frame_start = 1
particleSystem.settings.frame_end = 1
particleSystem.settings.lifetime = len(locations)+1
particleSystem.settings.physics_type = 'NO'
particleSystem.settings.render_type = 'OBJECT'
particleSystem.settings.instance_object = bpy.data.objects['Cone']
particleSystem.settings.particle_size = 1
# this is for the bond positions
object.modifiers.new("ParticleSystem", 'PARTICLE_SYSTEM')
particleSystem = object.particle_systems[1]
particleSystem.settings.count = len(bond_location)
particleSystem.settings.frame_start = 1
particleSystem.settings.frame_end = 1
particleSystem.settings.lifetime = len(locations)+1
particleSystem.settings.physics_type = 'NO'
particleSystem.settings.render_type = 'OBJECT'
particleSystem.settings.instance_object = bpy.data.objects['Cylinder']
particleSystem.settings.particle_size = 1

# particleSystem.renter
object.show_instancer_for_viewport = False
degp = bpy.context.evaluated_depsgraph_get()

#clear the post frame handler
bpy.app.handlers.frame_change_post.clear()

#run the function on each frame
bpy.app.handlers.frame_change_post.append(particleSetter)

bpy.context.scene.frame_end = numframes

bpy.context.scene.render.use_motion_blur = False

bpy.context.scene.frame_set(len(locations))

bpy.ops.object.select_all(action='DESELECT')

# bpy.ops.object.light_add(type='AREA', align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
# bpy.ops.transform.translate(value=(0, 0, 10), orient_axis_ortho='X', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, False, True), mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
# bpy.context.object.data.energy = 1000
# bpy.context.object.data.size = 6.68

bpy.ops.object.light_add(type='SPOT', align='WORLD', location=(0, 0, -5.), scale=(1, 1, 1))
bpy.context.object.rotation_euler[0] = 3.14159
bpy.context.object.data.energy = 15000
bpy.context.object.data.spot_size = 1.0
# bpy.context.object.data.color = (0.090788, 0.32937, 1.0)
bpy.context.object.data.color = (1, 0, 1)

#bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, -0.5), scale=(1, 1, 1))

bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))

bpy.ops.object.camera_add(enter_editmode=False, align='VIEW', location=(0, -5, -3.25), rotation=(1, -3.141, 0), scale=(1, 1, 1))
bpy.context.object.data.type = 'ORTHO'
#bpy.context.object.data.dof.use_dof = True
#bpy.context.object.data.dof.focus_object = bpy.data.objects["Empty"]
#bpy.context.object.data.dof.aperture_fstop = 10
bpy.context.object.data.ortho_scale = 13

# # bpy.app.debug = True

# # # Settings
# # name = 'ee_grid'
# # rows = len(locations_EE)
# # columns = 1
# # size = .5

# # def face(column, row):
# #     """ Create a single face """

# #     return (column* rows + row,
# #            (column + 1) * rows + row,
# #            (column + 1) * rows + 1 + row,
# #            column * rows + 1 + row)

# # # Looping to create the grid
# # verts = [loc for loc in locations[0]]
# # faces = []

# # # Create Mesh Datablock
# # mesh = bpy.data.meshes.new(name)
# # mesh.from_pydata(verts, [], faces)

# # # Create Object and link to scene
# # obj = bpy.data.objects.new(name, mesh)
# # bpy.context.scene.collection.objects.link(obj)

# # # Select the object
# # bpy.context.view_layer.objects.active = obj