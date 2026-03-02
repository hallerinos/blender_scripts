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

def create_arrow(location, direction, length=0.1, width=0.02):
    bm = bmesh.new()
    
    # --- 1. Create the Shaft (Cylinder) ---
    shaft_height = length * 0.7
    bmesh.ops.create_cone(
        bm,
        cap_ends=True,
        segments=8,
        radius1=width * 0.5, # Thinner than the head
        radius2=width * 0.5,
        depth=shaft_height
    )
    # Move shaft so its base is at the origin
    bmesh.ops.translate(bm, verts=bm.verts, vec=(0, 0, shaft_height / 2))
    
    # --- 2. Create the Head (Cone) ---
    head_height = length * 0.3
    # Get reference to existing verts to only move the new ones
    old_verts = list(bm.verts)
    bmesh.ops.create_cone(
        bm,
        cap_ends=True,
        segments=8,
        radius1=width,
        radius2=0,
        depth=head_height
    )
    # Move only the new cone verts to the end of the shaft
    new_verts = [v for v in bm.verts if v not in old_verts]
    bmesh.ops.translate(bm, verts=new_verts, vec=(0, 0, shaft_height + (head_height / 2)))

    # --- 3. Orientation & Placement ---
    # Standard Blender meshes are created along Z. 
    # Track-to 'Z' ensures the point of the arrow follows the direction.
    rotation = direction.to_track_quat('Z', 'Y')
    bmesh.ops.rotate(bm, verts=bm.verts, matrix=rotation.to_matrix())
    bmesh.ops.translate(bm, verts=bm.verts, vec=location)
    
    # Finalize Mesh
    arrow_mesh = bpy.data.meshes.new("ArrowMesh")
    bm.to_mesh(arrow_mesh)
    bm.free()
    
    arrow_obj = bpy.data.objects.new("Arrow", arrow_mesh)
    bpy.context.collection.objects.link(arrow_obj)
    
    return arrow_obj

def create_vector_field_on_sphere(radius=1.05, num_points_1=11, num_points_2=11, arc=3/4, length=0.1, width=0.02):
    for i in range(num_points_1+1):
        for j in range(num_points_2+1):
            # Calculate spherical coordinates
            u = arc * 2 * math.pi / num_points_1 * i + math.pi/2
            # v = math.acos(2 / num_points_2 * j - 1)
            v = math.pi / num_points_2 * j
            
            x = radius * math.sin(v) * math.cos(u)
            y = radius * math.sin(v) * math.sin(u)
            z = radius * math.cos(v)
            
            location = Vector((x, y, z))
            
            # Calculate vector direction
            direction = Vector((-x, -y, -z)).normalized()
            
            # Create the arrow as an individual object
            arrow_obj = create_arrow(location, direction, length=length, width=width)

            # Calculate color based on direction
            rgb = hsv_to_rgb(direction, 0, 1)

            set_arrow_materials(rgb, arrow_obj)

def set_arrow_materials(rgb, arrow_obj):
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

def create_even_vector_field(radius=1.0, num_points=1000, arc=0.75):
    # Golden ratio offset for even spacing
    golden_ratio = (1 + 5**0.5) / 2
    
    for i in range(num_points):
        # 1. Height (z) distribution from -1 to 1
        z_norm = 1 - (i / (num_points - 1)) * 2
        
        # 2. Longitude (u)
        # Using the golden ratio to ensure points don't align in "ribs"
        u = (2 * math.pi * i / golden_ratio) % (2 * math.pi)
        
#        # --- CUT-OUT LOGIC ---
#        # Only place the arrow if it's within your 3/4 arc (270 degrees)
#        # Assuming the cut starts at 0 and goes to arc * 2pi
        if 0.5*math.pi > u:
            continue
            
        # 3. Radius at this height
        r_at_z = math.sqrt(1 - z_norm**2)
        
        # 4. Final Coordinates
        x = radius * r_at_z * math.cos(u)
        y = radius * r_at_z * math.sin(u)
        z = radius * z_norm
        
        location = Vector((x, y, z))
        # Direction points toward the origin (Sink) as per your original script
        direction = Vector((-x, -y, -z)).normalized()
        
        # Create and color the arrow
        arrow_obj = create_arrow(location, direction)

        # Calculate color based on direction
        rgb = hsv_to_rgb(direction, 0, 1)

        set_arrow_materials(rgb, arrow_obj)


def create_even_vector_field(radius=1.0, num_points=250, arc=0.75):
    """
    Distributes points uniformly using a Fibonacci Spiral.
    arc: 0.75 represents 270 degrees (3/4 of a sphere).
    """
    golden_ratio = (1 + 5**0.5) / 2
    
    for i in range(num_points):
        # 1. Height distribution (z) from -1 to 1
        z_norm = 1 - (i / (num_points - 1)) * 2
        
        # 2. Longitude (u) - The Sunflower Spiral angle
        u = (2 * math.pi * i / golden_ratio) % (2 * math.pi)
        
        # --- CUT-OUT LOGIC ---
        # Align this with your sphere's rotation (offset by pi/2 if needed)
        u_shifted = (u + math.pi/2) % (2 * math.pi)
        if u_shifted > (arc * 2 * math.pi):
            continue
            
        # 3. Calculate radius at this specific height
        r_at_z = math.sqrt(max(0, 1 - z_norm**2))
        
        # 4. Final Coordinates
        x = radius * r_at_z * math.cos(u)
        y = radius * r_at_z * math.sin(u)
        z = radius * z_norm
        
        location = Vector((x, y, z))
        direction = Vector((-x, -y, -z)).normalized()
        
        # Create and color
        arrow_obj = create_arrow(location, direction)
        rgb = hsv_to_rgb(direction, 0, 1)
        set_arrow_materials(rgb, arrow_obj)

def create_even_vector_field2(radius=1.0, num_points=250, arc=0.75):
    """
    Distributes points uniformly using a Fibonacci Spiral.
    arc: 0.75 represents 270 degrees (3/4 of a sphere).
    """
    golden_ratio = (1 + 5**0.5) / 2
    
    for i in range(num_points):
        # 1. Height distribution (z) from -1 to 1
        z_norm = 1 - (i / (num_points - 1)) * 2
        
        # 2. Longitude (u) - The Sunflower Spiral angle
        u = (2 * math.pi * i / golden_ratio) % (2 * math.pi)
        
        # --- CUT-OUT LOGIC ---
        # Align this with your sphere's rotation (offset by pi/2 if needed)
        u_shifted = (u - math.pi/2) % (2 * math.pi)
        if u_shifted > (arc * 2 * math.pi):
            continue
            
        # 3. Calculate radius at this specific height
        r_at_z = math.sqrt(max(0, 1 - z_norm**2))
        
        # 4. Final Coordinates
        x = radius * r_at_z * math.cos(u)
        y = radius * r_at_z * math.sin(u)
        z = radius * z_norm
        
        location = Vector((x, y, z))
        direction = Vector((-x, -y, -z)).normalized()
        
        # Create and color
        arrow_obj = create_arrow(location, direction)
        rgb = hsv_to_rgb(direction, 0, 1)
        set_arrow_materials(rgb, arrow_obj)

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

def setup_smoke_material(obj):
    mat = bpy.data.materials.new(name="Thick_Grey_Smoke")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    # Nodes
    node_vol = nodes.new('ShaderNodeVolumePrincipled')
    node_out = nodes.new('ShaderNodeOutputMaterial')
    
    # Settings for thick grey smoke
    node_vol.inputs['Color'].default_value = (0.2, 0.2, 0.2, 1.0) # Grey
    node_vol.inputs['Density'].default_value = 60.0 # Visible thickness
    node_vol.inputs['Anisotropy'].default_value = 0.1
    
    # CRITICAL: Link to Volume (Index 1)
    links.new(node_vol.outputs[0], node_out.inputs[1])
    
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

def delete_everything():
    # 1. Select and delete all objects in the current scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    
    # 2. Purge orphaned data (meshes, materials, textures, etc.)
    # This removes data blocks that have zero users.
    # The 'do_recursive=True' flag ensures it cleans up deeply nested orphaned data.
    if bpy.app.version >= (2, 90, 0):
        bpy.ops.outliner.orphans_purge(do_recursive=True)
    else:
        # Fallback for much older versions of Blender
        for block in bpy.data.meshes: bpy.data.meshes.remove(block)
        for block in bpy.data.materials: bpy.data.materials.remove(block)
        for block in bpy.data.textures: bpy.data.textures.remove(block)

def setup_camera(target_obj, location=(5, -5, 5)):
    # 1. Create the Camera
    cam_data = bpy.data.cameras.new("Camera")
    cam_obj = bpy.data.objects.new("Camera", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    
    # Set as active camera for the scene
    bpy.context.scene.camera = cam_obj
    cam_obj.location = location
    
    # 2. Add the "Track To" Constraint
    constraint = cam_obj.constraints.new(type='TRACK_TO')
    constraint.target = target_obj
    
    # Blender's default camera looks down -Z, with Y as Up
    constraint.track_axis = 'TRACK_NEGATIVE_Z'
    constraint.up_axis = 'UP_Y'
    cam_obj.data.lens = 20
    
    return cam_obj

def main():
    # Clear existing scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    delete_everything()
    
    # Call the function with the path to your .blend file and object name
    sphere = append_object_from_file('/Users/andreas/gits/blender_scripts/bloch_point/cut_sphere.blend', 'Sphere')
    sphere.name = 'cut_sphere'
    setup_smoke_material(sphere)

    # create_even_vector_field(radius=1.0, num_points=200)
    # 2. Layered Vector Field (Uniformly Distributed)
    # Total points are high, but the 'arc' check will remove 25% of them
    for r in [1.05, 0.9, 0.7, 0.5, 0.3]:
        # Scale the number of points by radius squared for consistent density
        pts = int(15 * (r**2)) + 3
        # create_even_vector_field2(radius=r, num_points=max(pts, 20), arc=0.75)
        create_vector_field_on_sphere(radius=r, num_points_1=pts, num_points_2=pts, length=r*0.1, width=r*0.02)
    
    # Set up camera and lighting
    setup_camera(target_obj=sphere, location=(1, 1, 2))
    # bpy.ops.object.light_add(type='SUN', location=(5, 5, 5))
    
    # Set render settings
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.samples = 300  # Increase samples for better quality
    bpy.context.scene.render.resolution_x = 1920  # Set resolution
    bpy.context.scene.render.resolution_y = 1080

    # bpy.context.scene.cycles.max_bounces = 12
    # bpy.context.scene.cycles.volume_bounces = 4

if __name__ == "__main__":
    main()
