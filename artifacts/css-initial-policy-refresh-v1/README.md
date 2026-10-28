# Registered initial-value policy refresh

Research captured on 2026-10-28; URLs, fetch times and response hashes are in FETCH.json. The specification snapshot and issue13211 discussion still leave the CSS @property computational-independence policy inconclusive. The JavaScript registration algorithm explicitly checks independence. This archive does not resolve the CSS policy or accept a native repair.

SEARCHFOX-stylist.rs records the upstream registration and initial-value rebuild path inspected for selected-value retention. No retention implementation was written in this work session. The proposed next step remains preserving the parsed selected value through initial computation, with complete independence validation and ordinary syntax-alternative selection handled separately. Existing draft designs and their limitations remain authoritative.
