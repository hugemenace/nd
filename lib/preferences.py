# “Commons Clause” License Condition v1.0
# 
# See LICENSE for license details. If you did not receive a copy of the license,
# it may be obtained at https://github.com/hugemenace/nd/blob/main/LICENSE.
# 
# Software: ND Blender Addon
# License: MIT
# Licensor: T.S. & I.J. (HugeMenace)

import bpy


def get_registered_addon_name():
    return __name__.partition('.')[0]


def get_preferences():
    return bpy.context.preferences.addons[get_registered_addon_name()].preferences