import Fixture

namespace CssUnordered
open CssGrammar

set_option maxRecDepth 4096
set_option maxHeartbeats 1000000

theorem text_decode : decode textProgram = some textGrammar := by decide

theorem text_json : readGrammar textJson = .ok textGrammar := by rfl

theorem text_language : (language textGrammar).Perm referenceWords := by decide

theorem text_accepts (words : List String) :
    accepts textGrammar words = true ↔ words ∈ referenceWords := by
  rw [accepts_language]
  exact text_language.mem_iff

theorem text_remainder (input rest : List String) :
    rest ∈ CssGrammar.run textGrammar input ↔
      ∃ consumed ∈ referenceWords, input = consumed ++ rest := by
  rw [CssGrammar.run_iff]
  constructor
  · intro derivation
    obtain ⟨consumed, member, equal⟩ := language_sound derivation
    exact ⟨consumed, text_language.mem_iff.mp member, equal⟩
  · rintro ⟨consumed, member, rfl⟩
    simpa using matches_append (language_complete textGrammar consumed (text_language.mem_iff.mpr member)) rest

theorem reference_size : referenceWords.length = 38 := by decide

theorem reference_distinct : referenceWords.Nodup := by decide

end CssUnordered
