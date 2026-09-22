# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# Rewrite the dependency file written by `swiftc -emit-dependencies` into the
# one the build includes for an object. swiftc has no equivalent of `-MP`, so
# this adds the empty rules that keep a removed header or module from breaking
# the next build.

import sys

from mozbuild.makeutil import read_dep_makefile, write_dep_makefile


def main(argv):
    source, target, dest = argv
    deps = []
    with open(source) as fh:
        for rule in read_dep_makefile(fh):
            deps.extend(rule.dependencies())
    with open(dest, "w") as fh:
        write_dep_makefile(fh, target, deps)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
