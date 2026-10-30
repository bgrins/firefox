The frozen original completed 60532/49584e/0 with two PASS callbacks and one OK ending. The frozen candidate completed 66670/684695/1 with two FAIL callbacks and one OK ending. Both complete candidate records were posted; the aggregate FEEDBACK-RECORDS receipt was not written because the strict comparison raised first. Root independently verified restoration and removed the owned 1,008,605,176-byte backup (35467/4d6357/0). This report authenticated both complete manifests and the candidate terminal, then compared their records (24da25/0). No runtime was modified.

Original manifest: `44c326436b34e868ffde5fa9b91a7e1be07fb18f16d3cb4894da94915482218b`. Candidate manifest: `6e66d3dccdcec0d092d862c86f1e92e13f779c9226674028882d78b6dd936d20`. Exact terminal, raw, assessment and record pins are in REFERENCES.json. VALUES.tsv contains every role’s acquisition and phase values; OBSERVED.json preserves outcome and equality summaries.

The candidate fails the fixed script-override controls that passed in the original. After updateTiming sets duration to 2000ms, both effects report time 750ms and progress .375, but the coupled target keeps font 22.85px and opacity .428571 instead of 22px and .375. The zero-start target keeps font 0px instead of 12px. These mismatches persist through the subsequent return and repeat phases. Literal 2s targets have the correct values in the same records. The callback failures are therefore a candidate regression in fixed-duration controls, independent of any chosen self-feedback fixed-point policy. No fix is accepted by this observation.

| Role | Coupled candidate | Zero-start candidate |
| --- | --- | --- |
| Acquisition before/after ready | Font16px, CSS1s, effect1000ms/progress0 | Font0px, CSS0s, effect0ms/progress1 |
| Passive at750 | Font22.85px, opacity.428571, effect1428.125ms/progress.525164 | Font0px, effect0ms/progress1 |
| Real seek751 then750 | Reported time/progress changes, rendered font/opacity stays unchanged | Time changes; font remains0px |
| Outline add then remove | Font24.05px then24px; opacity.502793 then.5; duration1503.125 then1500ms | Font32px then12px; duration2000 then750ms |
| Script override2000 | Reported progress.375; font22.85px/opacity.428571 persist | Reported progress.375; font0px persists |
| Literal2000 | Font22px, opacity.375, progress.375 | Font12px, progress.375 |

The original passive and outline roles retain effect1000ms with font28px (coupled) or24px (zero-start). Its real seek changes rendered values and returns them on the750ms seek. Its override and literal controls agree at2000ms, progress.375 and font22px/12px. Original zero-start acquisition has CSS0s/font0px but effect1000ms/progress0, unlike the candidate's initial0ms/progress1.

All 100 ordered reads in each runtime have equal primary/repeat/after-membership style values, equal held/repeat/current timing snapshots, and every phase agrees between the two getter orders. Animation and effect identities remain true. Thus these records do not support replacement or observable getter-order differences as the explanation. They do not prove atomic sampling: all reads are sequential and getAnimations may flush. The successful ordinary outline restyle changes the rendered state, while the real seek and timing override do not refresh it in these observations; the records alone do not establish the internal invalidation or scheduler cause.

The self-dependent passive, seek and outline values remain measurements. No native cycle, convergence, hang, generic CSS feedback rule or additional accepted bug follows from them. The failed override assertion can prevent later assertions from running; the posted literal measurements are not relabelled as separately passed callbacks.
