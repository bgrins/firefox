def simple(word):
    return bool(word & 0x80000000)


def cluster_start(word):
    return simple(word) or not word & 0x20000


def ligature_start(word):
    return simple(word) or not word & 0x40000


def advance(record, letter=0):
    word, details = record
    if simple(word):
        return (word >> 16) & 4095
    return sum(d[1] for d in details) + (len(details) - 1) * letter * bool(details and word & 0x80000)


def snapshot(records):
    return [[word, advance((word, details)), details] for word, details in records]


def oracle(case, unicode, original=False, signed=False, binary32=False):
    import struct
    def f32(value):
        return struct.unpack("<f",struct.pack("<f",value))[0] if binary32 else value
    records = [(g[0], [list(d) for d in g[1]]) for g in case["glyphs"]]
    before = snapshot(records)
    trace = []
    detail_count = sum(len(ds) for _, ds in records)
    for index, width, cp, eligible in unicode.decode(case["text"], case["latin"]):
        if original and unicode.categories[cp] == "Co":
            eligible = False
        if not eligible:
            for i in range(index, index + width):
                word, details = records[i]
                if simple(word):
                    trace.append(f"allocate:{detail_count}:1")
                    detail_count += 1
                    details = [[word & 65535, (word >> 16) & 4095, 0, 0]]
                    word = (word & 0x70000000) | 0x10001
                records[i] = (word | 0x400000, details)
    after = snapshot(records)
    words = [r[0] for r in records]
    n = len(records)
    cluster_starts = [i for i, w in enumerate(words) if cluster_start(w)]
    ligature_starts = [i for i, w in enumerate(words) if ligature_start(w)]
    ligatures = list(zip(ligature_starts, ligature_starts[1:] + [n]))
    has_spacing = case["provider"] and case["spacing_enabled"] and case["provider_enabled"]

    def partial_width(a, b):
        if a == b:
            return 0
        first, last = next((x, y) for x, y in ligatures if x <= a < y)
        assert b <= last
        width = sum(advance(g, case["letter"] if case["provider"] else 0) for g in records[first:last])
        if case["provider"]:
            trace.append(f"letter-spacing:{case['letter']}")
        starts = [i for i in cluster_starts if first <= i < last]
        selected = [i for i in starts if a <= i < b]
        count = len(starts)
        if signed:
            quotient = (abs(width)//count) * (-1 if width < 0 else 1)
            answer = len(selected)*quotient
            all_parts = count*quotient
        else:
            quotient = (width % (1 << 32))//count
            answer = (len(selected)*quotient) % (1 << 32)
            all_parts = (count*quotient) % (1 << 32)
        if b == last:
            answer += width-all_parts
        if case["provider"] and case["spacing_enabled"]:
            if a == first:
                trace.append(f"spacing:{a}:{a+1}:{int(case['provider_enabled'])}")
                if has_spacing:
                    answer += case["spacing"][a][0]
            if b == last:
                trace.append(f"spacing:{b-1}:{b}:{int(case['provider_enabled'])}")
                if has_spacing:
                    answer += case["spacing"][b - 1][1]
        return answer

    point = list(map(f32,case["point"]))
    axis = int(case["vertical"])
    direction = case["direction"]
    draw_spacing = has_spacing and not case["allocation_failure"]
    draws, identities = [], []
    for run_index, (ra, rb) in enumerate(zip(case["runs"], case["runs"][1:] + [n])):
        a, b = max(ra, case["range"][0]), min(rb, case["range"][1])
        selected_first = ra <= case["range"][0] < rb or (case["range"][0] == n and rb == n)
        if not selected_first and (a > b or ra >= case["range"][1] or rb <= case["range"][0]):
            continue
        boundaries = [i for i in ligature_starts + [n] if a <= i <= b]
        first = boundaries[0] if boundaries else b
        last = boundaries[-1] if boundaries else b
        point[axis] = f32(point[axis] + direction * partial_width(a, first))
        if case["provider"] and case["spacing_enabled"]:
            if case["allocation_failure"]:
                trace.append("spacing-allocation-failed")
            else:
                trace.append(f"allocate:0:{last-first}")
                if last > first:
                    trace.append(f"spacing:{first}:{last}:{int(case['provider_enabled'])}")
        starts = [i for i in cluster_starts if first <= i < last]
        for ca, cb in zip(starts, starts[1:] + [last]):
            spacing = case["spacing"][ca:cb] if draw_spacing else [(0, 0)] * (cb - ca)
            eligible = any(not w & 0x10000000 and (simple(w) or not w & 0x400000) for w in words[ca:cb])
            if binary32:
                head = f32(point[axis] + direction*spacing[0][0])
                for j,(record,(before_space,after_space)) in enumerate(zip(records[ca:cb],spacing)):
                    point[axis] = f32(point[axis]+direction*before_space)
                    point[axis] = f32(point[axis]+direction*advance(record))
                    if j+1 == cb-ca and eligible:
                        cluster_advance = f32(point[axis]-head)
                        delta = f32((cluster_advance+case["mark_advance"])/2)
                        point[axis] = f32(point[axis]-delta)
                        draws.append(list(point))
                        identities.append([run_index,ca,cb])
                        trace.append("draw:0:1")
                        point[axis] = f32(point[axis]+delta)
                    point[axis] = f32(point[axis]+direction*after_space)
            else:
                head = point[axis] + direction * spacing[0][0]
                cluster_advance = direction * (sum(advance(g) for g in records[ca:cb]) + sum(x + y for x, y in spacing) - spacing[0][0] - spacing[-1][1])
                if eligible:
                    position = list(point)
                    position[axis] = head + (cluster_advance - case["mark_advance"]) / 2
                    draws.append(position)
                    identities.append([run_index, ca, cb])
                    trace.append("draw:0:1")
                point[axis] += direction * (sum(advance(g) for g in records[ca:cb]) + sum(x + y for x, y in spacing))
        point[axis] = f32(point[axis] + direction * partial_width(last, b))
    return {"before": before, "after": after, "draws": draws, "identities": identities, "draw_units": [row[2]-1 for row in identities], "trace": trace}


def encode(case):
    n = len(case["text"])
    header = [n, int(case["latin"]), *case["range"], int(case["vertical"]), case["direction"], int(case["provider"]), int(case["provider_enabled"]), int(case["spacing_enabled"]), int(case["allocation_failure"]), case["mark_advance"], *case["point"], len(case["runs"]), case["letter"]]
    output = [" ".join(map(str, header))]
    for cp, (word, details), spacing in zip(case["text"], case["glyphs"], case["spacing"]):
        output.append(" ".join(map(str, [cp, word, len(details), *(v for d in details for v in d), *spacing])))
    output.append(" ".join(map(str, case["runs"])))
    return "\n".join(output) + "\n"
