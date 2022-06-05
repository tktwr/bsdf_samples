import bpy
from . import util as ut


class MY_OT_bake_btn(bpy.types.Operator):
    bl_label = "Bake"
    bl_idname = "my.bake_btn"

    def execute(self, context):
        scene = context.scene
        obj = context.object
        mat = obj.data.materials[0]

        obj.select_set(True)
        context.view_layer.objects.active = obj

        ut.make_bake(mat, scene.BSAM_bake_type, scene.BSAM_bake_width, scene.BSAM_bake_colorspace)

        return {'FINISHED'}


