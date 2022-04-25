// “Commons Clause” License Condition v1.0
//
// See LICENSE for license details. If you did not receive a copy of the license,
// it may be obtained at https://github.com/hugemenace/nd/blob/main/LICENSE.
//
// Software: ND Blender Addon
// License: MIT
// Licensor: T.S. & I.J. (HugeMenace)

module.exports.readVersion = function (contents) {
    const regex = /"version": \(([0-9]+), ([0-9]+), ([0-9]+)\),/gm;
    const match = regex.exec(contents);

    return `${match[1]}.${match[2]}.${match[3]}`;
}

module.exports.writeVersion = function (contents, version) {
    const regex = /"version": \([0-9]+, [0-9]+, [0-9]+\),/gm;
    const v = version.split('.');

    return contents.replace(regex, `"version": (${v[0]}, ${v[1]}, ${v[2]}),`);
}