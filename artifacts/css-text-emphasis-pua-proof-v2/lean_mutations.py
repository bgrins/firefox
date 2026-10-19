from fractions import Fraction
from lean_cases import boolean, rational


def record(term,spacing):
    word,details=term
    ds=",".join(f"⟨{d[0]},{d[1]},{rational(d[2])},{rational(d[3])}⟩" for d in details)
    return f"⟨{word},[{ds}],{spacing[0]},{spacing[1]}⟩"


def emit_mutations(mutants,unicode,output):
    lines=["import RawBridge","namespace Emphasis.DispatchWitness",
           "set_option maxRecDepth 200000","set_option maxHeartbeats 0"]
    for mutant in mutants:
        name=mutant["name"];case=mutant["witness"]["input"];actual=mutant["witness"]["actual"]
        before=",".join(record(g,s) for g,s in zip(case["glyphs"],case["spacing"]))
        after=",".join(record([g[0],g[2]],s) for g,s in zip(actual["after"],case["spacing"]))
        units=",".join(f"⟨{cp},by decide⟩" for cp in case["text"])
        accepted=sorted({cp for _,_,cp,eligible in unicode.decode(case["text"],case["latin"]) if eligible})
        eligibility=" || ".join(f"cp == {cp}" for cp in accepted) or "false"
        binder="cp" if accepted else "_"
        provider=f"⟨{boolean(case['provider'])},{boolean(case['spacing_enabled'])},(fun _ _ => {boolean(case['provider_enabled'])}),(fun _ => {boolean(case['allocation_failure'])}),{case['letter']}⟩"
        n=len(case["text"]);runs=",".join(f"⟨{a},{b}⟩" for a,b in zip(case["runs"],case["runs"][1:]+[n]))
        axis=int(case["vertical"])
        positions=[2*Fraction(p[axis]) for p in actual["draws"]]
        assert all(p.denominator==1 for p in positions)
        positions=",".join(str(p.numerator) for p in positions)
        ids=",".join(map(str,actual["draw_units"]))
        lines.append(f"def input_{name} : List RawBridge.Record := [{before}]")
        lines.append(f"def actual_{name} : List RawBridge.Record := [{after}]")
        lines.append(f"theorem {name} : let after := List.zipWith RawBridge.flagRecord input_{name} (loopFlags (fun {binder} => {eligibility}) [{units}]); let result := Ordinary.nativeOrdinary .legacyUnsigned32 {provider} (after.map RawBridge.decodeUnit) ({case['direction']}) ({case['mark_advance']}) [{runs}] ⟨{case['range'][0]},{case['range'][1]}⟩ ({case['point'][axis]}); (after,result.draws,result.identities) ≠ (actual_{name},[{positions}],[{ids}]) := by decide +kernel")
    lines.append("end Emphasis.DispatchWitness")
    output.write_text("\n\n".join(lines)+"\n")
