# Identifier serialization WPT completion

The existing WPT serializes a stylesheet containing an import, replaces the
style element's text and immediately reads `document.styleSheets[0]`. Root's
retained baseline throws at the second read, after the first serialization has
succeeded. The final equality assertion is never reached.

The correction uses `promise_test`, creates a fresh style element containing
the serialized text, and waits for its own load/error event before reading its
sheet. Listeners are registered before insertion, avoiding events from an
earlier update. Both events indicate completion; importing the nonexistent
resource successfully is not required to compare the import rule's cssText.
The entire original ordered rule corpus and equality assertion are preserved.
Cleanup removes the new element.

The final test passes with the obsolete expected-failure metadata removed.
The focused WPT lint and diff whitespace check pass. All source/configuration
and binary pins shared with the baseline remain identical except for the test
and its metadata. This is the existing shared experimental Firefox build;
an isolated upstream build was not run. Exact apply/reverse checks at upstream
and the working branch establish standalone source applicability.

The earlier same-element waiting variant passed but is superseded because a
fresh node gives an unambiguous event origin. Its evidence is retained in v1.
The independent 36-case diagnostic also passes, but is not added to the WPT
repair. This is a test-harness repair, not an additional native CSS bug. The
native repair count remains 62. Research/evidence precedes the separate
two-file WPT-and-metadata commit.
