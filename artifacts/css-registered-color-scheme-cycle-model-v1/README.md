# Selected color dependency model

The model distinguishes a registration that can accept a color from a selected value that actually needs the element’s color scheme. A union-wide edge produces a cycle for a selected identifier in the two-node graph; selecting the first successful clause removes that false cycle while preserving the genuine system-color cycle.

`Selection.lean` contains 15 kernel-checked theorems. The pinned Lean run rejected seven deliberately false claims. It uses no project imports or additional axioms; the audit logs and exact compiler hash are retained in `run1`.

The finite parser has two clauses (`ident`, `color`) and five token classes. `light` and `dark` select identifiers in either union order. `red` overlaps the clauses but a selected absolute color needs no scheme. `canvas` stands for a system-color identifier accepted by both clauses: identifier-first selects an identifier, while color-first selects a scheme-dependent color. This is an explicit abstract parser, not a proof of CSS tokenization, complete union parsing, registration validity, or the native parser.

The graph has two vertices: the consuming `color-scheme` property and the custom property. The sink-to-custom edge is an explicit admission input; the reverse edge comes from either possible color syntax or the selected value. An independent oracle enumerates self edges and two-vertex cycles, covering every simple cycle in this two-vertex graph. A theorem relates that enumeration to the two directed edges. This is not a Tarjan implementation or a result about arbitrary CSS graphs.

The unused-fallback case separates syntax inventory from substitution. A valid primary never selects its fallback in the model. Nevertheless, an inventoried `attr()` can admit the sink edge in the existing source path, exposing the union-wide false cycle. A plain non-admitted sink has no modeled cycle even under the broad rule. The admission Boolean is an assumption supplied by the frozen source analysis, not derived by Lean. A selected fallback can supply a genuine system color; suppressing all color edges would be wrong.

Invalid syntax has no selected computation edge here. The model does not represent initial/inherited/default values, their computation, invalid-at-computed-value processing, physical attribute recursion, animation taint, images, list components, browser scheduling, or native restoration. In particular, the invalid-token theorem is not permission to discard dependencies of a separately selected default value. The source repair must independently preserve those behaviors.

Actual run: session 47472, launch 9b48bb, terminal 6ddcfd, exit 0. All 15 audits passed; seven false controls failed because Lean proved their propositions false. The owned scratch directory was removed. No browser, native build, source overlay, Git operation, accepted-fix increment, or native-refinement proof occurred.
