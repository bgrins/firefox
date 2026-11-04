use super::{Arc, ArcInner};
use stable_deref_trait::{CloneStableDeref, StableDeref};
use std::alloc::{self, Layout};
use std::ffi::c_void;
use std::fmt;
use std::marker::PhantomData;
use std::mem::{self, ManuallyDrop};
use std::ops::Deref;
use std::ptr::{self, NonNull};
use std::sync::atomic::AtomicUsize;

#[repr(C)]
pub struct HeaderSlice<H, T> {
    pub header: H,
    len: usize,
    data: [ManuallyDrop<T>],
}
impl<H, T> HeaderSlice<H, T> {
    pub fn slice(&self) -> &[T] {
        unsafe { std::slice::from_raw_parts(self.data.as_ptr().cast(), self.data.len()) }
    }
    pub fn slice_mut(&mut self) -> &mut [T] {
        unsafe { std::slice::from_raw_parts_mut(self.data.as_mut_ptr().cast(), self.data.len()) }
    }
    pub fn len(&self) -> usize {
        self.data.len()
    }
    pub fn is_empty(&self) -> bool { self.data.is_empty() }
    pub fn retained_len(&self) -> usize {
        self.len
    }
}

impl<H, T> Drop for HeaderSlice<H, T> {
    fn drop(&mut self) {
        unsafe {
            ptr::drop_in_place(ptr::slice_from_raw_parts_mut(
                self.data.as_mut_ptr().cast::<T>(),
                self.data.len(),
            ));
        }
    }
}

/// cbindgen:derive-eq=false
/// cbindgen:derive-neq=false
#[repr(C)]
struct Prefix<H, T> {
    header: H,
    len: usize,
    data: [T; 0],
}

type ThinArcPointer<H, T> = NonNull<ArcInner<Prefix<H, T>>>;

fn allocation_layout<H, T>(len: usize) -> Layout {
    let offset = mem::offset_of!(ArcInner<Prefix<H, T>>, data.data);
    let prefix =
        Layout::from_size_align(offset, mem::align_of::<ArcInner<Prefix<H, T>>>()).unwrap();
    let (layout, actual_offset) = prefix
        .extend(Layout::array::<T>(len).expect("overflow"))
        .expect("overflow");
    assert_eq!(offset, actual_offset);
    layout.pad_to_align()
}

// The original allocation pointer must own a fully initialized matching DST.
unsafe fn fat_pointer<H, T>(p: ThinArcPointer<H, T>) -> NonNull<ArcInner<HeaderSlice<H, T>>> {
    let len = unsafe { ptr::addr_of!((*p.as_ptr()).data.len).read() };
    let fat = ptr::slice_from_raw_parts_mut(p.as_ptr().cast::<T>(), len)
        as *mut ArcInner<HeaderSlice<H, T>>;
    unsafe { NonNull::new_unchecked(fat) }
}

/// cbindgen:derive-eq=false
/// cbindgen:derive-neq=false
#[repr(C)]
pub struct ThinArc<H, T> {
    p: ThinArcPointer<H, T>,
    marker: PhantomData<Arc<HeaderSlice<H, T>>>,
}
unsafe impl<H: Send + Sync, T: Send + Sync> Send for ThinArc<H, T> {}
unsafe impl<H: Send + Sync, T: Send + Sync> Sync for ThinArc<H, T> {}

impl<H, T> ThinArc<H, T> {
    pub fn from_header_and_iter<I: ExactSizeIterator<Item = T>>(header: H, items: I) -> Self {
        let len = items.len();
        Self::from_header_and_iter_with_size(header, items, len)
    }
    pub fn from_header_and_iter_with_size<I: Iterator<Item = T>>(
        header: H,
        items: I,
        len: usize,
    ) -> Self {
        unsafe {
            Self::from_header_and_iter_alloc(
                |layout| alloc::alloc(layout),
                header,
                items,
                len,
                false,
            )
        }
    }
    /// # Safety
    /// Storage must satisfy the requested layout and outlive all static owners, or support global deallocation with that layout.
    pub unsafe fn from_header_and_iter_alloc<
        F: FnOnce(Layout) -> *mut u8,
        I: Iterator<Item = T>,
    >(
        allocate: F,
        header: H,
        mut items: I,
        len: usize,
        is_static: bool,
    ) -> Self {
        assert!(
            len == 0 || mem::size_of::<T>() != 0,
            "Nonempty ZST tails are unsupported"
        );
        let layout = allocation_layout::<H, T>(len);
        let p = NonNull::new(allocate(layout))
            .unwrap_or_else(|| alloc::handle_alloc_error(layout))
            .cast::<ArcInner<Prefix<H, T>>>();
        unsafe {
            ptr::addr_of_mut!((*p.as_ptr()).count).write(AtomicUsize::new(if is_static {
                super::STATIC_REFCOUNT
            } else {
                1
            }));
            #[cfg(feature = "track_alloc_size")]
            ptr::addr_of_mut!((*p.as_ptr()).alloc_size).write(layout.size());
            ptr::addr_of_mut!((*p.as_ptr()).data.header).write(header);
            ptr::addr_of_mut!((*p.as_ptr()).data.len).write(len);
            let start = p
                .as_ptr()
                .cast::<u8>()
                .add(mem::offset_of!(ArcInner<Prefix<H, T>>, data.data))
                .cast::<T>();
            for i in 0..len {
                start.add(i).write(items.next().expect("iterator length"));
            }
            assert!(items.next().is_none(), "iterator length");
        }
        #[cfg(feature = "gecko_refcount_logging")]
        unsafe {
            if !is_static {
                super::NS_LogCtor(p.as_ptr().cast(), b"ServoArc\0".as_ptr().cast(), 8);
            }
        }
        let owner = Self {
            p,
            marker: PhantomData,
        };
        assert_eq!(owner.dynamic_layout(), layout);
        owner
    }
    pub fn get_mut(this: &mut Self) -> Option<&mut HeaderSlice<H, T>> {
        if this.with_fat_arc(|a| a.is_unique()) {
            Some(unsafe { &mut (*fat_pointer(this.p).as_ptr()).data })
        } else {
            None
        }
    }
    fn with_fat_arc<R>(&self, f: impl FnOnce(&Arc<HeaderSlice<H, T>>) -> R) -> R {
        let arc = ManuallyDrop::new(Arc {
            p: unsafe { fat_pointer(self.p) },
            phantom: PhantomData,
        });
        f(&arc)
    }
    pub fn is_unique(&self) -> bool {
        self.with_fat_arc(|a| a.is_unique())
    }
    pub fn is_static(&self) -> bool {
        self.with_fat_arc(|a| a.is_static())
    }
    pub fn mark_as_intentionally_leaked(&self) {
        self.with_fat_arc(|a| a.mark_as_intentionally_leaked())
    }
    pub fn raw_ptr(&self) -> NonNull<()> {
        self.p.cast()
    }
    pub fn heap_ptr(&self) -> *const c_void {
        if self.is_static() {
            ptr::null()
        } else {
            self.p.as_ptr().cast()
        }
    }
    pub fn ptr_eq(a: &Self, b: &Self) -> bool {
        a.p == b.p
    }
    pub fn borrow_arc(&self) -> ThinArcBorrow<'_, H, T> {
        ThinArcBorrow {
            p: self.p,
            marker: PhantomData,
        }
    }
    pub fn dynamic_layout(&self) -> Layout {
        unsafe { Layout::for_value(&*fat_pointer(self.p).as_ptr()) }
    }
    pub fn offsets(&self) -> (usize, usize, usize) {
        (
            mem::offset_of!(ArcInner<Prefix<H, T>>, data.header),
            mem::offset_of!(ArcInner<Prefix<H, T>>, data.len),
            mem::offset_of!(ArcInner<Prefix<H, T>>, data.data),
        )
    }
    pub fn dst_offsets(&self) -> (usize, usize, usize) {
        let p = unsafe { fat_pointer(self.p).as_ptr() };
        let base = self.p.as_ptr().addr();
        unsafe {
            (
                ptr::addr_of!((*p).data.header).addr() - base,
                ptr::addr_of!((*p).data.len).addr() - base,
                ptr::addr_of!((*p).data.data).cast::<T>().addr() - base,
            )
        }
    }
    pub fn legacy_allocation_layout(len: usize) -> Layout {
        Layout::new::<ArcInner<Prefix<H, T>>>()
            .extend(Layout::array::<T>(len).unwrap())
            .unwrap()
            .0
    }
    pub fn into_raw(this: Self) -> NonNull<()> {
        let p =
            unsafe { NonNull::new_unchecked(ptr::addr_of_mut!((*this.p.as_ptr()).data).cast()) };
        mem::forget(this);
        p
    }
    /// # Safety
    /// Consume exactly one previous `into_raw` output with unchanged metadata and matching types.
    pub unsafe fn from_raw(p: NonNull<()>) -> Self {
        Self {
            p: unsafe {
                NonNull::new_unchecked(
                    p.cast::<u8>()
                        .as_ptr()
                        .sub(mem::offset_of!(ArcInner<Prefix<H, T>>, data))
                        .cast(),
                )
            },
            marker: PhantomData,
        }
    }
}
impl<H, T> Deref for ThinArc<H, T> {
    type Target = HeaderSlice<H, T>;
    fn deref(&self) -> &Self::Target {
        unsafe { &(*fat_pointer(self.p).as_ptr()).data }
    }
}
impl<H, T> Clone for ThinArc<H, T> {
    fn clone(&self) -> Self {
        let arc = self.with_fat_arc(Clone::clone);
        let p = arc.p.cast();
        mem::forget(arc);
        Self {
            p,
            marker: PhantomData,
        }
    }
}
impl<H, T> Drop for ThinArc<H, T> {
    fn drop(&mut self) {
        drop(Arc {
            p: unsafe { fat_pointer(self.p) },
            phantom: PhantomData,
        });
    }
}
#[repr(transparent)]
pub struct ThinArcBorrow<'a, H: 'a, T: 'a> {
    p: ThinArcPointer<H, T>,
    marker: PhantomData<&'a ThinArc<H, T>>,
}
unsafe impl<H: Send + Sync, T: Send + Sync> Send for ThinArcBorrow<'_, H, T> {}
unsafe impl<H: Send + Sync, T: Send + Sync> Sync for ThinArcBorrow<'_, H, T> {}
impl<H, T> Copy for ThinArcBorrow<'_, H, T> {}
impl<H, T> Clone for ThinArcBorrow<'_, H, T> {
    fn clone(&self) -> Self {
        *self
    }
}
impl<'a, H, T> ThinArcBorrow<'a, H, T> {
    pub fn with_arc<R>(&self, f: impl FnOnce(&ThinArc<H, T>) -> R) -> R {
        let owner = ManuallyDrop::new(ThinArc {
            p: self.p,
            marker: PhantomData,
        });
        f(&owner)
    }
    pub fn ptr_eq(a:&Self,b:&Self)->bool {a.p==b.p}
    pub fn get(&self) -> &'a HeaderSlice<H, T> {
        unsafe { &(*fat_pointer(self.p).as_ptr()).data }
    }
    pub fn clone_arc(&self) -> ThinArc<H, T> {
        let owner = ManuallyDrop::new(ThinArc {
            p: self.p,
            marker: PhantomData,
        });
        (*owner).clone()
    }
}

impl<H: PartialEq, T: PartialEq> PartialEq for HeaderSlice<H, T> {
    fn eq(&self, other: &Self) -> bool {
        self.header == other.header && self.slice() == other.slice()
    }
}
impl<H: Eq, T: Eq> Eq for HeaderSlice<H, T> {}
impl<H: fmt::Debug, T: fmt::Debug> fmt::Debug for HeaderSlice<H, T> {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        f.debug_struct("HeaderSlice")
            .field("header", &self.header)
            .field("slice", &self.slice())
            .finish()
    }
}
impl<H: PartialEq, T: PartialEq> PartialEq for ThinArc<H, T> {
    fn eq(&self, other: &Self) -> bool {
        Self::ptr_eq(self, other) || **self == **other
    }
}
impl<H: Eq, T: Eq> Eq for ThinArc<H, T> {}
impl<H: fmt::Debug, T: fmt::Debug> fmt::Debug for ThinArc<H, T> {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        (**self).fmt(f)
    }
}
unsafe impl<H, T> StableDeref for ThinArc<H, T> {}
unsafe impl<H, T> CloneStableDeref for ThinArc<H, T> {}
impl<H, T> AsRef<HeaderSlice<H, T>> for ThinArc<H, T> {
    fn as_ref(&self) -> &HeaderSlice<H, T> {
        self
    }
}
impl<H, T> std::borrow::Borrow<HeaderSlice<H, T>> for ThinArc<H, T> {
    fn borrow(&self) -> &HeaderSlice<H, T> {
        self
    }
}
impl<H, T> Deref for ThinArcBorrow<'_, H, T> {
    type Target = HeaderSlice<H, T>;
    fn deref(&self) -> &Self::Target {
        self.get()
    }
}
impl<H: fmt::Debug, T: fmt::Debug> fmt::Debug for ThinArcBorrow<'_, H, T> {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        self.get().fmt(f)
    }
}
#[repr(transparent)]
pub struct UniqueThinArc<H, T>(ThinArc<H, T>);
impl<H, T> UniqueThinArc<H, T> {
    pub fn from_header_and_iter<I: ExactSizeIterator<Item = T>>(header: H, items: I) -> Self {
        Self(ThinArc::from_header_and_iter(header, items))
    }
    pub fn from_header_and_iter_with_size<I: Iterator<Item = T>>(
        header: H,
        items: I,
        len: usize,
    ) -> Self {
        Self(ThinArc::from_header_and_iter_with_size(header, items, len))
    }
    pub fn shareable(self) -> ThinArc<H, T> {
        self.0
    }
    pub fn header_mut(&mut self) -> &mut H {
        &mut ThinArc::get_mut(&mut self.0).unwrap().header
    }
    pub fn data_mut(&mut self) -> &mut [T] {
        ThinArc::get_mut(&mut self.0).unwrap().slice_mut()
    }
}
impl<H, T> Deref for UniqueThinArc<H, T> {
    type Target = HeaderSlice<H, T>;
    fn deref(&self) -> &Self::Target {
        &self.0
    }
}

#[repr(transparent)]
pub struct ThinArcUnion<H1, T1, H2, T2> {
    p: NonNull<()>,
    marker: PhantomData<(ThinArc<H1, T1>, ThinArc<H2, T2>)>,
}
unsafe impl<H1: Send + Sync, T1: Send + Sync, H2: Send + Sync, T2: Send + Sync> Send
    for ThinArcUnion<H1, T1, H2, T2>
{
}
unsafe impl<H1: Send + Sync, T1: Send + Sync, H2: Send + Sync, T2: Send + Sync> Sync
    for ThinArcUnion<H1, T1, H2, T2>
{
}
#[derive(Debug)]
pub enum ThinArcUnionBorrow<'a, H1: 'a, T1: 'a, H2: 'a, T2: 'a> {
    First(ThinArcBorrow<'a, H1, T1>),
    Second(ThinArcBorrow<'a, H2, T2>),
}
// The pointer must retain a tagged live allocation of the matching types for 'a.
unsafe fn thin_union_borrow<'a, H1, T1, H2, T2>(
    p: NonNull<()>,
) -> ThinArcUnionBorrow<'a, H1, T1, H2, T2> {
    if p.as_ptr().addr() & 1 == 0 {
        ThinArcUnionBorrow::First(ThinArcBorrow {
            p: p.cast(),
            marker: PhantomData,
        })
    } else {
        ThinArcUnionBorrow::Second(ThinArcBorrow {
            p: p.map_addr(|a| std::num::NonZeroUsize::new(a.get() & !1).unwrap())
                .cast(),
            marker: PhantomData,
        })
    }
}
impl<H1, T1, H2, T2> ThinArcUnion<H1, T1, H2, T2> {
    pub fn from_first(value: ThinArc<H1, T1>) -> Self {
        let p = value.p.cast();
        mem::forget(value);
        Self {
            p,
            marker: PhantomData,
        }
    }
    pub fn from_second(value: ThinArc<H2, T2>) -> Self {
        let p = value.p.cast::<()>().map_addr(|a| a | 1);
        mem::forget(value);
        Self {
            p,
            marker: PhantomData,
        }
    }
    pub fn borrow(&self) -> ThinArcUnionBorrow<'_, H1, T1, H2, T2> {
        unsafe { thin_union_borrow(self.p) }
    }
    pub fn as_first(&self) -> Option<ThinArcBorrow<'_, H1, T1>> {
        match self.borrow() {
            ThinArcUnionBorrow::First(x) => Some(x),
            _ => None,
        }
    }
    pub fn as_second(&self) -> Option<ThinArcBorrow<'_, H2, T2>> {
        match self.borrow() {
            ThinArcUnionBorrow::Second(x) => Some(x),
            _ => None,
        }
    }
    pub fn ptr(&self) -> NonNull<()> {
        self.p
    }
    pub fn ptr_eq(this: &Self, other: &Self) -> bool {
        this.p == other.p
    }
    pub fn is_first(&self) -> bool {
        self.p.as_ptr().addr() & 1 == 0
    }
    pub fn is_second(&self) -> bool {
        !self.is_first()
    }
}
impl<H1, T1, H2, T2> Clone for ThinArcUnion<H1, T1, H2, T2> {
    fn clone(&self) -> Self {
        match self.borrow() {
            ThinArcUnionBorrow::First(x) => Self::from_first(x.clone_arc()),
            ThinArcUnionBorrow::Second(x) => Self::from_second(x.clone_arc()),
        }
    }
}
impl<H1, T1, H2, T2> Drop for ThinArcUnion<H1, T1, H2, T2> {
    fn drop(&mut self) {
        match self.borrow() {
            ThinArcUnionBorrow::First(x) => drop(ThinArc {
                p: x.p,
                marker: PhantomData,
            }),
            ThinArcUnionBorrow::Second(x) => drop(ThinArc {
                p: x.p,
                marker: PhantomData,
            }),
        }
    }
}
impl<H1: PartialEq, T1: PartialEq, H2: PartialEq, T2: PartialEq> PartialEq
    for ThinArcUnion<H1, T1, H2, T2>
{
    fn eq(&self, other: &Self) -> bool {
        match (self.borrow(), other.borrow()) {
            (ThinArcUnionBorrow::First(a), ThinArcUnionBorrow::First(b)) => a.get() == b.get(),
            (ThinArcUnionBorrow::Second(a), ThinArcUnionBorrow::Second(b)) => a.get() == b.get(),
            _ => false,
        }
    }
}
impl<H1: Eq, T1: Eq, H2: Eq, T2: Eq> Eq for ThinArcUnion<H1, T1, H2, T2> {}
impl<H1: fmt::Debug, T1: fmt::Debug, H2: fmt::Debug, T2: fmt::Debug> fmt::Debug
    for ThinArcUnion<H1, T1, H2, T2>
{
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        self.borrow().fmt(f)
    }
}
#[repr(transparent)]
pub struct ThinArcUnionBorrowPtr<'a, H1: 'a, T1: 'a, H2: 'a, T2: 'a> {
    p: NonNull<()>,
    marker: PhantomData<&'a ThinArcUnion<H1, T1, H2, T2>>,
}
unsafe impl<H1: Send + Sync, T1: Send + Sync, H2: Send + Sync, T2: Send + Sync> Send
    for ThinArcUnionBorrowPtr<'_, H1, T1, H2, T2>
{
}
unsafe impl<H1: Send + Sync, T1: Send + Sync, H2: Send + Sync, T2: Send + Sync> Sync
    for ThinArcUnionBorrowPtr<'_, H1, T1, H2, T2>
{
}
impl<H1, T1, H2, T2> Copy for ThinArcUnionBorrowPtr<'_, H1, T1, H2, T2> {}
impl<H1, T1, H2, T2> Clone for ThinArcUnionBorrowPtr<'_, H1, T1, H2, T2> {
    fn clone(&self) -> Self {
        *self
    }
}
impl<'a, H1, T1, H2, T2> ThinArcUnionBorrowPtr<'a, H1, T1, H2, T2> {
    pub fn from_union(owner: &'a ThinArcUnion<H1, T1, H2, T2>) -> Self {
        Self {
            p: owner.p,
            marker: PhantomData,
        }
    }
    pub fn from_first(value: ThinArcBorrow<'a, H1, T1>) -> Self {
        Self {
            p: value.p.cast(),
            marker: PhantomData,
        }
    }
    pub fn from_second(value: ThinArcBorrow<'a, H2, T2>) -> Self {
        Self {
            p: value.p.cast::<()>().map_addr(|a| a | 1),
            marker: PhantomData,
        }
    }
    pub fn borrow(self) -> ThinArcUnionBorrow<'a, H1, T1, H2, T2> {
        unsafe { thin_union_borrow(self.p) }
    }
    pub fn to_owned(self) -> ThinArcUnion<H1, T1, H2, T2> {
        match self.borrow() {
            ThinArcUnionBorrow::First(x) => ThinArcUnion::from_first(x.clone_arc()),
            ThinArcUnionBorrow::Second(x) => ThinArcUnion::from_second(x.clone_arc()),
        }
    }
    pub fn ptr_eq(this: &Self, other: &Self) -> bool {
        this.p == other.p
    }
}
