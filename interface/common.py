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

from .. import lib


def create_box(text, icon, layout):
    box = layout.box()
    if icon:
        box.label(text=text, icon=icon)
    else:
        box.label(text=text)

    return box.column()


def render_ops(ops, layout, new_row=True, use_separator=False):
    for op in ops:
        if op is None:
            if use_separator:
                layout.separator()
            continue

        op, icon, label, mode, deprecated = op
        if not deprecated or lib.preferences.get_preferences().enable_deprecated_features:
            if new_row:
                row = layout.row(align=True)
                row.scale_y = 1.2
            else:
                row = layout

            if mode:
                row.operator(op, icon=icon, text=label).mode = mode
            else: 
                row.operator(op, icon=icon, text=label)


def web_link(url, text, icon, layout):
    if icon:
        layout.operator("wm.url_open", text=text, icon=icon).url = url
    else:
        layout.operator("wm.url_open", text=text).url = url