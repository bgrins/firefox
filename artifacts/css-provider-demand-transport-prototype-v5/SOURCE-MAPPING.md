# Witness boundaries

- Witness.visit's occupied-index return corresponds to traverse() returning an index even after VarInfo.var has been taken. This is harmless only when later code does not mistake a pending default's raw declaration for its computed value.
- The primary/fallback decision corresponds to visit_value_references() examining as_universal().has_references() after visit_link(). The finite witness models only var references and constant/em default values.
- Pending component collection corresponds to the v4 participants vector and invalidated_pending set, populated before the default loop.
- Witness.default's applying set corresponds to apply_invalid_default() and GraphState.default_applying. It rejects reentry instead of inventing an invalid fallback/default result.
- The new pending guard precedes both deferred_registered dispatch and raw-map shortcuts. It calls the classified-default path, not the acyclic declaration path.
- The witness omits CSS parsing, DOM, registration admission, taint, attributes, external font/layout state, floating-point computation, and every unrelated graph/property kind. The completion policy and A-first DFS order are explicit assumptions.
- V4's ordinary production path is still None mode. This witness concerns the inactive strict path intended for future activation; it is not evidence of current release behavior.
