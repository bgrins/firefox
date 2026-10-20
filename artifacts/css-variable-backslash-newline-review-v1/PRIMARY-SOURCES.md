# Primary-source oracle, checked 2026-10-19

- https://drafts.csswg.org/css-syntax-3/#serialization (current ED, 16 October 2026): parsed structure must survive serialization, and a reverse-solidus delimiter requires a following newline. This special requirement prevents the delimiter becoming an escape at EOF. Root retained section identity: bf3cd1bb025de576040be71d759b5bc0e3fc669e00b5b2813f111d6d6ff7e687; its exact bytes are separately pinned by INPUTS.json.
- https://drafts.csswg.org/css-syntax-3/#check-if-two-code-points-are-a-valid-escape and #consume-token: backslash followed by newline is not an escape; backslash at EOF has a different tokenization. Newline preprocessing accounts for LF, CR, FF and CRLF.
- https://drafts.csswg.org/css-variables-1/#using-variables: substitution transfers the custom-property value into the consuming property. The dependent property still must satisfy its grammar.
- https://drafts.csswg.org/css-animations-1/#animation-name: names are custom identifiers or strings (or none); the property is noninherited with initial none. A standalone backslash delimiter is neither a name nor a string. Failed substitution-time grammar therefore yields none, not the previous author declaration.

Literal CSS.supports checks in every WPT case independently establish the input grammar. The expected none result is derived from the grammar/defaulting rules; it is not inferred from the implementation. Valid name controls check the browser actually consumes and updates the property. No animation execution or security claim is involved.
