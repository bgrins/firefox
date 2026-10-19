#![allow(dead_code)]
use std::io::{self, Read};

#[derive(Clone, Copy)]
struct ContainerType(u8);
impl ContainerType {
    const SIZE: Self = Self(2);
    const INLINE_SIZE: Self = Self(1);
    fn intersects(self, other: Self) -> bool { self.0 & other.0 != 0 }
}

#[derive(Clone, Copy)]
struct WritingMode(bool);
impl WritingMode {
    fn is_vertical(self) -> bool { self.0 }
    fn is_horizontal(self) -> bool { !self.0 }
}

#[derive(Clone, Copy)]
struct FeatureFlags(u8);
impl FeatureFlags {
    const CONTAINER_REQUIRES_INLINE_AXIS: Self = Self(1 << 2);
    const CONTAINER_REQUIRES_BLOCK_AXIS: Self = Self(1 << 3);
    const CONTAINER_REQUIRES_WIDTH_AXIS: Self = Self(1 << 4);
    const CONTAINER_REQUIRES_HEIGHT_AXIS: Self = Self(1 << 5);
    fn empty() -> Self { Self(0) }
}
impl std::ops::BitOr for FeatureFlags {
    type Output = Self;
    fn bitor(self, other: Self) -> Self { Self(self.0 | other.0) }
}

struct ContainerSizeQueryResult {
    width: Option<i32>,
    height: Option<i32>,
}
enum TraversalResult<T> {
    Done(T),
    InProgress,
}
