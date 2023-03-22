# Blender addon to delete any empty vertex groups.
#
# GitHub eArmada8/misc_kiseki

bl_info = {
    "name": "Delete empty vertex groups",
    "description": "Small tool to delete vertex groups that do not have any vertices in them.  Will not delete locked empty groups.",
    "author": "github.com/eArmada8/misc_kiseki",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "Object Data Properties > Vertex Groups > Vertex Group Specials",
    "tracker_url": "https://github.com/eArmada8/misc_kiseki/issues",
    "category": "Mesh",
}

import bpy

class GroupDeleter(bpy.types.Operator):

    bl_idname = "object.groupdeleter"
    bl_label = "Delete empty (unlocked) vertex groups"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ob = bpy.context.object
        if ob.type == 'MESH':
            bpy.ops.object.mode_set(mode='OBJECT')
            mesh = ob
            mesh.update_from_editmode()
            # Obtain list of all groups
            all_groups = []
            for group in mesh.vertex_groups:
                all_groups.append(group.index)
            assigned_groups = []
            # Obtain list of all groups with vertices assigned to them
            for vertex in mesh.data.vertices:
                for group in vertex.groups:
                    assigned_groups.append(group.group)
            assigned_groups = list(set(assigned_groups))
            empty_groups = [x for x in all_groups if x not in assigned_groups]
            # Delete empty groups
            for i in reversed(range(len(mesh.vertex_groups))):
                if i in empty_groups and mesh.vertex_groups[i].lock_weight == False:
                    mesh.vertex_groups.remove(mesh.vertex_groups[i])
        return {'FINISHED'}

class GroupDeleterMenu(bpy.types.Operator):
    bl_idname = "object.group_deleter_menu"
    bl_label = "Delete empty (unlocked) vertex groups"
    bl_description = "Delete unlocked weight groups that have no vertices assigned to them"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute (self, context):
        bpy.ops.object.groupdeleter('INVOKE_DEFAULT')
        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(GroupDeleterMenu.bl_idname)

def register():
    bpy.utils.register_class(GroupDeleter)
    bpy.utils.register_class(GroupDeleterMenu)
    bpy.types.MESH_MT_vertex_group_context_menu.append(menu_func)

def unregister():
    bpy.utils.unregister_class(GroupDeleter)
    bpy.utils.unregister_class(GroupDeleterMenu)
    bpy.types.MESH_MT_vertex_group_context_menu.remove(menu_func)

if __name__ == "__main__":
    register()
    bpy.ops.object.groupdeleter('INVOKE_DEFAULT')
