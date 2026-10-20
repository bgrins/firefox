# CSS-SYNTAX-3#serialization

**Serialization** (heading)

**SHA**: hash:bf3cd1bb025de576040be71d759b5bc0e3fc669e00b5b2813f111d6d6ff7e687

## Content

The tokenizer described in this specification does not produce tokens for comments, or otherwise preserve them in any way. Implementations may preserve the contents of comments and their location in the token stream. If they do, this preserved information must have no effect on the parsing step.

This specification does not define how to serialize CSS in general, leaving that task to the \[CSSOM\] and individual feature specifications. In particular, the serialization of comments and whitespace is not defined.

The only requirement for serialization is that it must "round-trip" with parsing, that is, parsing the stylesheet must produce the same data structures as parsing, serializing, and parsing again, except for consecutive [\<whitespace-token>](CSS-SYNTAX-3#typedef-whitespace-token)s, which may be collapsed into a single token.

> **Note:** Note: This exception can exist because CSS grammars always interpret any amount of whitespace as identical to a single space.

> **Note:** To satisfy this requirement:
>
> *   A [\<delim-token>](CSS-SYNTAX-3#typedef-delim-token) containing U+005C REVERSE SOLIDUS (\\) must be serialized as U+005C REVERSE SOLIDUS followed by a [newline](CSS-SYNTAX-3#newline). (The tokenizer only ever emits such a token followed by a [\<whitespace-token>](CSS-SYNTAX-3#typedef-whitespace-token) that starts with a newline.)
> *   A [\<hash-token>](CSS-SYNTAX-3#typedef-hash-token) with the "unrestricted" type flag may not need as much escaping as the same token with the "id" type flag.
> *   The unit of a [\<dimension-token>](CSS-SYNTAX-3#typedef-dimension-token) may need escaping to disambiguate with scientific notation.
> *   For any consecutive pair of tokens, if the first token shows up in the row headings of the following table, and the second token shows up in the column headings, and there’s a ✗ in the cell denoted by the intersection of the chosen row and column, the pair of tokens must be serialized with a comment between them.If the tokenizer preserves comments, and there were comments originally between the token pair, the preserved comment(s) should be used; otherwise, an empty comment (`/**/`) must be inserted. (Preserved comments may be reinserted even if the following tables don’t require a comment between two tokens.)
>
>     Single characters in the row and column headings represent a [\<delim-token>](CSS-SYNTAX-3#typedef-delim-token) with that value, except for "`(`", which represents a [(-token](CSS-SYNTAX-3#tokendef-open-paren).
>
> | ident | function | url | bad url | - | number | percentage | dimension | CDC | ( | \* | % |
> | ----- | -------- | --- | ------- | - | ------ | ---------- | --------- | --- | - | -- | - |
> | ✗     | ✗        | ✗   | ✗       | ✗ | ✗      | ✗          | ✗         | ✗   | ✗ |    |   |
> | ✗     | ✗        | ✗   | ✗       | ✗ | ✗      | ✗          | ✗         | ✗   |   |    |   |
> | ✗     | ✗        | ✗   | ✗       | ✗ | ✗      | ✗          | ✗         | ✗   |   |    |   |
> | ✗     | ✗        | ✗   | ✗       | ✗ | ✗      | ✗          | ✗         | ✗   |   |    |   |
> | ✗     | ✗        | ✗   | ✗       | ✗ | ✗      | ✗          | ✗         | ✗   |   |    |   |
> | ✗     | ✗        | ✗   | ✗       | ✗ | ✗      | ✗          | ✗         | ✗   |   |    |   |
> | ✗     | ✗        | ✗   | ✗       |   | ✗      | ✗          | ✗         | ✗   |   |    | ✗ |
> | ✗     | ✗        | ✗   | ✗       | ✗ |        |            |           | ✗   |   |    |   |
> |       |          |     |         |   | ✗      | ✗          | ✗         |     |   |    |   |
> |       |          |     |         |   | ✗      | ✗          | ✗         |     |   |    |   |
> |       |          |     |         |   |        |            |           |     |   | ✗  |   |

Tests

*   [serialize-consecutive-tokens.html](https://wpt.fyi/results/css/css-syntax/serialize-consecutive-tokens.html) [(live test)](http://wpt.live/css/css-syntax/serialize-consecutive-tokens.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-syntax/serialize-consecutive-tokens.html)
*   [serialize-escape-identifiers.html](https://wpt.fyi/results/css/css-syntax/serialize-escape-identifiers.html) [(live test)](http://wpt.live/css/css-syntax/serialize-escape-identifiers.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-syntax/serialize-escape-identifiers.html)

### Serializing *\<a-n-plus-b>*

To **serialize an [\<a-n-plus-b>](CSS-SYNTAX-3#anb-production) value**, with integer values *A* and *B*:

1.  If *A* is zero, return the serialization of *B*.

2.  Otherwise, let *result* initially be an empty [string](INFRA#string).

3.  *A* is `1`

    Append "n" to *result*.

    *A* is `-1`

    Append "-n" to *result*.

    *A* is non-zero

    Serialize *A* and append it to *result*, then append "n" to *result*.

4.  *B* is greater than zero

    Append "+" to *result*, then append the serialization of *B* to *result*.

    *B* is less than zero

    Append the serialization of *B* to *result*.

5.  Return *result*.

## Navigation

- Prev: `css-stylesheets` — CSS stylesheets
- Next: `privacy` — Privacy Considerations
- Children: 1
  - `serializing-anb` — Serializing <a-n-plus-b>

## Outgoing refs (6)

`webspec-index refs CSS-SYNTAX-3#serialization -d outgoing -l 6`

## Incoming refs (1)

- CSS-SYNTAX-3#contents

### Possible effects

CSS-SYNTAX-3#serialization

Partial analysis: additional effects may exist.

No effects detected by this analysis.

Traces and conditions (bounded): `webspec-index effects "CSS-SYNTAX-3#serialization" --format markdown`
