import CssSemantics.CssScopeImportExpansionView
import CssSemantics.CssScopeImportPreparedOrigins

namespace CssSemantics.CssScopeImportExpansionTotality

open CssImportExpansion CssScopeImportPreparedOrigins CssScopeImportExpansionView

def DescentRich (planned : Plan) (children : List CssImportExpansion.Item) : Prop :=
  match planned with
  | .load _ _ sheet remaining => CatalogRich remaining → (∀ item ∈ sheet.marked, MarkedRich item) →
      ∃ rich, Enriched children rich
  | _ => True

theorem planned_enriched {config context resources item planned children}
    (known : Planned config context resources item (.ok planned))
    (source : MarkedRich item) (catalog : CatalogRich resources)
    (descended : DescentRich planned children) : ∃ rich, EnrichedItem (finish planned children) rich := by
  cases known with
  | ordinary =>
      obtain ⟨rich, moved, first, last⟩ := MarkedRich.restored source context.parent
        (CssImportIdentity.localId config.rootLocalCount context.instancePath)
      exact ⟨_, .ordinary first last⟩
  | importRule actual =>
      cases actual with
      | suppressed => exact ⟨_, .suppressed⟩
      | skipped => exact ⟨_, .skipped⟩
      | failed => exact ⟨_, .failed⟩
      | load support resolved skip cycle selected admitted =>
          have rich := selected_rich selected catalog
          obtain ⟨children, enriched⟩ := descended rich.2 (SheetRich.marked rich.1 admitted)
          exact ⟨_, .loaded enriched⟩

theorem Expanded.enriched {config context resources items result}
    (known : Expanded config context resources items result) :
    CatalogRich resources → (∀ item ∈ items, MarkedRich item) → ∃ rich, Enriched result rich := by
  refine Expanded.rec
    (motive_1 := fun context resources items result _ =>
      CatalogRich resources → (∀ item ∈ items, MarkedRich item) → ∃ rich, Enriched result rich)
    (motive_2 := fun planned children _ => DescentRich planned children)
    ?_ ?_ ?_ ?_ ?_ ?_ ?_ known
  · intros; exact ⟨[], .nil⟩
  · intro context resources item rest planned children tail actual descent expanded ihChild ihTail catalog sources
    obtain ⟨first, enrichedFirst⟩ := planned_enriched actual (sources _ List.mem_cons_self) catalog ihChild
    obtain ⟨last, enrichedLast⟩ := ihTail catalog (fun item member => sources item (List.mem_cons_of_mem _ member))
    exact ⟨first :: last, .cons enrichedFirst enrichedLast⟩
  · intros; trivial
  · intros; trivial
  · intros; trivial
  · intros; trivial
  · intro info address sheet remaining children actual ih
    exact ih

theorem Expanded.enrich_exists {config context resources items result}
    (known : Expanded config context resources items result)
    (catalog : CatalogRich resources) (sources : ∀ item ∈ items, MarkedRich item) :
    ∃ rich, enrich result = some rich := by
  obtain ⟨rich, actual⟩ := Expanded.enriched known catalog sources
  exact ⟨rich, (enrich_iff ..).mpr actual⟩

theorem Expanded.prepared_enrichment {config context resources result imported source sheet}
    (prepared : CssScopeImportPrepared.SheetPrepared imported source sheet)
    (admitted : sheet.Admitted)
    (known : Expanded config context resources sheet.registration.marked result)
    (catalog : CatalogRich resources) : ∃ rich, Enriched result rich :=
  Expanded.enriched known catalog (SheetRich.marked ⟨source, sheet, prepared, rfl⟩
    (sheet.registration_admitted_iff.mpr admitted))

end CssSemantics.CssScopeImportExpansionTotality
