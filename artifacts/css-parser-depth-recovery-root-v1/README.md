# Parser nesting-limit recovery

Accepted the one-call iterative cleanup repair with its 22-case WPT.
The original inline padding-left failure becomes a pass; all 46 other test
outcomes are unchanged. Root and independent source/kernel/native/browser
reviews pass. ROOT-SCOPED-ACCEPTANCE.json records the scope and evidence.

The 21-theorem component relates a flat cleanup stack to an independent nested
body/EOF grammar. Tokenization, native metadata/heap/compiler and general caller
admission remain open. Existing nesting-limit and outer-cleanup test bodies pass
against the fresh full candidate crate; this is not a full Cargo test-suite run.

The three-file patch contains only parser source, vendor checksum and WPT.
The upstream alternative preserves upstream checksum entries for other files.
It applies/reverses exactly, but was not separately browser-built. Discovery
was source inspection during formal work, followed by browser reproduction;
the proof followed discovery. No novelty or performance claim is made.
