import json
import subprocess
from negative_corpus import negative_corpus
from native_oracle import oracle, encode
from lean_cases import emit
from numeric_domain import inspect as inspect_numeric_domain


def replay_negative(root, out, unicode, compile):
    cases=negative_corpus()
    data="".join(map(encode,cases))
    (out/"NEGATIVE-CORPUS.json").write_text(json.dumps(cases,separators=(",",":"))+"\n")
    receipts=[]
    observed={}
    for original in [False,True]:
        for signed in [False,True]:
            name="negative-"+("original" if original else "pua")+("-signed" if signed else "-legacy")
            executable=compile(name,"original" if original else "candidate",signed=signed)
            result=subprocess.run([str(executable)],input=data,capture_output=True,text=True)
            (out/(name+".stdout.jsonl")).write_text(result.stdout)
            (out/(name+".stderr.txt")).write_text(result.stderr)
            assert result.returncode==0,name
            actual=[json.loads(line) for line in result.stdout.splitlines()]
            assert len(actual)==len(cases)
            domains=[inspect_numeric_domain(case,signed) for case in cases]
            if signed:assert all(row["exact_operation_domain"] for row in domains)
            (out/(name+".numeric-domain.json")).write_text(json.dumps(domains,indent=2)+"\n")
            rounded=[oracle(case,unicode,original=original,signed=signed,binary32=True) for case in cases]
            exact=[oracle(case,unicode,original=original,signed=signed) for case in cases]
            for i,(a,r) in enumerate(zip(actual,rounded)):
                assert all(a[k]==r[k] for k in ["before","after","draws","trace","draw_units"]),(name,i,a,r)
            mismatches=[i for i,(a,e) in enumerate(zip(actual,exact)) if a["draws"]!=e["draws"]]
            if signed:assert not mismatches
            observed[(original,signed)]=actual
            receipts.append(dict(name=name,cases=len(cases),status="PASS",binary32_reference="matched",
                                 rational_geometry_differences=mismatches,
                                 claim="finite actual native dispatch with explicit binary32 reference; exact geometry theorem requires exact-operation premises"))
    unchanged=[]
    for original in [False,True]:
        for i,case in enumerate(cases):
            if case["glyphs"][0][1][0][1]>=0:
                assert observed[(original,False)][i]==observed[(original,True)][i]
                unchanged.append([original,i])
    ascii_changes=[]
    for original in [False,True]:
        changed=[i for i,case in enumerate(cases) if case["text"]==[65,66,67] and
                 observed[(original,False)][i]["draws"]!=observed[(original,True)][i]["draws"]]
        assert changed
        ascii_changes.append(dict(original_classifier=original,changed_draw_cases=changed))
    signed_expected=[oracle(case,unicode,signed=True) for case in cases]
    emit(cases,signed_expected,unicode,out/"NegativeFinite.lean",namespace="NegativeFinite",policy="signed",historical=False)
    (out/"NEGATIVE-RESULT.json").write_text(json.dumps(dict(variants=receipts,
        nonnegative_native_unchanged=unchanged,ascii_observable_changes=ascii_changes,signed_kernel_cases=len(cases)),indent=2)+"\n")
    return cases,receipts
