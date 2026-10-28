Searchfox discovery 045410/0 located `third_party/rust/bitflags/src/iter.rs`. Full source returned successfully in tool f1d9be/0. Relevant predicate transcribed from that result:

```rust
if self.source.contains(B::from_bits_retain(bits))
    && self.remaining.intersects(B::from_bits_retain(bits))
{
    self.remaining.remove(B::from_bits_retain(bits));
    return Some((flag.name(), B::from_bits_retain(bits)));
}
```

Iteration follows the declared flags array. A repeated fetch to save the complete response failed DNS (011576/1); this is an excerpt of the prior observed tool output, not a claimed byte-exact source capture or pinned upstream revision.
