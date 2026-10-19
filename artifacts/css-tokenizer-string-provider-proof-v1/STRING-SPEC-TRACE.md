# String-token transition trace

Primary source: retained CSS Syntax draft, sections “Preprocessing the input stream”, “Consume a token”, “Consume a string token” and “Consume an escaped code point”. Full HTML and selected exact text are under spec/; the original fetch receipt is retained. This trace concerns tokenizer strings only.

1. Input preprocessing supplies Unicode code points, converting CRLF/CR/FF to newline and NUL to U+FFFD. The implementation keeps raw bytes and performs those effects locally. No raw surrogate can inhabit a valid Rust str; the upstream conversion boundary is not proved here.
2. A quote token dispatch chooses that quote as the ending code point. The ending quote returns the accumulated string, while the opposite quote is ordinary content. The modeled raw wrapper checks the input quote itself.
3. EOF returns the accumulated string and is a parse error, not a BadString. A newline returns BadString and reconsumes the newline. The native helper therefore leaves the raw newline/CRLF in the suffix. Its diagnostic decoded prefix is an API extension, not a required BadString value in the specification.
4. Backslash followed by EOF contributes nothing. Backslash followed by a preprocessed newline consumes it and contributes nothing; this includes a two-byte raw CRLF. Other backslashes invoke escaped-code-point consumption. Generic escape EOF replacement must not be applied to the string-specific EOF branch.
5. Escaped code points consume at most six hexadecimal digits and optional whitespace, with zero, surrogates and out-of-range values mapped to U+FFFD. Simple escaped NUL also maps to U+FFFD; other simple Unicode characters preserve their scalar value. The old helper proof is composed only after matching complete provider source hashes.
6. The string value is the decoded output; sourceURL markers within it are ordinary text and do not call the comment directive writer. Native replay asserts both observer fields remain unchanged.

Verdict: REACHED for these tokenizer transition expectations under the explicit raw/Unicode admission boundary. This does not adjudicate Stylo custom-property raw-text persistence or serialization. Existing escaped-eof.html and serialize-escape-identifiers.html expected failures remain separate work owned by the parent/other agent.
