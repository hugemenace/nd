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

import bpy
from . addons import get_registered_addon_name


def get_preferences():
    return bpy.context.preferences.addons[get_registered_addon_name()].preferences


def get_scene_unit_scale():
    if bpy.context.scene.unit_settings.system == 'NONE':
        return 1.0

    return bpy.context.scene.unit_settings.scale_length


def get_scene_unit_factor():
    if bpy.context.scene.unit_settings.system == 'NONE':
        return 1.0

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

    if bpy.context.scene.unit_settings.length_unit == 'ADAPTIVE':
        if bpy.context.scene.unit_settings.system == 'METRIC':
            return units['METERS']
        if bpy.context.scene.unit_settings.system == 'IMPERIAL':
            return units['FEET']

    return units[bpy.context.scene.unit_settings.length_unit]


def get_scene_unit_suffix():
    if bpy.context.scene.unit_settings.system == 'NONE':
        return ""

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

    if bpy.context.scene.unit_settings.length_unit == 'ADAPTIVE':
        if bpy.context.scene.unit_settings.system == 'METRIC':
            return units['METERS']
        if bpy.context.scene.unit_settings.system == 'IMPERIAL':
            return units['FEET']

    return units[bpy.context.scene.unit_settings.length_unit]
