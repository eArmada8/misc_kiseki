# Short script to change Y up / -X forward to Z up / Y forward.  Run inside Blender.
# GitHub eArmada8/kiseki_stuff

import bpy
ob = bpy.context.object
assert ob.type == "MESH"
bpy.ops.object.mode_set(mode='OBJECT')

# Obtain list of all groups with vertices assigned to them
for i in range(len(ob.data.vertices)):
    position = ob.data.vertices[i].co
    ob.data.vertices[i].co = [position[0], position[2], -position[1]]
