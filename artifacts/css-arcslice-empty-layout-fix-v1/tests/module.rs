
#[cfg(test)]
mod tests {
    use super::ArcSlice;
    use std::{iter, mem};

    #[repr(align(64))]
    struct Aligned {
        _payload: [u8; 64],
    }

    #[repr(align(64))]
    struct AlignedZst;

    fn check_empty<T>() {
        for value in [ArcSlice::<T>::default(), ArcSlice::from_iter(iter::empty())] {
            assert!(value.is_empty());
            assert_eq!(value.as_ptr().addr() % mem::align_of::<T>(), 0);
            let cloned = value.clone();
            drop(value);
            assert!(cloned.is_empty());
            drop(cloned);
        }
    }

    #[test]
    fn empty_slices_preserve_element_layout() {
        check_empty::<u64>();
        check_empty::<()>();
        check_empty::<Aligned>();
        check_empty::<AlignedZst>();
    }
}
