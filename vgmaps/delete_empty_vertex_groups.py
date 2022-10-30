# Short script to delete any empty vertex groups.  Run inside Blender.
# GitHub eArmada8/gust_stuff

import bpy
ob = bpy.context.object
assert ob.type == "MESH"
bpy.ops.object.mode_set(mode='OBJECT')
# Obtain list of all groups
all_groups = []
for group in ob.vertex_groups:
    all_groups.append(group.index)
assigned_groups = []
# Obtain list of all groups with vertices assigned to them
for vertex in ob.data.vertices:
    for group in vertex.groups:
        assigned_groups.append(group.group)
assigned_groups = list(set(assigned_groups))
empty_groups = [x for x in all_groups if x not in assigned_groups]
# Delete empty groups
for group in ob.vertex_groups:
    if group.index in empty_groups:
        ob.vertex_groups.remove(group)
