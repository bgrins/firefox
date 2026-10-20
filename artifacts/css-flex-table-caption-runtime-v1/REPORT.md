# Table caption percentage-height cache lead

Installed release and the restored shared project build produce identical results
for 16 warm-versus-fresh configurations. Four fail: auto-height caption,
percentage-height table, center or last-baseline flex alignment, grow or shrink.
The other twelve (fixed-height caption or literal table height) agree. All sixteen
initial, restoration and repeated-update controls pass in both browsers.

When the flex container grows from 200px to 300px, the warm table's computed
height stays 100px and its wrapper height is 120px including the 20px caption.
Fresh layout resolves 150px and 170px respectively. Shrinking reverses the stale
sizes. This is ordinary-size geometry and computed-style evidence. It does not
yet identify which native cache branch runs or prove the complete source cause.

The original source diagnostic is retained; the executed page only appends a
loopback result POST. Source/probe/driver/browser identities are pinned before
and after each run. Isolated temporary profiles were removed. No native source
was changed. The shared build includes other pending fixes, including the flex
final-size repair, while installed release reproduces the same discrepancy.

Status: reproduced unaccepted lead. Next: trace the measuring and final-reflow
cache keys and percentage containing-block input, propose a minimal standalone
repair and WPT, then perform a paired native build/browser experiment and source
review. Full allocation F11/F12 stays open.
