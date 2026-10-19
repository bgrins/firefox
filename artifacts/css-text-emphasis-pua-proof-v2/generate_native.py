import json
import re
from pathlib import Path
from extract import definition, digest
from mutations import MUTATIONS
from arithmetic_mutations import ARITHMETIC_MUTATIONS


def generate(root, output, variant="candidate", mutant=None, signed=False, arithmetic_mutant=None):
    records = []
    applied = []
    definitions = {}

    def macro(path, name):
        source = (root / path).read_text()
        start = source.index("#define " + name + "(")
        end = source.index("\n", start)
        while source[end - 1] == "\\":
            end = source.index("\n", end + 1)
        value = source[start:end]
        records.append({"path": path, "macro": name, "sha256": digest(value), "bytes": len(value.encode())})
        return value

    def whole(path, marker, semi=False):
        source = (root / path).read_text()
        value = definition(source, marker, semi)
        records.append({"path": path, "marker": marker, "sha256": digest(value), "bytes": len(value.encode())})
        if mutant and MUTATIONS[mutant][0] == marker:
            _, before, after = MUTATIONS[mutant]
            assert value.count(before) == 1, (mutant, marker)
            value = value.replace(before, after)
            applied.append(mutant)
        if arithmetic_mutant and marker == "gfxTextRun::LigatureData gfxTextRun::ComputeLigatureData":
            assert signed
            before,after=ARITHMETIC_MUTATIONS[arithmetic_mutant]
            assert value.count(before)==1
            value=value.replace(before,after)
            applied.append(arithmetic_mutant)
        if marker == "void gfxFont::DrawEmphasisMarks":
            call = "aParams.mark->Draw(markRange, *aPt, params, aImgParams);"
            observed = value.replace(call, "drawUnits.push_back(idx);\n      " + call)
            assert observed.replace("drawUnits.push_back(idx);\n      ", "") == value
            records[-1]["observer_insertions"] = value.count(call)
            records[-1]["observer_body_sha256"] = digest(observed)
            value = observed
        definitions[marker] = value
        return value

    def section(path, start, end):
        source = (root / path).read_text()
        i = source.index(start)
        j = source.index(end, i + len(start))
        value = source[i:j]
        records.append({"path": path, "start": start, "end": end, "sha256": digest(value), "bytes": len(value.encode())})
        return value

    font_h = "sources/gfx/thebes/gfxFont.h"
    font_cpp = "sources/gfx/thebes/gfxFont.cpp"
    run_h = "sources/gfx/thebes/gfxTextRun.h"
    run_cpp = "negative-candidate/gfx/thebes/gfxTextRun.cpp" if signed else "sources/gfx/thebes/gfxTextRun.cpp"
    frame = variant + "/layout/generic/nsTextFrame.cpp"
    trie = "sources/intl/icu/source/common/utrie2.h"
    result = [(root / "native_support.inc").read_text()]
    result += ["using UChar32=int32_t; using UBool=bool; struct UNewTrie2; using UVersionInfo=uint8_t[4];"]
    result += [whole(trie, "struct UTrie2 {", True)]
    result += [section(trie, "enum {\n    /** Shift size", "/* Internal functions and macros")]
    for name in ["_UTRIE2_INDEX_RAW", "_UTRIE2_INDEX_FROM_SUPP", "_UTRIE2_INDEX_FROM_CP", "_UTRIE2_GET", "UTRIE2_GET16"]:
        result.append(macro(trie, name))
    result += [section("sources/intl/icu/source/common/uchar_props_data.h", "static const UVersionInfo dataVersion", "static const uint16_t propsVectorsTrie_index")]
    for path, name in [("sources/intl/icu/source/common/uchar.cpp", "GET_PROPS"), ("sources/intl/icu/source/common/uprops.h", "GET_CATEGORY")]:
        result.append(macro(path, name))
    result += [whole("sources/intl/icu/source/common/uchar.cpp", "u_charType(UChar32 c)")]
    result[-1] = "int8_t\n" + result[-1]
    result += [whole("sources/intl/icu/source/common/unicode/uchar.h", "typedef enum UCharCategory", False) + " UCharCategory;"]
    result += [whole("sources/gfx/harfbuzz/src/hb-unicode.h", "typedef enum\n{", False) + " hb_unicode_general_category_t;"]
    result += [whole("sources/intl/unicharutil/nsUGenCategory.h", "enum class nsUGenCategory", True)]
    result += ["namespace mozilla::intl {", whole("sources/intl/components/src/GeneralCategory.h", "enum class GeneralCategory", True), "struct UnicodeProperties {", whole("sources/intl/components/src/UnicodeProperties.h", "static inline GeneralCategory CharType"), "}; }"]
    result += ["namespace mozilla::unicode {"]
    for marker in ["const nsUGenCategory sDetailedToGeneralCategory", "const hb_unicode_general_category_t sICUtoHBcategory"]:
        result += [whole("sources/intl/unicharutil/util/nsUnicodeProperties.cpp", marker, True)]
    for marker in ["inline uint8_t GetGeneralCategory", "inline nsUGenCategory GetGenCategory"]:
        result += [whole("sources/intl/unicharutil/util/nsUnicodeProperties.h", marker)]
    result += ["}", "using namespace mozilla;"]
    result += ["constexpr inline char32_t kPlane1Base = 0x00010000;"]
    for marker in ["constexpr bool IsHighSurrogate", "constexpr bool IsLowSurrogate", "constexpr bool IsSurrogatePair", "constexpr char32_t SurrogateToUCS4"]:
        result += [whole("sources/mfbt/Utf16.h", marker)]
    result += [whole(frame, "static bool MayCharacterHaveEmphasisMark")]
    result += ["class gfxShapedText { public:"]
    for marker in ["class CompressedGlyph {", "struct DetailedGlyph {", "class DetailedGlyphStore {"]:
        result += [whole(font_h, marker, True)]
    result += [(root / "native_shaped.inc").read_text()]
    for marker in ["DetailedGlyph* GetDetailedGlyphs", "void EnsureComplexGlyph(uint32_t aIndex, CompressedGlyph&", "uint32_t GetLength() const"]:
        result += [whole(font_h, marker)]
    result += ["};"]
    result += ["class gfxTextRun; struct EmphasisMarkDrawParams; class gfxFont { public:", whole(font_h, "struct Spacing {", True)]
    result += ["void DrawEmphasisMarks(const gfxTextRun*, gfx::Point*, uint32_t, uint32_t, const EmphasisMarkDrawParams&, imgDrawingParams&); };", whole(font_h, "struct MOZ_STACK_CLASS EmphasisMarkDrawParams", True)]
    result += ["class gfxTextRun : public gfxShapedText { public:", whole(run_h, "struct Range {", True), whole(run_h, "struct LigatureData {", True)]
    result += [(root / "native_run.inc").read_text()]
    result += [whole(run_h, "class MOZ_STACK_CLASS GlyphRunIterator", True)]
    for marker in ["bool IsClusterStart(uint32_t aPos) const", "bool IsLigatureGroupStart(uint32_t aPos) const", "bool CharMayHaveEmphasisMark(uint32_t aPos) const", "void SetNoEmphasisMark(uint32_t aIndex)", "CompressedGlyph& EnsureComplexGlyph(uint32_t aIndex)", "nscoord GetAdvanceForGlyph(uint32_t aIndex,"]:
        result += [whole(run_h, marker)]
    result += ["};"]
    for marker in ["gfxShapedText::DetailedGlyph* gfxShapedText::AllocateDetailedGlyphs", "void gfxShapedText::SetDetailedGlyphs", "void gfxFont::DrawEmphasisMarks"]:
        result += [whole(font_cpp, marker)]
    for marker in ["void gfxTextRun::GlyphRunIterator::NextRun", "const gfxTextRun::GlyphRun* gfxTextRun::FindFirstGlyphRunContaining", "gfxTextRun::LigatureData gfxTextRun::ComputeLigatureData", "gfxFloat gfxTextRun::ComputePartialLigatureWidth", "int32_t gfxTextRun::GetAdvanceForGlyphs", "static bool GetAdjustedSpacing(", "bool gfxTextRun::GetAdjustedSpacingArray", "bool gfxTextRun::ShrinkToLigatureBoundaries", "void gfxTextRun::DrawEmphasisMarks"]:
        result += [whole(run_cpp, marker)]
    result += ["struct BuildTextRunsScanner { bool mDoubleByteText; void SetupTextEmphasisForTextRun(gfxTextRun*, const void*); };", whole(frame, "void BuildTextRunsScanner::SetupTextEmphasisForTextRun")]
    numeric = definitions["gfxTextRun::LigatureData gfxTextRun::ComputeLigatureData"]
    first = numeric.index("  const int64_t advancePerCluster") if signed else numeric.index("  result.mPartAdvance = partClusterIndex")
    last = numeric.index("  if (aProvider &&", first)
    arithmetic = numeric[first:last]
    records.append({"path": run_cpp, "kind": "arithmetic-slice", "parent": "gfxTextRun::ComputeLigatureData", "sha256": digest(arithmetic), "bytes": len(arithmetic.encode())})
    result += ["gfxTextRun::LigatureData ArithmeticFragment(int32_t ligatureWidth,uint32_t totalClusterCount,uint32_t partClusterIndex,uint32_t partClusterCount,bool final) {\n gfxTextRun::LigatureData result; result.mRange.end=1; gfxTextRun::Range aPartRange(0,final?1:0);\n"+arithmetic+"\n return result;\n}"]
    result += [(root/"native_main.inc").read_text()]
    text = "\n\n".join(result) + "\n"
    assert applied == ([mutant] if mutant else []) + ([arithmetic_mutant] if arithmetic_mutant else [])
    output.write_text(text)
    return records


if __name__ == "__main__":
    import sys
    root = Path(__file__).resolve().parent
    output = Path(sys.argv[1])
    rows = generate(root, output, sys.argv[2] if len(sys.argv)>2 else "candidate")
    output.with_suffix(".extraction.json").write_text(json.dumps(rows, indent=2)+"\n")
