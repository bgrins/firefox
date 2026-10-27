# Signed CSS validation checkpoint

- demand-validation: `0ae3b531168912283bff436d65e948e5f453196d` (signature verified).
- attr-cycle-research: `595345eb51aef3c4862c8b4ad9dde7f992febdb7` (signature verified).
- number-research: `35f7ace19fd9deb0dadabc0f47a63d4d5f8f7d12` (signature verified).
- joint-context: `567def3805d91d6406a2b5229d26417932654034` (signature verified).
- fallback-review: `bab9092e4e6a48f47823eb189f984fbb77d521a8` (signature verified).

Typed demand: full native build and20GTests pass, including22resolvercalls. Ordinary WPT:253PASS+3existingexpectedFAIL,4OKharnesses,no unexpected results.
Attribute leads: both reproduced on release and branch; used-fallback repair now has34proposedWPTs and independent source review, but has not been applied/compiled/browser-compared. Registered-number comparison retains7release discrepancies and1additionallocal prototype failure.
The joint-context proposal is source-only. Canonical Lean coverage and135acceptedfixes unchanged. Unfinished source bodies remain preserved; all work local.
