
namespace Composite
namespace IndependentAudit
def versionProviders : Providers := {
 computedValues := fun env frames => frames.map fun f => f.properties.map fun d =>
   (d.property, (d.value.getD 0 : Rat) + env.styleVersion)
 base := fun env segments => (segments.map Segment.property).eraseDups.map fun property =>
   (property, (10 : Rat) + env.styleVersion)
}
def fresh := optimizedSetter owner versionProviders initial [rproperty .add]
def changedContext := {witnessEnvironment with styleVersion := 1}
def stale := nativeStep owner versionProviders fresh (.context changedContext)
def skipped := optimizedSetter owner versionProviders stale [rproperty .add]
theorem fresh_property_cache : fresh.state.properties =
 buildConsumer versionProviders fresh.state.environment fresh.state.frames fresh.state.derived fresh.state.default := by decide +kernel
theorem fresh_base_cache : fresh.state.base = versionProviders.base fresh.state.environment fresh.state.properties := by decide +kernel
theorem stale_still_Valid : Valid stale.state := by unfold Valid; decide +kernel
theorem stale_still_Represents : Represents owner stale := by unfold Represents; decide +kernel
theorem skipped_equal_input : skipped.state = stale.state := by decide +kernel
theorem skipped_property_cache_incoherent : skipped.state.properties ≠
 buildConsumer versionProviders skipped.state.environment skipped.state.frames skipped.state.derived skipped.state.default := by decide +kernel
theorem skipped_base_cache_incoherent : skipped.state.base ≠
 versionProviders.base skipped.state.environment skipped.state.properties := by decide +kernel
theorem delivered_style_restores_property_cache :
 (nativeStep owner versionProviders stale (.style 1)).state.properties =
 buildConsumer versionProviders stale.state.environment stale.state.frames stale.state.derived stale.state.default := by decide +kernel
theorem delivered_style_restores_base_cache :
 (nativeStep owner versionProviders stale (.style 1)).state.base =
 versionProviders.base stale.state.environment
 (nativeStep owner versionProviders stale (.style 1)).state.properties := by decide +kernel
end IndependentAudit
end Composite
