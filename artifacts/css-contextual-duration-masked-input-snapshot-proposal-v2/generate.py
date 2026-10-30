import difflib
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def replace_once(body, old, new):
    assert body.count(old) == 1, old
    return body.replace(old, new)


def generate():
    bodies = {}

    def edit(name, old, new):
        source = bodies.get(name, (HERE / "base" / name).read_text())
        bodies[name] = replace_once(source, old, new)

    edit("layout/style/GeckoBindings.h", "enum class UpdateAnimationsTasks : uint8_t;",
         "enum class UpdateAnimationsTasks : uint16_t;")
    edit("layout/style/ServoTypes.h", "enum class UpdateAnimationsTasks : uint8_t {",
         "enum class UpdateAnimationsTasks : uint16_t {")
    edit("layout/style/ServoTypes.h", "  TimelineScopes = 1 << 7,\n",
         "  TimelineScopes = 1 << 7,\n  VerifyAnimationDurationInput = 1 << 8,\n")
    edit("servo/components/style/context.rs", "pub struct UpdateAnimationsTasks: u8 {",
         "pub struct UpdateAnimationsTasks: u16 {")
    edit("servo/components/style/context.rs",
         "        const TIMELINE_SCOPES = structs::UpdateAnimationsTasks_TimelineScopes;\n",
         "        const TIMELINE_SCOPES = structs::UpdateAnimationsTasks_TimelineScopes;\n"
         "        /// Verify contextual duration input without forcing a CSS animation update.\n"
         "        const VERIFY_ANIMATION_DURATION_INPUT = structs::UpdateAnimationsTasks_VerifyAnimationDurationInput;\n")
    edit("servo/components/style/matching.rs",
         "            tasks.insert(UpdateAnimationsTasks::CSS_ANIMATIONS);\n"
         "            tasks.insert(UpdateAnimationsTasks::EFFECT_PROPERTIES);\n"
         "        }\n\n        let before_change_style =",
         "            tasks.insert(UpdateAnimationsTasks::CSS_ANIMATIONS);\n"
         "            tasks.insert(UpdateAnimationsTasks::EFFECT_PROPERTIES);\n"
         "        } else if self.has_css_animations(context.shared, None) {\n"
         "            tasks.insert(UpdateAnimationsTasks::VERIFY_ANIMATION_DURATION_INPUT);\n"
         "        }\n\n        let before_change_style =")
    edit("layout/style/AnimationCollection.h", '#include "mozilla/RefPtr.h"\n',
         '#include "mozilla/RefPtr.h"\n#include "mozilla/ServoStyleConsts.h"\n')
    edit("layout/style/AnimationCollection.h", "  nsTArray<RefPtr<AnimationType>> mAnimations;\n",
         "  nsTArray<RefPtr<AnimationType>> mAnimations;\n\n"
         "  // Empty means unsampled; a computed duration list is nonempty.\n"
         "  nsTArray<StyleAnimationDuration> mLastAnimationDurationInput;\n")
    edit("layout/style/GeckoBindings.cpp", '#include "mozilla/ServoElementSnapshot.h"\n',
         '#include "mozilla/ServoElementSnapshot.h"\n#include "mozilla/ServoStyleSet.h"\n')
    edit("layout/style/GeckoBindings.cpp",
         "  if (aTasks & UpdateAnimationsTasks::CSSAnimations) {\n"
         "    presContext->AnimationManager()->UpdateAnimations(\n"
         "        const_cast<Element*>(element), pseudoRequest, aComputedData);\n"
         "  }",
         "  if (aTasks & (UpdateAnimationsTasks::CSSAnimations |\n"
         "                UpdateAnimationsTasks::VerifyAnimationDurationInput)) {\n"
         "    RefPtr<ComputedStyle> durationInput;\n"
         "    if (aComputedData) {\n"
         "      durationInput = presContext->StyleSet()->GetBaseContextForElement(\n"
         "          const_cast<Element*>(aElement), aComputedData);\n"
         "    }\n"
         "    const bool verifyOnly = !(aTasks & UpdateAnimationsTasks::CSSAnimations);\n"
         "    presContext->AnimationManager()->UpdateAnimations(\n"
         "        const_cast<Element*>(element), pseudoRequest, aComputedData,\n"
         "        durationInput, verifyOnly);\n"
         "  }")
    edit("layout/style/nsAnimationManager.h",
         "                        const mozilla::ComputedStyle* aComputedValues);",
         "                        const mozilla::ComputedStyle* aComputedValues,\n"
         "                        const mozilla::ComputedStyle* aDurationInput,\n"
         "                        bool aVerifyDurationInputOnly);")
    edit("layout/style/nsAnimationManager.h",
         "                          ServoCSSAnimationBuilder& aBuilder);",
         "                          ServoCSSAnimationBuilder& aBuilder,\n"
         "                          const nsStyleUIReset* aDurationInput,\n"
         "                          bool aVerifyDurationInputOnly);")
    edit("layout/style/nsAnimationManager.cpp",
         "    const ComputedStyle* aComputedStyle) {\n",
         "    const ComputedStyle* aComputedStyle,\n"
         "    const ComputedStyle* aDurationInput, bool aVerifyDurationInputOnly) {\n")
    edit("layout/style/nsAnimationManager.cpp",
         "  DoUpdateAnimations(target, *aComputedStyle->StyleUIReset(), builder);",
         "  DoUpdateAnimations(target, *aComputedStyle->StyleUIReset(), builder,\n"
         "                     aDurationInput ? aDurationInput->StyleUIReset() : nullptr,\n"
         "                     aVerifyDurationInputOnly);")
    edit("layout/style/nsAnimationManager.cpp",
         "    ServoCSSAnimationBuilder& aBuilder) {\n",
         "    ServoCSSAnimationBuilder& aBuilder, const nsStyleUIReset* aDurationInput,\n"
         "    bool aVerifyDurationInputOnly) {\n")
    edit("layout/style/nsAnimationManager.cpp",
         "  nsAutoAnimationMutationBatch mb(aTarget.mElement->OwnerDoc());\n",
         "  if (aVerifyDurationInputOnly && !collection) {\n"
         "    return;\n"
         "  }\n\n"
         "  nsTArray<StyleAnimationDuration> durationInput;\n"
         "  if (aDurationInput) {\n"
         "    durationInput.SetCapacity(aDurationInput->mAnimationDurationCount);\n"
         "    for (uint32_t i = 0; i < aDurationInput->mAnimationDurationCount; ++i) {\n"
         "      durationInput.AppendElement(aDurationInput->GetAnimationDuration(i));\n"
         "    }\n"
         "    if (aVerifyDurationInputOnly &&\n"
         "        collection->mLastAnimationDurationInput == durationInput) {\n"
         "      return;\n"
         "    }\n"
         "  }\n\n"
         "  nsAutoAnimationMutationBatch mb(aTarget.mElement->OwnerDoc());\n")
    edit("layout/style/nsAnimationManager.cpp",
         "  collection->mAnimations.SwapElements(newAnimations);\n",
         "  collection->mAnimations.SwapElements(newAnimations);\n"
         "  collection->mLastAnimationDurationInput = std::move(durationInput);\n")
    return bodies


if __name__ == "__main__":
    records = {}
    patches = []
    for name, text in sorted(generate().items()):
        target = HERE / "candidate" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)
        base = HERE / "base" / name
        records[name] = {
            "base_capture": str(base.relative_to(ROOT)),
            "base_sha256": hashlib.sha256(base.read_bytes()).hexdigest(),
            "candidate_capture": str(target.relative_to(ROOT)),
            "candidate_sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
        }
        patches.extend(difflib.unified_diff(base.read_text().splitlines(True),
                       text.splitlines(True), fromfile="a/" + name, tofile="b/" + name))
    (HERE / "native.patch").write_text("".join(patches))
    (HERE / "SOURCE-ROLES.json").write_text(json.dumps(records, indent=2, sort_keys=True) + "\n")
