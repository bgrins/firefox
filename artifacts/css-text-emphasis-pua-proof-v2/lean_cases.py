from fractions import Fraction
from native_oracle import cluster_start, ligature_start, simple


def boolean(value):
    return "true" if value else "false"


def rational(value):
    n = Fraction(value)
    return f"({n.numerator}/{n.denominator}:Rat)"


def glyph(record):
    word, details = record
    common = f"⟨⟨{(word >> 29) & 3},by decide⟩,{boolean(word & 0x10000000)}⟩"
    if simple(word):
        return f"(.simple {common} ⟨{word & 65535},by decide⟩ ⟨{(word >> 16) & 4095},by decide⟩ : Glyph)"
    flags = [not word & 0x20000, not word & 0x40000, not word & 0x10000, word & 0x100000, word & 0x200000, word & 0x800000, word & 0x80000, word & 0x400000]
    detail_terms = [f"⟨{d[0]},{d[1]},{rational(d[2])},{rational(d[3])}⟩" for d in details]
    return f"(.complex {common} ⟨{','.join(map(boolean,flags))}⟩ [{','.join(detail_terms)}] : Glyph)"


def emit(cases, expected, unicode, output, namespace="Finite", policy="legacyUnsigned32", historical=True):
    lines = ["import TextInput", f"namespace Emphasis.{namespace}", "set_option maxRecDepth 200000", "set_option maxHeartbeats 0", "set_option linter.unusedVariables false"]
    for number, (case, want) in enumerate(zip(cases, expected)):
        old = [glyph(g) for g in case["glyphs"]]
        after = [glyph([g[0], g[2]]) for g in want["after"]]
        units = ",".join(f"⟨{cp},by decide⟩" for cp in case["text"])
        decoded = unicode.decode(case["text"], case["latin"])
        accepted = sorted({cp for _, _, cp, eligible in decoded if eligible})
        eligibility = " || ".join(f"cp == {cp}" for cp in accepted) or "false"
        lines += [f"def before{number} : List Glyph := [{','.join(old)}]", f"def after{number} : List Glyph := [{','.join(after)}]"]
        lines.append(f"theorem flags{number} : applyFlags before{number} (loopFlags (fun cp => {eligibility}) [{units}]) = after{number} := by decide +kernel")
        words = [g[0] for g in want["after"]]
        n = len(words)
        cluster_starts = [i for i, w in enumerate(words) if cluster_start(w)]
        ligature_starts = [i for i, w in enumerate(words) if ligature_start(w)]
        has_spacing = case["provider"] and case["spacing_enabled"] and case["provider_enabled"]
        raw_data = []
        for i, term in enumerate(after):
            before, tail = case["spacing"][i] if has_spacing else (0, 0)
            raw_data.append(f"⟨{term},{before},{tail}⟩")
        clusters = {a: "[" + ",".join(raw_data[a:b]) + "]" for a, b in zip(cluster_starts, cluster_starts[1:] + [n])}
        ligatures = {a: "[" + ",".join(clusters[c] for c in cluster_starts if a <= c < b) + "]" for a, b in zip(ligature_starts, ligature_starts[1:] + [n])}
        runs = ["[" + ",".join(ligatures[l] for l in ligature_starts if a <= l < b) + "]" for a, b in zip(case["runs"], case["runs"][1:] + [n])]
        bounds = cluster_starts + [n]
        first, last = (bounds.index(x) for x in case["range"])
        draw_spacing = has_spacing and not case["allocation_failure"]
        letter = case["letter"] if case["provider"] else 0
        axis = int(case["vertical"])
        events = [Fraction(point[axis]) * 2 for point in want["draws"]]
        assert all(e.denominator == 1 for e in events)
        lines.append(f"def runs{number} : List Run.RawFontRun := [{','.join(runs)}]")
        lines.append(f"theorem shape{number} : Run.ValidShape runs{number} := by simp [Run.ValidShape,runs{number}]")
        if historical:
            lines.append(f"theorem geometry{number} : (Run.nativeActions {case['mark_advance']} (Run.ordinaryPlan runs{number} {boolean(draw_spacing)} ({case['direction']}) {letter} {first} {last}) ({case['point'][axis]})).2 = [{','.join(str(e.numerator) for e in events)}] := by decide +kernel")
        raw_units = [f"⟨{term},{case['spacing'][i][0]},{case['spacing'][i][1]}⟩" for i, term in enumerate(after)]
        raw_runs = [f"⟨{a},{b}⟩" for a,b in zip(case["runs"],case["runs"][1:]+[n])]
        provider = f"⟨{boolean(case['provider'])},{boolean(case['spacing_enabled'])},(fun _ _ => {boolean(case['provider_enabled'])}),(fun _ => {boolean(case['allocation_failure'])}),{case['letter']}⟩"
        setup_allocations = sum(simple(a[0]) and not simple(b[0]) for a,b in zip(case["glyphs"],want["after"]))
        dispatch_trace = want["trace"][setup_allocations:]
        event_terms = []
        positions = iter(events)
        for item in dispatch_trace:
            fields = item.split(":")
            if fields[0] == "draw":
                event_terms.append(f".draw ({next(positions).numerator})")
            elif fields[0] == "letter-spacing":
                event_terms.append(f".provider (.letter ({fields[1]}))")
            elif fields[0] == "allocate":
                assert fields[1] == "0"
                event_terms.append(f".provider (.allocation {fields[2]})")
            elif fields[0] == "spacing-allocation-failed":
                event_terms.append(".provider .allocationFailure")
            elif fields[0] == "spacing":
                event_terms.append(f".provider (.spacing {fields[1]} {fields[2]} {boolean(int(fields[3]))})")
            else:
                raise AssertionError(item)
        def raw_record(record,index):
            word,details=record
            ds=",".join(f"⟨{d[0]},{d[1]},{rational(d[2])},{rational(d[3])}⟩" for d in details)
            before,after=case["spacing"][index]
            return f"⟨{word},[{ds}],{before},{after}⟩"
        before_records=",".join(raw_record(g,i) for i,g in enumerate(case["glyphs"]))
        after_records=",".join(raw_record([g[0],g[2]],i) for i,g in enumerate(want["after"]))
        lines.append(f"def rawBefore{number} : List RawBridge.Record := [{before_records}]")
        lines.append(f"def rawAfter{number} : List RawBridge.Record := [{after_records}]")
        lines.append(f"theorem rawSetup{number} : List.zipWith RawBridge.flagRecord rawBefore{number} (loopFlags (fun cp => {eligibility}) [{units}]) = rawAfter{number} := by decide +kernel")
        lines.append(f"def rawUnits{number} : List Ligature.Unit := [{','.join(raw_units)}]")
        lines.append(f"theorem rawBridge{number} : rawAfter{number}.map RawBridge.decodeUnit = rawUnits{number} := by decide +kernel")
        lines.append(f"def rawRuns{number} : List Selection.Interval := [{','.join(raw_runs)}]")
        lines.append(f"theorem inputValid{number} : TextInput.Admitted rawBefore{number} [{units}] rawRuns{number} ⟨{case['range'][0]},{case['range'][1]}⟩ := ⟨by decide +kernel,by decide +kernel,by decide +kernel,by decide +kernel⟩")
        lines.append(f"theorem dispatch{number} : let result := Ordinary.nativeOrdinary .{policy} {provider} rawUnits{number} ({case['direction']}) ({case['mark_advance']}) rawRuns{number} ⟨{case['range'][0]},{case['range'][1]}⟩ ({case['point'][axis]}); result.draws = [{','.join(str(e.numerator) for e in events)}] ∧ result.events = [{','.join(event_terms)}] ∧ result.identities = [{','.join(map(str,want["draw_units"]))}] := by decide +kernel")
    lines.append(f"end Emphasis.{namespace}")
    output.write_text("\n\n".join(lines) + "\n")
