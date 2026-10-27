# Raw-index clarification

The sealed duration-comparison REPORT.md contains an incorrect sentence claiming current raw-index endpoint equality. ROOT-COMPLETION.json and RAW-INDEX-OBSERVATION.json correctly report that this equality is false. This clarification supersedes that sentence; the original report and receipt bytes remain preserved.

Activation raw SHA256:6d786076f9719e7f2e556cfb347ab484546b7e4a3252a7020b4647bf19d5f790.
Final/root-check raw SHA256:75dd5be919c4f15c10f69e5be2843b1fa347e34566e10c0713ec009935674e9b.

HEAD, index entries, cached diff, all925 staged blobs and their working payloads remain equal under the completed root verifier. Current raw bytes were stable during that verifier. The cause of the intervening raw-byte change is unestablished; no index rewrite or restoration was performed by the root verifier. This is semantic staging preservation, not raw-byte equality. No native acceptance follows from the comparison alone.

The viewport observation review also remains qualified: initial150px on baseline versus later100px on both candidate and restored captures. Both forms were observed on earlier originals; they do not provide repair credit and do not justify full182 outcome equality.
