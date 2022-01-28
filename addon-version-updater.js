module.exports.readVersion = function (contents) {
    const regex = /"version": \(([0-9]), ([0-9]), ([0-9])\),/gm;
    const match = regex.exec(contents);

    return `${match[1]}.${match[2]}.${match[3]}`;
}

module.exports.writeVersion = function (contents, version) {
    const regex = /"version": \([0-9], [0-9], [0-9]\),/gm;
    const v = version.split('.');

    return contents.replace(regex, `"version": (${v[0]}, ${v[1]}, ${v[2]}),`);
}