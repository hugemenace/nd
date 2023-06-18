# ███╗   ██╗██████╗ 
# ████╗  ██║██╔══██╗
# ██╔██╗ ██║██║  ██║
# ██║╚██╗██║██║  ██║
# ██║ ╚████║██████╔╝
# ╚═╝  ╚═══╝╚═════╝ 
# 
# “Commons Clause” License Condition v1.0
# 
# See LICENSE for license details. If you did not receive a copy of the license,
# it may be obtained at https://github.com/hugemenace/nd/blob/main/LICENSE.
# 
# Software: ND Blender Addon
# License: MIT
# Licensor: T.S. & I.J. (HugeMenace)
# 
# ---
# Contributors: Tristo (HM)
# ---

import bpy
from .. lib.collections import move_to_utils_collection, isolate_in_utils_collection
from .. lib.preferences import get_preferences
from .. lib.modifiers import new_modifier, remove_problematic_bevels


keys = []


class ND_OT_bool_slice(bpy.types.Operator):
    bl_idname = "nd.bool_slice"
    bl_label = "Slice"
    bl_description = """Perform a boolean operation on the selected objects
ALT — Do not clean the reference object's mesh"""
    bl_options = {'UNDO'}

    
    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT':
            return len(context.selected_objects) == 2 and all(obj.type == 'MESH' for obj in context.selected_objects)


    def execute(self, context):
        solver = 'FAST' if get_preferences().use_fast_booleans else 'EXACT'

        a, b = context.selected_objects
        reference_obj = a if a.name != context.active_object.name else b
        
        difference_obj = context.active_object

        intersecting_obj = context.active_object.copy()
        intersecting_obj.data = context.active_object.data.copy()
        intersecting_obj.animation_data_clear()
        context.collection.objects.link(intersecting_obj)

        boolean_diff = new_modifier(difference_obj, "Difference — ND Bool", 'BOOLEAN', rectify=True)
        boolean_diff.operation = 'DIFFERENCE'
        boolean_diff.object = reference_obj
        boolean_diff.solver = solver

        boolean_isect = new_modifier(intersecting_obj, "Intersection — ND Bool", 'BOOLEAN', rectify=True)
        boolean_isect.operation = 'INTERSECT'
        boolean_isect.object = reference_obj
        boolean_isect.solver = solver
        
        reference_obj.display_type = 'WIRE'
        reference_obj.hide_render = True
        reference_obj.name = " — ".join(['Bool', reference_obj.name])
        reference_obj.data.name = reference_obj.name

        if not self.do_not_clean_mesh:
            remove_problematic_bevels(reference_obj)

        reference_obj.parent = difference_obj
        intersecting_obj.parent = difference_obj

        reference_obj.matrix_parent_inverse = difference_obj.matrix_world.inverted()
        intersecting_obj.matrix_parent_inverse = difference_obj.matrix_world.inverted()

        move_to_utils_collection(reference_obj)
        isolate_in_utils_collection([reference_obj])

        bpy.ops.object.select_all(action='DESELECT')
        reference_obj.select_set(True)
        bpy.context.view_layer.objects.active = reference_obj

        return {'FINISHED'}


    def invoke(self, context, event):
        self.do_not_clean_mesh = event.alt

        return self.execute(context)

    
def register():
    bpy.utils.register_class(ND_OT_bool_slice)

    for mapping in [('Mesh', 'EMPTY'), ('Object Mode', 'EMPTY')]:
        keymap = bpy.context.window_manager.keyconfigs.addon.keymaps.new(name=mapping[0], space_type=mapping[1])
        entry = keymap.keymap_items.new("nd.bool_slice", 'NUMPAD_SLASH', 'PRESS', ctrl = True)
        keys.append((keymap, entry))


def unregister():
    for keymap, entry in keys:
        keymap.keymap_items.remove(entry)

    keys.clear()

    bpy.utils.unregister_class(ND_OT_bool_slice)
