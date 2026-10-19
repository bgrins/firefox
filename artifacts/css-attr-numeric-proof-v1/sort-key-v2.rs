/// This determines the order in which we serialize members of a calc() sum.
///
/// See https://drafts.csswg.org/css-values-4/#sort-a-calculations-children
#[derive(
    AsRefStr, Clone, Copy, Debug, Eq, Ord, Parse, PartialEq, PartialOrd, MallocSizeOf, ToShmem,
)]
#[strum(serialize_all = "lowercase")]
#[allow(missing_docs)]
pub enum SortKey {
    #[strum(serialize = "")]
    Number,
    #[css(skip)]
    #[strum(serialize = "%")]
    Percentage,
    Cap,
    Ch,
    Cqb,
    Cqh,
    Cqi,
    Cqmax,
    Cqmin,
    Cqw,
    Deg,
    Dppx,
    Dvb,
    Dvh,
    Dvi,
    Dvmax,
    Dvmin,
    Dvw,
    Em,
    Ex,
    Ic,
    Lh,
    Lvb,
    Lvh,
    Lvi,
    Lvmax,
    Lvmin,
    Lvw,
    Ms,
    Px,
    Rcap,
    Rch,
    Rem,
    Rex,
    Ric,
    Rlh,
    S, // Sec
    Svb,
    Svh,
    Svi,
    Svmax,
    Svmin,
    Svw,
    Vb,
    Vh,
    Vi,
    Vmax,
    Vmin,
    Vw,
    #[css(skip)]
    ColorComponent,
    #[css(skip)]
    Other,
}