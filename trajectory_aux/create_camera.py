from bpy import ops, data, context

def create_camera(cam_loc=(9,9,9)):
    ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
    ops.object.camera_add(enter_editmode=False, align='VIEW', location=cam_loc, rotation=(0, 0, 0), scale=(1, 1, 1))
    cam = data.objects["Camera"]
    cam.constraints.new(type='TRACK_TO')
    cam.constraints['Track To'].target = data.objects["Empty"]
    cam.constraints["Track To"].track_axis = 'TRACK_NEGATIVE_Z'
    cam.constraints["Track To"].up_axis = 'UP_Y'
    cam.data.lens = 42
    cam.data.type = 'ORTHO'
    cam.data.ortho_scale = 14.5
    context.scene.camera = context.object
