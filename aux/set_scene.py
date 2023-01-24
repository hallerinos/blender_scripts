from bpy import context, data

def set_scene():
    # Set transparent
    scene = context.scene
    # scene.render.film_transparent = True
    scene.render.engine = 'CYCLES'
    standard_res = 1080
    scene.render.resolution_x = standard_res
    scene.render.resolution_y = standard_res
    scene.cycles.samples = 16