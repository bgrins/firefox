# Producer postprocessing for standalone v4

This directory contains producer tooling for the parent-owned experiment. It is not an independent review. No script here builds Firefox, launches a browser, writes native source, or reads/writes the live Git index.

After the parent explicitly reports terminal completion:

1. Run `python3 -I -S -B capture.py --terminal-confirmed`. It requires terminal STATE and the reviewed driver/INPUTS/oracle pins, copies the runtime directory read-only, and checks stable hashes before/after copying. It never modifies the source runtime artifact.
2. Run `python3 -I -S -B analyze.py`. Success requires exact keyed 74-subtest/23-file historical integer-only outcomes, intentional exit 1, all five candidate/source-restoration roles, fixed native inputs, successful build/lint receipts and historical HEAD/index preservation.
3. Write the final REPORT only after analysis. Run `python3 -I -S -B seal.py`, then `verify.py --files-sha256 <external pin>`.

The final verifier works from the closed capture, including raw WPT events and retained source/test inputs. It deliberately uses historical HEAD/index receipts rather than querying the repository, so subsequent authorized commits do not invalidate past restoration evidence. The original 400-input preflight is pinned; immutable external research dependencies were checked by the reviewed driver before execution, not re-executed by this postprocessor. Historical binary hashes are retained, not the binaries themselves.

No timing data or broad native/upstream acceptance is inferred. A failed experiment/capture is retained and investigated; it must not be relabeled as a passing standalone run.
