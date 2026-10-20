    pub(crate) fn advance(&mut self, n: usize) {
        if cfg!(debug_assertions) {
            // Each byte must either be an ASCII byte or a sequence
            // leader, but not a 4-byte leader; also newlines are
            // rejected.
            for i in 0..n {
                let b = self.byte_at(i);
                debug_assert!(b.is_ascii() || (b & 0xF0 != 0xF0 && b & 0xC0 != 0x80));
                debug_assert!(b != b'\r' && b != b'\n' && b != b'\x0C');
            }
        }
        self.state.position += n
    }
