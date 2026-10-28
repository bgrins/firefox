import base64
import hashlib
import json
from pathlib import Path
import struct
import sys
import zlib



def decode_png(data):
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    offset = 8
    compressed = bytearray()
    while offset < len(data):
        size = struct.unpack_from(">I", data, offset)[0]
        kind = data[offset + 4:offset + 8]
        payload = data[offset + 8:offset + 8 + size]
        crc = struct.unpack_from(">I", data, offset + 8 + size)[0]
        assert zlib.crc32(kind + payload) & 0xffffffff == crc
        if kind == b"IHDR":
            width, height, depth, color, compression, filtering, interlace = struct.unpack(">IIBBBBB", payload)
            assert (depth, color, compression, filtering, interlace) == (8, 6, 0, 0, 0)
        elif kind == b"IDAT":
            compressed.extend(payload)
        offset += 12 + size
        if kind == b"IEND":
            break
    raw = zlib.decompress(compressed)
    stride = width * 4
    assert len(raw) == height * (stride + 1)
    rows = []
    previous = bytearray(stride)
    for y in range(height):
        start = y * (stride + 1)
        mode = raw[start]
        current = bytearray(raw[start + 1:start + 1 + stride])
        assert mode <= 4
        for i in range(stride):
            left = current[i - 4] if i >= 4 else 0
            above = previous[i]
            upper_left = previous[i - 4] if i >= 4 else 0
            predictors = (0, left, above, (left + above) // 2)
            if mode == 4:
                estimate = left + above - upper_left
                distances = [abs(estimate - x) for x in (left, above, upper_left)]
                predictor = (left, above, upper_left)[distances.index(min(distances))]
            else:
                predictor = predictors[mode]
            current[i] = (current[i] + predictor) & 255
        rows.append(current)
        previous = current
    return width, height, rows


def inspect(data):
    width, height, rows = decode_png(data)
    green = []
    other = set()
    for y, row in enumerate(rows):
        for x in range(width):
            pixel = tuple(row[4*x:4*x+4])
            if pixel == (0, 128, 0, 255):
                green.append((x, y))
            elif pixel != (255, 255, 255, 255):
                other.add(pixel)
    return {
        "width": width, "height": height,
        "green_pixels": len(green),
        "green_bounds_inclusive": [min(x for x, y in green), min(y for x, y in green),
                                   max(x for x, y in green), max(y for x, y in green)] if green else None,
        "other_nonwhite_colors": sorted(other),
        "sha256": hashlib.sha256(data).hexdigest(),
    }

