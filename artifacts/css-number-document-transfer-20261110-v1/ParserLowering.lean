import ExtendedBackend
import ParserIR

namespace CssParserLowering

open CssDerivation CssDerivation.ParserIR

def lower : Parser shape → Program (Option shape.Value)
  | .legacy program =>
    .bind (.legacy (FirstOrder.lower program .nil)) fun value => pure (some value)
  | .take predicate =>
    transaction (.bind (.legacy .read) fun value =>
      match value with
      | none => pure none
      | some c => if accepts predicate c then pure (some c) else pure none)
  | .scan predicate =>
    .bind .getState fun before =>
    .bind (.legacy (.scan before.input.length (accepts predicate))) fun chars => pure (some chars)
  | .nonempty parser =>
    transaction (.bind (lower parser) fun value =>
      match value with
      | some [] => pure none
      | result => pure result)
  | .pair left right =>
    transaction (.bind (lower left) fun first =>
      match first with
      | none => pure none
      | some a => .bind (lower right) fun second => pure (second.map fun b => (a, b)))
  | .right left right =>
    transaction (.bind (lower left) fun first =>
      match first with
      | none => pure none
      | some _ => lower right)
  | .optional parser => .bind (lower parser) fun result => pure (some result)

end CssParserLowering
