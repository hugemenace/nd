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

from . polling import app_minor_version


use_attribute_suffix = "_use_attribute"
attribute_name_suffix = "_attribute_name"


# From Blender 5.2, a geometry nodes modifier keeps its inputs on RNA, where earlier
# versions used ID properties. The modifier no longer supports ID properties at all,
# so every socket reader and writer has to branch on this.
def sockets_are_rna():
    return app_minor_version() >= (5, 2)


def node_input_entry(modifier, identifier):
    return getattr(modifier.properties.inputs, identifier, None)


def node_input_identifiers(modifier):
    if not sockets_are_rna():
        return [key for key in modifier.keys()
            if not key.endswith(use_attribute_suffix) and not key.endswith(attribute_name_suffix)]

    identifiers = []

    for input_property in modifier.properties.inputs.bl_rna.properties:
        if input_property.identifier in {'rna_type', 'name'}:
            continue

        entry = node_input_entry(modifier, input_property.identifier)

        # Geometry sockets carry no value at all, so they cannot be read or synced.
        if entry is None or not hasattr(entry, 'value'):
            continue

        identifiers.append(input_property.identifier)

    return identifiers


def get_node_input(modifier, identifier):
    if not sockets_are_rna():
        return modifier[identifier]

    return node_input_entry(modifier, identifier).value


def set_node_input(modifier, identifier, value):
    if not sockets_are_rna():
        modifier[identifier] = value
        return

    node_input_entry(modifier, identifier).value = value


def get_node_input_attribute_state(modifier, identifier):
    state = {}

    if not sockets_are_rna():
        if identifier + use_attribute_suffix in modifier:
            state["use_attribute"] = modifier[identifier + use_attribute_suffix]

        if identifier + attribute_name_suffix in modifier:
            state["attribute_name"] = modifier[identifier + attribute_name_suffix]

        return state

    entry = node_input_entry(modifier, identifier)

    if hasattr(entry, 'attribute_name'):
        state["use_attribute"] = entry.type == 'ATTRIBUTE'
        state["attribute_name"] = entry.attribute_name

    return state


def set_node_input_attribute_state(modifier, identifier, state):
    if not sockets_are_rna():
        if "use_attribute" in state:
            modifier[identifier + use_attribute_suffix] = bool(state["use_attribute"])

        if "attribute_name" in state:
            modifier[identifier + attribute_name_suffix] = state["attribute_name"]

        return

    entry = node_input_entry(modifier, identifier)

    if not hasattr(entry, 'attribute_name'):
        return

    if "use_attribute" in state:
        entry.type = 'ATTRIBUTE' if state["use_attribute"] else 'VALUE'

    if "attribute_name" in state:
        entry.attribute_name = state["attribute_name"]


def node_input_variable_path(modifier, identifier):
    if not sockets_are_rna():
        return f'modifiers["{modifier.name}"]["{identifier}"]'

    return f'modifiers["{modifier.name}"].properties.inputs.{identifier}.value'


def node_input_is_array(modifier, identifier):
    if not sockets_are_rna():
        value = modifier[identifier]
        return hasattr(value, '__len__') and not isinstance(value, str)

    return node_input_entry(modifier, identifier).bl_rna.properties['value'].array_length > 0


# Array sockets get one driver per component, which the single-driver callers
# cannot wire up, so refuse them outright rather than leaving a half-built
# driver on each component behind.
def add_node_input_driver(modifier, identifier):
    if node_input_is_array(modifier, identifier):
        return None

    if not sockets_are_rna():
        return modifier.driver_add(f'["{identifier}"]')

    return node_input_entry(modifier, identifier).driver_add('value')


def remove_node_input_driver(modifier, identifier):
    if not sockets_are_rna():
        return modifier.driver_remove(f'["{identifier}"]')

    entry = node_input_entry(modifier, identifier)

    if entry is None:
        return False

    return entry.driver_remove('value')
