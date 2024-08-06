from bpy import context, ops

def render_scene(filename):
    # export scene
    context.scene.frame_set(1)
    context.scene.render.filepath = filename
    ops.render.render(write_still=True)
