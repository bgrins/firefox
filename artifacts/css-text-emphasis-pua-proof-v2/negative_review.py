import hashlib
import json
import struct
from extract import definition


def sha(data):
    return hashlib.sha256(data).hexdigest()


def u16(data,offset):
    return struct.unpack_from(">H",data,offset)[0]


def u32(data,offset):
    return struct.unpack_from(">I",data,offset)[0]


def checksum(data):
    data=data+bytes(-len(data)%4)
    return sum(struct.unpack(">"+"I"*(len(data)//4),data))%(1<<32)


def tables(data):
    assert u32(data,0)==0x10000 and checksum(data)==0xB1B0AFBA
    result={}
    for i in range(u16(data,4)):
        tag,want,start,size=struct.unpack_from(">4sIII",data,12+16*i)
        assert start+size<=len(data) and tag not in result
        body=data[start:start+size]
        check=body[:8]+bytes(4)+body[12:] if tag==b"head" else body
        assert checksum(check)==want,tag
        result[tag]=body
    return result


def cmap(data,cp):
    found=set()
    for i in range(u16(data,2)):
        base=u32(data,8+8*i)
        if u16(data,base)!=4:continue
        segments=u16(data,base+6)//2
        ends=base+14;starts=ends+2*segments+2;deltas=starts+2*segments;ranges=deltas+2*segments
        for j in range(segments):
            lo,hi=u16(data,starts+2*j),u16(data,ends+2*j)
            if not lo<=cp<=hi:continue
            delta=struct.unpack_from(">h",data,deltas+2*j)[0]
            offset=u16(data,ranges+2*j)
            value=cp if not offset else u16(data,ranges+2*j+offset+2*(cp-lo))
            found.add((value+delta)%65536 if value or not offset else 0)
    assert len(found)==1 and 0 not in found
    return found.pop()


def layout(data,tag,kind):
    assert u32(data,0)==0x10000
    scripts,features,lookups=(u16(data,i) for i in [4,6,8])
    assert u16(data,scripts)==1 and data[scripts+2:scripts+6]==b"DFLT"
    script=scripts+u16(data,scripts+6);language=script+u16(data,script)
    assert u16(data,script+2)==0 and u16(data,language+2)==0xFFFF
    assert u16(data,language+4)==1 and u16(data,language+6)==0
    assert u16(data,features)==1 and data[features+2:features+6]==tag
    feature=features+u16(data,features+6)
    assert u16(data,feature)==0 and u16(data,feature+2)==1 and u16(data,feature+4)==0
    assert u16(data,lookups)==1
    lookup=lookups+u16(data,lookups+2)
    assert u16(data,lookup)==kind and u16(data,lookup+2)==0 and u16(data,lookup+4)==1
    return lookup+u16(data,lookup+6)


def coverage(data,start):
    assert u16(data,start)==1
    return [u16(data,start+4+2*i) for i in range(u16(data,start+2))]


def font_review(data):
    t=tables(data);mapping={cp:cmap(t[b"cmap"],cp) for cp in [65,66,67]}
    units=u16(t[b"head"],18);metrics=u16(t[b"hhea"],34)
    advances={cp:u16(t[b"hmtx"],4*min(glyph,metrics-1)) for cp,glyph in mapping.items()}
    sub=t[b"GSUB"];base=layout(sub,b"liga",4)
    assert u16(sub,base)==1 and u16(sub,base+4)==1
    covered=coverage(sub,base+u16(sub,base+2))
    ligset=base+u16(sub,base+6);assert u16(sub,ligset)==1
    ligature=ligset+u16(sub,ligset+2)
    replacement=u16(sub,ligature);components=u16(sub,ligature+2)
    assert covered==[mapping[65]] and components==2 and u16(sub,ligature+4)==mapping[66]
    assert replacement==mapping[67]
    pos=t[b"GPOS"];base=layout(pos,b"kern",1)
    assert u16(pos,base)==1 and u16(pos,base+4)==4
    assert coverage(pos,base+u16(pos,base+2))==[replacement]
    adjustment=struct.unpack_from(">h",pos,base+6)[0]
    assert units==1000 and advances=={65:1000,66:1000,67:1000} and adjustment==-2500
    return dict(font_sha256=sha(data),glyph_mapping=mapping,units_per_em=units,
                base_advances=advances,substitution="A B -> C",positioning_xAdvance=adjustment,
                resulting_advance_units=advances[67]+adjustment,resulting_advance_at_20px=-30,
                scope="independent SFNT table/feature/lookup/coverage/metric decoding; not a HarfBuzz or font-sanitizer proof")


def statuses(path):
    rows={}
    for line in path.read_text().splitlines():
        row=json.loads(line)
        if row.get("action") not in ["test_status","test_end"]:continue
        key=(row["action"],row["test"],row.get("subtest",""))
        assert key not in rows
        rows[key]=(row["status"],row.get("expected",row["status"]),tuple(row.get("known_intermittent",[])))
    return rows


def review(root,out):
    evidence=root/"negative-review"
    for row in json.loads((evidence/"RETAINED.json").read_text()):
        assert sha((evidence/row["path"]).read_bytes())==row["sha256"]
    font=evidence/"sources/testing/web-platform/tests/css/css-text/shaping/support/negative-ligature-advance.ttf"
    report=font_review(font.read_bytes())
    before=statuses(evidence/"wpt-baseline-v1.jsonl");after=statuses(evidence/"wpt-candidate-v1.jsonl")
    assert before.keys()==after.keys() and len(before)==49
    predictions=[]
    for key,value in before.items():
        if key[0]=="test_end":assert value[0]==after[key][0]=="OK";continue
        text,liga,kern,direction,partition=key[2].split(", ")
        vulnerable=text=="AB" and liga=="liga 1" and kern=="kern 1" and partition in ["nodes","spans"]
        expected="FAIL" if vulnerable else "PASS"
        assert value[0]==expected and after[key][0]=="PASS"
        predictions.append(dict(subtest=key[2],predicted_original=expected,observed_original=value[0],candidate=after[key][0]))
    assert sum(row["predicted_original"]=="FAIL" for row in predictions)==4
    pairs=[]
    for prefix in ["wpt","regressions"]:
        a=json.loads((evidence/(prefix+"-baseline-v1-receipt.json")).read_text())
        b=json.loads((evidence/(prefix+"-candidate-v1-receipt.json")).read_text())
        for row in [a,b]:
            assert row["pins_before"]==row["pins_after"] and row["all_inputs_unchanged"]
            assert row["absent_before"]==row["absent_after"] and row["suite_end_count"]==1
        assert a["pins_before"].keys()==b["pins_before"].keys()
        changed=[key for key in a["pins_before"] if a["pins_before"][key]!=b["pins_before"][key]]
        assert set(changed)=={"gfx/thebes/gfxTextRun.cpp","objdir-full.noindex/dist/Nightly.app/Contents/MacOS/XUL","objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox"}
        pairs.append(dict(kind=prefix,pins=len(a["pins_before"]),changed=changed))
    regressions_before=statuses(evidence/"regressions-baseline-v1.jsonl")
    regressions_after=statuses(evidence/"regressions-candidate-v1.jsonl")
    assert regressions_before==regressions_after
    source_only={
        "gfx/thebes/gfxHarfBuzzShaper.cpp":["bool gfxHarfBuzzShaper::ShapeText", "nsresult gfxHarfBuzzShaper::SetGlyphsFromRun"],
        "gfx/thebes/gfxTextRun.cpp":["void gfxTextRun::DrawPartialLigature", "void gfxTextRun::AccumulateMetricsForRun", "void gfxTextRun::AccumulatePartialLigatureMetrics", "gfxTextRun::Metrics gfxTextRun::MeasureText", "uint32_t gfxTextRun::BreakAndMeasureText", "gfxFloat gfxTextRun::GetAdvanceWidth", "gfxFloat gfxTextRun::GetMinAdvanceWidth"],
    }
    inventory=[];retained=out/"negative-source-callers";retained.mkdir()
    for path,markers in source_only.items():
        source=(evidence/"sources"/path).read_text()
        for marker in markers:
            body=definition(source,marker);name=f"{len(inventory):02}.cpp.txt"
            (retained/name).write_text(body+"\n")
            inventory.append(dict(path=path,marker=marker,body_sha256=sha(body.encode()),body_bytes=len(body.encode()),retained=name,status="complete source-only provider/consumer; not compiled or universally proved by the emphasis bridge"))
    (retained/"INVENTORY.json").write_text(json.dumps(inventory,indent=2)+"\n")
    result=dict(source_only_closure=inventory,font=report,wpt_predictions=predictions,pairs=pairs,regression_raw_keys=len(regressions_before),
                limitations=["Recorded root browser executions are reviewed; this worker did not rerun browser/build.",
                "The 25/80 pin invariance and binary identity are rooted in retained execution receipts, not fresh hashes of historical binaries.",
                "Exact negative-width clipping/rasterization is not a WPT assertion or formal claim.",
                "Current primary CSS/OpenType retrieval blocked by API authentication; dated-source freshness review remains open."])
    (out/"NEGATIVE-INDEPENDENT-REVIEW.json").write_text(json.dumps(result,indent=2)+"\n")
    return result
