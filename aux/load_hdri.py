from bpy import context, data

def load_hdri(filename):
    scn = context.scene

    # Get the environment node tree of the current scene
    node_tree = scn.world.node_tree
    tree_nodes = node_tree.nodes

    # Clear all nodes
    tree_nodes.clear()

    # Add Background node
    node_background1 = tree_nodes.new(type='ShaderNodeBackground')

    # Add Environment Texture node
    node_environment = tree_nodes.new('ShaderNodeTexEnvironment')
    # Load and assign the image to the node property
    node_environment.image = data.images.load(filename) # Relative path
    node_environment.location = -300,-200

    # Add Output node
    node_output = tree_nodes.new(type='ShaderNodeOutputWorld')   
    node_output.location = 300,0


    # Add LightPath node
    node_lightpath = tree_nodes.new(type='ShaderNodeLightPath')
    node_lightpath.location = -300,200
    
    # Add second background node
    node_background2 = tree_nodes.new(type='ShaderNodeBackground')
    node_background2.location = 0,-200
    node_background2.inputs['Color'].default_value = (0,0,0,1)
    node_background2.inputs['Color'].default_value = (1,1,1,1)
    
    # Add MixShader node
    node_mixshader = tree_nodes.new(type='ShaderNodeMixShader')

    # Link all nodes
    links = node_tree.links
    link = links.new(node_environment.outputs["Color"], node_background1.inputs["Color"])
    link = links.new(node_background1.outputs["Background"], node_mixshader.inputs[1])
    link = links.new(node_background2.outputs["Background"], node_mixshader.inputs[2])
    link = links.new(node_lightpath.outputs[0], node_mixshader.inputs['Fac'])
    link = links.new(node_mixshader.outputs['Shader'], node_output.inputs['Surface'])