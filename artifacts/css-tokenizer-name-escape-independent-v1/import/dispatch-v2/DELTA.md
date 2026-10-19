# Version 2: source admission correction

The independent review found that version 1's source reader accepted two named wildcard arms in one macro invocation, while the real procedural macro asserts that at most one named binding is present. The exact retained witness replaces the first `b'\0'` arm of `serialize_name` with `other`, leaving its final named `b` arm. Version 1's current-source tables remain correct because each original invocation has at most one named binding; the future-source admission claim was too permissive.

Version 2 counts named bindings (excluding `_`) per invocation and rejects a second binding immediately. The complete original source is unchanged. A checker regression applies the exact retained source mutation in an isolated output copy and requires the specific multiple-binding diagnostic. The independent review's version 1 passing receipt and mutated full source remain under evidence/v1-reader-counterexample. Version 1 itself is unchanged.

The reviewer also found that `byte_start` held a Python Unicode character offset. Version 2 explicitly retains `source_character_start` and computes `byte_start` from the UTF-8 prefix length. The checker verifies both coordinate interpretations against raw source. Invocation/body hashes, patterns, table entries and Lean input remain identical.

The universal theorem, proof scope, actual 22 source invocations and all 5,632 selected table entries are unchanged. Fresh replay retains all earlier source/proof/mutation gates and adds the second-binding rejection and UTF-8 coordinate checks. This corrects source admission; it does not prove the tokenizer or broaden any prior claim.
