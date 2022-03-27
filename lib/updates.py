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
