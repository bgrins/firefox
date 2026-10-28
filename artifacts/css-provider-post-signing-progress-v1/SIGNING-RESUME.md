# Signing continuation after staged-state adoption

The first36-file research patch is still staged unchanged at HEAD9abc806ef333f4cf9567ba28c3243ab9d9bc26e8. Runtime state now honestly records that staging. The metadata-only adoption completed successfully in provider-staging-adoption-1 (session71267, terminal325525/0), preserving source/index/binary/ROLE/OWNED bytes. Current epoch is ca83420911046fe09ab09cb6102330c02779633110459c08c1572928770cedcc until the next controlled native transition.

Do not run the old v26 resume-first.py, finish.py or synchronize.py as a current continuation. Their epoch assumptions are historical. Keep their captured inputs and failed signing logs as evidence. A successor signing executor must verify the exact existing staged patch against the then-current native/binary epoch, sign it unchanged, verify signature/tree/parent, and only then switch from the staged guard to the ordinary empty-staging guard. Do not unstage, bypass signing, or treat the old v4 snapshot as the current candidate after a later transition.

The four prepared v26 research selections remain intact. Additional completed research is inventoried in COMPLETED-SELECTION.json. No new signed commit was created by adoption and no fix was accepted.
