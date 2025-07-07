import bpy
import mathutils
import bpy_extras

draw_data = {
    "start_point": None,
    "end_point": None,
    "hit_normal": None,
    "plane_axes": None,
}


def ray_plane_intersection(ray_origin, ray_direction, plane_point, plane_normal):
    denom = ray_direction.dot(plane_normal)
    if abs(denom) < 1e-6:
        return None
    d = (plane_point - ray_origin).dot(plane_normal) / denom
    if d < 0:
        return None
    return ray_origin + ray_direction * d


def get_stable_plane_axes(normal):
    up = mathutils.Vector((0.0, 0.0, 1.0))
    if abs(normal.dot(up)) > 0.999:
        up = mathutils.Vector((0.0, 1.0, 0.0))
    tangent = normal.cross(up).normalized()
    bitangent = normal.cross(tangent).normalized()
    return tangent, bitangent


class ModalRectangleOperator(bpy.types.Operator):
    bl_idname = "mesh.modal_rectangle_operator"
    bl_label = "Modal Rectangle Operator"
    bl_options = {'REGISTER', 'UNDO'}

    def __init__(self):
        self.dragging = False

    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            self.dragging = False
            draw_data["start_point"] = None
            draw_data["end_point"] = None
            draw_data["hit_normal"] = None
            draw_data["plane_axes"] = None

            context.window_manager.modal_handler_add(self)
            context.area.tag_redraw()
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not found, can't run operator")
            return {'CANCELLED'}

    def get_mouse_raycast(self, context, event):
        region = context.region
        rv3d = context.space_data.region_3d
        coord = (event.mouse_region_x, event.mouse_region_y)

        depsgraph = context.evaluated_depsgraph_get()

        view_vector = bpy_extras.view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
        ray_origin = bpy_extras.view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)

        result, location, normal, _, _, _ = context.scene.ray_cast(depsgraph, ray_origin, view_vector)

        return result, location, normal

    def create_rectangle_mesh(self):
        start = draw_data["start_point"]
        end = draw_data["end_point"]
        normal = draw_data["hit_normal"]
        tangent, bitangent = draw_data["plane_axes"]

        if None in (start, end, normal, tangent, bitangent):
            print("Missing data, can't create rectangle")
            return

        local_vector = end - start
        x_len = local_vector.dot(tangent)
        y_len = local_vector.dot(bitangent)

        corners = [
            start,
            start + tangent * x_len,
            start + tangent * x_len + bitangent * y_len,
            start + bitangent * y_len,
        ]

        mesh = bpy.data.meshes.new("ModalRectangle")
        mesh.from_pydata(corners, [], [(0, 1, 2, 3)])
        mesh.update()

        obj = bpy.data.objects.new("ModalRectangle", mesh)
        bpy.context.collection.objects.link(obj)

        print("Rectangle created")

    def modal(self, context, event):
        if event.type in {'ESC', 'RIGHTMOUSE'}:
            return {'CANCELLED'}

        if event.type == 'LEFTMOUSE':
            if event.value == 'PRESS':
                hit, location, normal = self.get_mouse_raycast(context, event)
                if hit:
                    draw_data["start_point"] = location
                    draw_data["hit_normal"] = normal

                    tangent, bitangent = get_stable_plane_axes(normal)
                    draw_data["plane_axes"] = (tangent, bitangent)
                    draw_data["end_point"] = location
                    self.dragging = True
            elif event.value == 'RELEASE' and self.dragging:
                self.create_rectangle_mesh()
                return {'FINISHED'}

        if event.type == 'MOUSEMOVE' and self.dragging:
            region = context.region
            rv3d = context.space_data.region_3d
            coord = (event.mouse_region_x, event.mouse_region_y)

            view_vector = bpy_extras.view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
            ray_origin = bpy_extras.view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)

            plane_point = draw_data["start_point"]
            plane_normal = draw_data["hit_normal"]

            end_point = ray_plane_intersection(ray_origin, view_vector, plane_point, plane_normal)

            if end_point is not None:
                draw_data["end_point"] = end_point

        context.area.tag_redraw()
        return {'RUNNING_MODAL'}


addon_keymaps = []


def register():
    bpy.utils.register_class(ModalRectangleOperator)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new(ModalRectangleOperator.bl_idname, type='Q', value='PRESS', alt=True)
        addon_keymaps.append((km, kmi))


def unregister():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    bpy.utils.unregister_class(ModalRectangleOperator)


if __name__ == "__main__":
    register()
