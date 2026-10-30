# Font metric dependency matrix

Thirteen isolated-document callbacks compare registered font-relative lengths with literal width references at 20px and 30px. The matrix varies family, weight, style, stretch, font-size-adjust and orientation. Weight cases cover em/ex/cap/ch plus unregistered aliases, registered aliases and typed attr. Explicit synthetic face descriptors map normal values to Ahem and alternate selections to Noto, so references calibrate the selected face without relying on installed fonts.

All eight bundled font faces load before target creation. Each phase reads the registered value first; all four observations are collected before assertions. Positive ch widths and differences over 1px calibrate the tested axis. Computed properties and em references check the selected state. Comparisons tolerate 0.02px of layout rounding. A prerequisite or serialization failure must be distinguished from a custom-value mismatch; complete failure JSON is retained. PASS callbacks do not expose hidden observation values.

The preparation script uses actual WPT manifest and lint code and an inert callback roster; it does not run the browser. No native fix or outcome is claimed by this fixture. All font and harness assets are unchanged existing resources. This extends the earlier three-case fixture; previous logs are immutable.
