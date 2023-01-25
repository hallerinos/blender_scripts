from bpy import context, data

def set_scene(engine='CYCLES', res=1080, ar=16.0/9.0, samples=16, fstart=1, fend=250):
    # Set transparent
    scene = context.scene
    context.scene.frame_start = fstart
    context.scene.frame_end = fend


    # scene.render.film_transparent = True
    scene.render.use_motion_blur = True
    scene.cycles.use_denoising = False
    scene.render.engine = engine
    scene.render.resolution_x = int(res*ar)
    scene.render.resolution_y = res
    scene.cycles.samples = samples