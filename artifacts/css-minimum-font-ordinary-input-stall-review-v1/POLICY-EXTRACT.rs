#![allow(dead_code)]
#[derive(Clone, Copy, Debug)]
enum LonghandId { FontSynthesisWeight, FontSynthesisStyle, FontSynthesisSmallCaps, FontSynthesisPosition, FontKerning, FontOpticalSizing, FontVariantLigatures }
#[derive(Clone, Copy, Debug)]
enum PrioritaryPropertyId { FontSize, FontWeight, FontWidth, FontStyle, FontSizeAdjust, Direction, WritingMode, TextOrientation }
struct PrioritaryPropertyIdSet(u16);
impl PrioritaryPropertyIdSet { fn contains(&self, id: PrioritaryPropertyId) -> bool { self.0 & (1 << id as u16) != 0 } }
fn is_synthesis_longhand(id: LonghandId) -> bool {
    matches!(
        id,
        LonghandId::FontSynthesisWeight
            | LonghandId::FontSynthesisStyle
            | LonghandId::FontSynthesisSmallCaps
            | LonghandId::FontSynthesisPosition
    )
}
fn font_publication_demand(
        demand: FontDependencyDemand,
        complete: &PrioritaryPropertyIdSet,
        unprepared_font_inputs: Option<LonghandId>,
    ) -> PublicationDemand {
        use PrioritaryPropertyId::*;
        if demand == FontDependencyDemand::None {
            return PublicationDemand::Ready;
        }
        if !complete.contains(FontSize) {
            return PublicationDemand::Unresolved;
        }
        if demand >= FontDependencyDemand::FontMetrics {
            for id in [FontWeight, FontWidth, FontStyle, FontSizeAdjust] {
                if !complete.contains(id) {
                    return PublicationDemand::Metric(id);
                }
            }
        }
        if demand == FontDependencyDemand::OrientedMetrics {
            for id in [Direction, WritingMode, TextOrientation] {
                if !complete.contains(id) {
                    return PublicationDemand::Metric(id);
                }
            }
        }
        if demand >= FontDependencyDemand::FontMetrics
            && let Some(id) = unprepared_font_inputs
        {
            return if is_synthesis_longhand(id) {
                PublicationDemand::Synthesis(id)
            } else {
                PublicationDemand::Unresolved
            };
        }
        PublicationDemand::Ready
    }
enum PublicationDemand {
        Ready,
        Metric(PrioritaryPropertyId),
        Synthesis(LonghandId),
        Unresolved,
    }
#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd, Default)]
pub enum FontDependencyDemand {
    /// No font inputs.
    #[default]
    None,
    /// The computed font size.
    ComputedSize,
    /// Computed size and current font metrics.
    FontMetrics,
    /// Font metrics and writing-mode-dependent orientation.
    OrientedMetrics,
}
fn main() {
 use FontDependencyDemand::*;
 let all = PrioritaryPropertyIdSet(255);
 let mode = std::env::args().nth(1).unwrap();
 if mode == "controls" {
  assert!(matches!(font_publication_demand(None,&all,Some(LonghandId::FontKerning)),PublicationDemand::Ready));
  assert!(matches!(font_publication_demand(ComputedSize,&all,Some(LonghandId::FontKerning)),PublicationDemand::Ready));
  assert!(matches!(font_publication_demand(FontMetrics,&all,Option::None),PublicationDemand::Ready));
  assert!(matches!(font_publication_demand(FontMetrics,&PrioritaryPropertyIdSet(254),Option::None),PublicationDemand::Unresolved));
  assert!(matches!(font_publication_demand(FontMetrics,&PrioritaryPropertyIdSet(253),Option::None),PublicationDemand::Metric(PrioritaryPropertyId::FontWeight)));
  assert!(matches!(font_publication_demand(OrientedMetrics,&PrioritaryPropertyIdSet(223),Option::None),PublicationDemand::Metric(PrioritaryPropertyId::Direction)));
  for id in [LonghandId::FontSynthesisWeight,LonghandId::FontSynthesisStyle,LonghandId::FontSynthesisSmallCaps,LonghandId::FontSynthesisPosition] {
   assert!(matches!(font_publication_demand(FontMetrics,&all,Some(id)),PublicationDemand::Synthesis(_)));
  }
  println!("10 scoped policy controls passed");return;
 }
 let id = match mode.as_str() { "kerning"=>LonghandId::FontKerning,"optical"=>LonghandId::FontOpticalSizing,"ligatures"=>LonghandId::FontVariantLigatures,_=>panic!("unknown mode") };
 let result = font_publication_demand(FontMetrics,&all,Some(id));
 assert!(!matches!(result,PublicationDemand::Unresolved),"ORPHAN_PENDING: known unfinished ordinary font input has no action");
}
