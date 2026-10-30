# Selected-color candidate V3: compile failure

Actual owner 85310/e7082d/51ecf0 exited 1. The native build exited 2 with Rust E0502 in substitute_references_if_needed_and_apply: the extracted apply_substituted_value call requests mutable context while Substitution may still borrow context.builder.substitution_functions. No browser tests ran. This is a candidate implementation error, not a new browser bug or a failed semantic test.

Independent reviewer 72917/51f609/3abddc/0 verified source bytes and identities, the original application, semantic index and staging, process cleanup and retained backup. Root rechecked source/application and the owned backup inventory, then removed 1,008,605,176 backup bytes. Only raw-index bookkeeping was refreshed; canonical native acceptance remains false and HEAD/149 accepted fixes are unchanged.

The failed owner, compiler log and diagnostic receipts are retained. Correct the helper borrow boundary without adding copies to the ordinary substitution path, then run a new candidate against the unchanged clean-original42 baseline. No outcome for the candidate42 browser suite is inferred from this build.
