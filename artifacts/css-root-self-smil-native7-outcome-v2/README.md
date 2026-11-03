# Disabled SMIL7 native7-outcome successor

This preserves the sealed v1 preparation and changes only the expected owner to css-root-self-smil-candidate-browser-v2 and runtime to css-root-self-smil-candidate-browser-runtime-v2, as confirmed by its author. All future result, terminal and execution bindings remain null/disabled.

The v1 owner failed before build/runtime creation (701826/session66683/060e65, exit 1), because the input consumer expected a flat manifest. No candidate build or WPT result follows from that failed attempt. Root and the candidate author own its correction and actual execution.

The source is exactly the parent script with owner and runtime-name substitutions. Saved checks here authenticate the parent and this exact difference plus disabled future bindings; the original stream/signature checks are reused from the pinned parent CHECK receipt, not rerun or relabeled as a new result. Parent README retains the restoration, full-signature and source/build/fixture scope and limitations. No live operation is performed.
