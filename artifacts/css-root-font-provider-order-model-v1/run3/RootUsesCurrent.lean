import Provider
open RootFontProvider
example : read initialMetrics (initial underlying) .root .fontSize .rem = some (.font (.size 23)) := by decide
