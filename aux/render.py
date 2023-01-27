from bpy import context, ops

def render_frame(filename, frame=1, write_still=True):
    # export single frame
    context.scene.frame_set(frame)
    context.scene.render.filepath = filename
    ops.render.render(write_still=write_still)

def render_animation(filename, write_still=True):
    # export as video
    context.scene.render.filepath = filename
    ops.render.render(animation=True)
