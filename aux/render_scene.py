from bpy import context, ops

def render_scene(filename, frame=1, write_still=True):
    # export scene
    context.scene.frame_set(frame)
    context.scene.render.filepath = filename
    ops.render.render(write_still=write_still)
