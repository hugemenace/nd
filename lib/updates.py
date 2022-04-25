# “Commons Clause” License Condition v1.0
# 
# See LICENSE for license details. If you did not receive a copy of the license,
# it may be obtained at https://github.com/hugemenace/nd/blob/main/LICENSE.
# 
# Software: ND Blender Addon
# License: MIT
# Licensor: T.S. & I.J. (HugeMenace)

import bpy
import re
import requests


def update_available(version_tuple):
    try:
        response = requests.get('https://hugemenace.co/api/products/nd/version', timeout=2)

        if response.status_code == 200:
            json = response.json()
            latest_version = json["version"]
            current_version = '.'.join(map(str, list(version_tuple)))

            return current_version != latest_version
        else:
            return False
    except:
        return False
