# Installed local build: relative overflow and table-caption repairs

Both bounded accepted repairs are installed in the shared local tree. The
combined native build passed. Four focused WPT files pass510 subtests:140
relative-overflow,16 table-caption resize,336 flex final-size overflow and18
percentage-padding measurement tests. All selected source/test/reference/metadata
inputs and binary hashes stayed stable during execution.

The exact formatted relative-position CPP and tested table-caption CPP match
the accepted pins. The earlier final-size and padding-key fixes remain present.
HEAD and the297-file staged snapshot are unchanged. This is a combined local
integration check, not isolated upstream validation or full CSS verification.
No unsigned commit, push, or Phabricator submission occurred. verify.py checks
retained input hashes and recounts all510 unique passing observations.
