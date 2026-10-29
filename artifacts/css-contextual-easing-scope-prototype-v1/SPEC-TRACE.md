# Scope and counting oracle

Fresh Values5 Editor Draft27 October2026, https://drafts.csswg.org/css-values-5/#tree-counting, defines counting over DOM siblings and zero for a failed loosely matched tree-scoped reference. Its examples distinguish outer part references from host/slotted references. Thus the unique outer-document keyframes used by these candidate tests require count0, while same-tree keyframes use actual target siblings. Existing native fallback1 is a separate repair prerequisite, not changed here.

Fresh Shadow1 Editor Draft28 April2026, https://drafts.csswg.org/css-shadow-1/#tree-scoped-reference, attaches the declaring root to a reference and searches that root then ancestors for global names. The existing element-applicable-data lookup lacks this input. This patch preserves its winner order and transports the winner's scope; it does not implement the full reference-root rule. Tests avoid duplicate names and do not establish general lookup conformance.

At progress0.75, literal steps(1+index,end) gives2/3 for index2 and3/4 for index3; failed outer matching0 gives0. Tests compare against actual literal easing controls, retaining nonanimated inputs. No activation, browser result or complete invalidation proof follows from this oracle alone.
