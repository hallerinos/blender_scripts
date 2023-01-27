from bpy import ops, context, data

def create_particlesystem(pos=(0,0,0), obj=None):
    ops.mesh.primitive_uv_sphere_add(radius=1, enter_editmode=False, align='WORLD', location=pos, scale=(1, 1, 1))
    particle_system = context.active_object
    particle_system.name = 'particle_system'

    ops.object.particle_system_add()
    ps = particle_system.particle_systems[0]
    ps.settings.render_type = 'OBJECT'
    ps.settings.lifetime = 1000
    ps.settings.count = 10000
    ps.settings.effector_weights.gravity = 0
    ps.settings.instance_object = obj
    ps.settings.normal_factor = 10
    ps.settings.particle_size = 0.1
    ps.settings.frame_end = 500



    return particle_system


