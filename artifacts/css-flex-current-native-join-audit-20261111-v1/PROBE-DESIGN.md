# Proposed initial clamp-state chrome probe (unrun)

Use the existing `getAsFlexContainer().getLines()[0].getItems()[0]` chrome interface and read `clampState`, recorded base/min/max, and actual item height after layout. No web-exposed API or WPT claim is intended. The current source audit pins the complete candidate version; record actual browser identity before testing.

All cases use a single column item, a 200px-high container, zero border/padding/margins, `flex:0 0 auto`, `min-height:0`, and a 20px child unless overridden:

| Case | Change | Expected size | Expected clamp state |
|---|---|---:|---|
| Measured below max | max-height:100px | 20px | unclamped |
| Measured above max | max-height:10px | 10px | clamped_to_max |
| Measured below min | min-height:30px; max-height:100px | 30px | clamped_to_min |
| Measured exactly max | max-height:20px | 20px | unclamped |
| No finite max | max-height:none | 20px | unclamped |
| Explicit basis control | flex-basis:20px; max-height:100px | 20px | unclamped |
| Explicit clamp control | flex-basis:20px; max-height:10px | 10px | clamped_to_max |
| Flexible control | flex:0 1 auto; max-height:100px | 20px | unclamped |

Repeat relevant cases in row with matching width constraints and column-reverse. No spacing/alignment inference is needed. Preserve raw API values, not just a pass count. If the initial ReflowInput already resolves the content base, the proposed stale-unconstrained route may not be reached; record that result rather than treating source possibility as reproduction.

The exact source prediction is specific: when the initial saved base is unconstrained and finite max is positive, early classification sets max-clamped before content measurement. The measured actual size can be correct while diagnostic metadata is wrong. An initial max flag could also conceal a later min clamp. The aspect-ratio route is secondary and should only be added after inspecting actual base values.

No implementation, browser invocation, fixture installation, or native edit is authorized by this document. Root owns the next experiment.
