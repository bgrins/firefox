# Parser declaration winners

Independent whole-history specification: remove every normal declaration whose identity has an important occurrence anywhere in the source, then retain only the last remaining occurrence for each identity, preserving the winning occurrences' original relative order. Prove equality to PublicStorage.parseExtend for arbitrary finite streams and arbitrary valid unique initial blocks treated as source prefixes. Incoming identities may repeat; payloads are arbitrary and need no equality.

Prove last-important/otherwise-last characterization, membership, uniqueness and source-order retention. Connect the result to the committed PublicStorage raw representation theorem without claiming a new native compiler bridge. Add exact parser push/extend change-bit semantics after the winner theorem; true need not imply a different value, order or serialization.

Dependencies are copied/authenticated committed model files and the frozen public-operations source/spec audit. PublicStorage is an actively reviewed checkpoint; its native interpretation remains conditional. No edits to parent or frozen artifacts, production source, WPT, browser, Mach or Git.
