# Paired float timings

All values are milliseconds. Recovery columns are medians of five per-round sums, each summing 16 measurements. Hot columns are medians of five batches, each with 16,384 reads. Each cell is baseline → candidate.

| Shape / state / floats | Prepare | First | Repeat | Clean same | Clean cycle |
|---|---:|---:|---:|---:|---:|
| direct/visible/1 | 0 → 0 | 0 → 0 | 0 → 0 | 2 → 2 | 2 → 2 |
| direct/visible/32 | 1 → 1 | 0 → 0 | 0 → 0 | 2 → 2 | 2 → 2 |
| direct/visible/128 | 2 → 2 | 0 → 0 | 0 → 0 | 2 → 3 | 2 → 2 |
| direct/hidden/1 | 0 → 0 | 0 → 0 | 0 → 0 | 2 → 2 | 2 → 3 |
| direct/hidden/32 | 0 → 1 | 0 → 0 | 0 → 0 | 2 → 2 | 2 → 2 |
| direct/hidden/128 | 0 → 0 | 0 → 2 | 0 → 0 | 2 → 2 | 2 → 2 |
| inline-nested/visible/1 | 0 → 0 | 0 → 0 | 0 → 0 | 3 → 2 | 2 → 2 |
| inline-nested/visible/32 | 1 → 1 | 0 → 0 | 0 → 0 | 2 → 2 | 2 → 2 |
| inline-nested/visible/128 | 2 → 2 | 0 → 0 | 0 → 0 | 2 → 2 | 3 → 2 |
| inline-nested/hidden/1 | 0 → 0 | 0 → 0 | 0 → 0 | 2 → 2 | 2 → 2 |
| inline-nested/hidden/32 | 0 → 0 | 0 → 0 | 0 → 0 | 2 → 2 | 2 → 2 |
| inline-nested/hidden/128 | 0 → 0 | 0 → 3 | 0 → 0 | 2 → 2 | 2 → 2 |

The hidden baseline returned stale geometry on 80 of 160 recovery reads in each group (40 first, 40 repeat). The candidate returned correct geometry on every read. Those first/repeat times do not compare equivalent work.

Every immediate-repeat sample and every visible first-query sample is zero in both phases. The measurements are quantized to whole milliseconds; zero is unresolved timing, not zero work. All raw per-round samples, ranges, and zero counts are retained in PAIRED-TIMINGS.json.

The candidate hidden128 first-query distributions are direct [2, 1, 2, 2, 3] and inline [3, 2, 1, 3, 3] ms per 16 transitions. Clean hot medians remain 2 ms for 20 of 24 paired buckets; two rise 2→3 ms and two fall 3→2 ms. These local, fixed-order, five-round samples have overlapping ranges and do not establish a general regression guarantee.
