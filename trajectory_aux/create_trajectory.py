from bpy import ops, context
from mathutils import Vector
import numpy as np

def create_trajectory(dataframe):
    # Create a bezier circle and enter edit mode.
    ops.curve.primitive_bezier_curve_add(radius=1,
                                        location=(0.0, 0.0, 0.0),
                                        enter_editmode=True)
    # Subdivide the trajectory by a number of cuts, giving the
    # random vertex function more points to work with.
    ops.curve.subdivide(number_cuts=len(dataframe)-3)
    trajectory = context.active_object
    trajectory.name = 'trajectory'

    # Locate the array of bezier points.
    bez_pts = trajectory.data.splines[0].bezier_points
    for (id, b) in enumerate(bez_pts):
        d0 = np.asfarray(dataframe[['x', 'y', 'z']].iloc[id+1])
        dl = np.asfarray(dataframe[['x', 'y', 'z']].iloc[id])
        b.co = Vector(d0)
        b.handle_left = Vector(d0+0.1*(dl-d0))
        b.handle_right  = Vector(d0-0.1*(dl-d0))

    # Scale the curve while in edit mode.
    #ops.transform.resize(value=(2.0, 2.0, 3.0))

    # Return to object mode.
    ops.object.mode_set(mode='OBJECT')

    # Store a shortcut to the curve object's data.
    obj_data = context.active_object.data

    # Which parts of the curve to extrude ['HALF', 'FRONT', 'BACK', 'FULL'].
    obj_data.fill_mode = 'FULL'

    # Breadth of extrusion.
    obj_data.extrude = 0.0

    # Depth of extrusion.
    obj_data.bevel_depth = 0.03

    # Smoothness of the segments on the curve.
    obj_data.resolution_u = 64
    obj_data.render_resolution_u = 64
    
    return trajectory