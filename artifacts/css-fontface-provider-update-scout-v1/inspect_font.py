import hashlib
import struct
from pathlib import Path

def inspect(path):
    data = Path(path).read_bytes()
    def u16(offset):
        return struct.unpack_from(">H", data, offset)[0]
    def u32(offset):
        return struct.unpack_from(">I", data, offset)[0]
    tables = {}
    for index in range(u16(4)):
        off = 12 + 16 * index
        name = data[off:off + 4].decode("ascii")
        start, length = u32(off + 8), u32(off + 12)
        assert start + length <= len(data)
        tables[name] = (start, length)
    units = u16(tables["head"][0] + 18)
    cmap = tables["cmap"][0]
    glyphs = []
    for index in range(u16(cmap + 2)):
        row = cmap + 4 + 8 * index
        if u16(row) not in [0, 3]:
            continue
        sub = cmap + u32(row + 4)
        if u16(sub) != 4:
            continue
        count = u16(sub + 6) // 2
        ends = sub + 14
        starts = ends + 2 * count + 2
        deltas = starts + 2 * count
        offsets = deltas + 2 * count
        for i in range(count):
            if u16(starts + 2 * i) <= 0x58 <= u16(ends + 2 * i):
                delta = u16(deltas + 2 * i)
                ro = u16(offsets + 2 * i)
                if ro:
                    address = offsets + 2 * i + ro + 2 * (0x58 - u16(starts + 2 * i))
                    glyph = u16(address)
                    if glyph:
                        glyph = (glyph + delta) & 0xffff
                else:
                    glyph = (0x58 + delta) & 0xffff
                glyphs.append(glyph)
                break
    assert glyphs and len(set(glyphs)) == 1
    glyph = glyphs[0]
    metrics = u16(tables["hhea"][0] + 34)
    advance = u16(tables["hmtx"][0] + 4 * min(glyph, metrics - 1))
    assert units == 1000 and advance == 1000
    return {"sha256": hashlib.sha256(data).hexdigest(), "unitsPerEm": units,
            "X_glyph": glyph, "X_advance": advance,
            "four_X_at_20px": 4 * 20 * advance / units,
            "four_X_at_20px_half_size": 4 * 20 * advance / units / 2}
