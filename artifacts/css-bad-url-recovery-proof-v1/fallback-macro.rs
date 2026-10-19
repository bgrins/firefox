#[cfg(not(feature = "fast_match_byte"))]
#[macro_use]
mod mac {
    /// Expand a TokenStream corresponding to the `match_byte` macro.
    ///
    /// ## Example
    ///
    /// ```rust,ignore
    /// match_byte! { tokenizer.next_byte_unchecked(),
    ///     b'a'..b'z' => { ... }
    ///     b'0'..b'9' => { ... }
    ///     b'\n' | b'\\' => { ... }
    ///     foo => { ... }
    ///  }
    ///  ```
    ///
    #[macro_export]
    macro_rules! match_byte {
      ($value:expr, $($rest:tt)* ) => {
          match $value {
              $(
                  $rest
              )+
          }
      };
  }
}

