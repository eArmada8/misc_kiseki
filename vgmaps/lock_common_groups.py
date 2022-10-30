# Short script to lock common groups based on vgmap diff file in JSON. Run inside Blender.
# Thank you to Sinestesia
# GitHub eArmada8/misc_kiseki

import bpy, os, json
from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator

class GroupLocker(Operator, ImportHelper):

    bl_idname = "grouplocker.open_filebrowser"
    bl_label = "Select File"

    filter_glob: StringProperty(
        default='*.json',
        options={'HIDDEN'}
    )

    def execute(self, context):
        ob = bpy.context.object
        assert ob.type == "MESH"

        bpy.ops.object.mode_set(mode='OBJECT')

        with open(self.filepath, 'r') as f:
            missing_groups = json.loads(f.read())

        for group in ob.vertex_groups:
            if group.name in missing_groups:
                group.lock_weight = False
            else:
                group.lock_weight = True

        return {'FINISHED'}

def register():
    bpy.utils.register_class(GroupLocker)

def unregister():
    bpy.utils.unregister_class(GroupLocker)

if __name__ == "__main__":
    register()

    bpy.ops.grouplocker.open_filebrowser('INVOKE_DEFAULT')
