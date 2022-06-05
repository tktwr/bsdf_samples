import bpy


#------------------------------------------------------
# util
#------------------------------------------------------
def radians3(deg3):
    return [math.radians(i) for i in deg3]


#------------------------------------------------------
# node_tree
#------------------------------------------------------
def print_nodes(node_tree):
    if node_tree != None:
        for i in node_tree.nodes:
            print(i)


def find_node(node_tree, idname):
    if node_tree != None:
        for i in node_tree.nodes:
            if i.bl_idname == idname:
                return i
    return None


def find_principled_bsdf_node(mat):
    if mat.node_tree != None:
        for i in mat.node_tree.nodes:
            if i.bl_idname == 'ShaderNodeBsdfPrincipled':
                return i
    return None


#------------------------------------------------------
# link
#------------------------------------------------------
def get_to_socket(mat, socket_name):
    if mat.node_tree != None:
        for i in mat.node_tree.links:
            if i.to_node.bl_idname == 'ShaderNodeBsdfPrincipled' and \
               i.to_socket.identifier == socket_name:
                return i.to_socket
    return None


def get_from_socket(mat, socket_name):
    if mat.node_tree != None:
        for i in mat.node_tree.links:
            if i.to_node.bl_idname == 'ShaderNodeBsdfPrincipled' and \
               i.to_socket.identifier == socket_name:
                return i.from_socket
    return None


def make_link(mat, to_socket, from_socket):
    mat.node_tree.links.new(to_socket, from_socket)


#------------------------------------------------------
# bake
#------------------------------------------------------
def make_bake(mat, socket_type, width, colorspace):
    scene = bpy.context.scene

    orig_params = ( \
        scene.cycles.samples, \
        scene.display_settings.display_device, \
        scene.view_settings.view_transform \
    )

    scene.render.engine = 'CYCLES'
    scene.cycles.feature_set = 'SUPPORTED'
    scene.cycles.device = 'GPU'
    scene.cycles.samples = 1
    scene.display_settings.display_device = 'None'
    scene.view_settings.view_transform = 'Standard'
    pass_filter = set()

    bsdf_node = find_principled_bsdf_node(mat)
    if socket_type == 'Base Color' or \
       socket_type == 'Subsurface Color' or \
       socket_type == 'Specular' or \
       socket_type == 'Roughness':
        bake_type = 'EMIT'
        from_socket = get_from_socket(mat, socket_type)
        to_socket = bsdf_node.inputs['Emission']
        make_link(mat, to_socket, from_socket)
    elif socket_type == 'INDIRECT':
        bake_type = 'COMBINED'
        pass_filter = {'INDIRECT', 'DIFFUSE', 'GLOSSY', 'TRANSMISSION'}
        scene.cycles.samples = 1024
    elif socket_type == 'AO':
        bake_type = 'AO'
        scene.cycles.samples = 1024

    img_name = 'BakeTex'
    w = width
    h = width

    img = bpy.data.images.new(img_name, width=w, height=h)
    img.colorspace_settings.name = colorspace

    nodes = mat.node_tree.nodes
    node = nodes.new('ShaderNodeTexImage')
    node.name = 'BakeNode'
    node.image = img
    node.select = True
    nodes.active = node

    bpy.ops.object.bake(type=bake_type, pass_filter=pass_filter)
    img.pack()

    scene.cycles.samples, \
    scene.display_settings.display_device, \
    scene.view_settings.view_transform = orig_params


#------------------------------------------------------
# gltf
#------------------------------------------------------
def add_gltf_shader_node(node_tree):
    GLTF_GROUP_NAME = 'glTF Settings'

    if GLTF_GROUP_NAME in bpy.data.node_groups:
        gltf_grp = bpy.data.node_groups[GLTF_GROUP_NAME]
    else:
        gltf_grp = bpy.data.node_groups.new(GLTF_GROUP_NAME, 'ShaderNodeTree')
        gltf_grp.inputs.new('NodeSocketFloat', 'Occlusion')
        gltf_grp.nodes.new('NodeGroupOutput')
        gltf_grp.nodes.new('NodeGroupInput')

    gltf_ao = node_tree.nodes.new('ShaderNodeGroup')
    gltf_ao.node_tree = gltf_grp
    return gltf_ao


