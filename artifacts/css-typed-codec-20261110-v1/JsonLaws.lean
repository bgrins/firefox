import JsonCodec

namespace CssDerivation.TypedCodec

theorem object_fields_rejected (aliases : Aliases) (fields : List (String × Layer))
    (invalid : exactFields ["op", "args"] fields = false) :
    objectNode aliases fields = {} := by
  simp [objectNode, invalid]

theorem no_implicit_aliases (name : String) :
    expressionNode [] "use" [{ text := some name }] = none := by rfl

end CssDerivation.TypedCodec
