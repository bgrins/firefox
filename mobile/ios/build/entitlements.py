# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# Generate the entitlements the iOS Simulator reads from the __entitlements
# (XML) and __ents_der (DER) sections of a binary. Simulator builds are signed
# ad hoc, which can't carry entitlements the way a device signature does.

import plistlib


def xml(output, entitlements, team_id, bundle_id):
    with open(entitlements, "rb") as fh:
        values = plistlib.load(fh)
    values["application-identifier"] = f"{team_id}.{bundle_id}"
    plistlib.dump(values, output, sort_keys=True)


def _der(tag, content):
    length = len(content)
    if length < 0x80:
        encoded_length = bytes([length])
    else:
        size = (length.bit_length() + 7) // 8
        encoded_length = bytes([0x80 | size]) + length.to_bytes(size, "big")
    return bytes([tag]) + encoded_length + content


def _der_value(value):
    if isinstance(value, bool):
        return _der(0x01, b"\xff" if value else b"\x00")
    if isinstance(value, int):
        size = (value.bit_length() + 8) // 8
        return _der(0x02, value.to_bytes(size, "big", signed=True))
    if isinstance(value, str):
        return _der(0x0C, value.encode("utf-8"))
    if isinstance(value, list):
        return _der(0x30, b"".join(_der_value(v) for v in value))
    if isinstance(value, dict):
        return _der(
            0xB0,
            b"".join(
                _der(0x30, _der_value(k) + _der_value(v))
                for k, v in sorted(value.items())
            ),
        )
    raise TypeError(f"Unsupported entitlement value: {value!r}")


def der(output, xcent):
    with open(xcent, "rb") as fh:
        values = plistlib.load(fh)
    output.write(_der(0x70, _der_value(1) + _der_value(values)))
