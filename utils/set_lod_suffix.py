import bpy
import re


class ND_OT_set_lod_suffix(bpy.types.Operator):
    bl_idname = "nd.set_lod_suffix"
    bl_label = "Set LOD Suffix"
    bl_description = "Suffixes all selected objects with the specified LOD"
    bl_options = {'UNDO'}


    suffix: bpy.props.EnumProperty(items=[
        ('HIGH', 'High', 'Updates the selected object names with a _high suffix'),
        ('LOW', 'Low', 'Updates the selected object names with a _low suffix'),
    ], name="Suffix", default='HIGH')


    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT':
            return len(context.selected_objects) >= 1 and all(obj.type == 'MESH' for obj in context.selected_objects)


    def execute(self, context):
        for obj in context.selected_objects:
            # Remove Blender's .001, .002, etc naming convention
            old_name = re.sub(r"(.+?)(\.[0-9]{3})$", r"\1", obj.name)

            name_segments = old_name.split("_")
            
            # Remove existing _high / _low suffixes.
            if name_segments[-1].startswith("high") or name_segments[-1].startswith("low"):
                name_segments = name_segments[:-1]
            
            name_segments.append(self.suffix.lower())
            new_name = "_".join(name_segments)

            obj.name = new_name
            obj.data.name = new_name

        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(ND_OT_set_lod_suffix.bl_idname, text=ND_OT_set_lod_suffix.bl_label)


def register():
    bpy.utils.register_class(ND_OT_set_lod_suffix)


def unregister():
    bpy.utils.unregister_class(ND_OT_set_lod_suffix)
