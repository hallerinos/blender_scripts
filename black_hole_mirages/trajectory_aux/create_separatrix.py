from bpy import ops, data, context

def create_separatrix(pos=(0,0,0), rs=1.5, zscale=10):
    ops.mesh.primitive_cylinder_add(radius=rs, depth=2, enter_editmode=False, align='WORLD', location=pos, scale=(1, 1, zscale))
    separatrix = context.active_object
    separatrix.name = 'separatrix'
    
    # Create particle material
    mat = data.materials.new(name="separatrix_material")
    separatrix.data.materials.append(mat)
    mat.use_nodes = True

    # Get the node tree of the current object
    node_tree = mat.node_tree
    tree_nodes = node_tree.nodes

    # Clear all nodes
    tree_nodes.clear()

    # output node
    node_output = tree_nodes.new("ShaderNodeOutputMaterial")

    node_volume = tree_nodes.new("ShaderNodeVolumePrincipled")
    node_volume.inputs['Color'].default_value = (0, 0, 0, 1)
    node_volume.inputs['Density'].default_value = 1

    links = node_tree.links
    links.new(node_volume.outputs["Volume"], node_output.inputs["Volume"])
    return separatrix



