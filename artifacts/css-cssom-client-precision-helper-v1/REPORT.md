# Client integer conversion helper

The exact proposed private helper extraction compiles against the actual nsCoord/AppUnits headers under undefined-behavior and integer sanitizers. Its independent quotient/remainder oracle, integral identity, negative ties, signed endpoints and ordinary-domain preservation checks pass. CHECK.json records compiler/command, source/header dependencies, exits and output. No sanitizer diagnostics were emitted. All generated binary/dependency/debug products were removed.

This exercises the exact arithmetic extraction, not the complete Element class or browser. The old expression uses the actual NSAppUnitsToFloatPixels helper followed by double half addition and floor; it is source-shaped correspondence, not a compilation of the full old gfx adapter. Full native build and paired WPT remain required.
