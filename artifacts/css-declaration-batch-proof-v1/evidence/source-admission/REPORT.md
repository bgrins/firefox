# Declaration source admission

This audit connects ordinary batching's source premises to the current callers
and generated publication code. No new browser defect was found. It does not
prove the complete batching algorithm or each property's value grammar.

## Current callers

Searchfox discovery identifies the definition of `set_property_to_declarations`
and eight direct callers. The retained current `glue.rs` has the same roster.
`SOURCE-CHECK.json` contains each complete function and its source hash.

- `set_property` and `Servo_DeclarationBlock_SetPropertyTypedValue` allocate fresh
  scratch, parse one property and update only on success.
- The six remaining callers construct `SourcePropertyDeclaration::with_one`.
  Their source is trivially unique and contains no opposing pair, independently
  of the payload's value equality.
- `set_property_to_declarations` constructs a fresh update plan, prepares against
  the block, invokes the mutation closure, then drains the scratch into update.
  Callback stability between preparation and execution remains an explicit
  premise. This audit does not prove scheduler behavior.

## Publication shape

`PropertyDeclaration::parse_into` asserts empty scratch. For an ordinary
longhand, the successful parser callback publishes one declaration only after
`parse_entirely` succeeds. The CSS-wide and deferred callbacks also publish one
fixed identity. Custom properties publish a singleton; `CSSWideKeyword::parse`
checks exhaustion, so an identifier prefix alone does not prematurely commit
the keyword route.

In `helpers.mako.rs`, each ordinary shorthand's generated `parse_into` calls
`parse_entirely(parse_value)` before its `map` closure publishes declarations.
The value parser receives context and input, not the declaration scratch. The
publisher traverses `shorthand.sub_properties` exactly once, constructing each
fixed declaration variant from its corresponding `Longhands` field. Conditional
admission can omit an identity; it cannot duplicate or reorder that traversal.

The keyword and deferred shorthand callbacks traverse the same unique metadata
through `longhands()`. `all` uses its separate field and is excluded from the
ordinary capacity. `properties.mako.rs` routes ordinary parsing of `all` to an
error without publication. The accepted declaration-publication repair clears
abandoned ordinary success before deferred publication. Failed generated
shorthand parsing publishes nothing because publication follows successful
exhaustive parsing. Complete parsing failure is not passed to the setter.

These are source/interface observations, not a formal translation of the Mako
generator, Rust compiler or every parser callback. The prior publication
component and this shape lemma have not yet been mechanically composed into a
whole native parser-to-batch theorem.

## Metadata and universal helper

The checker independently reads the retained TOML. All 94 explicit shorthands
have unique names and one mapping kind within each logical group. Their complete
ordered lists match the accepted generated provider receipt, including Gecko
extras. Every generated longhand's group and mapping kind match the TOML. The
largest ordinary expansion is `font`, with 19 entries.

`MAX_SHORTHAND_EXPANDED` is generated as the maximum subproperty count excluding
`all`; `SubpropertiesVec` uses that bound. Filtering an empty-source publication
therefore cannot overflow that capacity under the inspected generator contract.
Allocation, unsafe representation and machine/compiler correctness remain
external.

`Publication.lean` proves five general results for a publisher that visits fixed
identities and optionally emits one payload per identity: the resulting identity
list is a filter of the input, so uniqueness, pairwise compatibility and capacity
are preserved. `admitted_source` combines those obligations. The proof permits
arbitrary identities and payloads and does not assume payload equality. It does
not prove that arbitrary native `PropertyDeclaration::PartialEq` is reflexive.

The source-to-model publication interpretation is explicit. Finite metadata
checks instantiate its identity assumptions; they do not verify every future
metadata configuration or replace the pending universal batch/storage proof.

## Replay

Authenticate `MANIFEST.json` and `FREEZE.json` before running `check.py`. Run with
Python `-I -S`; `--output` must name a new directory outside this capsule. A fresh
replay checks the source/metadata roster, recompiles the five Lean results and
audits their exact axiom reports. `--live` additionally checks current repository
files against the retained inputs. Source-only evidence contains no Lean object.
