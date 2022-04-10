import bpy
import os
import math


MAT_PARAM_30 = {
    "Base Color": 0,
    "Subsurface": 1,
    "Subsurface Radius": 2,
    "Subsurface Color": 3,
    "Subsurface IOR": 4,
    "Subsurface Anisotropy": 5,
    "Metallic": 6,
    "Specular": 7,
    "Specular Tint": 8,
    "Roughness": 9,
    "Anisotropic": 10,
    "Anisotropic Rotation": 11,
    "Sheen": 12,
    "Sheen Tint": 13,
    "Clearcoat": 14,
    "Clearcoat Roughness": 15,
    "IOR": 16,
    "Transmission": 17,
    "Transmission Roughness": 18,
    "Emission": 19,
    "Emission Strength": 20,
    "Alpha": 21,
    "Normal": 22,
    "Clearcoat Normal": 23,
    "Tangent": 24,
}


#======================================================
def radians3(deg3):
    return [math.radians(i) for i in deg3]


def clear_all():
    for i in bpy.data.cameras:
        bpy.data.cameras.remove(i)
    for i in bpy.data.lights:
        bpy.data.lights.remove(i)
    for i in bpy.data.meshes:
        bpy.data.meshes.remove(i)
    for i in bpy.data.materials:
        bpy.data.materials.remove(i)
    for i in bpy.data.objects:
        bpy.data.objects.remove(i)
    for i in bpy.data.collections:
        bpy.data.collections.remove(i)


def set_mat_custom_props():
    for mat in bpy.data.materials:
        print(f'mat.name = {mat.name}')
        bsdf = find_principled_bsdf_node(mat)
        if bsdf != None:
            print(f'bsdf.name = {bsdf.name}')
            mat['u_subsurface'] = get_mat_param(mat, 'Subsurface')
            mat['u_subsurface_radius'] = get_mat_param(mat, 'Subsurface Radius')
            mat['u_specular'] = get_mat_param(mat, 'Specular')
            mat['u_specular_tint'] = get_mat_param(mat, 'Specular Tint')
            mat['u_sheen'] = get_mat_param(mat, 'Sheen')
            mat['u_sheen_tint'] = get_mat_param(mat, 'Sheen Tint')
            mat['u_clearcoat'] = get_mat_param(mat, 'Clearcoat')
            mat['u_clearcoat_roughness'] = get_mat_param(mat, 'Clearcoat Roughness')
            mat['u_ior'] = get_mat_param(mat, 'IOR')
            mat['u_transmission'] = get_mat_param(mat, 'Transmission')
            mat['u_transmission_roughness'] = get_mat_param(mat, 'Transmission Roughness')

            normal_scale = get_normal_map_strength(mat)
            mat['u_normal_scale'] = (normal_scale, normal_scale, 1.0)


#------------------------------------------------------
# add
#------------------------------------------------------
def add_collection_to_scene(coll):
    bpy.context.scene.collection.children.link(coll)


def add_object_to_scene(obj):
    bpy.context.scene.collection.objects.link(obj)


def link_object_to_collection(obj, coll):
    coll.objects.link(obj)
    bpy.context.scene.collection.objects.unlink(obj)


#------------------------------------------------------
# create
#------------------------------------------------------
def create_collection(name):
    return bpy.data.collections.new(name)


def create_camera(name, loc, rot_deg):
    data = bpy.data.cameras.new(name=name)
    obj = bpy.data.objects.new(name, data)
    obj.location = loc
    obj.rotation_euler = radians3(rot_deg)
    return obj


def create_light(name, loc, power):
    data = bpy.data.lights.new(name=name, type='POINT')
    data.energy = power
    obj = bpy.data.objects.new(name=name, object_data=data)
    obj.location = loc
    return obj


def create_sphere(name, radius, loc):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=loc, scale=(1, 1, 1))
    bpy.ops.object.shade_smooth()
    obj = bpy.context.view_layer.objects.active
    obj.name = name
    obj.data.name = name
    return obj


def create_material(name):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    return mat


def rename_all(src, dst):
    for obj in bpy.data.objects:
        if src in obj.name:
            obj.name = obj.name.replace(src, dst)
        if src in obj.data.name:
            obj.data.name = obj.data.name.replace(src, dst)
    for mat in bpy.data.materials:
        if src in mat.name:
            mat.name = mat.name.replace(src, dst)


#------------------------------------------------------
# material
#------------------------------------------------------
def find_principled_bsdf_node(mat):
    if mat.node_tree != None:
        for i in mat.node_tree.nodes:
            if i.bl_idname == 'ShaderNodeBsdfPrincipled':
                return i
    return None


def get_normal_map_strength(mat):
    if mat.node_tree != None:
        for i in mat.node_tree.links:
            if i.to_node.bl_idname == 'ShaderNodeBsdfPrincipled' and i.to_socket.identifier == 'Normal' and i.from_node.bl_idname == 'ShaderNodeNormalMap':
                normal_map_node = i.from_node
                return normal_map_node.inputs[0].default_value
    return 1.0


def set_obj_material(obj, mat):
    obj_matslots = obj.material_slots
    if len(obj_matslots) == 0:
        obj.data.materials.append(mat)
    else:
        obj_matslots[obj.active_material_index].material = mat


def set_mat_param(mat, mat_param_name, val):
    #bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf = find_principled_bsdf_node(mat)
    mat_param_id = MAT_PARAM_30[mat_param_name]
    bsdf.inputs[mat_param_id].default_value = val


def get_mat_param(mat, mat_param_name):
    #bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf = find_principled_bsdf_node(mat)
    mat_param_id = MAT_PARAM_30[mat_param_name]
    return bsdf.inputs[mat_param_id].default_value


#======================================================
# main
#======================================================
MAT_BLENDER_DEFAULT = {
    "Base Color": (0.8, 0.8, 0.8, 1.0),
    "Subsurface": 0.0,
    "Subsurface Radius": (1.0, 0.2, 0.1),
    "Subsurface Color": (0.8, 0.8, 0.8, 1.0),
    "Subsurface IOR": 1.4,
    "Subsurface Anisotropy": 0.0,
    "Metallic": 0.0,
    "Specular": 0.5,
    "Specular Tint": 0.0,
    "Roughness": 0.5,
    "Anisotropic": 0.0,
    "Anisotropic Rotation": 0.0,
    "Sheen": 0.0,
    "Sheen Tint": 0.5,
    "Clearcoat": 0.0,
    "Clearcoat Roughness": 0.03,
    "IOR": 1.45,
    "Transmission": 0.0,
    "Transmission Roughness": 0.0,
    "Emission": (0.0, 0.0, 0.0, 1.0),
    "Emission Strength": 1.0,
    "Alpha": 1.0,
    #"Normal": (0.0, 0.0, 1.0),
    #"Clearcoat Normal": (0.0, 0.0, 1.0),
    #"Tangent": (0.0, 0.0, 1.0),
}

MAT_DEFAULT = {
    "Specular": 0.5,
    "Roughness": 0.2,
}

MAT_SAMPLES = (
    {
        "name": "Subsurface",
        "Base Color": (1.000, 0.258, 0.123, 1.000),
        "Subsurface Color": (1.000, 0.258, 0.123, 1.000),
        "min":  0.0,
        "max":  1.0,
    }, {
        "name": "Metallic",
        "Base Color": (1.000, 0.780, 0.040, 1.000),
        "min":  0.0,
        "max":  1.0,
    }, {
        "name": "Specular",
        "Base Color": (1.000, 0.028, 0.026, 1.000),
        "min":  0.0,
        "max":  1.0,
    }, {
        "name": "Specular Tint",
        "Base Color": (1.000, 0.028, 0.026, 1.000),
        "min":  0.0,
        "max":  1.0,
    }, {
        "name": "Roughness",
        "Base Color": (0.093, 0.161, 1.000, 1.000),
        "min":  0.0,
        "max":  1.0,
    }, {
        "name": "Sheen",
        "Base Color": (0.141, 0.00083, 0.006, 1.000),
        "Roughness": 0.9,
        "Sheen Tint": 0.0,
        "min":  0.0,
        "max":  1.0,
    }, {
        "name": "Sheen Tint",
        "Base Color": (0.141, 0.00083, 0.006, 1.000),
        "Roughness": 0.9,
        "Sheen": 1.0,
        "min":  0.0,
        "max":  1.0,
    }, {
        "name": "Clearcoat",
        "Base Color": (0.011, 0.063, 0.066, 1.000),
        "Specular": 0.0,
        "min":  0.0,
        "max":  1.0,
    }, {
        "name": "Clearcoat Roughness",
        "Base Color": (0.011, 0.063, 0.066, 1.000),
        "Specular": 0.0,
        "Clearcoat": 1.0,
        "min":  0.0,
        "max":  1.0,
    }, {
        "name": "IOR",
        "Base Color": (0.238, 1.000, 0.117, 1.000),
        "Transmission": 1.0,
        "min":  1.0,
        "max":  2.0,
    }, {
        "name": "Transmission",
        "Base Color": (0.238, 1.000, 0.117, 1.000),
        "min":  0.0,
        "max":  1.0,
    }, {
        "name": "Transmission Roughness",
        "Base Color": (0.238, 1.000, 0.117, 1.000),
        "Transmission": 1.0,
        "min":  0.0,
        "max":  1.0,
    }
)


def create_bsdf_samples(nx, ny):
    w = 512
    bpy.context.scene.render.resolution_x = w
    bpy.context.scene.render.resolution_y = int(w * ny / nx)
    bpy.context.scene.render.resolution_percentage = 100

    l = 1.1 * ny / 2 / math.tan(math.radians(39.6/2))

    cam_loc = ((nx-1)/2, -l, -(ny-1)/2)
    cam_rot = (90, 0, 0)
    cam = create_camera('Camera_0', cam_loc, cam_rot)
    add_object_to_scene(cam)

    lit_loc = (0, -5, 0)
    lit = create_light('Light_0', lit_loc, 1000)
    add_object_to_scene(lit)

    shapes_coll = create_collection("Shapes")
    add_collection_to_scene(shapes_coll)

    for j in range(0, ny):
        for i in range(0, nx):
            loc = (i, 0, -j)
            name = f"Sphere_{j}_{i}"
            obj = create_sphere(name, 0.4, loc)
            mat = create_material(name)

            # set fixed material params
            for sample in (MAT_BLENDER_DEFAULT, MAT_DEFAULT, MAT_SAMPLES[j]):
                for key in MAT_PARAM_30.keys():
                    if key in sample:
                        set_mat_param(mat, key, sample[key])

            # set a variable material param
            alpha = i/(nx-1)
            val = (1-alpha) * sample["min"] + alpha * sample["max"]
            set_mat_param(mat, sample["name"], val)

            set_obj_material(obj, mat)
            link_object_to_collection(obj, shapes_coll)

    set_mat_custom_props()


#======================================================
# UI
#======================================================
bl_info = {
    "name": "BSDF Samples",
    "author": "Takehiro Tawara",
    "version": (0, 1),
    "blender": (3, 0, 0),
    "location": "",
    "description": "create bsdf samples panel",
    "warning": "",
    "support": "TESTING",
    "doc_url": "",
    "tracker_url": "",
    "category": "Material"
}


class MY_OT_info_btn(bpy.types.Operator):
    bl_label = "Info"
    bl_idname = "my.info_btn"

    def execute(self, context):
        print(f"CWD: {os.getcwd()}")
        print(bpy.data.objects)
        print(bpy.data.materials)
        print(bpy.data.textures)
        return {'FINISHED'}


class MY_OT_clear_btn(bpy.types.Operator):
    bl_label = "Clear"
    bl_idname = "my.clear_btn"

    def execute(self, context):
        clear_all()
        return {'FINISHED'}


class MY_OT_create_btn(bpy.types.Operator):
    bl_label = "Create"
    bl_idname = "my.create_btn"

    def execute(self, context):
        scene = context.scene
        create_bsdf_samples(scene.bsdf_samples_nx, len(MAT_SAMPLES))
        return {'FINISHED'}


class MY_OT_extra_btn(bpy.types.Operator):
    bl_label = "Extra"
    bl_idname = "my.extra_btn"

    def execute(self, context):
        set_mat_custom_props()
        return {'FINISHED'}


class MY_OT_rename_btn(bpy.types.Operator):
    bl_label = "Rename"
    bl_idname = "my.rename_btn"

    def execute(self, context):
        scene = context.scene
        rename_all(scene.bsdf_samples_src_text, scene.bsdf_samples_dst_text)
        return {'FINISHED'}


class MY_PT_ui(bpy.types.Panel):
    bl_label = "BSDF Samples"
    bl_category = "Material"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        obj = context.object

        layout.operator("my.clear_btn")

        layout.prop(scene, "bsdf_samples_nx")
        layout.operator("my.create_btn")

        layout.separator()

        layout.operator("my.extra_btn")

        layout.separator()

        layout.prop(scene, "bsdf_samples_src_text")
        layout.prop(scene, "bsdf_samples_dst_text")
        layout.operator("my.rename_btn")

        layout.separator()

        layout.operator("my.info_btn")
        layout.operator("render.render")


classes = (
    MY_PT_ui,
    MY_OT_info_btn,
    MY_OT_clear_btn,
    MY_OT_create_btn,
    MY_OT_extra_btn,
    MY_OT_rename_btn,
)


#------------------------------------------------------
# props
#------------------------------------------------------
def init_props():
    scene = bpy.types.Scene
    scene.bsdf_samples_nx = bpy.props.IntProperty(
        name="nx",
        description="the number of columns",
        default=7,
        min=1,
        max=11
    )
    scene.bsdf_samples_src_text = bpy.props.StringProperty(
        name="src_text",
        description="src_text",
    )
    scene.bsdf_samples_dst_text = bpy.props.StringProperty(
        name="dst_text",
        description="dst_text",
    )


def clear_props():
    scene = bpy.types.Scene
    del scene.bsdf_samples_nx
    del scene.bsdf_samples_src_text
    del scene.bsdf_samples_dst_text


#------------------------------------------------------
# register
#------------------------------------------------------
def register():
    for c in classes:
        bpy.utils.register_class(c)
    init_props()


def unregister():
    clear_props()
    for c in classes:
        bpy.utils.unregister_class(c)


#------------------------------------------------------
# main
#------------------------------------------------------
if __name__ == "__main__":
    register()
