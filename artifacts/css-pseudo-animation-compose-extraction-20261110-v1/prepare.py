#!/usr/bin/env python3
from pathlib import Path
import difflib

ROOT = Path(__file__).resolve().parent
CPP = "dom/animation/KeyframeEffect.cpp"
HEADER = "dom/animation/KeyframeEffect.h"
cpp = (ROOT / "source" / CPP).read_text()
h = (ROOT / "source" / HEADER).read_text()
rule_start = cpp.index("void KeyframeEffect::ComposeStyleRule(")
compose_start = cpp.index("void KeyframeEffect::ComposeStyle(\n", rule_start)
loop_start = cpp.index("  for (size_t propIdx = 0, propEnd = mProperties.Length();", compose_start)
overflow_start = cpp.index("  // If the animation produces a change hint", loop_start)
loop = cpp[loop_start:overflow_start]
loop = loop.replace("mProperties", "aProperties").replace("computedTiming", "aComputedTiming")
old_call = "    ComposeStyleRule(aComposeResult, prop, *segment, aComputedTiming);"
assert loop.count(old_call) == 1
loop = loop.replace(old_call, """    Servo_AnimationCompose(&aComposeResult, opaqueTable, &prop.mProperty,
                           segment, &prop.mSegments.LastElement(),
                           &aComputedTiming, aIterationComposite);""")
helper = """/* static */
void KeyframeEffect::ComposeProperties(
    StyleAnimationValueMap& aComposeResult,
    const nsTArray<AnimationProperty>& aProperties,
    const BaseValuesHashmap& aBaseValues, const ComputedTiming& aComputedTiming,
    IterationCompositeOperation aIterationComposite,
    const InvertibleAnimatedPropertyIDSet& aPropertiesToSkip) {
  MOZ_ASSERT(!aComputedTiming.mProgress.IsNull());
  const auto* opaqueTable =
      reinterpret_cast<const RawServoAnimationValueTable*>(&aBaseValues);

""" + loop.rstrip() + "\n}\n\n"
call = """  ComposeProperties(aComposeResult, mProperties, mBaseValues, computedTiming,
                    mEffectOptions.mIterationComposite, aPropertiesToSkip);

"""
new_cpp = cpp[:rule_start] + helper + cpp[compose_start:loop_start] + call + cpp[overflow_start:]
alias = """  using BaseValuesHashmap =
      nsRefPtrHashtable<nsGenericHashKey<CSSPropertyId>, StyleAnimationValue>;
"""
assert h.count(alias) == 1
new_h = h.replace(alias, "")
marker = "  // Updates |aComposeResult| with the animation values produced by this\n"
assert new_h.count(marker) == 1
new_h = new_h.replace(marker, alias + """
  // Requires non-null progress and valid, non-empty segment arrays.
  // Does not update effect bookkeeping.
  static void ComposeProperties(
      StyleAnimationValueMap& aComposeResult,
      const nsTArray<AnimationProperty>& aProperties,
      const BaseValuesHashmap& aBaseValues,
      const ComputedTiming& aComputedTiming,
      IterationCompositeOperation aIterationComposite,
      const InvertibleAnimatedPropertyIDSet& aPropertiesToSkip);

""" + marker)
old_decl = """  void ComposeStyleRule(StyleAnimationValueMap& aAnimationValues,
                        const AnimationProperty& aProperty,
                        const AnimationPropertySegment& aSegment,
                        const ComputedTiming& aComputedTiming);

"""
assert new_h.count(old_decl) == 1
new_h = new_h.replace(old_decl, "")
patch = []
for name, old, new in [(CPP, cpp, new_cpp), (HEADER, h, new_h)]:
    p = ROOT / "candidate" / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(new)
    patch.extend(difflib.unified_diff(old.splitlines(True), new.splitlines(True), fromfile="a/" + name, tofile="b/" + name))
(ROOT / "extraction.patch").write_text("".join(patch))
