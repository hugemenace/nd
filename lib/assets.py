# “Commons Clause” License Condition v1.0
# 
# See LICENSE for license details. If you did not receive a copy of the license,
# it may be obtained at https://github.com/hugemenace/nd/blob/main/LICENSE.
# 
# Software: ND Blender Addon
# License: MIT
# Licensor: T.S. & I.J. (HugeMenace)

import os


def get_asset_path(name):
    script_file = os.path.realpath(__file__)
    directory = os.path.dirname(script_file)
    asset_path = os.path.join(directory, "..", "assets", "{}.blend".format(name))

    return os.path.abspath(asset_path)
