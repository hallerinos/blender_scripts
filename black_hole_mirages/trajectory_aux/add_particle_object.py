from bpy import ops, data, context

def add_particle_object(pos=(0,0,0)):
    ops.mesh.primitive_uv_sphere_add(radius=1, enter_editmode=False, align='WORLD', location=pos, scale=(1, 1, 1))
    particle = context.active_object
    particle.name = 'particle'
    
    # Create particle material
    mat = data.materials.new(name="particle_material")
    particle.data.materials.append(mat)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs[0].default_value = (0, 1, 1, 1)
    bsdf.inputs[7].default_value = 0
    bsdf.inputs[19].default_value = (0, 1, 1, 1)
    bsdf.inputs[20].default_value = 50
    return particle



