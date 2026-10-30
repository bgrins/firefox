fn frame_font_demand(
    registered: bool,
    flags: ReferenceFlags,
    is_root: bool,
) -> FontDependencyDemand {
    let mut demand = FontDependencyDemand::None;
    if registered {
        flags.for_each_non_custom_dependency(is_root, |dependency| {
            demand = demand.join(dependency.font_demand);
        });
    }
    demand
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

fn preparation_needs_font_inputs(flags: ReferenceFlags, is_root: bool) -> bool {
    flags.intersects(ReferenceFlags::ATTR)
        && frame_font_demand(true, flags, is_root) != FontDependencyDemand::None
}

