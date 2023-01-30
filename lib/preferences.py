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
from . addons import get_registered_addon_name


def get_preferences():
    return bpy.context.preferences.addons[get_registered_addon_name()].preferences


def get_scene_unit_factor():
    units = {
        'KILOMETERS' : 1000,
        'METERS'     : 1,
        'CENTIMETERS': 0.01,
        'MILLIMETERS': 0.001,
        'MICROMETERS': 1e-6,
        'MILES'      : 1609.34,
        'FEET'       : 0.3048,
        'INCHES'     : 0.0254,
        'THOU'       : 0.0254 / 1000,
    }

    return units[bpy.context.scene.unit_settings.length_unit]


def get_scene_unit_suffix():
    units = {
        'KILOMETERS' : 'km',
        'METERS'     : 'm',
        'CENTIMETERS': 'cm',
        'MILLIMETERS': 'mm',
        'MICROMETERS': 'μm',
        'MILES'      : 'mi',
        'FEET'       : "'",
        'INCHES'     : '"',
        'THOU'       : 'thou',
    }

    return units[bpy.context.scene.unit_settings.length_unit]
