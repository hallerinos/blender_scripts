import bpy
import bmesh
import math
import sys
import subprocess
from mathutils import Vector

def color_fun(h):
    if 0 <= h < 60:
        return h / 60
    elif 60 <= h < 180:
        return 1
    elif 240 <= h <= 360:
        return 0
    elif 180 <= h < 240:
        return 4 - h / 60
    return 0

def hsv_to_rgb(n, in_v, in_h):
    nom = math.sqrt(n[0]**2 + n[1]**2 + n[2]**2) + 1e-10
    f = math.atan2(n[1]/nom, n[0]/nom)
    h = 360 * in_h + (1 - 2*in_h) * (f if f >= 0 else 2*math.pi + f) * 180/math.pi
    h = h % 360
    
    m1 = 1 - abs(n[2])/nom if (1 - 2*in_v) * n[2]/nom < 0 else 1
    m2 = 0 if (1 - 2*in_v) * n[2]/nom < 0 else abs(n[2])/nom
    
    max_v = 0.5 + nom * (m1 - 0.5)
    min_v = 0.5 - nom * (0.5 - m2)
    d_v = max_v - min_v
    
    rgb = list(n)
    rgb[0] = color_fun((h + 120) % 360) * d_v + min_v
    rgb[1] = color_fun(h % 360) * d_v + min_v
    rgb[2] = color_fun((h - 120) % 360) * d_v + min_v
    
    return rgb

def create_arrow(location, direction, length=0.1, width=0.03):
    # Create a new bmesh for the arrow
    bm = bmesh.new()
    bmesh.ops.create_cone(
        bm,
        cap_ends=True,
        cap_tris=False,
        segments=8,
        radius1=width,
        radius2=0,
        depth=length
    )
    
    # Translate cone to align it with the direction
    bmesh.ops.translate(bm, verts=bm.verts, vec=(0, 0, length/2))
    
    # Rotate the arrow to match the direction
    rotation = direction.to_track_quat('-Z', 'Y')
    bmesh.ops.rotate(
        bm,
        verts=bm.verts,
        cent=(0, 0, 0),
        matrix=rotation.to_matrix()
    )
    
    # Translate to the desired location
    bmesh.ops.translate(bm, verts=bm.verts, vec=location)
    
    # Create a new mesh and object for this arrow
    arrow_mesh = bpy.data.meshes.new("ArrowMesh")
    bm.to_mesh(arrow_mesh)
    bm.free()
    
    arrow_obj = bpy.data.objects.new("Arrow", arrow_mesh)
    bpy.context.collection.objects.link(arrow_obj)
    
    return arrow_obj

def create_vector_field_on_sphere(radius=1, num_points_1=5, num_points_2=5, arc=3/4):
    # Create the sphere for reference (not part of the arrows)
#    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, segments=32, ring_count=16)
#    sphere = bpy.context.active_object
    
    for i in range(num_points_1 + 1):
        for j in range(num_points_2 + 1):
            # Calculate spherical coordinates
            u = arc * 2 * math.pi / num_points_1 * i
            v = math.acos(2 / num_points_2 * j - 1)
            
            x = radius * math.sin(v) * math.cos(u)
            y = radius * math.sin(v) * math.sin(u)
            z = radius * math.cos(v)
            
            location = Vector((x, y, z))
            
            # Calculate vector direction
            direction = Vector((-x, -y, -z)).normalized()
            
            # Create the arrow as an individual object
            arrow_obj = create_arrow(location, direction)
            
            # Calculate color based on direction
            rgb = hsv_to_rgb(direction, 0, 1)
            
            # Assign color to the arrow object
            mat = bpy.data.materials.new(name="ArrowMaterial")
            mat.use_nodes = True
            arrow_obj.data.materials.append(mat)
            
            # Configure material nodes for color
            nodes = mat.node_tree.nodes
            links = mat.node_tree.links
            
            # Clear existing nodes
            nodes.clear()
            
            # Create necessary nodes
            node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
            node_output = nodes.new(type='ShaderNodeOutputMaterial')
            
            # Link nodes
            links.new(node_bsdf.outputs[0], node_output.inputs[0])
            
            # Set base color from RGB values
            node_bsdf.inputs['Base Color'].default_value = (*rgb, 1)  # RGB + Alpha

def duplicate_object(object_name):
    # Ensure the object exists
    if object_name in bpy.data.objects:
        # Set the object as active and select it
        obj = bpy.data.objects[object_name]
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        
        # Duplicate the object
        bpy.ops.object.duplicate()
        
        # Optionally, deselect the original object
        obj.select_set(False)
        
        # Get the newly duplicated object
        new_obj = bpy.context.selected_objects[0]  # Assumes only the new object is selected
        return new_obj
    else:
        print(f"Object '{object_name}' not found!")
        return None

def append_object_from_file(filepath, object_name):
    # Define the directory path and the blend file path
    directory = filepath
    
    # Load the objects from the blend file
    with bpy.data.libraries.load(directory, link=False) as (data_from, data_to):
        # Load only the object with the specific name if it exists in the blend file
        if object_name in data_from.objects:
            data_to.objects = [object_name]
        else:
            print(f"Object '{object_name}' not found in the blend file.")
            return
    
    # Link the object to the current scene
    for obj in data_to.objects:
        if obj is not None:
            # Add the object to the current collection
            bpy.context.collection.objects.link(obj)
            print(f"Appended '{obj.name}' to the current scene.")
    return obj

def main():
    # Clear existing scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Call the function with the path to your .blend file and object name
    sphere = append_object_from_file('/Users/andreas/gits/blender_scripts/bloch_point/cut_sphere.blend', 'Sphere')
    sphere.name = 'cut_sphere'
    # duplicate_object(sphere.name)

    # create_vector_field_on_sphere()
    
    # Set up camera and lighting
    bpy.ops.object.camera_add(location=(3, -3, 3))
    bpy.context.object.data.lens = 50  # Set camera lens (optional)
    bpy.ops.object.light_add(type='SUN', location=(5, 5, 5))
    
    # Set render settings
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.samples = 300  # Increase samples for better quality
    bpy.context.scene.render.resolution_x = 1920  # Set resolution
    bpy.context.scene.render.resolution_y = 1080

if __name__ == "__main__":
    main()
