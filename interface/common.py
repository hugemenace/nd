# ███╗   ██╗██████╗
# ████╗  ██║██╔══██╗
# ██╔██╗ ██║██║  ██║
# ██║╚██╗██║██║  ██║
# ██║ ╚████║██████╔╝
# ╚═╝  ╚═══╝╚═════╝
#
# ND (Non-Destructive) Blender Add-on
# Copyright (C) 2024 Tristan S. & Ian J. (HugeMenace)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# ---
# Contributors: Tristo (HM)
# ---

from .. lib.preferences import get_preferences


def create_box(text, layout, props, prop_name, icons, shortcuts):
    box = layout.box()
    row = box.row(align=True)

    prop_active = getattr(props, prop_name)

    row.prop(props, prop_name,
        icon="TRIA_DOWN" if prop_active else "TRIA_RIGHT", icon_only=True, emboss=False
    )

    row.label(text=text)

    for op, mode in shortcuts:
        if mode:
            row.operator(op, icon=icons[f'{op}+{mode}'], text="").mode = mode
        else:
            row.operator(op, icon=icons[op], text="")

    if prop_active:
        return box.column()
    else:
        return None


def render_ops(ops, layout, new_row=True, use_separator=False):
    for op in ops:
        if op is None:
            if use_separator:
                layout.separator()
            continue

        op, icon, label, mode, experimental = op

        if experimental and not get_preferences().enable_experimental_features:
            continue

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
