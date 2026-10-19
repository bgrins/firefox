import hashlib
import json
import re
from pathlib import Path

from bridge import definition

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def extract(text, kind):
    if kind == "AutoIfOutside":
        a = text.index("  static int32_t AutoIfOutside(")
        return text[a:text.index("\n  }", a)+4]+"\n"
    if kind == "LineRangeAdapter":
        a = text.index("struct nsGridContainerFrame::LineRange {")
        b = text.index("  bool IsDefinite()", a)
        ua = text.index("  union {", b)
        ub = text.index("\n protected:", ua)
        return text[a:b].replace("struct nsGridContainerFrame::LineRange {", "struct LineRange {")+text[ua:ub]+"\n};\n"
    if kind == "declarations":
        declarations=[]
        for prefix in ["LinePair ResolveLineRangeHelper(","LineRange ResolveLineRange("]:
            a=text.index("  "+prefix)
            declarations.append(text[a:text.index(";",a)+1]+"\n")
        return "\n".join(declarations)
    if kind == "constants":
        pairs = [("int32_t","kMaxLine"),("int32_t","kMinLine"),("uint32_t","kTranslatedMaxLine"),("uint32_t","kAutoLine")]
        return "\n".join(l for l in text.splitlines() if any(l.startswith("static const "+t+" "+n+" =") for t,n in pairs))+"\n"
    return definition(text, kind)


def compact(text):
    return re.sub(r"\s+", "", re.sub(r"//[^\n]*|/\*.*?\*/", "", text, flags=re.S))


def shape(read):
    if "boolaIsAbsPos=false" not in compact(read("declarations.inc")):
        raise RuntimeError("Normal-flow default changed")
    helper = compact(read("ResolveLineRangeHelper-before.inc"))
    helper = helper.replace("constnsStylePosition*aStyle)","constnsStylePosition*aStyle,int32_taClampMinLine,int32_taClampMaxLine)")
    helper = helper.replace("aNameMap.mClampMinLine","aClampMinLine").replace("aNameMap.mClampMaxLine","aClampMaxLine")
    if helper != compact(read("ResolveLineRangeHelper-after.inc")):
        raise RuntimeError("Unexpected helper delta")
    final = compact(read("ResolveLineRange-before.inc"))
    final = final.replace("aNameMap.mClampMinLine","clampMinLine").replace("aNameMap.mClampMaxLine","clampMaxLine")
    final = final.replace("constnsStylePosition*aStyle){", "constnsStylePosition*aStyle,boolaIsAbsPos){constint32_tclampMinLine=aIsAbsPos?kMinLine:aNameMap.mClampMinLine;constint32_tclampMaxLine=aIsAbsPos?kMaxLine:aNameMap.mClampMaxLine;")
    final = final.replace("aExplicitGridEnd,aStyle);", "aExplicitGridEnd,aStyle,clampMinLine,clampMaxLine);")
    if final != compact(read("ResolveLineRange-after.inc")):
        raise RuntimeError("Unexpected finalizer delta")
    caller = compact(read("ResolveAbsPosLineRange-before.inc"))
    caller = caller.replace("ResolveLineRange(aStart,aEnd,aNameMap,aAxis,aExplicitGridEnd,aStyle)","ResolveLineRange(aStart,aEnd,aNameMap,aAxis,aExplicitGridEnd,aStyle,true)")
    if caller != compact(read("ResolveAbsPosLineRange-after.inc")):
        raise RuntimeError("Unexpected abspos caller delta")


def validate_record(record):
    if not isinstance(record,dict) or set(record) != {"source","before_source_sha256","after_source_sha256","records"}:
        raise RuntimeError("Source record shape")
    if record["source"] != "layout/generic/nsGridContainerFrame.cpp":
        raise RuntimeError("Source path")
    for key in ["before_source_sha256","after_source_sha256"]:
        if not isinstance(record[key],str) or not re.fullmatch(r"[0-9a-f]{64}",record[key]):
            raise RuntimeError("Source digest")
    expected = [(n+"-before.inc",n) for n in ["ResolveLine","ResolveLineRangeHelper","ResolveLineRange","ResolveAbsPosLineRange"]]
    expected += [("AutoIfOutside.inc","AutoIfOutside")]
    expected += [(n+"-after.inc",n) for n in ["ResolveLineRangeHelper","ResolveLineRange","ResolveAbsPosLineRange"]]
    expected += [("LineRange-adapter.inc","LineRangeAdapter"),("constants.inc","constants"),("declarations.inc","declarations")]
    if not isinstance(record["records"],list) or len(record["records"]) != len(expected):
        raise RuntimeError("Source inventory")
    for row,(name,kind) in zip(record["records"],expected):
        if not isinstance(row,dict) or set(row) != {"snapshot","kind","sha256"} or row["snapshot"] != name or row["kind"] != kind:
            raise RuntimeError("Source row")
        if not isinstance(row["sha256"],str) or not re.fullmatch(r"[0-9a-f]{64}",row["sha256"]):
            raise RuntimeError("Snapshot digest")


def sources(read, live=False):
    record = json.loads(read("SOURCE-v1.json"))
    validate_record(record)
    for row in record["records"]:
        if hashlib.sha256(read(row["snapshot"]).encode()).hexdigest() != row["sha256"]:
            raise RuntimeError("Source snapshot changed: "+row["snapshot"])
        if live and (not row["snapshot"].endswith("-before.inc") or row["kind"] == "ResolveLine"):
            if extract((ROOT/record["source"]).read_text(),row["kind"]) != read(row["snapshot"]):
                raise RuntimeError("Live source differs: "+row["kind"])
    if live and sha(ROOT/record["source"]) != record["after_source_sha256"]:
        raise RuntimeError("Live whole-source drift")
    shape(read)
    return record
