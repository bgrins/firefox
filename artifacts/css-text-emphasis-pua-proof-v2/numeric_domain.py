from native_oracle import advance, ligature_start


def inspect(case,signed):
    records=case["glyphs"]
    letter=case["letter"] if case["provider"] else 0
    assert all(isinstance(v,int) for v in case["point"]+[case["mark_advance"],letter])
    assert all(isinstance(v,int) for pair in case["spacing"] for v in pair)
    assert all(-(1<<31)<=d[1]<(1<<31) for _,details in records for d in details)
    width_abs=sum(abs(advance(g,letter))+abs(advance(g)) for g in records)
    spacing_abs=sum(abs(v) for pair in case["spacing"] for v in pair)
    bound=max(map(abs,case["point"]))+4*len(case["runs"])*(2*width_abs+spacing_abs)+2*width_abs+2*spacing_abs+abs(case["mark_advance"])+1
    starts=[i for i,(word,_) in enumerate(records) if ligature_start(word)]
    totals=[sum(advance(g,letter) for g in records[a:b]) for a,b in zip(starts,starts[1:]+[len(records)])]
    assert all(-(1<<31)<=width<(1<<31) for width in totals)
    exact_domain=(signed or all(width>=0 for width in totals)) and bound<(1<<22)
    return dict(policy="signed" if signed else "legacyUnsigned32",raw_units=len(records),
                signed_ligature_totals=totals,conservative_half_grid_bound=bound,
                exact_operation_domain=exact_domain,
                basis="raw integer inputs; signed apportionment magnitude bound (or nonnegative legacy agreement); every ordinary coordinate/midpoint/restore remains on a binary32-exact half-integer grid within conservative bound; no universal IEEE/compiler proof")
