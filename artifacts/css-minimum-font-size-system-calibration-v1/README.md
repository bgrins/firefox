# Minimum font-size calibration on System Firefox

Firefox 158 was run headlessly with explicit Western variable/monospace sizes
16/13 and minimum size first 24, then 0. The same standards-mode iframe measured
sixteen zero glyphs in ordinary monospace text, with registered 1ch and 1em
custom properties. No dynamic attribute or experimental source was involved.

With minimum 24, the 8px and 24px elements both measured about 231.2px wide and
29px high, and their registered 1ch values were both 14.45px. Computed font-size
and the registered em value stayed 8px and 24px respectively. With minimum 0,
the 8px element measured about 77.0667px wide and 10px high, with 1ch=4.81667px;
the 24px reference stayed about 231.2px wide and 29px high, with 1ch=14.45px.

This confirms that used text geometry and registered ch distinguish this
minimum-size effect while computed font-size and em do not. It calibrates the
ordinary reference for a future dependency test; it is not a candidate pass,
source-bound native result, or a new bug.

Each evaluated function removed its iframe. The connector's server-owned
browser was closed after the runs. Headless was restored to false, and minimum
size to 0. The connector restart API merges preference options, so its startup
configuration still includes explicit Western defaults 16/13/0 in addition to
the original browser.ml.enable=true. The final-info receipt records that
residual configuration; exact original option restoration is not claimed.
No user profile or local Nightly build was changed.
