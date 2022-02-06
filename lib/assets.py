import os


def get_asset_path(name):
    script_file = os.path.realpath(__file__)
    directory = os.path.dirname(script_file)
    asset_path = os.path.join(directory, "..", "assets", "{}.blend".format(name))

    return os.path.abspath(asset_path)
