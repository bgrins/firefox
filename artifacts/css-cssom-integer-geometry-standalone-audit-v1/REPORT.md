# Integer CSSOM geometry standalone applicability

The proposed combined fix112 patch applies and reverses exactly on retained HEAD90 and upstream976279105b2e. It contains only Element.cpp, Element.h and two regression WPT files (32+8 cases). Both tests are absent on both bases. This establishes textual applicability, not runtime independence on a clean upstream build. Expanded acceptance remains pending. Temporary directories were removed; the working tree and index were not modified.
