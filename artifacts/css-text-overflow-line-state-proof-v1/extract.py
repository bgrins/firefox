from pathlib import Path
import hashlib
import re

BASE = Path(__file__).resolve().parent


def mask_cpp(text):
    pattern = r'//[^\n]*|/\*[\s\S]*?\*/|R"([^ ()\\\t\n]{0,16})\([\s\S]*?\)\1"|"(?:\\[\s\S]|[^"\\])*"|\'(?:\\[\s\S]|[^\'\\])*\''
    return re.sub(pattern, lambda m: " " * len(m[0]), text)


def complete(text, signature, semicolon=False):
    assert text.count(signature) == 1, signature
    start = text.index(signature)
    masked = mask_cpp(text)
    opening = masked.index("{", start)
    depth = 1
    end = opening + 1
    while depth:
        depth += (masked[end] == "{") - (masked[end] == "}")
        end += 1
    if semicolon:
        assert text[end] == ";"
        end += 1
    return text[start:end], start, end


HEADER = ["struct AlignmentEdges", "struct InnerClipEdges", "class Marker"]
FUNCTIONS = [
    "static bool IsAtomicElement(",
    "static bool IsFullyClipped(",
    "static void InflateIStart(",
    "static void InflateIEnd(",
    "LogicalRect TextOverflow::GetLogicalScrollableOverflowRectRelativeToBlock(",
    "void TextOverflow::ExamineFrameSubtree(",
    "void TextOverflow::AnalyzeMarkerEdges(",
    "LogicalRect TextOverflow::ExamineLineFrames(",
    "void TextOverflow::ProcessLine(",
    "void TextOverflow::Marker::SetupString(",
]
OBSERVER_ANCHOR = "    if (!foundVisibleTextOrAtomic && retryEmptyLine) {"
OBSERVER = "    ObserveAttempt(contentArea, insideMarkersArea, *aFramesToHide, *aAlignmentEdges, foundVisibleTextOrAtomic, clippedMarkerEdges);\n"


def extract(variant="candidate", mutation=None):
    path = BASE / "source" / variant / "TextOverflow.cpp"
    header_path = BASE / "source/TextOverflow.h"
    cpp, header = path.read_text(), header_path.read_text()
    parts, declarations, binding = [], [], []
    for source, signatures, dest, semi, name in [
        (header, HEADER, declarations, True, "source/TextOverflow.h"),
        (cpp, FUNCTIONS, parts, False, str(path.relative_to(BASE))),
    ]:
        for signature in signatures:
            code, start, end = complete(source, signature, semi)
            dest.append(code)
            binding.append(dict(source=name, signature=signature, start=start,
                                end=end, sha256=hashlib.sha256(code.encode()).hexdigest()))
    core = "\n\n".join(parts)
    decl = "\n\n".join(declarations)
    if mutation:
        core, decl = mutation(core, decl)
    assert core.count(OBSERVER_ANCHOR) == 1
    observed = core.replace(OBSERVER_ANCHOR, OBSERVER + OBSERVER_ANCHOR)
    assert observed.replace(OBSERVER, "") == core
    return decl, observed, binding


def capsule(variant="candidate", mutation=None):
    decl, core, binding = extract(variant, mutation)
    prefix = (BASE / "adapter-prefix.cpp").read_text()
    middle = (BASE / "adapter-middle.cpp").read_text().replace("@@DECLARATIONS@@", decl)
    suffix = (BASE / "adapter-suffix.cpp").read_text()
    return prefix + middle + core + suffix, binding
