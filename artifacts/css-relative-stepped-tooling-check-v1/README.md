Specification tooling check

webspec-index was absent from PATH and the standard cargo/mozbuild binary locations. Searchfox's current upstream bootstrap includes it, but this checkout's bootstrap did not install it. The required no-system-changes bootstrap invocation exited0 and unexpectedly rewrote mozconfig after automatically accepting its artifact-mode mismatch prompt. No native build ran under that configuration.

Root immediately restored mozconfig from mozconfig-full only after its exact hash matched the canonical epoch. RESTORATION.json records both bodies and the preserved identity during restoration. Subsequent source/binary/configuration observations verified the expected original hash. The missing CLI remains unavailable; the specification reviews used official CSSWG sources directly. No claim of a successful tooling installation is made.
