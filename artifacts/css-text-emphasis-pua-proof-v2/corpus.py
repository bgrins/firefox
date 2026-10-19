import random


def case_for(codepoints, seed=0, latin=False):
    rng = random.Random(seed)
    text, starts = [], []
    for cp in codepoints:
        starts.append(len(text))
        if cp < 65536:
            text.append(cp)
        else:
            text += [0xD800 + (cp - 65536) // 1024, 0xDC00 + (cp - 65536) % 1024]
    n = len(text)
    clusters = [i for i in starts if i == 0 or rng.randrange(3)]
    ligatures = [i for i in clusters if i == 0 or rng.randrange(3)]
    runs = [i for i in ligatures if i == 0 or rng.randrange(4) == 0]
    glyphs = []
    for i, cp in enumerate(text):
        common = rng.randrange(4) << 29 | (0x10000000 if cp == 32 else 0)
        glyph_id, advance = rng.randrange(65536), rng.randrange(1, 64)
        if i in ligatures and rng.randrange(2):
            word, details = common | 0x80000000 | advance << 16 | glyph_id, []
        else:
            count = rng.randrange(4)
            word = common | 0x10000 | (0 if i in clusters else 0x20000) | (0 if i in ligatures else 0x40000) | count
            word |= rng.choice([0, 0x100000, 0x200000, 0x800000, 0x80000])
            details = [[(glyph_id + j) % 65536, advance + j, j / 2, -j / 2] for j in range(count)]
        glyphs.append([word, details])
    spacing = [[rng.randrange(-2, 4) if i in ligatures else 0, rng.randrange(-2, 4) if i + 1 in ligatures or i + 1 == n else 0] for i in range(n)]
    bounds = clusters + [n]
    a, b = sorted([rng.choice(bounds), rng.choice(bounds)])
    return {"text": text, "glyphs": glyphs, "latin": latin, "range": [a, b], "runs": runs, "spacing": spacing, "vertical": bool(seed % 2), "direction": -1 if seed % 3 == 0 else 1, "provider": bool(seed % 5), "provider_enabled": bool(seed % 7), "spacing_enabled": bool(seed % 4), "allocation_failure": seed % 13 == 0, "letter": seed % 4, "mark_advance": seed % 9, "point": [seed % 11, -seed % 7]}


def corpus():
    result = []
    singles = [0, 9, 10, 32, 33, 35, 37, 38, 64, 65, 0xA7, 0xB6, 0x300, 0x378, 0x600, 0x609, 0x60A, 0x66A, 0x2000, 0x200D, 0x2028, 0x2029, 0x2030, 0x2031, 0x204A, 0x204B, 0x2053, 0x303D, 0xD7FF, 0xD800, 0xDBFF, 0xDC00, 0xDFFF, 0xE000, 0xF8FF, 0xF900, 0xFE5F, 0xFE60, 0xFE6A, 0xFE6B, 0xFF03, 0xFF05, 0xFF06, 0xFF20, 0xFFFF, 0x10000, 0x1F600, 0xEFFFF, 0xF0000, 0xFFFFD, 0xFFFFE, 0x100000, 0x10FFFD, 0x10FFFE, 0x10FFFF]
    for i, cp in enumerate(singles):
        for seed in range(4):
            c = case_for([cp], i * 4 + seed)
            c["range"] = [0, len(c["text"])]
            result.append(c)
    result.append(case_for([]))
    for seed in range(512):
        rng = random.Random(34567 + seed)
        cps = [rng.choice(singles) for _ in range(rng.randrange(1, 25))]
        # Do not construct an accidental adjacent surrogate pair across raw scalar entries.
        cps = [cp if not 0xD800 <= cp <= 0xDFFF else 0xE000 for cp in cps]
        result.append(case_for(cps, seed + 300))
    for seed in range(80):
        result.append(case_for(list(range(seed, seed + 32)), seed, True))
    for text in [[0xD800, 65], [65, 0xDC00], [0xDC00, 0xD800], [0xD800, 0xD800], [0xDC00, 0xDC00], [0xD800]]:
        for seed in range(8):
            c = case_for(text, seed)
            c["range"] = [0, len(text)]
            result.append(c)
    for i, record in enumerate([
        [0x8000FFFF, []],
        [0x8FFFFFFF, []],
        [0x00000001, [[0, 0, 0, 0]]],
        [0x00010000, []],
        [0x00410001, [[97, 23, 0.5, -0.5]]],
        [0x00F90001, [[65535, 4095, -0.5, 0.5]]],
    ]):
        for cp in [0xE000, 0x20, 0x41]:
            c = case_for([cp], 30 + i)
            c["glyphs"] = [[record[0] | (0x10000000 if cp == 0x20 else 0), record[1]]]
            c["range"] = [0, 1]
            c["runs"] = [0]
            result.append(c)
    for seed in range(8):
        c = case_for([0x20, 0x301], seed)
        c["glyphs"] = [[0x10010001, [[32, 10, 0, 0]]], [0x00070001, [[769, 0, 0, 0]]]]
        c["range"], c["runs"], c["spacing"] = [0, 2], [0], [[0, 0], [0, 0]]
        result.append(c)
    return result
