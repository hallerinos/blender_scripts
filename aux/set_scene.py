from bpy import context, data

def set_scene(engine='CYCLES', res=1080, samples=16):
    # Set transparent
    scene = context.scene
    # scene.render.film_transparent = True
    scene.render.engine = engine
    scene.render.resolution_x = int(res*16.0/9.0)
    scene.render.resolution_y = res
    scene.cycles.samples = samples