import MathMLRectObservation
open CssSemantics.ProviderObservation MathMLRectObservation

theorem selected_size_only_restores_rectangle :
    (query admitted sizeOnlyProvider observe marked .leaf).map Prod.snd =
      some expectedRect := by
  simp only [marked_eq]
  decide
