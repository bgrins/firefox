/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */

//! The main cascading algorithm of the style system.

use crate::applicable_declarations::{CascadePriority, RevertKind};
use crate::color::AbsoluteColor;
use crate::computed_value_flags::ComputedValueFlags;
use crate::context::TreeCountingCaches;
use crate::custom_properties::{
    CapturedAttributeInput, ComputedCustomProperties, ComputedSubstitutionFunctions,
    ComputedValue as ComputedPropertyValue, FontDependencyDemand, Name, NonCustomReferenceMap,
    PreparedCustomValue, ReferenceFlags, References, ResumableSubstitution,
    SingleNonCustomReference, SubstitutionFunctionKind, SubstitutionGuard, SubstitutionGuardKey,
    SubstitutionLookup, SubstitutionLookupKind, SubstitutionLookupReply, SubstitutionLookupValue,
    SubstitutionPoll, VariableValue, get_attr_value_for_cycle_resolution,
    handle_invalid_at_computed_value_time, invalid_custom_value_depends_on_color_scheme,
    prepare_completed_custom_value, prepare_custom_value, remove_and_insert_initial_value,
    substitute_references_if_needed_and_apply,
};
use crate::dom::{AttributeTracker, DummyElementContext, ElementContext, TElement};
#[cfg(feature = "gecko")]
use crate::font_metrics::FontMetricsOrientation;
use crate::properties::{
    CASCADE_PROPERTY, CSSWideKeyword, ComputedValues, DeclarationImportanceIterator, LonghandId,
    LonghandIdSet, PrioritaryPropertyId, PrioritaryPropertyIdSet, PropertyDeclaration,
    PropertyDeclarationId, PropertyFlags, PropertyIdRef, ShorthandsWithPropertyReferencesCache,
    StyleBuilder, property_counts,
};
use crate::properties::{CustomDeclaration, CustomDeclarationValue, PropertyId, UnparsedValue};
use crate::properties_and_values::rule::Descriptors as PropertyDescriptors;
use crate::properties_and_values::value::ComputedValue as ComputedRegisteredValue;
use crate::rule_cache::{RuleCache, RuleCacheConditions};
use crate::rule_tree::{CascadeLevel, CascadeOrigin, RuleCascadeFlags, StrongRuleNode};
use crate::selector_map::{PrecomputedHashMap, PrecomputedHashSet};
use crate::selector_parser::PseudoElement;
use crate::shared_lock::StylesheetGuards;
use crate::style_adjuster::StyleAdjuster;
use crate::stylesheets::UrlExtraData;
use crate::stylesheets::container_rule::ContainerSizeQuery;
use crate::stylesheets::layer_rule::LayerOrder;
use crate::stylist::Stylist;
use crate::values::computed::ToComputedValue;
#[cfg(feature = "gecko")]
use crate::values::specified::length::FontBaseSize;
use crate::values::specified::position::PositionTryFallbacksTryTactic;
use crate::values::{computed, specified};
use crate::{FxHashMap, Namespace};
use hashbrown::hash_map::{Entry, EntryRef};
use selectors::matching::ElementSelectorFlags;
use servo_arc::Arc;
use smallvec::SmallVec;
use std::borrow::Cow;
use std::cmp;

/// Whether we're resolving a style with the purposes of reparenting for ::first-line.
#[derive(Copy, Clone)]
#[allow(missing_docs)]
pub enum FirstLineReparenting<'a> {
    No,
    Yes {
        /// The style we're re-parenting for ::first-line. ::first-line only affects inherited
        /// properties so we use this to avoid some work and also ensure correctness by copying the
        /// reset structs from this style.
        style_to_reparent: &'a ComputedValues,
    },
}

/// Performs the CSS cascade, computing new styles for an element from its parent style.
///
/// The arguments are:
///
///   * `device`: Used to get the initial viewport and other external state.
///
///   * `rule_node`: The rule node in the tree that represent the CSS rules that
///   matched.
///
///   * `parent_style`: The parent style, if applicable; if `None`, this is the root node.
///
/// Returns the computed values.
///   * `flags`: Various flags.
///
pub fn cascade<E>(
    stylist: &Stylist,
    pseudo: Option<&PseudoElement>,
    rule_node: &StrongRuleNode,
    guards: &StylesheetGuards,
    parent_style: Option<&ComputedValues>,
    layout_parent_style: Option<&ComputedValues>,
    first_line_reparenting: FirstLineReparenting,
    try_tactic: &PositionTryFallbacksTryTactic,
    visited_rules: Option<&StrongRuleNode>,
    cascade_input_flags: ComputedValueFlags,
    included_cascade_flags: RuleCascadeFlags,
    rule_cache: Option<&RuleCache>,
    rule_cache_conditions: &mut RuleCacheConditions,
    element: Option<E>,
    tree_counting_caches: &mut TreeCountingCaches,
) -> Arc<ComputedValues>
where
    E: TElement,
{
    cascade_rules(
        stylist,
        pseudo,
        rule_node,
        guards,
        parent_style,
        layout_parent_style,
        first_line_reparenting,
        try_tactic,
        CascadeMode::Unvisited { visited_rules },
        cascade_input_flags,
        included_cascade_flags,
        rule_cache,
        rule_cache_conditions,
        element,
        tree_counting_caches,
    )
}

struct DeclarationIterator<'a> {
    // Global to the iteration.
    guards: &'a StylesheetGuards<'a>,
    restriction: PropertyFlags,
    // The rule we're iterating over.
    current_rule_node: Option<&'a StrongRuleNode>,
    // Per rule state.
    declarations: DeclarationImportanceIterator<'a>,
    priority: CascadePriority,
}

impl<'a> DeclarationIterator<'a> {
    #[inline]
    fn new(
        rule_node: &'a StrongRuleNode,
        guards: &'a StylesheetGuards,
        pseudo: Option<&PseudoElement>,
    ) -> Self {
        let restriction = pseudo.map_or(PropertyFlags::empty(), |p| p.property_restriction());
        let mut iter = Self {
            guards,
            current_rule_node: Some(rule_node),
            priority: CascadePriority::new(
                CascadeLevel::new(CascadeOrigin::UA),
                LayerOrder::root(),
                RuleCascadeFlags::empty(),
            ),
            declarations: DeclarationImportanceIterator::default(),
            restriction,
        };
        iter.update_for_node(rule_node);
        iter
    }

    fn update_for_node(&mut self, node: &'a StrongRuleNode) {
        self.priority = node.cascade_priority();
        let guard = self.priority.cascade_level().origin().guard(self.guards);
        self.declarations = match node.style_source() {
            Some(source) => source.read(guard).declaration_importance_iter(),
            None => DeclarationImportanceIterator::default(),
        };
    }
}

impl<'a> Iterator for DeclarationIterator<'a> {
    type Item = (&'a PropertyDeclaration, CascadePriority);

    #[inline]
    fn next(&mut self) -> Option<Self::Item> {
        loop {
            if let Some((decl, importance)) = self.declarations.next_back() {
                if self.priority.cascade_level().is_important() != importance.important() {
                    continue;
                }

                if !self.restriction.is_empty() {
                    // decl.id() is either a longhand or a custom
                    // property.  Custom properties are always allowed, but
                    // longhands are only allowed if they have our
                    // restriction flag set.
                    if let PropertyDeclarationId::Longhand(id) = decl.id()
                        && !id.flags().contains(self.restriction)
                        && self.priority.cascade_level().origin() != CascadeOrigin::UA
                    {
                        continue;
                    }
                }

                return Some((decl, self.priority));
            }

            let next_node = self.current_rule_node.take()?.parent()?;
            self.current_rule_node = Some(next_node);
            self.update_for_node(next_node);
        }
    }
}

fn cascade_rules<E>(
    stylist: &Stylist,
    pseudo: Option<&PseudoElement>,
    rule_node: &StrongRuleNode,
    guards: &StylesheetGuards,
    parent_style: Option<&ComputedValues>,
    layout_parent_style: Option<&ComputedValues>,
    first_line_reparenting: FirstLineReparenting,
    try_tactic: &PositionTryFallbacksTryTactic,
    cascade_mode: CascadeMode,
    cascade_input_flags: ComputedValueFlags,
    included_cascade_flags: RuleCascadeFlags,
    rule_cache: Option<&RuleCache>,
    rule_cache_conditions: &mut RuleCacheConditions,
    element: Option<E>,
    tree_counting_caches: &mut TreeCountingCaches,
) -> Arc<ComputedValues>
where
    E: TElement,
{
    apply_declarations(
        stylist,
        pseudo,
        rule_node,
        guards,
        DeclarationIterator::new(rule_node, guards, pseudo),
        parent_style,
        layout_parent_style,
        first_line_reparenting,
        try_tactic,
        cascade_mode,
        cascade_input_flags,
        included_cascade_flags,
        rule_cache,
        rule_cache_conditions,
        element,
        tree_counting_caches,
    )
}

/// Whether we're cascading for visited or unvisited styles.
#[derive(Clone, Copy)]
pub enum CascadeMode<'a, 'b> {
    /// We're cascading for unvisited styles.
    Unvisited {
        /// The visited rules that should match the visited style.
        visited_rules: Option<&'a StrongRuleNode>,
    },
    /// We're cascading for visited styles.
    Visited {
        /// The cascade for our unvisited style.
        unvisited_context: &'a computed::Context<'b>,
    },
}

fn iter_declarations<'c, 'decls: 'c>(
    iter: impl Iterator<Item = (&'decls PropertyDeclaration, CascadePriority)>,
    declarations: &mut Declarations<'decls>,
    mut custom: Option<(&mut Cascade<'c>, &mut computed::Context)>,
    attribute_tracker: &mut AttributeTracker,
) {
    for (declaration, priority) in iter {
        if let PropertyDeclaration::Custom(ref declaration) = *declaration {
            if let Some((ref mut cascade, ref mut context)) = custom {
                cascade.cascade_custom_property(context, declaration, priority);
            }
        } else {
            let id = declaration.id().as_longhand().unwrap();
            declarations.note_declaration(declaration, priority, id);
            if Cascade::might_have_non_custom_or_attr_dependency(id, declaration)
                && let Some((ref mut cascade, ref mut context)) = custom
            {
                cascade.maybe_note_non_custom_dependency(
                    context,
                    id,
                    declaration,
                    attribute_tracker,
                );
            }
        }
    }
}

/// NOTE: This function expects the declaration with more priority to appear
/// first.
pub fn apply_declarations<'decls, E, I>(
    stylist: &Stylist,
    pseudo: Option<&PseudoElement>,
    rules: &StrongRuleNode,
    guards: &StylesheetGuards,
    iter: I,
    parent_style: Option<&ComputedValues>,
    layout_parent_style: Option<&ComputedValues>,
    first_line_reparenting: FirstLineReparenting<'_>,
    try_tactic: &PositionTryFallbacksTryTactic,
    cascade_mode: CascadeMode,
    cascade_input_flags: ComputedValueFlags,
    included_cascade_flags: RuleCascadeFlags,
    rule_cache: Option<&RuleCache>,
    rule_cache_conditions: &mut RuleCacheConditions,
    element: Option<E>,
    tree_counting_caches: &mut TreeCountingCaches,
) -> Arc<ComputedValues>
where
    E: TElement,
    I: Iterator<Item = (&'decls PropertyDeclaration, CascadePriority)>,
{
    debug_assert!(layout_parent_style.is_none() || parent_style.is_some());
    let device = stylist.device();
    let inherited_style = parent_style.unwrap_or(device.default_computed_values());
    let is_root_element = pseudo.is_none() && element.is_some_and(|e| e.is_root());
    let container_size_query =
        ContainerSizeQuery::for_option_element(element, Some(inherited_style), pseudo.is_some());

    let originating_element = element.map(|e| e.ultimate_originating_element());
    let element_context = match originating_element {
        Some(ref e) => e as &dyn ElementContext,
        None => &DummyElementContext {},
    };

    let mut context = computed::Context::new(
        // We'd really like to own the rules here to avoid refcount traffic, but
        // animation's usage of `apply_declarations` make this tricky. See bug
        // 1375525.
        StyleBuilder::new(
            device,
            Some(stylist),
            parent_style,
            pseudo,
            Some(rules.clone()),
            is_root_element,
        ),
        stylist.quirks_mode(),
        rule_cache_conditions,
        container_size_query,
        included_cascade_flags,
        element_context,
        tree_counting_caches,
    );

    context.style().add_flags(cascade_input_flags);
    // Reuse flags from computing registered custom properties initial values, such as
    // whether they depend on viewport units.
    context
        .style()
        .add_flags(stylist.get_custom_property_initial_values_flags());

    let using_cached_reset_properties;
    let ignore_colors = context.builder.device.forced_colors().is_active();
    let mut cascade = Cascade::new(first_line_reparenting, stylist, ignore_colors);
    let mut declarations = Default::default();
    let mut shorthand_cache = ShorthandsWithPropertyReferencesCache::default();
    let mut attribute_tracker = AttributeTracker::new(element_context);

    let properties_to_apply = match cascade_mode {
        CascadeMode::Visited { unvisited_context } => {
            context.builder.substitution_functions =
                unvisited_context.builder.substitution_functions.clone();
            context.builder.writing_mode = unvisited_context.builder.writing_mode;
            context.builder.color_scheme = unvisited_context.builder.color_scheme;
            // We never insert visited styles into the cache so we don't need to try looking it up.
            // It also wouldn't be super-profitable, only a handful :visited properties are
            // non-inherited.
            using_cached_reset_properties = false;
            // If we match the same rules when visited and unvisited, and we know there isn't any
            // visited-dependent properties, we can avoid gathering the declarations, we know none
            // would be relevant.
            if unvisited_context.builder.rules.as_ref() != Some(rules)
                || unvisited_context
                    .builder
                    .flags()
                    .intersects(ComputedValueFlags::USES_VISITED_DEPENDENT_PROPERTIES)
            {
                iter_declarations(iter, &mut declarations, None, &mut attribute_tracker);
            }
            LonghandIdSet::visited_dependent()
        }
        CascadeMode::Unvisited { .. } => {
            cascade.init_custom_properties(&mut context);
            iter_declarations(
                iter,
                &mut declarations,
                Some((&mut cascade, &mut context)),
                &mut attribute_tracker,
            );
            // Detect cycles, remove properties participating in them, and resolve custom
            // properties, applying prioritary properties (font-size, color-scheme, line-height)
            // interleaved so that a custom property depending on `em`/`lh`/the used color-scheme is
            // substituted once the prioritary property it needs has been applied.
            cascade.apply_custom_and_prioritary_properties(
                &mut context,
                &declarations,
                &mut shorthand_cache,
                &mut attribute_tracker,
            );

            using_cached_reset_properties =
                cascade.try_to_use_cached_reset_properties(&mut context, rule_cache, guards);

            if using_cached_reset_properties {
                LonghandIdSet::late_group_only_inherited()
            } else {
                LonghandIdSet::late_group()
            }
        }
    };

    cascade.apply_non_prioritary_properties(
        &mut context,
        &declarations.longhand_declarations,
        &mut shorthand_cache,
        properties_to_apply,
        &mut attribute_tracker,
    );

    context.builder.attribute_references = attribute_tracker.finalize();

    cascade.finished_applying_properties(&mut context.builder);

    context.builder.clear_modified_reset();

    if let CascadeMode::Unvisited { visited_rules } = cascade_mode {
        // NOTE: This relies on finished_applying_properties() having already happened.
        if let Some(visited_rules) = visited_rules {
            cascade.compute_visited_style_if_needed(
                &mut context,
                element,
                parent_style,
                layout_parent_style,
                try_tactic,
                visited_rules,
                guards,
            );
        }

        StyleAdjuster::new(&mut context.builder).adjust(
            layout_parent_style.unwrap_or(inherited_style),
            element,
            try_tactic,
            &cascade.author_or_user_specified,
        );
    }

    if context.builder.modified_reset() || using_cached_reset_properties {
        // If we adjusted any reset structs, we can't cache this ComputedValues.
        //
        // Also, if we re-used existing reset structs, don't bother caching it back again. (Aside
        // from being wasted effort, it will be wrong, since context.rule_cache_conditions won't be
        // set appropriately if we didn't compute those reset properties.)
        context.rule_cache_conditions.borrow_mut().set_uncacheable();
    }

    if context
        .builder
        .flags()
        .intersects(ComputedValueFlags::tree_counting_function_flags())
    {
        if let Some(el) = element {
            el.apply_selector_flags(ElementSelectorFlags::MAY_HAVE_TREE_COUNTING_FUNCTION);
        } else {
            debug_assert!(
                false,
                "Tree counting function flag applied without an element?"
            );
        }
    }

    context.builder.build()
}

/// For ignored colors mode, we sometimes want to do something equivalent to
/// "revert-or-initial", where we `revert` for a given origin, but then apply a
/// given initial value if nothing in other origins did override it.
///
/// This is a bit of a clunky way of achieving this.
type DeclarationsToApplyUnlessOverriden = SmallVec<[PropertyDeclaration; 2]>;

fn is_base_appearance(context: &computed::Context) -> bool {
    use computed::Appearance;
    let box_style = context.builder.get_box();
    match *box_style.get_appearance() {
        Appearance::BaseSelect => {
            matches!(
                box_style.get__moz_default_appearance(),
                Appearance::Listbox | Appearance::Menulist
            )
        }
        Appearance::Base => *box_style.get__moz_default_appearance() != Appearance::None,
        _ => false,
    }
}

fn tweak_when_ignoring_colors(
    context: &computed::Context,
    longhand_id: LonghandId,
    origin: CascadeOrigin,
    declaration: &mut Cow<PropertyDeclaration>,
    declarations_to_apply_unless_overridden: &mut DeclarationsToApplyUnlessOverriden,
) {
    use crate::values::computed::ToComputedValue;
    use crate::values::specified::Color;

    if !longhand_id.ignored_when_document_colors_disabled() {
        return;
    }

    let is_ua_or_user_rule = matches!(origin, CascadeOrigin::User | CascadeOrigin::UA);
    if is_ua_or_user_rule {
        return;
    }

    // Always honor colors if forced-color-adjust is set to none.
    let forced = *context
        .builder
        .get_inherited_text()
        .get_forced_color_adjust();
    if forced == computed::ForcedColorAdjust::None {
        return;
    }

    fn alpha_channel(color: &Color, context: &computed::Context) -> f32 {
        // We assume here currentColor is opaque.
        color
            .to_computed_value(context)
            .resolve_to_absolute(&AbsoluteColor::BLACK)
            .alpha
    }

    // A few special-cases ahead.
    match **declaration {
        // Honor CSS-wide keywords like unset / revert / initial...
        PropertyDeclaration::CSSWideKeyword(..) => return,
        PropertyDeclaration::BackgroundColor(ref color) => {
            // We honor system colors and transparent colors unconditionally.
            //
            // NOTE(emilio): We honor transparent unconditionally, like we do
            // for color, even though it causes issues like bug 1625036. The
            // reasoning is that the conditions that trigger that (having
            // mismatched widget and default backgrounds) are both uncommon, and
            // broken in other applications as well, and not honoring
            // transparent makes stuff uglier or break unconditionally
            // (bug 1666059, bug 1755713).
            if color.honored_in_forced_colors_mode(context, /* allow_transparent = */ true) {
                return;
            }
            // For background-color, we revert or initial-with-preserved-alpha
            // otherwise, this is needed to preserve semi-transparent
            // backgrounds.
            let alpha = alpha_channel(color, context);
            if alpha == 0.0 {
                return;
            }
            let mut color = context.builder.device.default_background_color();
            color.alpha = alpha;
            declarations_to_apply_unless_overridden
                .push(PropertyDeclaration::BackgroundColor(color.into()))
        }
        PropertyDeclaration::Color(ref color) => {
            // We honor color: transparent and system colors.
            if color
                .0
                .honored_in_forced_colors_mode(context, /* allow_transparent = */ true)
            {
                return;
            }
            // If the inherited color would be transparent, but we would
            // override this with a non-transparent color, then override it with
            // the default color. Otherwise just let it inherit through.
            if context
                .builder
                .get_parent_inherited_text()
                .get_color()
                .alpha
                == 0.0
            {
                let color = context.builder.device.default_color();
                declarations_to_apply_unless_overridden.push(PropertyDeclaration::Color(
                    specified::ColorPropertyValue(color.into()),
                ))
            }
        }
        // We honor url background-images if backplating.
        #[cfg(feature = "gecko")]
        PropertyDeclaration::BackgroundImage(ref bkg) => {
            use crate::values::generics::image::Image;
            if crate::pref!("browser.display.permit_backplate")
                && bkg
                    .0
                    .iter()
                    .all(|image| matches!(*image, Image::Url(..) | Image::None))
            {
                return;
            }
        }
        _ => {
            // We honor system colors more generally for all colors.
            //
            // We used to honor transparent but that causes accessibility
            // regressions like bug 1740924.
            //
            // NOTE(emilio): This doesn't handle caret-color and accent-color
            // because those use a slightly different syntax (<color> | auto for
            // example).
            //
            // That's probably fine though, as using a system color for
            // caret-color doesn't make sense (using currentColor is fine), and
            // we ignore accent-color in high-contrast-mode anyways.
            if let Some(color) = declaration.color_value()
                && color
                    .honored_in_forced_colors_mode(context, /* allow_transparent = */ false)
            {
                return;
            }
        }
    }

    *declaration.to_mut() =
        PropertyDeclaration::css_wide_keyword(longhand_id, CSSWideKeyword::Revert);
}

/// We track the index only for prioritary properties. For other properties we can just iterate.
type DeclarationIndex = u32;

/// "Prioritary" properties are properties that other properties depend on in one way or another.
///
/// We keep track of their position in the declaration vector, in order to be able to cascade them
/// separately in precise order.
#[derive(Copy, Clone)]
struct PrioritaryDeclarationPosition {
    // DeclarationIndex::MAX signals no index.
    most_important: DeclarationIndex,
    least_important: DeclarationIndex,
}

impl Default for PrioritaryDeclarationPosition {
    fn default() -> Self {
        Self {
            most_important: DeclarationIndex::MAX,
            least_important: DeclarationIndex::MAX,
        }
    }
}

#[derive(Copy, Clone)]
struct Declaration<'a> {
    decl: &'a PropertyDeclaration,
    priority: CascadePriority,
    next_index: DeclarationIndex,
}

/// The set of property declarations from our rules.
#[derive(Default)]
pub(crate) struct Declarations<'a> {
    /// Whether we have any prioritary property. This is just a minor optimization.
    has_prioritary_properties: bool,
    /// A list of all the applicable longhand declarations.
    longhand_declarations: SmallVec<[Declaration<'a>; 64]>,
    /// The prioritary property position data.
    prioritary_positions: [PrioritaryDeclarationPosition; property_counts::PRIORITARY],
}

impl<'a> Declarations<'a> {
    fn note_prioritary_property(&mut self, id: PrioritaryPropertyId) {
        let new_index = self.longhand_declarations.len();
        if new_index >= DeclarationIndex::MAX as usize {
            // This prioritary property is past the amount of declarations we can track. Let's give
            // up applying it to prevent getting confused.
            return;
        }

        self.has_prioritary_properties = true;
        let new_index = new_index as DeclarationIndex;
        let position = &mut self.prioritary_positions[id as usize];
        if position.most_important == DeclarationIndex::MAX {
            // We still haven't seen this property, record the current position as the most
            // prioritary index.
            position.most_important = new_index;
        } else {
            // Let the previous item in the list know about us.
            self.longhand_declarations[position.least_important as usize].next_index = new_index;
        }
        position.least_important = new_index;
    }

    fn note_declaration(
        &mut self,
        decl: &'a PropertyDeclaration,
        priority: CascadePriority,
        id: LonghandId,
    ) {
        if let Some(id) = PrioritaryPropertyId::from_longhand(id) {
            self.note_prioritary_property(id);
        }
        self.longhand_declarations.push(Declaration {
            decl,
            priority,
            next_index: 0,
        });
    }
}

#[derive(Default)]
struct RevertedSet {
    // Just to avoid the hashmap lookup in the common case.
    longhands_set: LonghandIdSet,
    longhands: FxHashMap<LonghandId, (CascadePriority, RevertKind)>,
    custom: PrecomputedHashMap<Name, (CascadePriority, RevertKind)>,
}

#[derive(Default)]
struct SeenSubstitutionFunctions<'a> {
    /// The boolean means whether the value may have references. If false, we don't need to bother
    /// performing lookups for cycle detection.
    var: PrecomputedHashMap<&'a Name, bool>,
    attr: PrecomputedHashMap<&'a Namespace, PrecomputedHashSet<&'a Name>>,
}

#[derive(Default)]
struct SeenSet<'a> {
    longhands: LonghandIdSet,
    custom: SeenSubstitutionFunctions<'a>,
}

/// Only registered (typed) properties emit a non-custom edge, from their own value.
fn find_non_custom_references(
    registration: &PropertyDescriptors,
    value: &VariableValue,
    is_root_element: bool,
) -> ReferenceFlags {
    use crate::properties_and_values::syntax::data_type::DependentDataTypes;

    let mut result = ReferenceFlags::empty();
    let Some(syntax) = registration.syntax.as_ref() else {
        return result;
    };
    let dependent_types = syntax.dependent_types();
    let may_reference_length = dependent_types.intersects(DependentDataTypes::LENGTH);
    if may_reference_length {
        result |= value.references.non_custom_references(is_root_element);
    }
    let may_reference_image = syntax.components.iter().any(|component| {
        use crate::properties_and_values::syntax::{ComponentName, data_type::DataType};
        matches!(component.name(), ComponentName::DataType(DataType::Image))
    });
    if dependent_types.intersects(DependentDataTypes::COLOR) || may_reference_image {
        // Defer possible color computation; selected values determine the graph edge.
        result |= ReferenceFlags::COLOR_SCHEME;
    }
    result
}

/// Resolves the custom properties for a single `@keyframes` keyframe, layered on top of the base
/// style's already-computed custom properties.
///
/// `@keyframes` aren't part of the regular cascade (see bug 1883255), so this lets the caller seed
/// the substitution map with the element's computed custom properties, cascade the keyframe's
/// custom declarations on top, and resolve them (running cycle detection and substitution) into
/// `context.builder.substitution_functions`, which the subsequent animation-value computation reads
/// to substitute `var()` references.
pub struct KeyframeCustomPropertiesBuilder<'a> {
    cascade: Cascade<'a>,
    decls: Declarations<'a>,
    shorthand_cache: ShorthandsWithPropertyReferencesCache,
}

impl<'a> KeyframeCustomPropertiesBuilder<'a> {
    /// Creates a new builder, seeding the substitution map with `base` (typically the element's
    /// computed custom properties).
    pub fn new(
        stylist: &'a Stylist,
        context: &mut computed::Context,
        base: ComputedCustomProperties,
    ) -> Self {
        context.builder.substitution_functions =
            ComputedSubstitutionFunctions::new(Some(base), None);
        Self {
            cascade: Cascade::new_for_custom_properties_only(stylist),
            decls: Declarations::default(),
            shorthand_cache: ShorthandsWithPropertyReferencesCache::default(),
        }
    }

    /// Cascades a single custom-property declaration from the keyframe.
    pub fn cascade(
        &mut self,
        context: &mut computed::Context,
        declaration: &'a CustomDeclaration,
        priority: CascadePriority,
    ) {
        self.cascade
            .cascade_custom_property(context, declaration, priority);
    }

    /// Prepares typed attributes referenced by an ordinary keyframe declaration.
    pub fn prepare_attributes(
        &mut self,
        context: &mut computed::Context,
        value: &'a UnparsedValue,
        attribute_tracker: &mut AttributeTracker,
    ) {
        self.cascade
            .update_attributes_map(context, &value.variable_value, attribute_tracker);
    }

    /// Resolves the cascaded custom properties into `context.builder.substitution_functions`.
    pub fn build(
        mut self,
        context: &mut computed::Context,
        attribute_tracker: &mut AttributeTracker,
    ) {
        self.cascade.apply_custom_and_prioritary_properties(
            context,
            &self.decls,
            &mut self.shorthand_cache,
            attribute_tracker,
        );
    }
}

type NonCustomPropertyReferences = NonCustomReferenceMap<Vec<(LonghandId, Arc<UnparsedValue>)>>;

fn priority_has_dynamic_declarations(decls: &Declarations, id: PrioritaryPropertyId) -> bool {
    let mut index = decls.prioritary_positions[id as usize].most_important;
    if index == DeclarationIndex::MAX {
        return false;
    }
    loop {
        let entry = &decls.longhand_declarations[index as usize];
        if matches!(entry.decl, PropertyDeclaration::WithVariables(..)) {
            return true;
        }
        index = entry.next_index;
        if index == 0 {
            return false;
        }
    }
}

fn next_unprepared_font_input(
    decls: &Declarations,
    completed: &LonghandIdSet,
) -> Option<LonghandId> {
    decls.longhand_declarations.iter().find_map(|entry| {
        let PropertyDeclarationId::Longhand(id) = entry.decl.id() else {
            return None;
        };
        if completed.contains(id) {
            return None;
        }
        matches!(
            id.name(),
            "font-feature-settings"
                | "font-language-override"
                | "font-palette"
                | "font-synthesis-position"
                | "font-synthesis-small-caps"
                | "font-synthesis-style"
                | "font-synthesis-weight"
                | "font-variant-alternates"
                | "font-variant-east-asian"
                | "font-variant-ligatures"
                | "font-variant-numeric"
                | "font-variation-settings"
                | "font-variant-caps"
                | "font-kerning"
                | "font-variant-emoji"
                | "font-variant-position"
                | "font-optical-sizing"
                | "math-style"
                | "math-shift"
                | "-moz-osx-font-smoothing"
                | "-moz-math-variant"
        )
        .then_some(id)
    })
}

#[derive(Clone, Copy, Debug)]
enum FontTarget {
    Metric(PrioritaryPropertyId),
    Synthesis(LonghandId),
    ComputedSize,
}

impl FontTarget {
    fn same_as(self, other: Self) -> bool {
        match (self, other) {
            (Self::ComputedSize, Self::ComputedSize) => true,
            (Self::Metric(left), Self::Metric(right)) => left.to_longhand() == right.to_longhand(),
            (Self::Synthesis(left), Self::Synthesis(right)) => left == right,
            _ => false,
        }
    }
}

fn is_synthesis_longhand(id: LonghandId) -> bool {
    matches!(
        id,
        LonghandId::FontSynthesisWeight
            | LonghandId::FontSynthesisStyle
            | LonghandId::FontSynthesisSmallCaps
            | LonghandId::FontSynthesisPosition
    )
}

fn next_font_declaration(
    declarations: &Declarations,
    longhand: LonghandId,
    start: usize,
) -> Option<usize> {
    declarations
        .longhand_declarations
        .iter()
        .enumerate()
        .skip(start)
        .find_map(|(index, entry)| {
            (entry.decl.id() == PropertyDeclarationId::Longhand(longhand)).then_some(index)
        })
}

fn size_input_prefix_is_stable(
    declarations: &Declarations,
    id: PrioritaryPropertyId,
    flags: RuleCascadeFlags,
    mut revert: Option<(CascadePriority, RevertKind)>,
) -> bool {
    let mut index = declarations.prioritary_positions[id as usize].most_important;
    if index == DeclarationIndex::MAX {
        return true;
    }
    loop {
        let entry = declarations.longhand_declarations[index as usize];
        if entry
            .priority
            .flags()
            .intersects(RuleCascadeFlags::APPEARANCE_BASE)
        {
            return false;
        }
        if (entry.priority.flags() - flags).is_empty()
            && !revert.is_some_and(|(priority, kind)| {
                !priority.allows_when_reverted(&entry.priority, kind)
            })
        {
            if matches!(entry.decl, PropertyDeclaration::WithVariables(_)) {
                return false;
            }
            if let Some(kind) = entry
                .decl
                .get_css_wide_keyword()
                .and_then(|k| k.revert_kind())
            {
                revert = Some((entry.priority, kind));
            } else {
                return true;
            }
        }
        if entry.next_index == 0 {
            return true;
        }
        index = entry.next_index;
    }
}

struct ComputedSizePublicationWitness {
    parent: usize,
    device: usize,
    root: bool,
    parent_size: computed::FontSize,
    value: computed::FontSize,
    zoom: computed::Zoom,
    inherited_zoom: computed::Zoom,
    writing_mode: Option<crate::logical_geometry::WritingMode>,
}

impl ComputedSizePublicationWitness {
    fn capture(context: &computed::Context, reads_writing_mode: bool) -> Self {
        Self {
            parent: context.builder.get_parent_font() as *const _ as usize,
            device: context.device() as *const _ as usize,
            root: context.is_root_element(),
            parent_size: context.builder.get_parent_font().slow_clone_font_size(),
            value: context.builder.get_font().slow_clone_font_size(),
            zoom: context.builder.effective_zoom,
            inherited_zoom: context.builder.effective_zoom_for_inheritance,
            writing_mode: reads_writing_mode.then_some(context.builder.writing_mode),
        }
    }

    fn matches(&self, context: &computed::Context) -> bool {
        self.parent == context.builder.get_parent_font() as *const _ as usize
            && self.device == context.device() as *const _ as usize
            && self.root == context.is_root_element()
            && self.parent_size == context.builder.get_parent_font().slow_clone_font_size()
            && self.value == context.builder.get_font().slow_clone_font_size()
            && self.zoom == context.builder.effective_zoom
            && self.inherited_zoom == context.builder.effective_zoom_for_inheritance
            && self
                .writing_mode
                .is_none_or(|wm| wm == context.builder.writing_mode)
    }
}

struct ComputedSizeCertificate {
    identity: Arc<()>,
    flags: RuleCascadeFlags,
    operation: Option<PropertyDeclaration>,
    applied: PrioritaryPropertyIdSet,
    witness: ComputedSizePublicationWitness,
}

impl ComputedSizeCertificate {
    fn valid_for(&self, context: &computed::Context) -> bool {
        (self.flags - context.included_cascade_flags).is_empty()
            && ((context.included_cascade_flags - self.flags) - RuleCascadeFlags::APPEARANCE_BASE)
                .is_empty()
            && self.witness.matches(context)
    }
}

fn size_needs_keyword_family(
    operation: Option<&PropertyDeclaration>,
    parent_keyword: specified::FontSizeKeyword,
    inherited_zoom_is_one: bool,
) -> bool {
    let inherits_keyword = parent_keyword != specified::FontSizeKeyword::None;
    let Some(operation) = operation else {
        return inherited_zoom_is_one && inherits_keyword;
    };
    if let Some(keyword) = operation.get_css_wide_keyword() {
        return match keyword {
            CSSWideKeyword::Inherit | CSSWideKeyword::Unset => {
                inherited_zoom_is_one && inherits_keyword
            }
            CSSWideKeyword::Initial => true,
            CSSWideKeyword::Revert | CSSWideKeyword::RevertLayer | CSSWideKeyword::RevertRule => {
                unreachable!()
            }
        };
    }
    let PropertyDeclaration::FontSize(size) = operation else {
        unreachable!()
    };
    match size {
        specified::FontSize::Length(specified::LengthPercentage::Length(length)) => {
            length.length_unit() == specified::length::LengthUnit::Em && inherits_keyword
        }
        specified::FontSize::Length(specified::LengthPercentage::Percentage(_))
        | specified::FontSize::Smaller
        | specified::FontSize::Larger => inherits_keyword,
        specified::FontSize::Length(specified::LengthPercentage::Calc(_)) => false,
        specified::FontSize::Keyword(_) | specified::FontSize::System(_) => true,
    }
}

fn size_needs_math_depth(
    operation: Option<&PropertyDeclaration>,
    parent_keyword: specified::FontSizeKeyword,
    inherited_zoom_is_one: bool,
) -> bool {
    let Some(operation) = operation else {
        return inherited_zoom_is_one && parent_keyword.is_math();
    };
    if let Some(keyword) = operation.get_css_wide_keyword() {
        return matches!(keyword, CSSWideKeyword::Inherit | CSSWideKeyword::Unset)
            && inherited_zoom_is_one
            && parent_keyword.is_math();
    }
    let PropertyDeclaration::FontSize(size) = operation else {
        unreachable!()
    };
    match size {
        specified::FontSize::Keyword(info) => info.kw.is_math(),
        specified::FontSize::Length(specified::LengthPercentage::Length(length)) => {
            length.length_unit() == specified::length::LengthUnit::Em && parent_keyword.is_math()
        }
        specified::FontSize::Length(specified::LengthPercentage::Percentage(_))
        | specified::FontSize::Smaller
        | specified::FontSize::Larger => parent_keyword.is_math(),
        _ => false,
    }
}

fn size_length_reads_writing_mode(unit: specified::length::LengthUnit, root: bool) -> bool {
    use specified::length::LengthUnit::*;
    matches!(
        unit,
        Ch | Lh | Vi | Vb | Svi | Svb | Lvi | Lvb | Dvi | Dvb | Cqi | Cqb | Cqmin | Cqmax
    ) || (root && matches!(unit, Rch | Rlh))
}

fn size_reads_writing_mode(operation: Option<&PropertyDeclaration>, root: bool) -> bool {
    let Some(PropertyDeclaration::FontSize(specified::FontSize::Length(length))) = operation else {
        return false;
    };
    match length {
        specified::LengthPercentage::Length(length) => {
            size_length_reads_writing_mode(length.length_unit(), root)
        }
        specified::LengthPercentage::Percentage(_) => false,
        specified::LengthPercentage::Calc(calc) => {
            let mut reads = false;
            calc.0.node.clone().visit_depth_first(|node| {
                if let Some(specified::calc::Leaf::Length(length)) = node.as_leaf() {
                    reads |= size_length_reads_writing_mode(length.length_unit(), root);
                }
            });
            reads
        }
    }
}

struct ComputedSizePreparation<'a, 'b> {
    index: usize,
    size: MetricPreparation<'a, 'b>,
    text_scale: MetricPreparation<'a, 'b>,
    family: Option<MetricPreparation<'a, 'b>>,
}

impl ComputedSizePreparation<'_, '_> {
    fn poll(
        &mut self,
        cascade: &Cascade,
        context: &mut computed::Context,
        cache: &mut ShorthandsWithPropertyReferencesCache,
        tracker: &mut AttributeTracker,
        mut reply: Option<(LonghandId, FontSelectionReply)>,
    ) -> MetricPreparationStep {
        if reply.as_ref().is_some_and(|(id, _)| {
            let state = if *id == self.size.longhand {
                &self.size
            } else if *id == self.text_scale.longhand {
                &self.text_scale
            } else if self
                .family
                .as_ref()
                .is_some_and(|state| state.longhand == *id)
            {
                self.family.as_ref().unwrap()
            } else {
                return true;
            };
            state.complete || state.waiting.is_none()
        }) {
            return MetricPreparationStep::Invalidated;
        }
        for state in [&mut self.size, &mut self.text_scale]
            .into_iter()
            .chain(self.family.iter_mut())
        {
            let selected_reply = if reply.as_ref().is_some_and(|(id, _)| *id == state.longhand) {
                reply.take().map(|(_, value)| value)
            } else if reply.is_some() && !state.complete {
                return MetricPreparationStep::Invalidated;
            } else {
                None
            };
            match cascade.resume_font_selection(context, cache, tracker, state, selected_reply) {
                MetricPreparationStep::Complete => {}
                other => return other,
            }
        }
        MetricPreparationStep::Complete
    }

    fn operation(&self) -> Option<&PropertyDeclaration> {
        self.size.prepared.iter().rev().find_map(|entry| {
            (!entry
                .declaration
                .get_css_wide_keyword()
                .is_some_and(|keyword| keyword.revert_kind().is_some()))
            .then_some(&entry.declaration)
        })
    }
}

fn computed_size_selection_flags_stable(
    declarations: &Declarations,
    id: PrioritaryPropertyId,
) -> bool {
    let mut index = declarations.prioritary_positions[id as usize].most_important;
    if index == DeclarationIndex::MAX {
        return true;
    }
    loop {
        let entry = declarations.longhand_declarations[index as usize];
        if entry
            .priority
            .flags()
            .intersects(RuleCascadeFlags::APPEARANCE_BASE)
        {
            return false;
        }
        if entry.next_index == 0 {
            return true;
        }
        index = entry.next_index;
    }
}

struct PreparedMetricDeclaration {
    declaration: PropertyDeclaration,
    priority: CascadePriority,
}

struct MetricPreparation<'a, 'b> {
    longhand: LonghandId,
    declarations: &'a Declarations<'b>,
    cursor: Option<usize>,
    flags: RuleCascadeFlags,
    observed_flags: RuleCascadeFlags,
    initial_revert: Option<(CascadePriority, RevertKind)>,
    revert: Option<(CascadePriority, RevertKind)>,
    waiting: Option<Arc<UnparsedValue>>,
    substitution: Option<ResumableSubstitution<'static>>,
    substitution_generation: Option<Arc<()>>,
    prepared: SmallVec<[PreparedMetricDeclaration; 2]>,
    complete: bool,
}

struct FontSelectionReply {
    value: Arc<UnparsedValue>,
    generation: Arc<()>,
    lookup: Option<SubstitutionLookupReply>,
}

enum MetricPreparationStep {
    Prerequisites(&'static PrioritaryPropertyIdSet),
    References(LonghandId, Arc<UnparsedValue>),
    Lookup(LonghandId, Arc<UnparsedValue>, SubstitutionLookup),
    Complete,
    Invalidated,
}

impl MetricPreparation<'_, '_> {
    fn stable_for_appearance_addition(&self) -> bool {
        self.complete
            && ((self.observed_flags - self.flags) & RuleCascadeFlags::APPEARANCE_BASE).is_empty()
    }

    fn retain(&mut self, declaration: PropertyDeclaration, priority: CascadePriority) {
        debug_assert!(!matches!(
            declaration,
            PropertyDeclaration::WithVariables(..)
        ));
        let revert = declaration
            .get_css_wide_keyword()
            .and_then(|keyword| keyword.revert_kind());
        self.prepared.push(PreparedMetricDeclaration {
            declaration,
            priority,
        });
        if let Some(revert) = revert {
            self.revert = Some((priority, revert));
            self.advance();
        } else {
            self.complete = true;
        }
    }

    fn advance(&mut self) {
        let index = self
            .cursor
            .expect("advancing an exhausted declaration cursor");
        if PrioritaryPropertyId::from_longhand(self.longhand).is_none() {
            self.cursor = next_font_declaration(self.declarations, self.longhand, index + 1);
            return;
        }
        let next = self.declarations.longhand_declarations[index].next_index;
        self.cursor = (next != 0).then_some(next as usize);
    }
}

impl Cascade<'_> {
    fn begin_metric_preparation<'a, 'b>(
        &self,
        context: &computed::Context,
        declarations: &'a Declarations<'b>,
        id: PrioritaryPropertyId,
    ) -> MetricPreparation<'a, 'b> {
        use PrioritaryPropertyId::*;
        assert!(matches!(
            id,
            FontWeight
                | FontWidth
                | FontStyle
                | FontSizeAdjust
                | Direction
                | WritingMode
                | TextOrientation
                | Appearance
                | FontFamily
        ));
        self.begin_font_preparation(context, declarations, id.to_longhand())
    }

    fn begin_font_preparation<'a, 'b>(
        &self,
        context: &computed::Context,
        declarations: &'a Declarations<'b>,
        longhand: LonghandId,
    ) -> MetricPreparation<'a, 'b> {
        let cursor = if let Some(id) = PrioritaryPropertyId::from_longhand(longhand) {
            let index = declarations.prioritary_positions[id as usize].most_important;
            (index != DeclarationIndex::MAX).then_some(index as usize)
        } else {
            assert!(is_synthesis_longhand(longhand));
            next_font_declaration(declarations, longhand, 0)
        };
        let initial_revert = self.reverted.longhands.get(&longhand).copied();
        MetricPreparation {
            longhand,
            declarations,
            cursor,
            flags: context.included_cascade_flags,
            observed_flags: RuleCascadeFlags::empty(),
            initial_revert,
            revert: initial_revert,
            waiting: None,
            substitution: None,
            substitution_generation: None,
            prepared: SmallVec::new(),
            complete: false,
        }
    }

    // `completed` is supplied by the readiness scheduler, not the existing early-set ensured bit.
    fn resume_metric_preparation(
        &self,
        context: &mut computed::Context,
        cache: &mut ShorthandsWithPropertyReferencesCache,
        attribute_tracker: &mut AttributeTracker,
        state: &mut MetricPreparation,
        completed: &PrioritaryPropertyIdSet,
        resolved_reference: Option<FontSelectionReply>,
    ) -> MetricPreparationStep {
        let priority = PrioritaryPropertyId::from_longhand(state.longhand);
        if priority.is_some_and(|id| self.ensured_prioritary.contains(id))
            || state.flags != context.included_cascade_flags
            || self.seen.longhands.contains(state.longhand)
            || self.reverted.longhands.get(&state.longhand).copied() != state.initial_revert
        {
            return MetricPreparationStep::Invalidated;
        }
        if let Some(id) = priority {
            if !completed.contains_all(id.dependencies()) {
                return MetricPreparationStep::Prerequisites(id.dependencies());
            }
        }
        self.resume_font_selection(context, cache, attribute_tracker, state, resolved_reference)
    }

    fn resume_font_selection(
        &self,
        context: &mut computed::Context,
        cache: &mut ShorthandsWithPropertyReferencesCache,
        _attribute_tracker: &mut AttributeTracker,
        state: &mut MetricPreparation,
        mut resolved_reference: Option<FontSelectionReply>,
    ) -> MetricPreparationStep {
        let longhand = state.longhand;
        let priority = PrioritaryPropertyId::from_longhand(longhand);
        if priority.is_some_and(|id| self.ensured_prioritary.contains(id))
            || state.flags != context.included_cascade_flags
            || self.seen.longhands.contains(longhand)
            || self.reverted.longhands.get(&longhand).copied() != state.initial_revert
        {
            return MetricPreparationStep::Invalidated;
        }
        loop {
            if state.complete {
                return MetricPreparationStep::Complete;
            }
            let Some(index) = state.cursor else {
                state.complete = true;
                continue;
            };
            let entry = state.declarations.longhand_declarations[index];
            state.observed_flags |= entry.priority.flags();
            if let Some(value) = state.waiting.as_ref() {
                let mut reply = resolved_reference.take();
                if reply.as_ref().is_some_and(|reply| {
                    !Arc::ptr_eq(value, &reply.value)
                        || state
                            .substitution_generation
                            .as_ref()
                            .is_some_and(|generation| !Arc::ptr_eq(generation, &reply.generation))
                }) {
                    return MetricPreparationStep::Invalidated;
                }
                let PropertyDeclaration::WithVariables(variable) = entry.decl else {
                    return MetricPreparationStep::Invalidated;
                };
                if state.substitution.is_none() {
                    let Some(reference) = reply.as_ref() else {
                        return MetricPreparationStep::References(longhand, value.clone());
                    };
                    if reference.lookup.is_some() {
                        return MetricPreparationStep::Invalidated;
                    }
                    self.note_variable_substitution(context, variable);
                    state.substitution_generation = Some(reference.generation.clone());
                    match variable.begin_retained_substitution(context, cache) {
                        Ok(engine) => state.substitution = Some(engine),
                        Err(declaration) => {
                            state.waiting = None;
                            state.substitution_generation = None;
                            state.retain(declaration, entry.priority);
                            continue;
                        }
                    }
                }
                match state
                    .substitution
                    .as_mut()
                    .unwrap()
                    .poll(reply.take().and_then(|reply| reply.lookup))
                {
                    SubstitutionPoll::Lookup(request) => {
                        return MetricPreparationStep::Lookup(longhand, value.clone(), request);
                    }
                    SubstitutionPoll::Complete(result) => {
                        let declaration = variable
                            .finish_retained_substitution(result, context, cache)
                            .into_owned();
                        state.substitution = None;
                        state.substitution_generation = None;
                        state.waiting = None;
                        state.retain(declaration, entry.priority);
                        continue;
                    }
                    SubstitutionPoll::WrongReply | SubstitutionPoll::Finished => {
                        return MetricPreparationStep::Invalidated;
                    }
                }
            }
            if !(entry.priority.flags() - state.flags).is_empty()
                || state.revert.is_some_and(|(priority, kind)| {
                    !priority.allows_when_reverted(&entry.priority, kind)
                })
            {
                state.advance();
                continue;
            }
            if let PropertyDeclaration::WithVariables(value) = entry.decl {
                state.waiting = Some(value.value.clone());
                resolved_reference = None;
                continue;
            }
            state.retain(entry.decl.clone(), entry.priority);
        }
    }

    fn publish_prepared_metric<'a, 'b>(
        &mut self,
        context: &mut computed::Context,
        cache: &mut ShorthandsWithPropertyReferencesCache,
        attribute_tracker: &mut AttributeTracker,
        state: MetricPreparation<'a, 'b>,
        completed: &PrioritaryPropertyIdSet,
    ) -> Result<(), MetricPreparation<'a, 'b>> {
        let longhand = state.longhand;
        let priority = PrioritaryPropertyId::from_longhand(longhand);
        if priority.is_some_and(|id| self.ensured_prioritary.contains(id))
            || !state.complete
            || state.waiting.is_some()
            || priority.is_some_and(|id| !completed.contains_all(id.dependencies()))
            || state.flags != context.included_cascade_flags
            || self.seen.longhands.contains(longhand)
            || self.reverted.longhands.get(&longhand).copied() != state.initial_revert
        {
            return Err(state);
        }
        for entry in state.prepared {
            self.apply_one_longhand(
                context,
                longhand,
                &entry.declaration,
                entry.priority,
                cache,
                attribute_tracker,
            );
        }
        if let Some(id) = priority {
            if self.seen.longhands.contains(longhand) {
                self.did_apply_prioritary_property(context, id);
            }
            self.ensured_prioritary.insert(id);
        }
        Ok(())
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum ComputationStatus {
    Ready,
    Pending,
    Prepare(LonghandId),
}

#[derive(Default)]
struct PriorityCompletion {
    active: PrioritaryPropertyIdSet,
    complete: PrioritaryPropertyIdSet,
    claimed: PrioritaryPropertyIdSet,
    computed_size: Option<Arc<ComputedSizeCertificate>>,
}

impl PriorityCompletion {
    fn ensure_ordinary(
        &mut self,
        id: PrioritaryPropertyId,
        apply: &mut impl FnMut(PrioritaryPropertyId) -> ComputationStatus,
    ) -> ComputationStatus {
        if self.complete.contains(id) {
            return ComputationStatus::Ready;
        }
        if self.active.contains(id) || self.claimed.contains(id) {
            return ComputationStatus::Pending;
        }
        self.active.insert(id);
        for dependency in id.dependencies().iter() {
            let status = self.ensure_ordinary(dependency, apply);
            if status != ComputationStatus::Ready {
                self.suspend(id);
                return status;
            }
        }
        let status = apply(id);
        if status != ComputationStatus::Ready {
            self.suspend(id);
            return status;
        }
        self.finish(id);
        ComputationStatus::Ready
    }

    fn finish(&mut self, id: PrioritaryPropertyId) {
        assert!(self.active.contains(id));
        self.active.remove(id);
        self.complete.insert(id);
    }

    fn suspend(&mut self, id: PrioritaryPropertyId) {
        self.active.remove(id);
    }
}

struct MetricDrain<'a, 'b> {
    declarations: &'a Declarations<'b>,
    continuations: Vec<(PrioritaryPropertyId, MetricPreparation<'a, 'b>)>,
    complete: PrioritaryPropertyIdSet,
    requested: PrioritaryPropertyIdSet,
    cursor: usize,
}

enum MetricDrainStep {
    Prerequisite(PrioritaryPropertyId),
    References(LonghandId, Arc<UnparsedValue>),
    Lookup(LonghandId, Arc<UnparsedValue>, SubstitutionLookup),
    Published(PrioritaryPropertyId),
    Complete,
    Invalidated(PrioritaryPropertyId),
    WrongReply,
}

impl<'a, 'b> MetricDrain<'a, 'b> {
    fn new(declarations: &'a Declarations<'b>) -> Self {
        Self {
            declarations,
            continuations: Vec::new(),
            complete: PrioritaryPropertyIdSet::default(),
            requested: PrioritaryPropertyIdSet::default(),
            cursor: 0,
        }
    }

    fn request(
        &mut self,
        id: PrioritaryPropertyId,
        completion: &mut PriorityCompletion,
    ) -> Result<(), PrioritaryPropertyId> {
        if self.requested.contains(id) {
            return Ok(());
        }
        if completion.claimed.contains(id) || completion.active.contains(id) {
            return Err(id);
        }
        self.requested.insert(id);
        if completion.complete.contains(id) {
            self.complete.insert(id);
        } else {
            completion.claimed.insert(id);
        }
        Ok(())
    }

    fn poll(
        &mut self,
        cascade: &mut Cascade,
        context: &mut computed::Context,
        cache: &mut ShorthandsWithPropertyReferencesCache,
        attribute_tracker: &mut AttributeTracker,
        completion: &mut PriorityCompletion,
        mut reference: Option<(LonghandId, FontSelectionReply)>,
    ) -> MetricDrainStep {
        if let Some((longhand, value)) = reference.as_ref() {
            let valid = self.continuations.iter().any(|(id, state)| {
                id.to_longhand() == *longhand
                    && state
                        .waiting
                        .as_ref()
                        .is_some_and(|waiting| std::ptr::eq(waiting.as_ref(), value.value.as_ref()))
            });
            if !valid {
                return MetricDrainStep::WrongReply;
            }
        }
        let requested: Vec<_> = self.requested.iter().collect();
        for offset in 0..requested.len() {
            let position = (self.cursor + offset) % requested.len();
            let id = requested[position];
            if reference
                .as_ref()
                .is_some_and(|(longhand, _)| *longhand != id.to_longhand())
            {
                continue;
            }
            if self.complete.contains(id) {
                continue;
            }
            self.cursor = (position + 1) % requested.len();
            for dependency in id.dependencies().iter() {
                if !completion.complete.contains(dependency) {
                    if reference.is_some() {
                        return MetricDrainStep::Invalidated(id);
                    }
                    return MetricDrainStep::Prerequisite(dependency);
                }
            }
            let index = match self
                .continuations
                .iter()
                .position(|(candidate, _)| candidate.to_longhand() == id.to_longhand())
            {
                Some(index) => index,
                None => {
                    self.continuations.push((
                        id,
                        cascade.begin_metric_preparation(context, self.declarations, id),
                    ));
                    self.continuations.len() - 1
                }
            };
            let state = &mut self.continuations[index].1;
            let resolved = match reference.take() {
                Some((longhand, value)) if longhand == id.to_longhand() => Some(value),
                Some(_) => return MetricDrainStep::Invalidated(id),
                None => None,
            };
            match cascade.resume_metric_preparation(
                context,
                cache,
                attribute_tracker,
                state,
                &completion.complete,
                resolved,
            ) {
                MetricPreparationStep::Prerequisites(dependencies) => {
                    let dependency = dependencies
                        .iter()
                        .find(|dependency| !completion.complete.contains(*dependency))
                        .unwrap();
                    return MetricDrainStep::Prerequisite(dependency);
                }
                MetricPreparationStep::References(longhand, value) => {
                    return MetricDrainStep::References(longhand, value);
                }
                MetricPreparationStep::Lookup(longhand, value, request) => {
                    return MetricDrainStep::Lookup(longhand, value, request);
                }
                MetricPreparationStep::Invalidated => return MetricDrainStep::Invalidated(id),
                MetricPreparationStep::Complete => {}
            }
            let (_, state) = self.continuations.remove(index);
            if let Err(state) = cascade.publish_prepared_metric(
                context,
                cache,
                attribute_tracker,
                state,
                &completion.complete,
            ) {
                self.continuations.push((id, state));
                return MetricDrainStep::Invalidated(id);
            }
            self.complete.insert(id);
            completion.complete.insert(id);
            completion.claimed.remove(id);
            return MetricDrainStep::Published(id);
        }
        if reference.is_some() {
            return MetricDrainStep::WrongReply;
        }
        MetricDrainStep::Complete
    }
}

pub(crate) struct Cascade<'a> {
    first_line_reparenting: FirstLineReparenting<'a>,
    stylist: &'a Stylist,
    ignore_colors: bool,
    seen: SeenSet<'a>,
    reverted: RevertedSet,
    author_or_user_specified: LonghandIdSet,
    declarations_to_apply_unless_overridden: DeclarationsToApplyUnlessOverriden,
    may_have_custom_property_cycles: bool,
    references_from_non_custom_properties: NonCustomPropertyReferences,
    /// Set of prioritary properties that have already been applied.
    ensured_prioritary: PrioritaryPropertyIdSet,
    completed_prioritary: PrioritaryPropertyIdSet,
    priority_completion_flags: Option<RuleCascadeFlags>,
    preapplied_inherited_font_size: Option<Arc<ComputedSizeCertificate>>,
    attribute_inputs: FxHashMap<(Name, Namespace), CapturedAttributeInput>,
    attribute_value_urls: FxHashMap<(Name, Namespace), UrlExtraData>,
}

impl<'a> Cascade<'a> {
    fn new(
        first_line_reparenting: FirstLineReparenting<'a>,
        stylist: &'a Stylist,
        ignore_colors: bool,
    ) -> Self {
        Self {
            first_line_reparenting,
            stylist,
            ignore_colors,
            seen: Default::default(),
            author_or_user_specified: Default::default(),
            reverted: Default::default(),
            declarations_to_apply_unless_overridden: Default::default(),
            may_have_custom_property_cycles: false,
            ensured_prioritary: PrioritaryPropertyIdSet::default(),
            completed_prioritary: PrioritaryPropertyIdSet::default(),
            priority_completion_flags: None,
            preapplied_inherited_font_size: None,
            attribute_inputs: FxHashMap::default(),
            attribute_value_urls: FxHashMap::default(),
            references_from_non_custom_properties: Default::default(),
        }
    }

    /// Creates a `Cascade` for resolving custom properties outside of a full cascade (e.g. for
    /// keyframes). The visited-style and position-try paths aren't reachable in this mode.
    fn new_for_custom_properties_only(stylist: &'a Stylist) -> Self {
        Self {
            first_line_reparenting: FirstLineReparenting::No,
            stylist,
            ignore_colors: false,
            seen: Default::default(),
            author_or_user_specified: Default::default(),
            reverted: Default::default(),
            declarations_to_apply_unless_overridden: Default::default(),
            may_have_custom_property_cycles: false,
            ensured_prioritary: PrioritaryPropertyIdSet::default(),
            completed_prioritary: PrioritaryPropertyIdSet::default(),
            priority_completion_flags: None,
            preapplied_inherited_font_size: None,
            attribute_inputs: FxHashMap::default(),
            attribute_value_urls: FxHashMap::default(),
            references_from_non_custom_properties: Default::default(),
        }
    }

    fn note_variable_substitution(
        &self,
        context: &mut computed::Context,
        declaration: &crate::properties::VariableDeclaration,
    ) {
        if !declaration.id.inherited() {
            context.rule_cache_conditions.borrow_mut().set_uncacheable();

            // NOTE(emilio): We only really need to add the `display` /
            // `content` flag if the CSS variable has not been specified on our
            // declarations, but we don't have that information at this point,
            // and it doesn't seem like an important enough optimization to
            // warrant it.
            if matches!(declaration.id, LonghandId::Display | LonghandId::Content) {
                context
                    .builder
                    .add_flags(ComputedValueFlags::DISPLAY_OR_CONTENT_DEPEND_ON_INHERITED_STYLE);
            }
        }
    }

    fn substitute_variables_if_needed<'cache, 'decl>(
        &self,
        context: &mut computed::Context,
        shorthand_cache: &'cache mut ShorthandsWithPropertyReferencesCache,
        declaration: &'decl PropertyDeclaration,
        attribute_tracker: &mut AttributeTracker,
    ) -> Cow<'decl, PropertyDeclaration>
    where
        'cache: 'decl,
    {
        let declaration = match *declaration {
            PropertyDeclaration::WithVariables(ref declaration) => declaration,
            ref d => return Cow::Borrowed(d),
        };

        self.note_variable_substitution(context, declaration);

        debug_assert!(
            context.builder.stylist.is_some(),
            "Need a Stylist to substitute variables!"
        );
        declaration.substitute_variables(
            context.builder.substitution_functions(),
            context.builder.stylist.unwrap(),
            context,
            shorthand_cache,
            attribute_tracker,
        )
    }

    fn apply_one_prioritary_property(
        &mut self,
        context: &mut computed::Context,
        decls: &Declarations,
        cache: &mut ShorthandsWithPropertyReferencesCache,
        id: PrioritaryPropertyId,
        attr_provider: &mut AttributeTracker,
    ) {
        let mut index = decls.prioritary_positions[id as usize].most_important;
        if index == DeclarationIndex::MAX {
            return;
        }

        let longhand_id = id.to_longhand();
        debug_assert!(
            !longhand_id.is_logical(),
            "That could require more book-keeping"
        );
        loop {
            let decl = decls.longhand_declarations[index as usize];
            self.apply_one_longhand(
                context,
                longhand_id,
                decl.decl,
                decl.priority,
                cache,
                attr_provider,
            );
            if self.seen.longhands.contains(longhand_id) {
                // Found it!
                self.did_apply_prioritary_property(context, id);
                return;
            }
            debug_assert!(
                decl.next_index == 0 || decl.next_index > index,
                "should make progress! {} -> {}",
                index,
                decl.next_index,
            );
            index = decl.next_index;
            if index == 0 {
                return;
            }
        }
    }

    /// Some prioritary properties need book-keeping, which this takes care of.
    fn did_apply_prioritary_property(
        &mut self,
        context: &mut computed::Context,
        id: PrioritaryPropertyId,
    ) {
        use crate::properties::PrioritaryPropertyId::*;
        match id {
            Appearance => {
                if is_base_appearance(context) {
                    context
                        .style()
                        .add_flags(ComputedValueFlags::IS_IN_APPEARANCE_BASE_SUBTREE);
                    context
                        .included_cascade_flags
                        .insert(RuleCascadeFlags::APPEARANCE_BASE);
                }
            }
            WritingMode | Direction | TextOrientation => {
                context.builder.writing_mode =
                    crate::logical_geometry::WritingMode::new(context.builder.get_inherited_box());
            }
            Zoom => {
                context.builder.recompute_effective_zooms();
                if !context.builder.effective_zoom_for_inheritance.is_one() {
                    // NOTE(emilio): This is a bit of a hack, but matches the shipped WebKit and Blink
                    // behavior for now. Ideally, in the future, we have a pass over all
                    // implicitly-or-explicitly-inherited properties that can contain lengths and
                    // re-compute them properly, see https://github.com/w3c/csswg-drafts/issues/9397.
                    // TODO(emilio): we need to eagerly do this for line-height as well, probably.
                    self.recompute_font_size_for_zoom_change(&mut context.builder);
                }
            }
            XLang => {
                #[cfg(feature = "gecko")]
                self.recompute_initial_font_family_if_needed(&mut context.builder);
                self.recompute_keyword_font_size_if_needed(context);
            }
            FontFamily => {
                #[cfg(feature = "gecko")]
                self.prioritize_user_fonts_if_needed(&mut context.builder);
                self.recompute_keyword_font_size_if_needed(context);
            }
            FontSize => {
                if self.seen.longhands.contains(LonghandId::MathDepth) {
                    #[cfg(feature = "gecko")]
                    Self::recompute_math_font_size_if_needed(context);
                }
                if self.seen.longhands.contains(LonghandId::XLang)
                    || self.seen.longhands.contains(LonghandId::FontFamily)
                {
                    self.recompute_keyword_font_size_if_needed(context);
                }
                #[cfg(feature = "gecko")]
                self.constrain_font_size_if_needed(&mut context.builder);
            }
            XTextScale => {
                #[cfg(feature = "gecko")]
                self.unzoom_fonts_if_needed(&mut context.builder);
            }
            MozMinFontSizeRatio => {
                #[cfg(feature = "gecko")]
                self.constrain_font_size_if_needed(&mut context.builder);
            }
            ColorScheme => {
                context.builder.color_scheme =
                    context.builder.get_inherited_ui().color_scheme_bits();
            }
            MozDefaultAppearance | MathDepth | FontWeight | FontWidth | FontStyle
            | FontSizeAdjust | ForcedColorAdjust | LineHeight => {}
        }
    }

    fn apply_non_prioritary_properties(
        &mut self,
        context: &mut computed::Context,
        longhand_declarations: &[Declaration],
        shorthand_cache: &mut ShorthandsWithPropertyReferencesCache,
        properties_to_apply: &LonghandIdSet,
        attribute_tracker: &mut AttributeTracker,
    ) {
        debug_assert!(!properties_to_apply.contains_any(LonghandIdSet::prioritary_properties()));
        debug_assert!(self.declarations_to_apply_unless_overridden.is_empty());
        for declaration in longhand_declarations {
            let mut longhand_id = declaration.decl.id().as_longhand().unwrap();
            if !properties_to_apply.contains(longhand_id) {
                continue;
            }
            debug_assert!(PrioritaryPropertyId::from_longhand(longhand_id).is_none());
            let is_logical = longhand_id.is_logical();
            if is_logical {
                let wm = context.builder.writing_mode;
                context
                    .rule_cache_conditions
                    .borrow_mut()
                    .set_writing_mode_dependency(wm);
                longhand_id = longhand_id.to_physical(wm);
            }
            self.apply_one_longhand(
                context,
                longhand_id,
                declaration.decl,
                declaration.priority,
                shorthand_cache,
                attribute_tracker,
            );
        }
        if !self.declarations_to_apply_unless_overridden.is_empty() {
            debug_assert!(self.ignore_colors);
            for declaration in std::mem::take(&mut self.declarations_to_apply_unless_overridden) {
                let longhand_id = declaration.id().as_longhand().unwrap();
                debug_assert!(!longhand_id.is_logical());
                if !self.seen.longhands.contains(longhand_id) {
                    unsafe {
                        self.do_apply_declaration(context, longhand_id, &declaration);
                    }
                }
            }
        }

        if !context.builder.effective_zoom_for_inheritance.is_one() {
            self.recompute_zoom_dependent_inherited_lengths(context);
        }
    }

    #[cold]
    fn recompute_zoom_dependent_inherited_lengths(&self, context: &mut computed::Context) {
        debug_assert!(self.seen.longhands.contains(LonghandId::Zoom));
        for prop in LonghandIdSet::zoom_dependent_inherited_properties().iter() {
            if self.seen.longhands.contains(prop) {
                continue;
            }
            if prop == LonghandId::FontSize
                && let Some(certificate) = &self.preapplied_inherited_font_size
            {
                assert!(
                    certificate.valid_for(context),
                    "Already-consumed inherited size cannot be recomputed under changed inputs"
                );
                continue;
            }
            let declaration = PropertyDeclaration::css_wide_keyword(prop, CSSWideKeyword::Inherit);
            unsafe {
                self.do_apply_declaration(context, prop, &declaration);
            }
        }
    }

    fn apply_one_longhand(
        &mut self,
        context: &mut computed::Context,
        longhand_id: LonghandId,
        declaration: &PropertyDeclaration,
        priority: CascadePriority,
        cache: &mut ShorthandsWithPropertyReferencesCache,
        attribute_tracker: &mut AttributeTracker,
    ) {
        debug_assert!(!longhand_id.is_logical());
        if self.seen.longhands.contains(longhand_id) {
            return;
        }

        if !(priority.flags() - context.included_cascade_flags).is_empty() {
            return;
        }

        if self.reverted.longhands_set.contains(longhand_id)
            && let Some(&(reverted_priority, revert_kind)) =
                self.reverted.longhands.get(&longhand_id)
            && !reverted_priority.allows_when_reverted(&priority, revert_kind)
        {
            return;
        }

        let mut declaration =
            self.substitute_variables_if_needed(context, cache, declaration, attribute_tracker);

        // When document colors are disabled, do special handling of
        // properties that are marked as ignored in that mode.
        let origin = priority.cascade_level().origin();
        if self.ignore_colors {
            tweak_when_ignoring_colors(
                context,
                longhand_id,
                origin,
                &mut declaration,
                &mut self.declarations_to_apply_unless_overridden,
            );
        }
        let can_skip_apply = match declaration.get_css_wide_keyword() {
            Some(keyword) => {
                if let Some(revert_kind) = keyword.revert_kind() {
                    // We intentionally don't want to insert it into
                    // `self.seen.longhands`, `reverted` takes care of rejecting
                    // other declarations as needed.
                    self.reverted.longhands_set.insert(longhand_id);
                    self.reverted
                        .longhands
                        .insert(longhand_id, (priority, revert_kind));
                    return;
                }

                let inherited = longhand_id.inherited();
                let zoomed = !context.builder.effective_zoom_for_inheritance.is_one()
                    && longhand_id.zoom_dependent();
                match keyword {
                    CSSWideKeyword::Revert
                    | CSSWideKeyword::RevertLayer
                    | CSSWideKeyword::RevertRule => unreachable!(),
                    CSSWideKeyword::Unset => !zoomed || !inherited,
                    CSSWideKeyword::Inherit => inherited && !zoomed,
                    CSSWideKeyword::Initial => !inherited,
                }
            }
            None => false,
        };

        self.seen.longhands.insert(longhand_id);
        if origin != CascadeOrigin::UA {
            self.author_or_user_specified.insert(longhand_id);
        }

        if !can_skip_apply {
            // Set context.scope to this declaration's cascade level so that
            // tree-scoped properties (anchor-name, position-anchor, anchor-scope)
            // get the correct scope when converted to computed values.
            let old_scope = context.scope;
            let cascade_level = priority.cascade_level();
            context.scope = cascade_level;
            unsafe { self.do_apply_declaration(context, longhand_id, &declaration) }
            context.scope = old_scope;
        }
    }

    #[inline]
    unsafe fn do_apply_declaration(
        &self,
        context: &mut computed::Context,
        longhand_id: LonghandId,
        declaration: &PropertyDeclaration,
    ) {
        debug_assert!(!longhand_id.is_logical());
        unsafe {
            // We could (and used to) use a pattern match here, but that bloats this
            // function to over 100K of compiled code!
            //
            // To improve i-cache behavior, we outline the individual functions and
            // use virtual dispatch instead.
            (CASCADE_PROPERTY[longhand_id as usize])(declaration, context);
        }
    }

    // `RefCell<&mut T>::borrow_mut()` needs the explicit `&mut *` to get back
    // to `&mut T`; clippy's needless_borrow / explicit_auto_deref both
    // misfire on this double indirection and suggest incorrect rewrites.
    #[allow(clippy::needless_borrow, clippy::explicit_auto_deref)]
    fn compute_visited_style_if_needed<E>(
        &self,
        context: &mut computed::Context,
        element: Option<E>,
        parent_style: Option<&ComputedValues>,
        layout_parent_style: Option<&ComputedValues>,
        try_tactic: &PositionTryFallbacksTryTactic,
        visited_rules: &StrongRuleNode,
        guards: &StylesheetGuards,
    ) where
        E: TElement,
    {
        let is_link = context.builder.pseudo.is_none() && element.unwrap().is_link();

        macro_rules! visited_parent {
            ($parent:expr) => {
                if is_link {
                    $parent
                } else {
                    $parent.map(|p| p.visited_style().unwrap_or(p))
                }
            };
        }

        // We could call apply_declarations directly, but that'd cause
        // another instantiation of this function which is not great.
        let style = cascade_rules(
            context.builder.stylist.unwrap(),
            context.builder.pseudo,
            visited_rules,
            guards,
            visited_parent!(parent_style),
            visited_parent!(layout_parent_style),
            self.first_line_reparenting,
            try_tactic,
            CascadeMode::Visited {
                unvisited_context: &*context,
            },
            // Cascade input flags don't matter for the visited style, they are
            // in the main (unvisited) style.
            Default::default(),
            context.included_cascade_flags,
            // The rule cache doesn't care about caching :visited
            // styles, we cache the unvisited style instead. We still do
            // need to set the caching dependencies properly if present
            // though, so the cache conditions need to match.
            None, // rule_cache
            &mut *context.rule_cache_conditions.borrow_mut(),
            element,
            &mut *context.tree_counting_caches.borrow_mut(),
        );
        context.builder.visited_style = Some(style);
    }

    fn finished_applying_properties(&self, builder: &mut StyleBuilder) {
        #[cfg(feature = "gecko")]
        {
            if let Some(bg) = builder.get_background_if_mutated() {
                bg.fill_arrays();
            }

            if let Some(svg) = builder.get_svg_if_mutated() {
                svg.fill_arrays();
            }
        }

        // NOTE: This uses self.seen.longhands, not author_specified, because some UA styles do
        // specify visited-dependent properties.
        if self
            .seen
            .longhands
            .contains_any(LonghandIdSet::visited_dependent())
        {
            builder.add_flags(ComputedValueFlags::USES_VISITED_DEPENDENT_PROPERTIES);
        }

        if self
            .author_or_user_specified
            .contains_any(LonghandIdSet::border_background_properties())
        {
            builder.add_flags(ComputedValueFlags::HAS_AUTHOR_OR_USER_SPECIFIED_BORDER_BACKGROUND);
        }

        if self.author_or_user_specified.contains(LonghandId::Color) {
            builder.add_flags(ComputedValueFlags::HAS_AUTHOR_OR_USER_SPECIFIED_TEXT_COLOR);
        }

        if self
            .author_or_user_specified
            .contains(LonghandId::TextShadow)
        {
            builder.add_flags(ComputedValueFlags::HAS_AUTHOR_OR_USER_SPECIFIED_TEXT_SHADOW);
        }

        if self
            .author_or_user_specified
            .contains(LonghandId::GridAutoFlow)
        {
            builder.add_flags(ComputedValueFlags::HAS_AUTHOR_OR_USER_SPECIFIED_GRID_AUTO_FLOW);
        }

        #[cfg(feature = "servo")]
        {
            if let Some(font) = builder.get_font_if_mutated() {
                font.compute_font_hash();
            }
        }
    }

    fn try_to_use_cached_reset_properties(
        &self,
        context: &mut computed::Context<'a>,
        cache: Option<&'a RuleCache>,
        guards: &StylesheetGuards,
    ) -> bool {
        let style = match self.first_line_reparenting {
            FirstLineReparenting::Yes { style_to_reparent } => style_to_reparent,
            FirstLineReparenting::No => {
                let Some(cache) = cache else { return false };
                let Some(style) = cache.find(guards, context) else {
                    return false;
                };
                style
            }
        };

        context.builder.copy_reset_from(style);

        // We're using the same reset style as another element, and we'll skip
        // applying the relevant properties. So we need to do the relevant
        // bookkeeping here to keep these bits correct.
        //
        // Note that the border/background properties are non-inherited, so we
        // don't need to do anything else other than just copying the bits over.
        //
        // When using this optimization, we also need to copy whether the old
        // style specified viewport units / used font-relative lengths, this one
        // would as well.  It matches the same rules, so it is the right thing
        // to do anyways, even if it's only used on inherited properties.
        let bits_to_copy = ComputedValueFlags::HAS_AUTHOR_OR_USER_SPECIFIED_BORDER_BACKGROUND
            | ComputedValueFlags::HAS_AUTHOR_OR_USER_SPECIFIED_GRID_AUTO_FLOW
            | ComputedValueFlags::DEPENDS_ON_SELF_FONT_METRICS
            | ComputedValueFlags::DEPENDS_ON_INHERITED_FONT_METRICS
            | ComputedValueFlags::IS_IN_APPEARANCE_BASE_SUBTREE
            | ComputedValueFlags::USES_CONTAINER_UNITS
            | ComputedValueFlags::USES_VIEWPORT_UNITS
            | ComputedValueFlags::USES_FONT_OR_WM_RELATIVE_UNITS
            | ComputedValueFlags::DEPENDS_ON_CONTAINER_STYLE_QUERY
            | ComputedValueFlags::USES_SIBLING_COUNT
            | ComputedValueFlags::USES_SIBLING_INDEX
            | ComputedValueFlags::USES_VISITED_DEPENDENT_PROPERTIES
            | ComputedValueFlags::USES_ELEMENT_SCOPED_RANDOM;
        context.builder.add_flags(style.flags & bits_to_copy);

        true
    }

    /// The initial font depends on the current lang group so we may need to
    /// recompute it if the language changed.
    #[inline]
    #[cfg(feature = "gecko")]
    fn recompute_initial_font_family_if_needed(&self, builder: &mut StyleBuilder) {
        use crate::gecko_bindings::bindings;
        use crate::values::computed::font::FontFamily;

        let default_font_type = {
            let font = builder.get_font();

            if !font.mFont.family.is_initial {
                return;
            }

            let default_font_type = unsafe {
                bindings::Gecko_nsStyleFont_ComputeFallbackFontTypeForLanguage(
                    builder.device.document(),
                    font.mLanguage.0.as_ptr(),
                )
            };

            let initial_generic = font.mFont.family.families.single_generic();
            debug_assert!(
                initial_generic.is_some(),
                "Initial font should be just one generic font"
            );
            if initial_generic == Some(default_font_type) {
                return;
            }

            default_font_type
        };

        // NOTE: Leaves is_initial untouched.
        builder.mutate_font().mFont.family.families =
            FontFamily::generic(default_font_type).families.clone();
    }

    /// Prioritize user fonts if needed by pref.
    #[inline]
    #[cfg(feature = "gecko")]
    fn prioritize_user_fonts_if_needed(&self, builder: &mut StyleBuilder) {
        use crate::gecko_bindings::bindings;

        // Check the use_document_fonts setting for content, but for chrome
        // documents they're treated as always enabled.
        if crate::pref!("browser.display.use_document_fonts") != 0
            || builder.device.chrome_rules_enabled_for_document()
        {
            return;
        }

        let default_font_type = {
            let font = builder.get_font();

            if font.mFont.family.is_system_font {
                return;
            }

            if !font.mFont.family.families.needs_user_font_prioritization() {
                return;
            }

            unsafe {
                bindings::Gecko_nsStyleFont_ComputeFallbackFontTypeForLanguage(
                    builder.device.document(),
                    font.mLanguage.0.as_ptr(),
                )
            }
        };

        let font = builder.mutate_font();
        font.mFont
            .family
            .families
            .prioritize_first_generic_or_prepend(default_font_type);
    }

    /// Some keyword sizes depend on the font family and language.
    fn recompute_keyword_font_size_if_needed(&self, context: &mut computed::Context) {
        use crate::values::computed::ToComputedValue;

        if !self.seen.longhands.contains(LonghandId::XLang)
            && !self.seen.longhands.contains(LonghandId::FontFamily)
        {
            return;
        }

        let new_size = {
            let font = context.builder.get_font();
            let info = font.slow_clone_font_size().keyword_info;
            let new_size = match info.kw {
                specified::FontSizeKeyword::None => return,
                _ => {
                    context.for_non_inherited_property = false;
                    specified::FontSize::Keyword(info).to_computed_value(context)
                }
            };

            #[cfg(feature = "gecko")]
            if font.mScriptUnconstrainedSize == new_size.computed_size {
                return;
            }

            new_size
        };

        context.builder.mutate_font().set_font_size(new_size);
    }

    /// Some properties, plus setting font-size itself, may make us go out of
    /// our minimum font-size range.
    #[cfg(feature = "gecko")]
    fn constrain_font_size_if_needed(&self, builder: &mut StyleBuilder) {
        use crate::gecko_bindings::bindings;
        use crate::values::generics::NonNegative;

        let min_font_size = {
            let font = builder.get_font();
            let min_font_size = unsafe {
                bindings::Gecko_nsStyleFont_ComputeMinSize(&**font, builder.device.document())
            };

            if font.mFont.size.0 >= min_font_size {
                return;
            }

            NonNegative(min_font_size)
        };

        builder.mutate_font().mFont.size = min_font_size;
    }

    /// <svg:text> is not affected by text zoom, and it uses a preshint to disable it. We fix up
    /// the struct when this happens by unzooming its contained font values, which will have been
    /// zoomed in the parent.
    #[cfg(feature = "gecko")]
    fn unzoom_fonts_if_needed(&self, builder: &mut StyleBuilder) {
        debug_assert!(self.seen.longhands.contains(LonghandId::XTextScale));

        let parent_text_scale = *builder.get_parent_font().get__x_text_scale();
        let text_scale = *builder.get_font().get__x_text_scale();
        if parent_text_scale == text_scale {
            return;
        }
        debug_assert_ne!(
            parent_text_scale.text_zoom_enabled(),
            text_scale.text_zoom_enabled(),
            "There's only one value that disables it"
        );
        debug_assert!(
            !text_scale.text_zoom_enabled(),
            "We only ever disable text zoom never enable it"
        );
        let device = builder.device;
        builder.mutate_font().unzoom_fonts(device);
    }

    fn recompute_font_size_for_zoom_change(&self, builder: &mut StyleBuilder) {
        debug_assert!(self.seen.longhands.contains(LonghandId::Zoom));
        // NOTE(emilio): Intentionally not using the effective zoom here, since all the inherited
        // zooms are already applied.
        let old_size = builder.get_font().slow_clone_font_size();
        let new_size = old_size.zoom(builder.effective_zoom_for_inheritance);
        if old_size == new_size {
            return;
        }
        builder.mutate_font().set_font_size(new_size);
    }

    /// Special handling of font-size: math (used for MathML).
    /// https://w3c.github.io/mathml-core/#the-math-script-level-property
    /// TODO: Bug: 1548471: MathML Core also does not specify a script min size
    /// should we unship that feature or standardize it?
    #[cfg(feature = "gecko")]
    fn recompute_math_font_size_if_needed(context: &mut computed::Context) {
        use crate::values::generics::NonNegative;

        // Do not do anything if font-size: math or math-depth is not set.
        if context
            .builder
            .get_font()
            .slow_clone_font_size()
            .keyword_info
            .kw
            != specified::FontSizeKeyword::Math
        {
            return;
        }

        const SCALE_FACTOR_WHEN_INCREMENTING_MATH_DEPTH_BY_ONE: f32 = 0.71;

        // Helper function that calculates the scale factor applied to font-size
        // when math-depth goes from parent_math_depth to computed_math_depth.
        // This function is essentially a modification of the MathML3's formula
        // 0.71^(parent_math_depth - computed_math_depth) so that a scale factor
        // of parent_script_percent_scale_down is applied when math-depth goes
        // from 0 to 1 and parent_script_script_percent_scale_down is applied
        // when math-depth goes from 0 to 2. This is also a straightforward
        // implementation of the specification's algorithm:
        // https://w3c.github.io/mathml-core/#the-math-script-level-property
        fn scale_factor_for_math_depth_change(
            parent_math_depth: i32,
            computed_math_depth: i32,
            parent_script_percent_scale_down: Option<f32>,
            parent_script_script_percent_scale_down: Option<f32>,
        ) -> f32 {
            let mut a = parent_math_depth;
            let mut b = computed_math_depth;
            let c = SCALE_FACTOR_WHEN_INCREMENTING_MATH_DEPTH_BY_ONE;
            let scale_between_0_and_1 = parent_script_percent_scale_down.unwrap_or(c);
            let scale_between_0_and_2 = parent_script_script_percent_scale_down.unwrap_or(c * c);
            let mut s = 1.0;
            let mut invert_scale_factor = false;
            if a == b {
                return s;
            }
            if b < a {
                std::mem::swap(&mut a, &mut b);
                invert_scale_factor = true;
            }
            let mut e = b - a;
            if a <= 0 && b >= 2 {
                s *= scale_between_0_and_2;
                e -= 2;
            } else if a == 1 {
                s *= scale_between_0_and_2 / scale_between_0_and_1;
                e -= 1;
            } else if b == 1 {
                s *= scale_between_0_and_1;
                e -= 1;
            }
            s *= c.powi(e);
            if invert_scale_factor {
                1.0 / s.max(f32::MIN_POSITIVE)
            } else {
                s
            }
        }

        let (new_size, new_unconstrained_size) = {
            use crate::values::specified::font::QueryFontMetricsFlags;

            let builder = &context.builder;
            let font = builder.get_font();
            let parent_font = builder.get_parent_font();

            let delta = font.mMathDepth.saturating_sub(parent_font.mMathDepth);

            if delta == 0 {
                return;
            }

            let mut min = parent_font.mScriptMinSize;
            if font.mXTextScale.text_zoom_enabled() {
                min = builder.device.zoom_text(min);
            }

            // Calculate scale factor following MathML Core's algorithm.
            let scale = {
                // Script scale factors are independent of orientation.
                let font_metrics = context.query_font_metrics(
                    FontBaseSize::InheritedStyle,
                    FontMetricsOrientation::Horizontal,
                    QueryFontMetricsFlags::NEEDS_MATH_SCALES,
                );
                scale_factor_for_math_depth_change(
                    parent_font.mMathDepth as i32,
                    font.mMathDepth as i32,
                    font_metrics.script_percent_scale_down,
                    font_metrics.script_script_percent_scale_down,
                )
            };

            let parent_size = parent_font.mSize.0;
            let parent_unconstrained_size = parent_font.mScriptUnconstrainedSize.0;
            let new_size = parent_size.scale_by(scale);
            let new_unconstrained_size = parent_unconstrained_size.scale_by(scale);

            if scale <= 1. {
                // The parent size can be smaller than scriptminsize, e.g. if it
                // was specified explicitly. Don't scale in this case, but we
                // don't want to set it to scriptminsize either since that will
                // make it larger.
                if parent_size <= min {
                    (parent_size, new_unconstrained_size)
                } else {
                    (min.max(new_size), new_unconstrained_size)
                }
            } else {
                // If the new unconstrained size is larger than the min size,
                // this means we have escaped the grasp of scriptminsize and can
                // revert to using the unconstrained size.
                // However, if the new size is even larger (perhaps due to usage
                // of em units), use that instead.
                (
                    new_size.min(new_unconstrained_size.max(min)),
                    new_unconstrained_size,
                )
            }
        };
        let font = context.builder.mutate_font();
        font.mFont.size = NonNegative(new_size);
        font.mSize = NonNegative(new_size);
        font.mScriptUnconstrainedSize = NonNegative(new_unconstrained_size);
    }

    /// Seeds `context.builder.substitution_functions` with the inherited custom properties and the
    /// registered initial values, before custom-property declarations are cascaded into it.
    fn init_custom_properties(&mut self, context: &mut computed::Context) {
        let is_root_element = context.is_root_element();
        let initial_values = self.stylist.get_custom_property_initial_values();
        let inherited = if is_root_element {
            debug_assert!(context.inherited_custom_properties().is_empty());
            initial_values.inherited.clone()
        } else {
            context.inherited_custom_properties().inherited.clone()
        };
        let properties = ComputedCustomProperties {
            inherited,
            non_inherited: initial_values.non_inherited.clone(),
        };
        context.builder.substitution_functions =
            ComputedSubstitutionFunctions::new(Some(properties), None);
    }

    /// Resolves the custom properties and applies the prioritary properties in a single
    /// cycle-tracked walk: as a custom property depending on `em`/`lh`/the used color-scheme
    /// becomes resolvable, `substitute_all` applies the prioritary property it needs (via
    /// `ensure_prioritary_property`) so it computes against the right value. Any prioritary
    /// property not triggered that way is applied at the end.
    fn apply_custom_and_prioritary_properties(
        &mut self,
        context: &mut computed::Context,
        decls: &Declarations,
        shorthand_cache: &mut ShorthandsWithPropertyReferencesCache,
        attribute_tracker: &mut AttributeTracker,
    ) {
        let mut priority_completion = PriorityCompletion::default();
        if self.may_have_custom_property_cycles {
            let stylist = self.stylist;
            let seen = std::mem::take(&mut self.seen.custom);
            let references = std::mem::take(&mut self.references_from_non_custom_properties);
            substitute_all(
                &seen,
                &references,
                stylist,
                context,
                self,
                decls,
                shorthand_cache,
                attribute_tracker,
                &mut priority_completion,
            );
        }
        // Apply any prioritary property that wasn't applied while resolving custom properties.
        if decls.has_prioritary_properties {
            for id in PrioritaryPropertyId::each() {
                assert_eq!(
                    self.ensure_prioritary_property(
                        context,
                        decls,
                        shorthand_cache,
                        attribute_tracker,
                        id,
                        &mut priority_completion,
                        false,
                    ),
                    ComputationStatus::Ready,
                );
            }
        }
        self.finish_cascade_custom_properties(context);
    }

    /// Applies a prioritary property and the prioritary properties it depends on.
    fn refresh_priority_completion(&mut self, context: &computed::Context) {
        if self.priority_completion_flags != Some(context.included_cascade_flags) {
            self.completed_prioritary = PrioritaryPropertyIdSet::default();
            self.priority_completion_flags = Some(context.included_cascade_flags);
        }
    }

    fn ensure_prioritary_property(
        &mut self,
        context: &mut computed::Context,
        decls: &Declarations,
        cache: &mut ShorthandsWithPropertyReferencesCache,
        attribute_tracker: &mut AttributeTracker,
        id: PrioritaryPropertyId,
        completion: &mut PriorityCompletion,
        prepare_dynamic: bool,
    ) -> ComputationStatus {
        if completion.claimed.contains(id) || completion.active.contains(id) {
            return ComputationStatus::Pending;
        }
        if completion
            .computed_size
            .as_ref()
            .is_some_and(|certificate| {
                certificate.applied.contains(id) && !certificate.valid_for(context)
            })
        {
            return ComputationStatus::Pending;
        }
        if self.ensured_prioritary.contains(id) {
            return ComputationStatus::Ready;
        }
        completion.active.insert(id);
        let deps = id.dependencies();
        for dep in deps.iter() {
            let status = self.ensure_prioritary_property(
                context,
                decls,
                cache,
                attribute_tracker,
                dep,
                completion,
                prepare_dynamic,
            );
            if status != ComputationStatus::Ready {
                completion.active.remove(id);
                return status;
            }
        }
        if completion
            .computed_size
            .as_ref()
            .is_some_and(|certificate| {
                certificate.applied.contains(id) && !certificate.valid_for(context)
            })
        {
            completion.active.remove(id);
            return ComputationStatus::Pending;
        }
        let facet_applied = completion
            .computed_size
            .as_ref()
            .is_some_and(|certificate| {
                certificate.valid_for(context) && certificate.applied.contains(id)
            });
        if !facet_applied
            && prepare_dynamic
            && matches!(
                id,
                PrioritaryPropertyId::Appearance | PrioritaryPropertyId::FontFamily
            )
            && priority_has_dynamic_declarations(decls, id)
        {
            completion.active.remove(id);
            return ComputationStatus::Prepare(id.to_longhand());
        }
        if !facet_applied {
            self.apply_one_prioritary_property(context, decls, cache, id, attribute_tracker);
        }
        self.ensured_prioritary.insert(id);
        completion.active.remove(id);
        self.refresh_priority_completion(context);
        if self.completed_prioritary.contains_all(deps)
            && (facet_applied || !priority_has_dynamic_declarations(decls, id))
        {
            self.completed_prioritary.insert(id);
        }
        completion.complete = self.completed_prioritary.clone();
        ComputationStatus::Ready
    }

    /// Cascade a given custom property declaration.
    fn cascade_custom_property(
        &mut self,
        context: &mut computed::Context,
        declaration: &'a CustomDeclaration,
        priority: CascadePriority,
    ) {
        let CustomDeclaration {
            ref name,
            ref value,
        } = *declaration;

        if let Some(&(reverted_priority, revert_kind)) = self.reverted.custom.get(name)
            && !reverted_priority.allows_when_reverted(&priority, revert_kind)
        {
            return;
        }

        if !(priority.flags() - context.included_cascade_flags).is_empty() {
            return;
        }

        let entry = match self.seen.custom.var.entry(name) {
            Entry::Occupied(..) => return,
            Entry::Vacant(v) => v,
        };

        let registration = self.stylist.get_custom_property_registration(name);
        let initial_values = self.stylist.get_custom_property_initial_values();
        if !Self::value_may_affect_style(context, name, registration, initial_values, value) {
            entry.insert(false);
            return;
        }

        let has_references = match value {
            CustomDeclarationValue::GuaranteedInvalid => false,
            CustomDeclarationValue::Unparsed(unparsed_value) => {
                // Non-custom dependency is really relevant for registered custom properties
                // that require computed value of such dependencies.
                unparsed_value
                    .references
                    .flags
                    .intersects(ReferenceFlags::ATTR | ReferenceFlags::VAR)
                    || !find_non_custom_references(
                        registration,
                        unparsed_value,
                        context.is_root_element(),
                    )
                    .is_empty()
            }
            // XXX This matches the previous behavior but I don't think it's fully sound. Parsed
            // values may have non-custom references, can't they? But also how do we get a parsed
            // value at all here?
            CustomDeclarationValue::Parsed(..) => false,
            // If we're a wide keyword we either get an initial value or an inherited one (no
            // references). Revert might have references, but we remove the `seen` entry, so it
            // doesn't matter.
            CustomDeclarationValue::CSSWideKeyword(..) => false,
        };
        self.may_have_custom_property_cycles |= has_references;
        entry.insert(has_references);

        match value {
            CustomDeclarationValue::GuaranteedInvalid => {
                context
                    .builder
                    .substitution_functions
                    .remove_var(registration, name);
            }
            CustomDeclarationValue::Unparsed(unparsed_value) => {
                if !has_references {
                    // If the variable value has no references to other properties, perform
                    // substitution here instead of forcing a full traversal in `substitute_all`
                    // afterwards.
                    substitute_references_if_needed_and_apply(
                        name,
                        None,
                        unparsed_value,
                        self.stylist,
                        context,
                        // We just checked there are no attr dependencies.
                        &mut AttributeTracker::new_dummy(),
                    );
                    return;
                }
                let value = ComputedRegisteredValue::universal(Arc::clone(unparsed_value));
                context
                    .builder
                    .substitution_functions
                    .insert_var(registration, name, value);
            }
            CustomDeclarationValue::Parsed(parsed_value) => {
                let value = parsed_value.to_computed_value(context);
                context
                    .builder
                    .substitution_functions
                    .insert_var(registration, name, value);
            }
            CustomDeclarationValue::CSSWideKeyword(keyword) => match keyword.revert_kind() {
                Some(revert_kind) => {
                    self.seen.custom.var.remove(name);
                    self.reverted
                        .custom
                        .insert(name.clone(), (priority, revert_kind));
                }
                None => match keyword {
                    CSSWideKeyword::Initial => {
                        // For non-inherited custom properties, 'initial' was handled in value_may_affect_style.
                        debug_assert!(registration.inherits(), "Should've been handled earlier");
                        remove_and_insert_initial_value(
                            name,
                            registration,
                            initial_values,
                            &mut context.builder.substitution_functions,
                        );
                    }
                    CSSWideKeyword::Inherit => {
                        // For inherited custom properties, 'inherit' was handled in value_may_affect_style.
                        debug_assert!(!registration.inherits(), "Should've been handled earlier");
                        context
                            .style()
                            .add_flags(ComputedValueFlags::INHERITS_RESET_STYLE);
                        let inherited_value = context
                            .inherited_custom_properties()
                            .non_inherited
                            .get(name)
                            .cloned();
                        if let Some(inherited_value) = inherited_value {
                            context.builder.substitution_functions.insert_var(
                                registration,
                                name,
                                inherited_value,
                            );
                        } else {
                            context
                                .builder
                                .substitution_functions
                                .remove_var(registration, name);
                        }
                    }
                    // handled in value_may_affect_style or in the revert_kind branch above.
                    CSSWideKeyword::Revert
                    | CSSWideKeyword::RevertLayer
                    | CSSWideKeyword::RevertRule
                    | CSSWideKeyword::Unset => unreachable!(),
                },
            },
        }
    }

    /// Fast check to avoid calling maybe_note_non_custom_dependency in ~all cases.
    #[inline]
    pub fn might_have_non_custom_or_attr_dependency(
        id: LonghandId,
        decl: &PropertyDeclaration,
    ) -> bool {
        if let PropertyDeclaration::WithVariables(v) = decl {
            return matches!(id, LonghandId::LineHeight | LonghandId::FontSize)
                || v.value
                    .variable_value
                    .references
                    .flags
                    .intersects(ReferenceFlags::ATTR);
        }
        false
    }

    /// Note a non-custom property with variable reference that may in turn depend on that property.
    /// e.g. `font-size` depending on a custom property that may be a registered property using `em`.
    pub fn maybe_note_non_custom_dependency(
        &mut self,
        context: &mut computed::Context,
        id: LonghandId,
        decl: &'a PropertyDeclaration,
        attribute_tracker: &mut AttributeTracker,
    ) {
        debug_assert!(Self::might_have_non_custom_or_attr_dependency(id, decl));
        let PropertyDeclaration::WithVariables(v) = decl else {
            return;
        };
        let value = &v.value.variable_value;
        let refs = &value.references;

        if !refs
            .flags
            .intersects(ReferenceFlags::VAR | ReferenceFlags::ATTR)
        {
            return;
        }

        // Attributes in non-custom properties may reference `var()` or `attr()` in their
        // values, which we need to track to support chained references and detect cycles.
        if refs.flags.intersects(ReferenceFlags::ATTR) {
            self.update_attributes_map(context, value, attribute_tracker);
        }

        // The non-custom node(s) this property feeds. We don't try to figure out here which
        // referenced custom properties can actually cycle back to it: instead we record the whole
        // declaration value, and let `substitute_all` traverse its references (following fallbacks
        // only when the primary is invalid). This way, references that only appear in an unused
        // fallback (e.g. `var(--exists, var(--font-size-em))`) don't create a spurious cycle, while
        // references in a used fallback (e.g. `var(--noexist, var(--font-size-em))`) do.
        //
        // With unit algebra in `calc()`, references aren't limited to `font-size`. For example,
        // `--foo: 100ex; font-weight: calc(var(--foo) / 1ex);`, or
        // `--foo: 1em; zoom: calc(var(--foo) * 30px / 2em);`
        let references = match id {
            LonghandId::FontSize => ReferenceFlags::FONT_UNITS,
            LonghandId::LineHeight => ReferenceFlags::LH_UNITS | ReferenceFlags::FONT_UNITS,
            LonghandId::ColorScheme => ReferenceFlags::COLOR_SCHEME,
            _ => return,
        };

        references.for_each_non_custom(context.is_root_element(), |idx| {
            self.references_from_non_custom_properties[idx]
                .get_or_insert_with(Vec::new)
                .push((v.id, v.value.clone()));
        });
    }

    fn value_may_affect_style(
        context: &computed::Context,
        name: &Name,
        registration: &PropertyDescriptors,
        initial_values: &ComputedCustomProperties,
        value: &CustomDeclarationValue,
    ) -> bool {
        match *value {
            CustomDeclarationValue::CSSWideKeyword(CSSWideKeyword::Inherit) => {
                // For inherited custom properties, explicit 'inherit' means we
                // can just use any existing value in the inherited
                // CustomPropertiesMap.
                if registration.inherits() {
                    return false;
                }
            }
            CustomDeclarationValue::CSSWideKeyword(CSSWideKeyword::Initial) => {
                // For non-inherited custom properties, explicit 'initial' means
                // we can just use any initial value in the registration.
                if !registration.inherits() {
                    return false;
                }
            }
            CustomDeclarationValue::CSSWideKeyword(CSSWideKeyword::Unset) => {
                // Explicit 'unset' means we can either just use any existing
                // value in the inherited CustomPropertiesMap or the initial
                // value in the registration.
                return false;
            }
            _ => {}
        }

        let existing_value = context
            .builder
            .substitution_functions
            .get_var(registration, name);
        let Some(existing_value) = existing_value else {
            if matches!(
                value,
                CustomDeclarationValue::CSSWideKeyword(CSSWideKeyword::Initial)
            ) {
                debug_assert!(registration.inherits(), "Should've been handled earlier");
                // The initial value of a custom property without a
                // guaranteed-invalid initial value is the same as it
                // not existing in the map.
                if registration.initial_value.is_none() {
                    return false;
                }
            }
            return true;
        };
        match value {
            CustomDeclarationValue::GuaranteedInvalid => {}
            CustomDeclarationValue::Unparsed(value) => {
                // Don't bother overwriting an existing value with the same
                // specified value.
                if let Some(existing_unparsed) = existing_value.as_universal() {
                    return existing_value.attr_tainted != value.is_attr_tainted()
                        || existing_unparsed != value;
                }
            }
            CustomDeclarationValue::Parsed(..) => {
                // If the value has dependencies, context might not yield the same
                // result as the eventual value.
            }
            CustomDeclarationValue::CSSWideKeyword(kw) => {
                match kw {
                    CSSWideKeyword::Inherit => {
                        debug_assert!(!registration.inherits(), "Should've been handled earlier");
                        // Root inheritance uses the already-seeded initial value.
                        if context.is_root_element() {
                            return false;
                        }
                    }
                    CSSWideKeyword::Initial => {
                        debug_assert!(registration.inherits(), "Should've been handled earlier");
                        // Don't bother overwriting an existing value with the initial value
                        // specified in the registration.
                        if let Some(initial_value) = initial_values.get(registration, name) {
                            return existing_value.attr_tainted || existing_value != initial_value;
                        }
                    }
                    CSSWideKeyword::Unset => {
                        debug_assert!(false, "Should've been handled earlier");
                    }
                    CSSWideKeyword::Revert
                    | CSSWideKeyword::RevertLayer
                    | CSSWideKeyword::RevertRule => {}
                }
            }
        };

        true
    }

    /// For a given unparsed variable, update the attributes map with its attr references.
    pub fn update_attributes_map(
        &mut self,
        context: &mut computed::Context,
        value: &'a VariableValue,
        attribute_tracker: &mut AttributeTracker,
    ) {
        let refs = &value.references;
        if !refs.flags.intersects(ReferenceFlags::ATTR) {
            return;
        }
        self.may_have_custom_property_cycles = true;

        let mut refs_stack = SmallVec::<[&References; 5]>::new();
        refs_stack.push(refs);
        while let Some(refs) = refs_stack.pop() {
            for next in &refs.refs {
                if let Some(ref fallback) = next.fallback {
                    refs_stack.push(&fallback.references);
                }
                if !next.is_attr_with_type() {
                    // Only type() can have nested references, so we don't need to eagerly look at
                    // others.
                    continue;
                }
                let Some(namespace) = next.attribute_data.namespace() else {
                    continue;
                };
                if !self
                    .seen
                    .custom
                    .attr
                    .entry(namespace)
                    .or_default()
                    .insert(&next.name)
                {
                    continue;
                }
                let input = self
                    .attribute_inputs
                    .entry((next.name.clone(), namespace.clone()))
                    .or_insert_with(|| {
                        CapturedAttributeInput::query(&next.name, namespace, attribute_tracker)
                    });
                if let Ok(v) = input.parse(&value.url_data) {
                    self.attribute_value_urls.insert(
                        (next.name.clone(), namespace.clone()),
                        value.url_data.clone(),
                    );
                    context
                        .builder
                        .substitution_functions
                        .insert_attr(&next.name, namespace, v);
                }
            }
        }
    }

    /// Computes the map of applicable custom properties, saving the result into the computed
    /// context, and applies the prioritary properties interleaved with custom-property resolution.
    pub fn finish_cascade_custom_properties(&mut self, context: &mut computed::Context) {
        context
            .builder
            .substitution_functions
            .custom_properties
            .shrink_to_fit();

        // Some pages apply a lot of redundant custom properties, see e.g.
        // bug 1758974 comment 5. Try to detect the case where the values
        // haven't really changed, and save some memory by reusing the inherited
        // map in that case.
        let initial_values = self.stylist.get_custom_property_initial_values();
        let reuse_inherited = context.inherited_custom_properties().inherited
            == context
                .builder
                .substitution_functions
                .custom_properties
                .inherited;
        if reuse_inherited {
            let inherited = context.inherited_custom_properties().inherited.clone();
            context
                .builder
                .substitution_functions
                .custom_properties
                .inherited = inherited;
        }
        if initial_values.non_inherited
            == context
                .builder
                .substitution_functions
                .custom_properties
                .non_inherited
        {
            let non_inherited = initial_values.non_inherited.clone();
            context
                .builder
                .substitution_functions
                .custom_properties
                .non_inherited = non_inherited;
        }
    }
}

struct InitializedCustomBindings {
    initial: ComputedCustomProperties,
    pending: PrecomputedHashSet<Name>,
    settled: PrecomputedHashMap<Name, Option<ComputedRegisteredValue>>,
    flags: RuleCascadeFlags,
    valid: bool,
    root: Arc<()>,
}

impl InitializedCustomBindings {
    fn new(seen: &SeenSubstitutionFunctions, context: &computed::Context) -> Self {
        Self {
            initial: context
                .builder
                .substitution_functions
                .custom_properties
                .clone(),
            pending: seen
                .var
                .iter()
                .filter_map(|(name, unresolved)| unresolved.then(|| (*name).clone()))
                .collect(),
            settled: PrecomputedHashMap::default(),
            flags: context.included_cascade_flags,
            valid: true,
            root: Arc::new(()),
        }
    }

    fn valid_for(&mut self, flags: RuleCascadeFlags) -> bool {
        self.valid &= flags == self.flags;
        self.valid
    }

    fn value(
        &self,
        name: &Name,
        registration: &PropertyDescriptors,
    ) -> Option<Option<ComputedRegisteredValue>> {
        if self.pending.contains(name) {
            return None;
        }
        Some(
            self.settled
                .get(name)
                .cloned()
                .unwrap_or_else(|| self.initial.get(registration, name).cloned()),
        )
    }

    fn record(&mut self, name: &Name, value: Option<ComputedRegisteredValue>) {
        if self.pending.remove(name) {
            self.settled.insert(name.clone(), value);
        }
    }
}

fn substitute_all(
    seen: &SeenSubstitutionFunctions,
    references_from_non_custom_properties: &NonCustomPropertyReferences,
    stylist: &Stylist,
    computed_context: &mut computed::Context,
    cascade: &mut Cascade,
    decls: &Declarations,
    shorthand_cache: &mut ShorthandsWithPropertyReferencesCache,
    attr_tracker: &mut AttributeTracker,
    priority_completion: &mut PriorityCompletion,
) {
    // The cycle dependencies removal in this function is a variant
    // of Tarjan's algorithm. It is mostly based on the pseudo-code
    // listed in
    // https://en.wikipedia.org/w/index.php?
    // title=Tarjan%27s_strongly_connected_components_algorithm&oldid=801728495

    #[derive(Clone, Eq, PartialEq, Debug)]
    enum VarType {
        Attr(Name, Namespace),
        Custom(Name),
        NonCustom(SingleNonCustomReference),
    }

    impl VarType {
        fn namespace(&self) -> Option<&Namespace> {
            match self {
                Self::Attr(_, namespace) => Some(namespace),
                _ => None,
            }
        }
    }

    enum ClosedValue {
        Prepared(Name, PreparedCustomValue),
        Substitute(VarType, Arc<ComputedPropertyValue>),
        Prioritary(PrioritaryPropertyId),
    }

    enum NodePublication<T> {
        SemanticOpen,
        CycleUnsettled,
        Pending(T),
        Applying,
        Complete,
        CycleSettled,
    }

    #[derive(Clone, Copy, Debug, Eq, PartialEq)]
    enum NodeReadiness {
        SemanticOpen,
        ComputationPending,
        Complete,
        CycleSettled,
    }

    impl<T> NodePublication<T> {
        fn readiness(&self) -> NodeReadiness {
            match self {
                Self::SemanticOpen => NodeReadiness::SemanticOpen,
                Self::CycleUnsettled | Self::Pending(_) | Self::Applying => {
                    NodeReadiness::ComputationPending
                }
                Self::Complete => NodeReadiness::Complete,
                Self::CycleSettled => NodeReadiness::CycleSettled,
            }
        }

        fn close(&mut self, value: T) {
            assert!(matches!(self, Self::SemanticOpen));
            *self = Self::Pending(value);
        }

        fn take_ready(&mut self, prerequisites_ready: bool) -> Option<T> {
            if !prerequisites_ready {
                return None;
            }
            assert!(matches!(self, Self::Pending(_)));
            let Self::Pending(value) = std::mem::replace(self, Self::Applying) else {
                unreachable!()
            };
            Some(value)
        }

        fn finish(&mut self) {
            assert!(matches!(self, Self::Applying));
            *self = Self::Complete;
        }

        fn begin_cycle(&mut self) {
            assert!(matches!(self, Self::SemanticOpen));
            *self = Self::CycleUnsettled;
        }

        fn settle_cycle(&mut self) {
            assert!(matches!(self, Self::CycleUnsettled));
            *self = Self::CycleSettled;
        }

        fn can_retire(&self) -> bool {
            matches!(self, Self::Complete | Self::CycleSettled)
        }
    }

    #[derive(Clone, Copy, Debug, Eq, PartialEq)]
    enum VisitResult {
        SemanticOpen(usize),
        ComputationPending(usize),
        ComputedSize(usize),
        Complete,
        CycleSettled,
    }

    /// Struct recording necessary information for each variable.
    struct VarInfo {
        /// The name of the variable. It will be taken when the corresponding variable is popped
        /// from the stack, which serves as a mark for whether the variable is currently in the
        /// stack below.
        var: Option<VarType>,
        /// If the variable is in a dependency cycle, lowlink represents a smaller index which
        /// corresponds to a variable in the same strong connected component, which is known to be
        /// accessible from this variable. It is not necessarily the root, though.
        lowlink: usize,
        publication: NodePublication<ClosedValue>,
    }

    #[derive(Debug, Default)]
    struct OrderIndexMap {
        /// The map from the custom property name to its order index.
        var: PrecomputedHashMap<Name, usize>,
        /// The map from the attribute name to its order index.
        attr: PrecomputedHashMap<Namespace, PrecomputedHashMap<Name, usize>>,
    }

    impl OrderIndexMap {
        fn clear(&mut self) {
            self.var.clear();
            self.attr.clear();
        }
    }

    /// Context struct for traversing the variable graph, so that we can
    /// avoid referencing all the fields multiple times.
    struct Context<'a, 'b: 'a, 'c, 'd> {
        lookup_bindings: InitializedCustomBindings,
        publication_names: Vec<VarType>,
        settled_attributes: FxHashMap<(Name, Namespace), Option<ComputedRegisteredValue>>,
        environment_inputs: Vec<(Name, UrlExtraData, Option<VariableValue>)>,
        metric_lookup: Option<MetricLookup>,
        lookup_reply: Option<(LonghandId, FontSelectionReply)>,
        /// Number of variables visited. This is used as the order index
        /// when we visit a new unresolved variable.
        count: usize,
        /// The map from a substitution function name to its order index.
        index_map: OrderIndexMap,
        /// Mapping from a non-custom dependency to its order index.
        non_custom_index_map: NonCustomReferenceMap<usize>,
        /// Information of each variable indexed by the order index.
        var_info: SmallVec<[VarInfo; 5]>,
        frames: Vec<TraversalFrame>,
        frame_root: Option<VarType>,
        frame_reply: Option<(VarType, VisitResult)>,
        priority_completion: &'a mut PriorityCompletion,
        metric_drain: MetricDrain<'a, 'd>,
        metric_action: Option<MetricAction>,
        metric_references: Option<MetricReferences>,
        font_preparation: Option<MetricPreparation<'a, 'd>>,
        size_preparation: Option<ComputedSizePreparation<'a, 'd>>,
        size_node: Option<usize>,
        size_identity: Arc<()>,
        deferred_size: Option<TraversalFrame>,
        finished_root: Option<VisitResult>,
        completed_font_inputs: LonghandIdSet,
        font_completion_flags: Option<RuleCascadeFlags>,
        /// The stack of order index of visited variables. It contains
        /// all unfinished strong connected components.
        stack: SmallVec<[usize; 5]>,
        /// The stylist is used to get registered properties, and to resolve the environment to
        /// substitute `env()` variables.
        stylist: &'a Stylist,
        /// The computed context is used to get inherited custom properties, compute registered
        /// custom properties, and apply prioritary properties.
        computed_context: &'a mut computed::Context<'b>,
        /// The cascade owns prioritary-property application; when a `NonCustom` node (or a
        /// color-scheme-dependent custom property) becomes resolvable, we apply the corresponding
        /// prioritary property directly through it.
        cascade: &'a mut Cascade<'c>,
        /// The declarations, needed to apply prioritary properties.
        decls: &'a Declarations<'d>,
        /// Shorthand cache, needed to apply prioritary properties.
        cache: &'a mut ShorthandsWithPropertyReferencesCache,
    }

    impl<'a, 'b: 'a, 'c, 'd> Context<'a, 'b, 'c, 'd> {
        fn record_lookup_publication(&mut self, index: usize) {
            assert!(self.var_info[index].publication.can_retire());
            let var = self.publication_names[index].clone();
            self.record_lookup_value(&var);
        }

        fn record_lookup_value(&mut self, var: &VarType) {
            if !self
                .lookup_bindings
                .valid_for(self.computed_context.included_cascade_flags)
            {
                return;
            }
            match var {
                VarType::Custom(name) => {
                    let value = self
                        .map()
                        .get_var(self.stylist.get_custom_property_registration(name), name)
                        .cloned();
                    self.lookup_bindings.record(name, value);
                }
                VarType::Attr(name, namespace) => {
                    let value = self.map().get_attr(name, namespace).cloned();
                    self.settled_attributes
                        .insert((name.clone(), namespace.clone()), value);
                }
                VarType::NonCustom(_) => {}
            }
        }

        fn captured_environment(
            &mut self,
            name: &Name,
            url_data: &UrlExtraData,
        ) -> Option<VariableValue> {
            if let Some((_, _, value)) = self
                .environment_inputs
                .iter()
                .find(|(cached_name, cached_url, _)| cached_name == name && cached_url == url_data)
            {
                return value.clone();
            }
            let device = self.stylist.device();
            let value = device.environment().get(name, device, url_data);
            self.environment_inputs
                .push((name.clone(), url_data.clone(), value.clone()));
            value
        }

        fn capture_attribute_input(
            &mut self,
            name: &Name,
            namespace: &Namespace,
            _url_data: &UrlExtraData,
            tracker: &mut AttributeTracker,
        ) -> &mut CapturedAttributeInput {
            self.cascade
                .attribute_inputs
                .entry((name.clone(), namespace.clone()))
                .or_insert_with(|| CapturedAttributeInput::query(name, namespace, tracker))
        }

        fn setup_attribute_input(
            &mut self,
            name: &Name,
            namespace: &Namespace,
            url_data: &UrlExtraData,
            tracker: &mut AttributeTracker,
        ) {
            if self.map().contains_attr(name, namespace) {
                return;
            }
            if let Ok(value) = self
                .capture_attribute_input(name, namespace, url_data, tracker)
                .parse(url_data)
            {
                self.cascade
                    .attribute_value_urls
                    .insert((name.clone(), namespace.clone()), url_data.clone());
                self.map_mut().insert_attr(name, namespace, value);
            }
        }

        fn owned_lookup_value(
            &mut self,
            request: &SubstitutionLookup,
            tracker: &mut AttributeTracker,
        ) -> Result<Option<SubstitutionLookupValue>, ()> {
            if !self
                .lookup_bindings
                .valid_for(self.computed_context.included_cascade_flags)
            {
                return Err(());
            }
            let value = match request.kind {
                SubstitutionLookupKind::Environment => {
                    return Ok(Some(
                        match self.captured_environment(&request.name, &request.url_data) {
                            Some(value) => SubstitutionLookupValue::Value(value, false),
                            None => SubstitutionLookupValue::Invalid,
                        },
                    ));
                }
                SubstitutionLookupKind::RawAttribute => {
                    let raw = request.namespace.as_ref().and_then(|namespace| {
                        self.capture_attribute_input(
                            &request.name,
                            namespace,
                            &request.url_data,
                            tracker,
                        )
                        .raw
                        .clone()
                    });
                    return Ok(Some(SubstitutionLookupValue::Attribute(raw)));
                }
                SubstitutionLookupKind::Variable => {
                    if let Some(result) = self.visited(&VarType::Custom(request.name.clone())) {
                        if !matches!(result, VisitResult::Complete | VisitResult::CycleSettled) {
                            return Ok(None);
                        }
                    }
                    let registration = self.stylist.get_custom_property_registration(&request.name);
                    let Some(value) = self.lookup_bindings.value(&request.name, registration)
                    else {
                        return Ok(None);
                    };
                    value
                }
                SubstitutionLookupKind::TypedAttribute => {
                    let namespace = request.namespace.as_ref().ok_or(())?;
                    if request.guards.is_empty() {
                        match self.visited(&VarType::Attr(request.name.clone(), namespace.clone()))
                        {
                            Some(VisitResult::CycleSettled) => return Err(()),
                            Some(result) if !matches!(result, VisitResult::Complete) => {
                                return Ok(None);
                            }
                            _ => {}
                        }
                    }
                    let input = self.capture_attribute_input(
                        &request.name,
                        namespace,
                        &request.url_data,
                        tracker,
                    );
                    if input.raw.is_none() {
                        return Err(());
                    }
                    return Ok(Some(match input.parse(&request.url_data) {
                        Ok(value) => {
                            SubstitutionLookupValue::AttributeSource(value.to_variable_value())
                        }
                        Err(()) => SubstitutionLookupValue::Invalid,
                    }));
                }
            };
            Ok(Some(match value {
                None => SubstitutionLookupValue::Invalid,
                Some(value) => {
                    let tokens = value.to_variable_value();
                    if tokens.has_references() {
                        return Err(());
                    }
                    SubstitutionLookupValue::Value(tokens, value.attr_tainted)
                }
            }))
        }

        fn reset(&mut self) {
            assert!(self.metric_lookup.is_none() && self.lookup_reply.is_none());
            assert!(self.metric_drain.continuations.is_empty());
            assert!(self.deferred_size.is_none() && self.finished_root.is_none());
            assert!(self.size_preparation.is_none());
            assert!(self.metric_action.is_none() && self.font_preparation.is_none());
            assert!(self.metric_references.is_none());
            assert!(
                self.priority_completion.active.is_empty()
                    && self.priority_completion.claimed.is_empty()
            );
            assert!(
                self.frames.is_empty() && self.frame_root.is_none() && self.frame_reply.is_none()
            );
            assert!(self.stack.is_empty());
            assert!(
                self.var_info
                    .iter()
                    .all(|info| info.publication.can_retire())
            );
            self.priority_completion.computed_size = None;
            self.size_node = None;
            self.size_identity = Arc::new(());
            self.lookup_bindings.root = Arc::new(());
            self.publication_names.clear();
            self.count = 0;
            self.index_map.clear();
            self.non_custom_index_map = Default::default();
            self.var_info.clear();
            self.stack.clear();
        }

        fn poll_root(
            &mut self,
            var: VarType,
            references: &NonCustomPropertyReferences,
            attribute_tracker: &mut AttributeTracker,
            publication_ready: &mut impl FnMut(
                FontDependencyDemand,
                &PrioritaryPropertyIdSet,
                Option<LonghandId>,
            ) -> PublicationDemand,
        ) -> VisitResult {
            if let Some(root) = &self.frame_root {
                assert_eq!(*root, var);
            } else {
                assert!(self.frames.is_empty() && self.frame_reply.is_none());
                self.frame_root = Some(var.clone());
                match start_frame(var, self, attribute_tracker) {
                    Ok(mut frame) => {
                        frame.enter_guarded_custom(Vec::new(), self);
                        self.frames.push(frame);
                    }
                    Err(result) => {
                        self.frame_root = None;
                        return result;
                    }
                }
            }
            if let Some(action) = &self.metric_action {
                return VisitResult::ComputationPending(action.index);
            }
            loop {
                let result =
                    self.poll_frames(references, attribute_tracker, publication_ready, 0, 0, None);
                if matches!(result, VisitResult::ComputationPending(_)) {
                    return result;
                }
                if let Some(frame) = self.deferred_size.take() {
                    assert!(self.finished_root.is_none());
                    self.finished_root = Some(result);
                    self.frames.push(frame);
                    continue;
                }
                self.frame_root = None;
                return self.finished_root.take().unwrap_or(result);
            }
        }

        fn poll_frames(
            &mut self,
            references: &NonCustomPropertyReferences,
            attribute_tracker: &mut AttributeTracker,
            publication_ready: &mut impl FnMut(
                FontDependencyDemand,
                &PrioritaryPropertyIdSet,
                Option<LonghandId>,
            ) -> PublicationDemand,
            depth: usize,
            semantic_floor: usize,
            attribute_attempt: Option<&Arc<()>>,
        ) -> VisitResult {
            loop {
                assert!(self.frames.len() > depth);
                let mut frame = self.frames.pop().expect("Active root owns a frame");
                if let Some((target, _)) = &frame.waiting {
                    if attribute_attempt.is_some()
                        && frame.guarded_custom.is_none()
                        && matches!(target, VarType::Attr(..))
                    {
                        let index = frame.index;
                        self.frames.push(frame);
                        return VisitResult::ComputationPending(index);
                    }
                    if let Some((_, VisitResult::SemanticOpen(index))) = &self.frame_reply {
                        if *index < semantic_floor {
                            let index = *index;
                            self.frames.push(frame);
                            return VisitResult::ComputationPending(index);
                        }
                    }
                    if let Some((target, result)) = self.frame_reply.take() {
                        assert!(frame.receive(target, result, self));
                    } else {
                        let target = target.clone();
                        let guards = frame
                            .guarded_custom
                            .as_ref()
                            .and_then(|state| state.request.as_ref())
                            .map(|request| request.guards.clone());
                        self.frames.push(frame);
                        match start_frame(target.clone(), self, attribute_tracker) {
                            Ok(mut child) => {
                                if let Some(guards) = guards {
                                    child.enter_guarded_custom(guards, self);
                                }
                                self.frames.push(child);
                            }
                            Err(VisitResult::ComputationPending(index))
                                if self.frames.last().is_some_and(|parent| {
                                    parent.accepts_computed_size(
                                        self.computed_context.is_root_element(),
                                    )
                                }) && self.computed_size_ready(index) =>
                            {
                                self.frame_reply = Some((target, VisitResult::ComputedSize(index)));
                            }
                            Err(VisitResult::ComputationPending(index)) => {
                                return VisitResult::ComputationPending(index);
                            }
                            Err(VisitResult::SemanticOpen(index)) if index < semantic_floor => {
                                return VisitResult::ComputationPending(index);
                            }
                            Err(result) => self.frame_reply = Some((target, result)),
                        }
                        continue;
                    }
                } else {
                    assert!(self.frame_reply.is_none());
                }
                match frame.step(references, self, attribute_tracker, publication_ready) {
                    FrameStep::Link(_) => self.frames.push(frame),
                    FrameStep::Pending(prerequisite) => {
                        let index = frame.index;
                        if depth == 0 {
                            self.metric_action = prerequisite.map(|prerequisite| MetricAction {
                                identity: Arc::new(()),
                                root: self.frame_root.as_ref().unwrap().clone(),
                                owner: frame.var.clone(),
                                index,
                                prerequisite,
                            });
                        }
                        self.frames.push(frame);
                        return VisitResult::ComputationPending(index);
                    }
                    FrameStep::ComputedSize => {
                        assert!(self.deferred_size.is_none());
                        assert!(self.frames.last().is_some_and(|parent| {
                            parent.accepts_computed_size(self.computed_context.is_root_element())
                        }));
                        let index = frame.index;
                        let var = frame.var.clone();
                        self.deferred_size = Some(frame);
                        self.frame_reply = Some((var, VisitResult::ComputedSize(index)));
                    }
                    FrameStep::Complete(result) => {
                        if self.frames.len() == depth {
                            return result;
                        }
                        assert!(self.frame_reply.is_none());
                        self.frame_reply = Some((frame.var, result));
                    }
                }
            }
        }

        fn computed_size_ready(&self, index: usize) -> bool {
            self.size_node == Some(index)
                && self.var_info.get(index).is_some_and(|info| {
                    matches!(
                        info.publication,
                        NodePublication::Pending(ClosedValue::Prioritary(
                            PrioritaryPropertyId::FontSize
                        ))
                    )
                })
                && self
                    .priority_completion
                    .computed_size
                    .as_ref()
                    .is_some_and(|certificate| {
                        std::ptr::eq(certificate.identity.as_ref(), self.size_identity.as_ref())
                            && certificate.valid_for(self.computed_context)
                    })
        }

        fn publication_readiness(
            &self,
            ordinary: &mut impl FnMut(
                FontDependencyDemand,
                &PrioritaryPropertyIdSet,
                Option<LonghandId>,
            ) -> PublicationDemand,
            demand: FontDependencyDemand,
            unprepared: Option<LonghandId>,
        ) -> PublicationDemand {
            if demand == FontDependencyDemand::ComputedSize
                && self
                    .size_node
                    .is_some_and(|index| self.computed_size_ready(index))
            {
                return PublicationDemand::Ready;
            }
            ordinary(demand, &self.priority_completion.complete, unprepared)
        }

        fn can_start_computed_size(&self, index: usize) -> bool {
            use PrioritaryPropertyId::*;
            if !matches!(
                self.var_info[index].publication,
                NodePublication::Pending(ClosedValue::Prioritary(FontSize))
            ) || self.priority_completion.computed_size.is_some()
                || self.priority_completion.claimed.contains(FontSize)
                || self.priority_completion.claimed.contains(XTextScale)
                || self.priority_completion.active.contains(FontSize)
                || self.priority_completion.active.contains(XTextScale)
                || self.cascade.ensured_prioritary.contains(FontSize)
                || self.cascade.ensured_prioritary.contains(XTextScale)
                || self.cascade.seen.longhands.contains(LonghandId::FontSize)
                || self.cascade.seen.longhands.contains(LonghandId::XTextScale)
            {
                return false;
            }
            let flags = self.computed_context.included_cascade_flags;
            for id in [Zoom] {
                if !size_input_prefix_is_stable(
                    self.decls,
                    id,
                    flags,
                    self.cascade
                        .reverted
                        .longhands
                        .get(&id.to_longhand())
                        .copied(),
                ) {
                    return false;
                }
            }
            true
        }

        fn prepare_computed_size(
            &mut self,
            index: usize,
            tracker: &mut AttributeTracker,
            reply: Option<(LonghandId, FontSelectionReply)>,
        ) -> MetricActionProgress {
            use PrioritaryPropertyId::*;
            if self.computed_size_ready(index) {
                return MetricActionProgress::AlreadyComplete;
            }
            if !self.can_start_computed_size(index) {
                return MetricActionProgress::Invalidated;
            }
            let flags = self.computed_context.included_cascade_flags;
            for id in [Zoom] {
                if self.apply_prioritary_property(id, tracker) != ComputationStatus::Ready {
                    return MetricActionProgress::Invalidated;
                }
            }
            self.import_priority_completion();
            if [Zoom]
                .iter()
                .any(|id| !self.priority_completion.complete.contains(*id))
                || flags != self.computed_context.included_cascade_flags
            {
                return MetricActionProgress::Invalidated;
            }
            let states = self
                .size_preparation
                .get_or_insert_with(|| ComputedSizePreparation {
                    index,
                    family: None,
                    size: self.cascade.begin_font_preparation(
                        self.computed_context,
                        self.decls,
                        LonghandId::FontSize,
                    ),
                    text_scale: self.cascade.begin_font_preparation(
                        self.computed_context,
                        self.decls,
                        LonghandId::XTextScale,
                    ),
                });
            if states.index != index {
                return MetricActionProgress::WrongAction;
            }
            match states.poll(
                self.cascade,
                self.computed_context,
                self.cache,
                tracker,
                reply,
            ) {
                MetricPreparationStep::Complete => {}
                MetricPreparationStep::References(id, value) => {
                    return MetricActionProgress::References(id, value);
                }
                MetricPreparationStep::Lookup(id, value, request) => {
                    return MetricActionProgress::Lookup(id, value, request);
                }
                _ => return MetricActionProgress::Invalidated,
            }
            if !states.size.stable_for_appearance_addition()
                || !states.text_scale.stable_for_appearance_addition()
            {
                eprintln!("CSS_MINIMUM_PENDING readset=selection-flags");
                return MetricActionProgress::ComputedSizeReadset;
            }
            let reads_writing_mode = size_reads_writing_mode(
                states.operation(),
                self.computed_context.is_root_element(),
            );
            let needs_family = size_needs_keyword_family(
                states.operation(),
                self.computed_context
                    .builder
                    .get_parent_font()
                    .slow_clone_font_size()
                    .keyword_info
                    .kw,
                self.computed_context
                    .builder
                    .effective_zoom_for_inheritance
                    .is_one(),
            );
            let needs_math = size_needs_math_depth(
                states.operation(),
                self.computed_context
                    .builder
                    .get_parent_font()
                    .slow_clone_font_size()
                    .keyword_info
                    .kw,
                self.computed_context
                    .builder
                    .effective_zoom_for_inheritance
                    .is_one(),
            );
            for (id, needed) in [
                (XLang, true),
                (MathDepth, needs_math),
                (MozMinFontSizeRatio, true),
            ] {
                if !needed {
                    continue;
                }
                if self.priority_completion.claimed.contains(id)
                    || self.priority_completion.active.contains(id)
                    || !size_input_prefix_is_stable(
                        self.decls,
                        id,
                        flags,
                        self.cascade
                            .reverted
                            .longhands
                            .get(&id.to_longhand())
                            .copied(),
                    )
                {
                    eprintln!("CSS_MINIMUM_PENDING readset=static-prerequisite-prefix");
                    return MetricActionProgress::ComputedSizeReadset;
                }
                if id.to_longhand() != LonghandId::MozMinFontSizeRatio
                    && self.apply_prioritary_property(id, tracker) != ComputationStatus::Ready
                {
                    eprintln!("CSS_MINIMUM_PENDING readset=static-prerequisite-application");
                    return MetricActionProgress::ComputedSizeReadset;
                }
            }
            self.import_priority_completion();
            let states = self.size_preparation.as_mut().unwrap();
            if needs_family
                && self.priority_completion.complete.contains(FontFamily)
                && !self.priority_completion.complete.contains(Appearance)
            {
                eprintln!("CSS_MINIMUM_PENDING readset=family-complete-before-appearance");
                return MetricActionProgress::ComputedSizeReadset;
            }
            if needs_family && !self.priority_completion.complete.contains(FontFamily) {
                if self.priority_completion.claimed.contains(FontFamily)
                    || self.priority_completion.active.contains(FontFamily)
                    || self.cascade.ensured_prioritary.contains(FontFamily)
                    || self.cascade.seen.longhands.contains(LonghandId::FontFamily)
                {
                    eprintln!("CSS_MINIMUM_PENDING readset=family-claimed-active-or-applied");
                    return MetricActionProgress::ComputedSizeReadset;
                }
                let family = states.family.get_or_insert_with(|| {
                    self.cascade.begin_font_preparation(
                        self.computed_context,
                        self.decls,
                        LonghandId::FontFamily,
                    )
                });
                if !family.complete {
                    match self.cascade.resume_font_selection(
                        self.computed_context,
                        self.cache,
                        tracker,
                        family,
                        None,
                    ) {
                        MetricPreparationStep::Complete => {}
                        MetricPreparationStep::References(id, value) => {
                            return MetricActionProgress::References(id, value);
                        }
                        MetricPreparationStep::Lookup(id, value, request) => {
                            return MetricActionProgress::Lookup(id, value, request);
                        }
                        _ => return MetricActionProgress::Invalidated,
                    }
                }
            }
            if states
                .family
                .as_ref()
                .is_some_and(|family| !family.stable_for_appearance_addition())
            {
                eprintln!("CSS_MINIMUM_PENDING readset=family-selection-flags");
                return MetricActionProgress::ComputedSizeReadset;
            }
            if reads_writing_mode {
                for id in [Direction, WritingMode, TextOrientation] {
                    if !computed_size_selection_flags_stable(self.decls, id)
                        || !size_input_prefix_is_stable(
                            self.decls,
                            id,
                            flags,
                            self.cascade
                                .reverted
                                .longhands
                                .get(&id.to_longhand())
                                .copied(),
                        )
                        || self.apply_prioritary_property(id, tracker) != ComputationStatus::Ready
                    {
                        eprintln!("CSS_MINIMUM_PENDING readset=orientation-prefix-or-application");
                        return MetricActionProgress::ComputedSizeReadset;
                    }
                }
                self.import_priority_completion();
                if [Direction, WritingMode, TextOrientation]
                    .iter()
                    .any(|id| !self.priority_completion.complete.contains(*id))
                {
                    eprintln!("CSS_MINIMUM_PENDING readset=orientation-incomplete");
                    return MetricActionProgress::ComputedSizeReadset;
                }
            }
            let states = self.size_preparation.take().unwrap();
            let valid = [&states.size, &states.text_scale]
                .into_iter()
                .chain(states.family.iter())
                .all(|state| {
                    state.flags == flags
                        && state.complete
                        && state.waiting.is_none()
                        && !self.cascade.seen.longhands.contains(state.longhand)
                        && self
                            .cascade
                            .reverted
                            .longhands
                            .get(&state.longhand)
                            .copied()
                            == state.initial_revert
                });
            if !valid {
                self.size_preparation = Some(states);
                return MetricActionProgress::Invalidated;
            }
            let operation = states.operation().cloned();
            let mut applied = PrioritaryPropertyIdSet::default();
            for state in states
                .family
                .into_iter()
                .chain([states.text_scale, states.size])
            {
                if state.longhand == LonghandId::FontSize {
                    assert_eq!(
                        self.apply_prioritary_property(MozMinFontSizeRatio, tracker),
                        ComputationStatus::Ready
                    );
                    self.import_priority_completion();
                }
                applied.insert(PrioritaryPropertyId::from_longhand(state.longhand).unwrap());
                for entry in state.prepared {
                    self.cascade.apply_one_longhand(
                        self.computed_context,
                        state.longhand,
                        &entry.declaration,
                        entry.priority,
                        self.cache,
                        tracker,
                    );
                }
                if self.cascade.seen.longhands.contains(state.longhand) {
                    self.cascade.did_apply_prioritary_property(
                        self.computed_context,
                        PrioritaryPropertyId::from_longhand(state.longhand).unwrap(),
                    );
                }
            }
            let inherited_size_preapplied =
                !self.cascade.seen.longhands.contains(LonghandId::FontSize)
                    && !self
                        .computed_context
                        .builder
                        .effective_zoom_for_inheritance
                        .is_one();
            if inherited_size_preapplied {
                let inherited = PropertyDeclaration::css_wide_keyword(
                    LonghandId::FontSize,
                    CSSWideKeyword::Inherit,
                );
                unsafe {
                    self.cascade.do_apply_declaration(
                        self.computed_context,
                        LonghandId::FontSize,
                        &inherited,
                    );
                }
            }
            assert!(
                self.computed_context
                    .builder
                    .get_font()
                    .slow_clone_font_size()
                    .keyword_info
                    .kw
                    == specified::FontSizeKeyword::None
                    || self.priority_completion.complete.contains(FontFamily)
                    || applied.contains(FontFamily)
            );
            self.size_node = Some(index);
            let certificate = Arc::new(ComputedSizeCertificate {
                identity: self.size_identity.clone(),
                flags,
                operation,
                applied,
                witness: ComputedSizePublicationWitness::capture(
                    self.computed_context,
                    reads_writing_mode,
                ),
            });
            if inherited_size_preapplied {
                self.cascade.preapplied_inherited_font_size = Some(certificate.clone());
            }
            self.priority_completion.computed_size = Some(certificate);
            self.metric_action = None;
            MetricActionProgress::Published(FontTarget::ComputedSize)
        }

        fn import_priority_completion(&mut self) {
            if self.font_completion_flags != Some(self.computed_context.included_cascade_flags) {
                self.completed_font_inputs = LonghandIdSet::default();
                self.font_completion_flags = Some(self.computed_context.included_cascade_flags);
            }
            self.cascade
                .refresh_priority_completion(self.computed_context);
            self.priority_completion.complete = self.cascade.completed_prioritary.clone();
        }

        fn pending_metric_action(&self) -> Option<MetricAction> {
            self.metric_action.clone()
        }

        fn metric_action_is_current(&self, action: &MetricAction, depth: usize) -> bool {
            let Some(current) = &self.metric_action else {
                return false;
            };
            std::ptr::eq(current.identity.as_ref(), action.identity.as_ref())
                && current.root == action.root
                && current.owner == action.owner
                && current.index == action.index
                && current.prerequisite.same_as(action.prerequisite)
                && self.frame_root.as_ref() == Some(&action.root)
                && depth > 0
                && self.frames.get(depth - 1).is_some_and(|frame| {
                    frame.index == action.index
                        && frame.var == action.owner
                        && matches!(frame.phase, FramePhase::Publish)
                })
                && matches!(
                    self.var_info[action.index].publication,
                    NodePublication::Pending(_)
                )
        }

        fn resolve_metric_lookup(
            &mut self,
            references: &NonCustomPropertyReferences,
            tracker: &mut AttributeTracker,
            publication_ready: &mut impl FnMut(
                FontDependencyDemand,
                &PrioritaryPropertyIdSet,
                Option<LonghandId>,
            ) -> PublicationDemand,
        ) -> Result<bool, ()> {
            let state = self.metric_lookup.take().unwrap();
            let result =
                self.resolve_metric_lookup_inner(&state, references, tracker, publication_ready);
            if !matches!(result, Ok(true)) {
                self.metric_lookup = Some(state);
            }
            result
        }

        fn resolve_metric_lookup_inner(
            &mut self,
            state: &MetricLookup,
            references: &NonCustomPropertyReferences,
            tracker: &mut AttributeTracker,
            publication_ready: &mut impl FnMut(
                FontDependencyDemand,
                &PrioritaryPropertyIdSet,
                Option<LonghandId>,
            ) -> PublicationDemand,
        ) -> Result<bool, ()> {
            if !self.metric_action_is_current(&state.action, state.depth)
                || state.flags != self.computed_context.included_cascade_flags
                || !Arc::ptr_eq(&state.generation, &self.lookup_bindings.root)
            {
                return Err(());
            }
            let mut value = if self.frames.len() > state.depth {
                None
            } else {
                self.owned_lookup_value(&state.request, tracker)?
            };
            if value.is_none() {
                let target = match state.request.kind {
                    SubstitutionLookupKind::Variable => VarType::Custom(state.request.name.clone()),
                    SubstitutionLookupKind::TypedAttribute => VarType::Attr(
                        state.request.name.clone(),
                        state.request.namespace.clone().ok_or(())?,
                    ),
                    _ => return Err(()),
                };
                let result = if self.frames.len() > state.depth {
                    if self.frames[state.depth].var != target {
                        return Err(());
                    }
                    self.poll_frames(
                        references,
                        tracker,
                        publication_ready,
                        state.depth,
                        state.semantic_floor,
                        state.request.attribute_attempt.as_ref(),
                    )
                } else {
                    if self.frames.len() != state.depth || self.frame_reply.is_some() {
                        return Err(());
                    }
                    match start_frame(target, self, tracker) {
                        Ok(mut frame) => {
                            if state.request.attribute_attempt.is_some() {
                                frame.enter_guarded_custom(state.request.guards.clone(), self);
                            }
                            self.frames.push(frame);
                            self.poll_frames(
                                references,
                                tracker,
                                publication_ready,
                                state.depth,
                                state.semantic_floor,
                                state.request.attribute_attempt.as_ref(),
                            )
                        }
                        Err(result) => result,
                    }
                };
                if !matches!(result, VisitResult::Complete | VisitResult::CycleSettled) {
                    return Ok(false);
                }
                value = self.owned_lookup_value(&state.request, tracker)?;
            }
            let Some(value) = value else { return Ok(false) };
            if self.frames.len() != state.depth || self.lookup_reply.is_some() {
                return Err(());
            }
            self.lookup_reply = Some((
                state.longhand,
                FontSelectionReply {
                    value: state.value.clone(),
                    generation: state.generation.clone(),
                    lookup: Some(SubstitutionLookupReply {
                        identity: state.request.identity.clone(),
                        value,
                    }),
                },
            ));
            Ok(true)
        }

        fn authorize_metric_substitution(
            &mut self,
            action: &MetricAction,
            longhand: LonghandId,
            value: Arc<UnparsedValue>,
        ) -> bool {
            if !self.metric_action_is_current(action, self.frames.len())
                || self.metric_references.is_some()
                || self.frame_reply.is_some()
                || self.lookup_reply.is_some()
                || !self
                    .lookup_bindings
                    .valid_for(self.computed_context.included_cascade_flags)
            {
                return false;
            }
            self.lookup_reply = Some((
                longhand,
                FontSelectionReply {
                    value,
                    generation: self.lookup_bindings.root.clone(),
                    lookup: None,
                },
            ));
            true
        }

        fn drive_metric_action(
            &mut self,
            action: &MetricAction,
            references: &NonCustomPropertyReferences,
            attribute_tracker: &mut AttributeTracker,
            publication_ready: &mut impl FnMut(
                FontDependencyDemand,
                &PrioritaryPropertyIdSet,
                Option<LonghandId>,
            ) -> PublicationDemand,
        ) -> MetricActionProgress {
            loop {
                if self.metric_lookup.is_some() {
                    match self.resolve_metric_lookup(
                        references,
                        attribute_tracker,
                        publication_ready,
                    ) {
                        Ok(true) => {}
                        Ok(false) => {
                            let pending = self.metric_lookup.as_ref().unwrap();
                            return MetricActionProgress::Lookup(
                                pending.longhand,
                                pending.value.clone(),
                                pending.request.clone(),
                            );
                        }
                        Err(()) => return MetricActionProgress::Invalidated,
                    }
                }

                if let Some(state) = &self.metric_references {
                    if !self.metric_action_is_current(action, state.depth)
                        || !std::ptr::eq(state.action.identity.as_ref(), action.identity.as_ref())
                        || state.flags != self.computed_context.included_cascade_flags
                    {
                        return MetricActionProgress::WrongAction;
                    }
                    if !self.resolve_metric_references(
                        references,
                        attribute_tracker,
                        publication_ready,
                    ) {
                        let state = self.metric_references.as_ref().unwrap();
                        return MetricActionProgress::References(
                            state.longhand,
                            state.value.clone(),
                        );
                    }
                }
                match self.perform_metric_action(action, attribute_tracker) {
                    MetricActionProgress::References(longhand, value) => {
                        if !self.authorize_metric_substitution(action, longhand, value) {
                            return MetricActionProgress::Invalidated;
                        }
                    }
                    MetricActionProgress::Lookup(longhand, value, request) => {
                        assert!(self.metric_lookup.is_none() && self.lookup_reply.is_none());
                        self.metric_lookup = Some(MetricLookup {
                            action: action.clone(),
                            longhand,
                            value,
                            request,
                            depth: self.frames.len(),
                            semantic_floor: self.count,
                            flags: self.computed_context.included_cascade_flags,
                            generation: self.lookup_bindings.root.clone(),
                        });
                    }
                    result => return result,
                }
            }
        }

        fn resolve_metric_references(
            &mut self,
            references: &NonCustomPropertyReferences,
            attribute_tracker: &mut AttributeTracker,
            publication_ready: &mut impl FnMut(
                FontDependencyDemand,
                &PrioritaryPropertyIdSet,
                Option<LonghandId>,
            ) -> PublicationDemand,
        ) -> bool {
            let mut state = self.metric_references.take().unwrap();
            let complete = loop {
                match state.walk.resume(
                    &state.value.variable_value.url_data,
                    Some(state.value.substitution_property_id(state.longhand)),
                    self,
                    attribute_tracker,
                    state.reply.take(),
                ) {
                    ReferenceWalkStep::Complete => break true,
                    ReferenceWalkStep::WrongReply => {
                        unreachable!("Action owns its reference reply")
                    }
                    ReferenceWalkStep::Link(target) => {
                        let result = if self.frames.len() > state.depth {
                            assert_eq!(self.frames[state.depth].var, target);
                            self.poll_frames(
                                references,
                                attribute_tracker,
                                publication_ready,
                                state.depth,
                                state.semantic_floor,
                                None,
                            )
                        } else {
                            assert_eq!(self.frames.len(), state.depth);
                            assert!(self.frame_reply.is_none());
                            match start_frame(target.clone(), self, attribute_tracker) {
                                Ok(frame) => {
                                    self.frames.push(frame);
                                    self.poll_frames(
                                        references,
                                        attribute_tracker,
                                        publication_ready,
                                        state.depth,
                                        state.semantic_floor,
                                        None,
                                    )
                                }
                                Err(result) => result,
                            }
                        };
                        let reply = match result {
                            VisitResult::Complete => ReferenceReadiness::Ready,
                            VisitResult::CycleSettled => ReferenceReadiness::SemanticCycle,
                            VisitResult::SemanticOpen(_)
                            | VisitResult::ComputationPending(_)
                            | VisitResult::ComputedSize(_) => {
                                break false;
                            }
                        };
                        state.reply = Some((target, reply));
                    }
                }
            };
            state.complete = complete;
            self.metric_references = Some(state);
            complete
        }

        fn perform_metric_action(
            &mut self,
            action: &MetricAction,
            attribute_tracker: &mut AttributeTracker,
        ) -> MetricActionProgress {
            let depth = self
                .metric_references
                .as_ref()
                .map_or(self.frames.len(), |state| state.depth);
            if !self.metric_action_is_current(action, depth)
                || self.frames.len() != depth
                || self.metric_references.as_ref().is_some_and(|state| {
                    !state.complete
                        || !std::ptr::eq(state.action.identity.as_ref(), action.identity.as_ref())
                        || state.flags != self.computed_context.included_cascade_flags
                })
            {
                return MetricActionProgress::WrongAction;
            }
            let reference = self.lookup_reply.take().or_else(|| {
                self.metric_references.take().map(|state| {
                    (
                        state.longhand,
                        FontSelectionReply {
                            value: state.value,
                            generation: self.lookup_bindings.root.clone(),
                            lookup: None,
                        },
                    )
                })
            });
            let target_id = match action.prerequisite {
                FontTarget::ComputedSize => {
                    return self.prepare_computed_size(action.index, attribute_tracker, reference);
                }
                FontTarget::Metric(id) => id,
                FontTarget::Synthesis(longhand) => {
                    return self.perform_synthesis_action(longhand, attribute_tracker, reference);
                }
            };
            use PrioritaryPropertyId::*;
            if !matches!(
                target_id,
                FontWeight
                    | FontWidth
                    | FontStyle
                    | FontSizeAdjust
                    | Direction
                    | WritingMode
                    | TextOrientation
                    | Appearance
                    | FontFamily
            ) {
                return MetricActionProgress::Unsupported;
            }
            if self
                .priority_completion
                .computed_size
                .as_ref()
                .is_some_and(|certificate| {
                    certificate.valid_for(self.computed_context)
                        && certificate.applied.contains(target_id)
                })
            {
                match self.apply_prioritary_property(target_id, attribute_tracker) {
                    ComputationStatus::Ready => {
                        self.import_priority_completion();
                        if self.priority_completion.complete.contains(target_id) {
                            self.metric_action = None;
                            return MetricActionProgress::AlreadyComplete;
                        }
                        return MetricActionProgress::GeneratedPrerequisite(target_id);
                    }
                    ComputationStatus::Prepare(id) => {
                        return MetricActionProgress::GeneratedPrerequisite(
                            PrioritaryPropertyId::from_longhand(id).unwrap(),
                        );
                    }
                    ComputationStatus::Pending => {
                        return MetricActionProgress::GeneratedPrerequisite(target_id);
                    }
                }
            }
            if self.priority_completion.complete.contains(target_id) {
                self.metric_action = None;
                return MetricActionProgress::AlreadyComplete;
            }
            if self
                .metric_drain
                .request(target_id, &mut self.priority_completion)
                .is_err()
            {
                return MetricActionProgress::Invalidated;
            }
            let flags = self.computed_context.included_cascade_flags;
            match self.metric_drain.poll(
                self.cascade,
                self.computed_context,
                self.cache,
                attribute_tracker,
                &mut self.priority_completion,
                reference,
            ) {
                MetricDrainStep::Published(id) => {
                    if flags != self.computed_context.included_cascade_flags {
                        self.cascade
                            .refresh_priority_completion(self.computed_context);
                        self.priority_completion.complete =
                            self.cascade.completed_prioritary.clone();
                        return MetricActionProgress::Invalidated;
                    }
                    self.cascade.completed_prioritary.insert(id);
                    if id.to_longhand() == target_id.to_longhand() {
                        assert!(self.priority_completion.complete.contains(id));
                        self.metric_action = None;
                    }
                    MetricActionProgress::Published(FontTarget::Metric(id))
                }
                MetricDrainStep::Prerequisite(id) => {
                    MetricActionProgress::GeneratedPrerequisite(id)
                }
                MetricDrainStep::References(id, value) => {
                    MetricActionProgress::References(id, value)
                }
                MetricDrainStep::Lookup(id, value, request) => {
                    MetricActionProgress::Lookup(id, value, request)
                }
                MetricDrainStep::Invalidated(_)
                | MetricDrainStep::WrongReply
                | MetricDrainStep::Complete => MetricActionProgress::Invalidated,
            }
        }

        fn perform_synthesis_action(
            &mut self,
            longhand: LonghandId,
            attribute_tracker: &mut AttributeTracker,
            reference: Option<(LonghandId, FontSelectionReply)>,
        ) -> MetricActionProgress {
            if !is_synthesis_longhand(longhand) {
                return MetricActionProgress::Unsupported;
            }
            if self.completed_font_inputs.contains(longhand) {
                self.metric_action = None;
                return MetricActionProgress::AlreadyComplete;
            }
            let state = self.font_preparation.get_or_insert_with(|| {
                self.cascade
                    .begin_font_preparation(self.computed_context, self.decls, longhand)
            });
            if state.longhand != longhand
                || reference.as_ref().is_some_and(|(id, _)| *id != longhand)
            {
                return MetricActionProgress::Invalidated;
            }
            match self.cascade.resume_metric_preparation(
                self.computed_context,
                self.cache,
                attribute_tracker,
                state,
                &self.priority_completion.complete,
                reference.map(|(_, value)| value),
            ) {
                MetricPreparationStep::References(id, value) => {
                    return MetricActionProgress::References(id, value);
                }
                MetricPreparationStep::Lookup(id, value, request) => {
                    return MetricActionProgress::Lookup(id, value, request);
                }
                MetricPreparationStep::Prerequisites(_) | MetricPreparationStep::Invalidated => {
                    return MetricActionProgress::Invalidated;
                }
                MetricPreparationStep::Complete => {}
            }
            let state = self.font_preparation.take().unwrap();
            if let Err(state) = self.cascade.publish_prepared_metric(
                self.computed_context,
                self.cache,
                attribute_tracker,
                state,
                &self.priority_completion.complete,
            ) {
                self.font_preparation = Some(state);
                return MetricActionProgress::Invalidated;
            }
            self.completed_font_inputs.insert(longhand);
            self.metric_action = None;
            MetricActionProgress::Published(FontTarget::Synthesis(longhand))
        }

        fn visited(&self, var: &VarType) -> Option<VisitResult> {
            let index = match var {
                VarType::Custom(name) => self.index_map.var.get(name).copied(),
                VarType::Attr(name, namespace) => self
                    .index_map
                    .attr
                    .get(namespace)
                    .and_then(|map| map.get(name))
                    .copied(),
                VarType::NonCustom(reference) => self.non_custom_index_map[*reference],
            }?;
            Some(match self.var_info[index].publication.readiness() {
                NodeReadiness::SemanticOpen => VisitResult::SemanticOpen(index),
                NodeReadiness::ComputationPending => VisitResult::ComputationPending(index),
                NodeReadiness::Complete => VisitResult::Complete,
                NodeReadiness::CycleSettled => VisitResult::CycleSettled,
            })
        }

        fn publish_closed(
            &mut self,
            index: usize,
            attr_tracker: &mut AttributeTracker,
        ) -> ComputationStatus {
            let priority = match &self.var_info[index].publication {
                NodePublication::Pending(ClosedValue::Prioritary(id)) => Some(*id),
                _ => None,
            };
            if let Some(id) = priority {
                let status = self.apply_prioritary_property(id, attr_tracker);
                if status != ComputationStatus::Ready {
                    return status;
                }
            }
            let value = self.var_info[index].publication.take_ready(true).unwrap();
            match value {
                ClosedValue::Prepared(name, prepared) => {
                    prepared.apply(&name, self.stylist, self.computed_context);
                }
                ClosedValue::Substitute(var, value) => {
                    let name = match &var {
                        VarType::Custom(name) | VarType::Attr(name, _) => name,
                        VarType::NonCustom(_) => unreachable!(),
                    };
                    substitute_references_if_needed_and_apply(
                        name,
                        var.namespace(),
                        &value,
                        self.stylist,
                        self.computed_context,
                        attr_tracker,
                    );
                }
                ClosedValue::Prioritary(_) => {}
            }
            self.var_info[index].publication.finish();
            self.record_lookup_publication(index);
            ComputationStatus::Ready
        }

        fn map(&self) -> &ComputedSubstitutionFunctions {
            &self.computed_context.builder.substitution_functions
        }

        fn map_mut(&mut self) -> &mut ComputedSubstitutionFunctions {
            &mut self.computed_context.builder.substitution_functions
        }

        /// Marks a given `name` as being in a loop.
        fn handle_loop(&mut self, name: &VarType) {
            match name {
                VarType::Attr(name, namespace) => {
                    self.computed_context
                        .builder
                        .substitution_functions
                        .remove_attr(name, namespace);
                }
                VarType::Custom(name) => {
                    // This variable is in a loop. Resolve to invalid.
                    handle_invalid_at_computed_value_time(
                        name,
                        self.stylist.get_custom_property_registration(name),
                        self.computed_context,
                    );
                }
                VarType::NonCustom(non_custom) => {
                    self.computed_context
                        .builder
                        .invalid_non_custom_properties
                        .insert(non_custom.to_prioritary_id().to_longhand());
                }
            }
        }

        /// Applies a prioritary property (and its dependencies) while resolving custom properties.
        ///
        /// The in-progress map lives outside `computed_context` during traversal; we move it into
        /// `computed_context.builder.substitution_functions` so the prioritary declaration's `var()`
        /// references resolve against the custom properties resolved so far, then take it back out.
        fn apply_prioritary_property(
            &mut self,
            id: PrioritaryPropertyId,
            attr_tracker: &mut AttributeTracker,
        ) -> ComputationStatus {
            self.cascade.ensure_prioritary_property(
                self.computed_context,
                self.decls,
                self.cache,
                attr_tracker,
                id,
                self.priority_completion,
                true,
            )
        }
    }

    #[derive(Clone, Copy, Eq, PartialEq)]
    enum ReferenceReadiness {
        Ready,
        SemanticOpen,
        SemanticCycle,
        ComputationPending,
    }

    struct ReferenceWalk {
        queued: SmallVec<[References; 5]>,
        current: Option<(References, usize)>,
        waiting: Option<VarType>,
        flags: ReferenceFlags,
    }

    enum ReferenceWalkStep {
        Link(VarType),
        Complete,
        WrongReply,
    }

    impl ReferenceWalk {
        fn new(root: &References) -> Self {
            let mut queued = SmallVec::new();
            queued.push(root.clone());
            Self {
                queued,
                current: None,
                waiting: None,
                flags: ReferenceFlags::empty(),
            }
        }

        fn resume(
            &mut self,
            url_data: &UrlExtraData,
            property_id: Option<PropertyIdRef>,
            context: &mut Context,
            attribute_tracker: &mut AttributeTracker,
            mut reply: Option<(VarType, ReferenceReadiness)>,
        ) -> ReferenceWalkStep {
            if let Some((target, readiness)) = reply.as_ref() {
                if self.waiting.as_ref() != Some(target) {
                    return ReferenceWalkStep::WrongReply;
                }
                if *readiness == ReferenceReadiness::ComputationPending {
                    return ReferenceWalkStep::Link(target.clone());
                }
            }
            loop {
                if self
                    .current
                    .as_ref()
                    .is_some_and(|(refs, next)| *next == refs.refs.len())
                {
                    self.current = None;
                }
                if self.current.is_none() {
                    let Some(refs) = self.queued.pop() else {
                        return ReferenceWalkStep::Complete;
                    };
                    self.flags |= refs.flags;
                    self.current = Some((refs, 0));
                }
                let (refs, cursor) = self.current.as_mut().unwrap();
                let Some(next) = refs.refs.get(*cursor) else {
                    continue;
                };
                if self.waiting.is_none() {
                    if next.substitution_kind == SubstitutionFunctionKind::Env {
                        if context.captured_environment(&next.name, url_data).is_none() {
                            if let Some(fallback) = &next.fallback {
                                self.queued.push(fallback.references.clone());
                            }
                        }
                        *cursor += 1;
                        continue;
                    }
                    let target = if next.substitution_kind == SubstitutionFunctionKind::Attr {
                        if !next.is_attr_with_type() {
                            if let Some(fallback) = &next.fallback {
                                if !next
                                    .attribute_data
                                    .non_type_primary_is_valid(&next.name, attribute_tracker)
                                {
                                    self.queued.push(fallback.references.clone());
                                }
                            }
                            *cursor += 1;
                            continue;
                        }
                        let Some(namespace) = next.attribute_data.namespace() else {
                            if let Some(fallback) = &next.fallback {
                                self.queued.push(fallback.references.clone());
                            }
                            *cursor += 1;
                            continue;
                        };
                        context.setup_attribute_input(
                            &next.name,
                            namespace,
                            url_data,
                            attribute_tracker,
                        );
                        VarType::Attr(next.name.clone(), namespace.clone())
                    } else {
                        VarType::Custom(next.name.clone())
                    };
                    self.waiting = Some(target.clone());
                    return ReferenceWalkStep::Link(target);
                }
                let Some((_, readiness)) = reply.take() else {
                    return ReferenceWalkStep::Link(self.waiting.as_ref().unwrap().clone());
                };
                debug_assert!(readiness != ReferenceReadiness::ComputationPending);
                let resolved = match next.substitution_kind {
                    SubstitutionFunctionKind::Var => {
                        let registration =
                            context.stylist.get_custom_property_registration(&next.name);
                        context.map().get_var(registration, &next.name)
                    }
                    SubstitutionFunctionKind::Attr => next
                        .attribute_data
                        .namespace()
                        .and_then(|namespace| context.map().get_attr(&next.name, namespace)),
                    SubstitutionFunctionKind::Env => unreachable!(),
                };
                let mut primary_valid = false;
                if let Some(resolved) = resolved {
                    if let Some(value) = resolved.as_universal() {
                        primary_valid = !value.has_references();
                        self.flags |= value.references.flags;
                    } else {
                        primary_valid = true;
                    }
                    if primary_valid && next.is_attr_with_type() {
                        let value = resolved.to_variable_value();
                        primary_valid = next
                            .attribute_data
                            .parse_typed_value(
                                &mut cssparser::Parser::new(&value.css),
                                url_data,
                                property_id,
                            )
                            .is_ok();
                    }
                }
                if !primary_valid {
                    if let Some(fallback) = &next.fallback {
                        self.queued.push(fallback.references.clone());
                    }
                }
                self.waiting = None;
                *cursor += 1;
            }
        }
    }

    /// Traverse the references in `root` (the value of a custom property or of a non-custom
    /// property feeding a `NonCustom` node), creating graph edges to the referenced substitution
    /// functions and updating `lowlink`/`self_ref` accordingly.
    ///
    /// We follow var()/attr()/env() fallbacks only when the primary substitution function is
    /// guaranteed-invalid (i.e. when the fallback is actually used). This matches the substitution
    /// order and the resolution of https://github.com/w3c/csswg-drafts/issues/11500: cycles (or
    /// dependencies) that only exist through an unused fallback don't count.
    ///
    /// We need to bubble up non custom references from unregistered properties.
    fn visit_value_references<'a, 'b, 'c, 'd>(
        root: &References,
        url_data: &UrlExtraData,
        property_id: Option<PropertyIdRef>,
        index: usize,
        references_from_non_custom_properties: &NonCustomPropertyReferences,
        context: &mut Context<'a, 'b, 'c, 'd>,
        lowlink: &mut usize,
        self_ref: &mut bool,
        attribute_tracker: &mut AttributeTracker,
        non_custom_references: &mut ReferenceFlags,
    ) {
        // FIXME: Maybe avoid visiting the same var twice if not needed?
        let mut refs_stack = SmallVec::<[&References; 5]>::new();
        refs_stack.push(root);
        while let Some(refs) = refs_stack.pop() {
            *non_custom_references |= refs.flags;
            for next in &refs.refs {
                if next.substitution_kind == SubstitutionFunctionKind::Env {
                    // env() doesn't reference custom properties, so it never participates in
                    // cycles; its fallback is used only when the environment doesn't provide
                    // the variable.
                    let present = context.captured_environment(&next.name, url_data).is_some();
                    if !present && let Some(ref fallback) = next.fallback {
                        refs_stack.push(&fallback.references);
                    }
                    continue;
                }

                let next_var = if next.substitution_kind == SubstitutionFunctionKind::Attr {
                    if !next.is_attr_with_type() {
                        if let Some(ref fallback) = next.fallback
                            && !next
                                .attribute_data
                                .non_type_primary_is_valid(&next.name, attribute_tracker)
                        {
                            refs_stack.push(&fallback.references);
                        }
                        continue;
                    }
                    let Some(namespace) = next.attribute_data.namespace() else {
                        if let Some(ref fallback) = next.fallback {
                            refs_stack.push(&fallback.references);
                        }
                        continue;
                    };
                    context.setup_attribute_input(
                        &next.name,
                        namespace,
                        url_data,
                        attribute_tracker,
                    );
                    VarType::Attr(next.name.clone(), namespace.clone())
                } else {
                    VarType::Custom(next.name.clone())
                };

                visit_link(
                    next_var,
                    index,
                    references_from_non_custom_properties,
                    context,
                    lowlink,
                    self_ref,
                    attribute_tracker,
                );

                // Now that the primary reference has been resolved, classify it to
                // decide whether its fallback is used.
                let kind = next.substitution_kind;
                let resolved = match kind {
                    SubstitutionFunctionKind::Var => {
                        let registration =
                            context.stylist.get_custom_property_registration(&next.name);
                        context.map().get_var(registration, &next.name)
                    }
                    SubstitutionFunctionKind::Attr => next
                        .attribute_data
                        .namespace()
                        .and_then(|namespace| context.map().get_attr(&next.name, namespace)),
                    SubstitutionFunctionKind::Env => unreachable!("Handled above"),
                };
                // The primary is guaranteed-invalid if it's absent from the map, or still
                // present but unresolved (i.e. part of a cycle currently being resolved).
                let mut primary_valid = false;
                if let Some(resolved) = resolved {
                    if let Some(v) = resolved.as_universal() {
                        primary_valid = !v.has_references();
                        *non_custom_references |= v.references.flags;
                    } else {
                        // Resolved and computed value, no other custom references left.
                        primary_valid = true;
                    }
                    if primary_valid && next.is_attr_with_type() {
                        let value = resolved.to_variable_value();
                        primary_valid = next
                            .attribute_data
                            .parse_typed_value(
                                &mut cssparser::Parser::new(&value.css),
                                url_data,
                                property_id,
                            )
                            .is_ok();
                    }
                }

                if !primary_valid && let Some(ref fallback) = next.fallback {
                    refs_stack.push(&fallback.references);
                }
            }
        }
    }

    /// Traverse a single dependency `var` of the variable at order index `index`, updating its
    /// `lowlink`/`self_ref` from the result.
    fn visit_link<'a, 'b, 'c, 'd>(
        var: VarType,
        index: usize,
        non_custom_references: &NonCustomPropertyReferences,
        context: &mut Context<'a, 'b, 'c, 'd>,
        lowlink: &mut usize,
        self_ref: &mut bool,
        attr_tracker: &mut AttributeTracker,
    ) {
        let next_index = match traverse(var, non_custom_references, context, attr_tracker) {
            VisitResult::SemanticOpen(index) => index,
            VisitResult::Complete | VisitResult::CycleSettled => return,
            VisitResult::ComputationPending(_) | VisitResult::ComputedSize(_) => {
                unreachable!("Recursive traversal cannot resume a suspended publication")
            }
        };
        let next_info = &context.var_info[next_index];
        if next_index > index {
            // The next variable has a larger index than us, so it
            // must be inserted in the recursive call above. We want
            // to get its lowlink.
            *lowlink = cmp::min(*lowlink, next_info.lowlink);
        } else if next_index == index {
            *self_ref = true;
        } else if next_info.var.is_some() {
            // The next variable has a smaller order index and it is
            // in the stack, so we are at the same component.
            *lowlink = cmp::min(*lowlink, next_index);
        }
    }

    /// Separates semantic ancestry from completed map outcomes.
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

    #[derive(Clone, Copy)]
    enum PublicationDemand {
        Ready,
        Metric(PrioritaryPropertyId),
        Synthesis(LonghandId),
        Unresolved,
    }

    #[derive(Clone)]
    struct MetricAction {
        identity: Arc<()>,
        root: VarType,
        owner: VarType,
        index: usize,
        prerequisite: FontTarget,
    }

    struct MetricLookup {
        action: MetricAction,
        longhand: LonghandId,
        value: Arc<UnparsedValue>,
        request: SubstitutionLookup,
        depth: usize,
        semantic_floor: usize,
        flags: RuleCascadeFlags,
        generation: Arc<()>,
    }

    struct MetricReferences {
        action: MetricAction,
        longhand: LonghandId,
        value: Arc<UnparsedValue>,
        walk: ReferenceWalk,
        reply: Option<(VarType, ReferenceReadiness)>,
        depth: usize,
        semantic_floor: usize,
        flags: RuleCascadeFlags,
        complete: bool,
    }

    enum MetricActionProgress {
        ComputedSizeReadset,
        Published(FontTarget),
        AlreadyComplete,
        GeneratedPrerequisite(PrioritaryPropertyId),
        References(LonghandId, Arc<UnparsedValue>),
        Lookup(LonghandId, Arc<UnparsedValue>, SubstitutionLookup),
        Invalidated,
        Unsupported,
        WrongAction,
    }

    #[derive(Clone, Copy)]
    enum FramePhase {
        References,
        Prepare,
        Units,
        PrioritySize,
        PriorityReferences,
        LateDefault,
        Close,
        Publish,
    }

    #[derive(Clone, Copy)]
    enum LinkPurpose {
        Reference,
        Unit,
        PrioritySize,
        LateDefault,
    }

    struct GuardedCustomFrame {
        substitution: ResumableSubstitution<'static>,
        request: Option<SubstitutionLookup>,
        flags: RuleCascadeFlags,
        generation: Arc<()>,
    }

    struct TraversalFrame {
        guarded_custom: Option<GuardedCustomFrame>,
        var: VarType,
        index: usize,
        lowlink: usize,
        self_ref: bool,
        registered: bool,
        selected_dependency_eligible: bool,
        value_non_custom_refs: ReferenceFlags,
        value: Option<Arc<ComputedPropertyValue>>,
        prepared_custom: Option<PreparedCustomValue>,
        phase: FramePhase,
        walk: Option<ReferenceWalk>,
        unit_links: SmallVec<[SingleNonCustomReference; 3]>,
        unit_cursor: usize,
        priority_cursor: usize,
        waiting: Option<(VarType, LinkPurpose)>,
        reference_reply: Option<(VarType, ReferenceReadiness)>,
    }

    enum FrameStep {
        Link(VarType),
        Complete(VisitResult),
        ComputedSize,
        Pending(Option<FontTarget>),
    }

    impl TraversalFrame {
        fn enter_guarded_custom(&mut self, guards: Vec<SubstitutionGuard>, context: &Context) {
            let VarType::Custom(name) = &self.var else {
                return;
            };
            assert!(self.guarded_custom.is_none());
            self.guarded_custom = Some(GuardedCustomFrame {
                substitution: ResumableSubstitution::for_custom(
                    (**self.value.as_ref().unwrap()).clone(),
                    name.clone(),
                    guards,
                ),
                request: None,
                flags: context.computed_context.included_cascade_flags,
                generation: context.lookup_bindings.root.clone(),
            });
        }

        fn guarded_references(
            &mut self,
            context: &mut Context,
            tracker: &mut AttributeTracker,
        ) -> Option<FrameStep> {
            let state = self.guarded_custom.as_mut().unwrap();
            if state.flags != context.computed_context.included_cascade_flags
                || !Arc::ptr_eq(&state.generation, &context.lookup_bindings.root)
            {
                return Some(FrameStep::Pending(None));
            }
            if state.substitution.body_marked()
                || self
                    .reference_reply
                    .as_ref()
                    .is_some_and(|(_, reply)| matches!(reply, ReferenceReadiness::SemanticOpen))
            {
                self.reference_reply = None;
                self.self_ref |= state.substitution.body_marked();
                self.phase = FramePhase::LateDefault;
                return None;
            }
            self.reference_reply = None;
            let mut reply = None;
            loop {
                if let Some(request) = state.request.as_ref() {
                    let value = match context.owned_lookup_value(request, tracker) {
                        Ok(Some(value)) => value,
                        Ok(None) => {
                            if request.kind != SubstitutionLookupKind::Variable {
                                return Some(FrameStep::Pending(None));
                            }
                            SubstitutionGuard::mark_reentry(
                                &request.guards,
                                &SubstitutionGuardKey::Property(PropertyId::Custom(
                                    request.name.clone(),
                                )),
                            );
                            let target = VarType::Custom(request.name.clone());
                            return Some(self.link(target, LinkPurpose::Reference));
                        }
                        Err(()) => return Some(FrameStep::Pending(None)),
                    };
                    reply = Some(SubstitutionLookupReply {
                        identity: request.identity.clone(),
                        value,
                    });
                    state.request = None;
                }
                match state.substitution.poll(reply.take()) {
                    SubstitutionPoll::Lookup(request) => state.request = Some(request),
                    SubstitutionPoll::Complete(result) => {
                        if state.substitution.body_marked() {
                            self.self_ref = true;
                            self.phase = FramePhase::LateDefault;
                            return None;
                        }
                        let VarType::Custom(name) = &self.var else {
                            unreachable!()
                        };
                        let (prepared, flags) = prepare_completed_custom_value(
                            name,
                            &self.value.as_ref().unwrap().url_data,
                            result,
                            context.stylist,
                            context.computed_context,
                        );
                        self.value_non_custom_refs |= flags;
                        self.value_non_custom_refs
                            .remove(ReferenceFlags::COLOR_SCHEME);
                        if prepared.depends_on_color_scheme() {
                            self.value_non_custom_refs |= ReferenceFlags::COLOR_SCHEME;
                        }
                        self.prepared_custom = Some(prepared);
                        self.phase = FramePhase::Prepare;
                        return None;
                    }
                    SubstitutionPoll::WrongReply | SubstitutionPoll::Finished => {
                        unreachable!("Guarded frame owns its exact lookup reply")
                    }
                }
            }
        }

        fn accepts_computed_size(&self, is_root: bool) -> bool {
            matches!(
                self.waiting,
                Some((
                    VarType::NonCustom(SingleNonCustomReference::FontUnits),
                    LinkPurpose::Unit
                ))
            ) && frame_font_demand(self.registered, self.value_non_custom_refs, is_root)
                == FontDependencyDemand::ComputedSize
        }

        fn link(&mut self, target: VarType, purpose: LinkPurpose) -> FrameStep {
            assert!(self.waiting.is_none());
            self.waiting = Some((target.clone(), purpose));
            FrameStep::Link(target)
        }

        fn receive(&mut self, target: VarType, result: VisitResult, context: &Context) -> bool {
            let Some((waiting, purpose)) = self.waiting.as_ref() else {
                return false;
            };
            if *waiting != target || matches!(result, VisitResult::ComputationPending(_)) {
                return false;
            }
            if let VisitResult::ComputedSize(index) = result {
                if !self.accepts_computed_size(context.computed_context.is_root_element())
                    || !context.computed_size_ready(index)
                {
                    return false;
                }
            }
            if let VisitResult::SemanticOpen(next_index) = result {
                let next = &context.var_info[next_index];
                assert!(matches!(
                    next.publication.readiness(),
                    NodeReadiness::SemanticOpen
                ));
                if next_index > self.index {
                    self.lowlink = cmp::min(self.lowlink, next.lowlink);
                } else if next_index == self.index {
                    self.self_ref = true;
                } else if next.var.is_some() {
                    self.lowlink = cmp::min(self.lowlink, next_index);
                }
            }
            match purpose {
                LinkPurpose::Reference => {
                    assert!(self.reference_reply.is_none());
                    self.reference_reply = Some((
                        target,
                        match result {
                            VisitResult::SemanticOpen(_) => ReferenceReadiness::SemanticOpen,
                            VisitResult::Complete => ReferenceReadiness::Ready,
                            VisitResult::CycleSettled => ReferenceReadiness::SemanticCycle,
                            VisitResult::ComputationPending(_) | VisitResult::ComputedSize(_) => {
                                unreachable!()
                            }
                        },
                    ));
                }
                LinkPurpose::Unit => self.unit_cursor += 1,
                LinkPurpose::PrioritySize | LinkPurpose::LateDefault => {}
            }
            self.waiting = None;
            true
        }

        fn step(
            &mut self,
            references: &NonCustomPropertyReferences,
            context: &mut Context,
            attribute_tracker: &mut AttributeTracker,
            publication_ready: &mut impl FnMut(
                FontDependencyDemand,
                &PrioritaryPropertyIdSet,
                Option<LonghandId>,
            ) -> PublicationDemand,
        ) -> FrameStep {
            assert!(self.waiting.is_none());
            loop {
                match self.phase {
                    FramePhase::References => {
                        if self.guarded_custom.is_some() {
                            if let Some(step) = self.guarded_references(context, attribute_tracker)
                            {
                                return step;
                            }
                            continue;
                        }
                        let value = self.value.as_ref().unwrap();
                        let name = match &self.var {
                            VarType::Custom(name) | VarType::Attr(name, _) => name,
                            VarType::NonCustom(_) => unreachable!(),
                        };
                        let walk = self
                            .walk
                            .get_or_insert_with(|| ReferenceWalk::new(&value.references));
                        match walk.resume(
                            &value.url_data,
                            Some(PropertyIdRef::from(name)),
                            context,
                            attribute_tracker,
                            self.reference_reply.take(),
                        ) {
                            ReferenceWalkStep::Link(target) => {
                                return self.link(target, LinkPurpose::Reference);
                            }
                            ReferenceWalkStep::WrongReply => {
                                unreachable!("Frame owns its reference reply")
                            }
                            ReferenceWalkStep::Complete => {}
                        }
                        self.value_non_custom_refs |= walk.flags;
                        self.walk = None;
                        self.phase = FramePhase::Prepare;
                    }
                    FramePhase::Prepare => {
                        if let VarType::Custom(ref name) = self.var {
                            if self.selected_dependency_eligible && self.prepared_custom.is_none() {
                                let may_compute_color = self
                                    .value_non_custom_refs
                                    .intersects(ReferenceFlags::COLOR_SCHEME);
                                if self.registered
                                    && may_compute_color
                                    && self.lowlink == self.index
                                    && !self.self_ref
                                    && context.stack.last() == Some(&self.index)
                                {
                                    if preparation_needs_font_inputs(
                                        self.value_non_custom_refs,
                                        context.computed_context.is_root_element(),
                                    ) {
                                        context.import_priority_completion();
                                        let demand = frame_font_demand(
                                            self.registered,
                                            self.value_non_custom_refs,
                                            context.computed_context.is_root_element(),
                                        );
                                        if !matches!(
                                            context.publication_readiness(
                                                publication_ready,
                                                demand,
                                                next_unprepared_font_input(
                                                    context.decls,
                                                    &context.completed_font_inputs
                                                )
                                            ),
                                            PublicationDemand::Ready
                                        ) {
                                            return FrameStep::Pending(None);
                                        }
                                    }
                                    self.value_non_custom_refs
                                        .remove(ReferenceFlags::COLOR_SCHEME);
                                    let prepared = prepare_custom_value(
                                        name,
                                        self.value.as_ref().unwrap(),
                                        context.stylist,
                                        context.computed_context,
                                        attribute_tracker,
                                    );
                                    if prepared.depends_on_color_scheme() {
                                        self.value_non_custom_refs |= ReferenceFlags::COLOR_SCHEME;
                                    }
                                    self.prepared_custom = Some(prepared);
                                } else {
                                    self.value_non_custom_refs
                                        .remove(ReferenceFlags::COLOR_SCHEME);
                                }
                            }
                        }
                        if self.registered && !self.value_non_custom_refs.is_empty() {
                            self.value_non_custom_refs.for_each_non_custom(
                                context.computed_context.is_root_element(),
                                |reference| self.unit_links.push(reference),
                            );
                        }
                        self.phase = FramePhase::Units;
                    }
                    FramePhase::Units => {
                        if let Some(reference) = self.unit_links.get(self.unit_cursor) {
                            return self.link(VarType::NonCustom(*reference), LinkPurpose::Unit);
                        }
                        self.phase = FramePhase::LateDefault;
                    }
                    FramePhase::PrioritySize => {
                        self.phase = FramePhase::PriorityReferences;
                        if self.var == VarType::NonCustom(SingleNonCustomReference::LhUnits) {
                            return self.link(
                                VarType::NonCustom(SingleNonCustomReference::FontUnits),
                                LinkPurpose::PrioritySize,
                            );
                        }
                    }
                    FramePhase::PriorityReferences => {
                        let VarType::NonCustom(reference) = self.var else {
                            unreachable!()
                        };
                        let entry = references[reference]
                            .as_ref()
                            .and_then(|values| values.get(self.priority_cursor));
                        let Some((longhand, value)) = entry else {
                            self.phase = FramePhase::LateDefault;
                            continue;
                        };
                        let walk = self.walk.get_or_insert_with(|| {
                            ReferenceWalk::new(&value.variable_value.references)
                        });
                        match walk.resume(
                            &value.variable_value.url_data,
                            Some(value.substitution_property_id(*longhand)),
                            context,
                            attribute_tracker,
                            self.reference_reply.take(),
                        ) {
                            ReferenceWalkStep::Link(target) => {
                                return self.link(target, LinkPurpose::Reference);
                            }
                            ReferenceWalkStep::WrongReply => {
                                unreachable!("Frame owns its reference reply")
                            }
                            ReferenceWalkStep::Complete => {}
                        }
                        self.walk = None;
                        self.priority_cursor += 1;
                    }
                    FramePhase::LateDefault => {
                        self.phase = FramePhase::Close;
                        if let VarType::Custom(ref name) = self.var {
                            let cyclic = self.self_ref
                                || self.lowlink < self.index
                                || context.stack.last() != Some(&self.index);
                            if self.registered
                                && self.selected_dependency_eligible
                                && cyclic
                                && !self
                                    .value_non_custom_refs
                                    .intersects(ReferenceFlags::COLOR_SCHEME)
                                && invalid_custom_value_depends_on_color_scheme(
                                    name,
                                    context.stylist,
                                    context.computed_context,
                                )
                            {
                                return self.link(
                                    VarType::NonCustom(SingleNonCustomReference::ColorScheme),
                                    LinkPurpose::LateDefault,
                                );
                            }
                        }
                    }
                    FramePhase::Close => {
                        context.var_info[self.index].lowlink = self.lowlink;
                        if self.lowlink != self.index {
                            return FrameStep::Complete(VisitResult::SemanticOpen(self.index));
                        }
                        let mut in_loop = self.self_ref;
                        let mut members = SmallVec::<[usize; 5]>::new();
                        loop {
                            let index = context.stack.pop().expect("Frame's SCC remains owned");
                            let var = context.var_info[index].var.take().expect("Node pops once");
                            if index != self.index {
                                in_loop = true;
                            }
                            if in_loop {
                                context.var_info[index].publication.begin_cycle();
                                members.push(index);
                                context.handle_loop(&var);
                            }
                            if index == self.index {
                                assert_eq!(var, self.var);
                                break;
                            }
                        }
                        if in_loop {
                            for index in members {
                                context.var_info[index].publication.settle_cycle();
                                context.record_lookup_publication(index);
                            }
                            return FrameStep::Complete(VisitResult::CycleSettled);
                        }
                        let publication = match &self.var {
                            VarType::Custom(name) | VarType::Attr(name, _) => {
                                if let Some(prepared) = self.prepared_custom.take() {
                                    ClosedValue::Prepared(name.clone(), prepared)
                                } else {
                                    ClosedValue::Substitute(
                                        self.var.clone(),
                                        self.value.take().unwrap(),
                                    )
                                }
                            }
                            VarType::NonCustom(reference) => {
                                ClosedValue::Prioritary(reference.to_prioritary_id())
                            }
                        };
                        context.var_info[self.index].publication.close(publication);
                        self.phase = FramePhase::Publish;
                    }
                    FramePhase::Publish => {
                        context.import_priority_completion();
                        if self.var == VarType::NonCustom(SingleNonCustomReference::FontUnits)
                            && !context
                                .priority_completion
                                .complete
                                .contains(PrioritaryPropertyId::FontSize)
                            && context.deferred_size.is_none()
                            && context.frames.last().is_some_and(|parent| {
                                parent.accepts_computed_size(
                                    context.computed_context.is_root_element(),
                                )
                            })
                        {
                            if context.computed_size_ready(self.index) {
                                return FrameStep::ComputedSize;
                            }
                            if context.size_preparation.is_some()
                                || context.can_start_computed_size(self.index)
                            {
                                return FrameStep::Pending(Some(FontTarget::ComputedSize));
                            }
                        }
                        let demand = frame_font_demand(
                            self.registered,
                            self.value_non_custom_refs,
                            context.computed_context.is_root_element(),
                        );
                        match context.publication_readiness(
                            publication_ready,
                            demand,
                            next_unprepared_font_input(
                                context.decls,
                                &context.completed_font_inputs,
                            ),
                        ) {
                            PublicationDemand::Ready => {}
                            PublicationDemand::Metric(id) => {
                                return FrameStep::Pending(Some(FontTarget::Metric(id)));
                            }
                            PublicationDemand::Synthesis(id) => {
                                return FrameStep::Pending(Some(FontTarget::Synthesis(id)));
                            }
                            PublicationDemand::Unresolved => return FrameStep::Pending(None),
                        }
                        match context.publish_closed(self.index, attribute_tracker) {
                            ComputationStatus::Ready => {}
                            ComputationStatus::Pending => return FrameStep::Pending(None),
                            ComputationStatus::Prepare(longhand) => {
                                let id = PrioritaryPropertyId::from_longhand(longhand).unwrap();
                                return FrameStep::Pending(Some(FontTarget::Metric(id)));
                            }
                        }
                        return FrameStep::Complete(VisitResult::Complete);
                    }
                }
            }
        }
    }

    fn start_frame<'a, 'b, 'c, 'd>(
        var: VarType,
        context: &mut Context<'a, 'b, 'c, 'd>,
        attribute_tracker: &mut AttributeTracker,
    ) -> Result<TraversalFrame, VisitResult> {
        if let Some(result) = context.visited(&var) {
            return Err(result);
        }
        // Some shortcut checks.
        // The non-custom (font/line-height/color-scheme) dependencies of this value, carried out
        // of the match so we can create the corresponding nodes once we've pushed this variable.
        let mut value_non_custom_refs = ReferenceFlags::empty();
        let mut registered = false;
        let mut selected_dependency_eligible = false;
        let value = match var {
            VarType::Custom(ref name) | VarType::Attr(ref name, _) => {
                let map = &context.computed_context.builder.substitution_functions;
                let (registration, value, kind) = if matches!(var, VarType::Custom(..)) {
                    let registration = context.stylist.get_custom_property_registration(name);
                    (
                        registration,
                        match map
                            .get_var(registration, name)
                            .and_then(|value| value.as_universal())
                        {
                            Some(value) => value,
                            None => return Err(VisitResult::Complete),
                        },
                        SubstitutionFunctionKind::Var,
                    )
                } else {
                    // `attr()` is always treated as unregistered.
                    (
                        PropertyDescriptors::unregistered(),
                        match map
                            .get_attr(name, var.namespace().unwrap())
                            .and_then(|value| value.as_universal())
                        {
                            Some(value) => value,
                            None => return Err(VisitResult::Complete),
                        },
                        SubstitutionFunctionKind::Attr,
                    )
                };
                let is_root = context.computed_context.is_root_element();
                value_non_custom_refs = find_non_custom_references(registration, value, is_root);
                registered = !registration.is_universal();
                selected_dependency_eligible = registration.syntax.as_ref().is_some_and(|syntax| {
                    syntax.dependent_types().intersects(
                        crate::properties_and_values::syntax::data_type::DependentDataTypes::COLOR,
                    ) || syntax.components.iter().any(|component| {
                        use crate::properties_and_values::syntax::{
                            ComponentName, data_type::DataType,
                        };
                        matches!(component.name(), ComponentName::DataType(DataType::Image))
                    })
                });
                let has_dependency = value
                    .references
                    .flags
                    .intersects(ReferenceFlags::ATTR | ReferenceFlags::VAR)
                    || !value_non_custom_refs.is_empty();
                // Nothing to resolve.
                if !has_dependency {
                    debug_assert!(
                        !value.references.flags.intersects(ReferenceFlags::ENV),
                        "Should've been handled earlier"
                    );
                    if kind == SubstitutionFunctionKind::Attr || registered {
                        // We might still need to compute the value if this is not an universal
                        // registration but we thought it had a dependency during the cascade and it
                        // turned out not to. Note that if this was already computed we would've
                        // bailed out in the as_universal() check.
                        let value = value.clone();
                        substitute_references_if_needed_and_apply(
                            name,
                            var.namespace(),
                            &value,
                            context.stylist,
                            context.computed_context,
                            attribute_tracker,
                        );
                    }
                    context.record_lookup_value(&var);
                    return Err(VisitResult::Complete);
                }

                // Has this variable been visited?
                let index_map = if kind == SubstitutionFunctionKind::Var {
                    &mut context.index_map.var
                } else {
                    context
                        .index_map
                        .attr
                        .entry(var.namespace().unwrap().clone())
                        .or_default()
                };
                match index_map.entry_ref(name) {
                    EntryRef::Occupied(entry) => {
                        return Err(VisitResult::SemanticOpen(*entry.get()));
                    }
                    EntryRef::Vacant(entry) => {
                        entry.insert(context.count);
                    }
                }
                // Hold a strong reference to the value so that we don't
                // need to keep reference to context.map.
                Some(value.clone())
            }
            VarType::NonCustom(ref non_custom) => {
                let entry = &mut context.non_custom_index_map[*non_custom];
                if let Some(v) = entry {
                    return Err(VisitResult::SemanticOpen(*v));
                }
                *entry = Some(context.count);
                None
            }
        };

        // Add new entry to the information table.
        let index = context.count;
        context.count += 1;
        debug_assert_eq!(index, context.var_info.len());
        context.publication_names.push(var.clone());
        context.var_info.push(VarInfo {
            var: Some(var.clone()),
            lowlink: index,
            publication: NodePublication::SemanticOpen,
        });
        context.stack.push(index);

        let phase = if value.is_some() {
            FramePhase::References
        } else {
            FramePhase::PrioritySize
        };
        Ok(TraversalFrame {
            guarded_custom: None,
            var,
            index,
            lowlink: index,
            self_ref: false,
            registered,
            selected_dependency_eligible,
            value_non_custom_refs,
            value,
            prepared_custom: None,
            phase,
            walk: None,
            unit_links: SmallVec::new(),
            unit_cursor: 0,
            priority_cursor: 0,
            waiting: None,
            reference_reply: None,
        })
    }

    fn traverse<'a, 'b, 'c, 'd>(
        var: VarType,
        references_from_non_custom_properties: &NonCustomPropertyReferences,
        context: &mut Context<'a, 'b, 'c, 'd>,
        attribute_tracker: &mut AttributeTracker,
    ) -> VisitResult {
        if let Some(result) = context.visited(&var) {
            return result;
        }
        // Some shortcut checks.
        // The non-custom (font/line-height/color-scheme) dependencies of this value, carried out
        // of the match so we can create the corresponding nodes once we've pushed this variable.
        let mut value_non_custom_refs = ReferenceFlags::empty();
        let mut registered = false;
        let mut selected_dependency_eligible = false;
        let value = match var {
            VarType::Custom(ref name) | VarType::Attr(ref name, _) => {
                let map = &context.computed_context.builder.substitution_functions;
                let (registration, value, kind) = if matches!(var, VarType::Custom(..)) {
                    let registration = context.stylist.get_custom_property_registration(name);
                    (
                        registration,
                        match map
                            .get_var(registration, name)
                            .and_then(|value| value.as_universal())
                        {
                            Some(value) => value,
                            None => return VisitResult::Complete,
                        },
                        SubstitutionFunctionKind::Var,
                    )
                } else {
                    // `attr()` is always treated as unregistered.
                    (
                        PropertyDescriptors::unregistered(),
                        match map
                            .get_attr(name, var.namespace().unwrap())
                            .and_then(|value| value.as_universal())
                        {
                            Some(value) => value,
                            None => return VisitResult::Complete,
                        },
                        SubstitutionFunctionKind::Attr,
                    )
                };
                let is_root = context.computed_context.is_root_element();
                value_non_custom_refs = find_non_custom_references(registration, value, is_root);
                registered = !registration.is_universal();
                selected_dependency_eligible = registration.syntax.as_ref().is_some_and(|syntax| {
                    syntax.dependent_types().intersects(
                        crate::properties_and_values::syntax::data_type::DependentDataTypes::COLOR,
                    ) || syntax.components.iter().any(|component| {
                        use crate::properties_and_values::syntax::{
                            ComponentName, data_type::DataType,
                        };
                        matches!(component.name(), ComponentName::DataType(DataType::Image))
                    })
                });
                let has_dependency = value
                    .references
                    .flags
                    .intersects(ReferenceFlags::ATTR | ReferenceFlags::VAR)
                    || !value_non_custom_refs.is_empty();
                // Nothing to resolve.
                if !has_dependency {
                    debug_assert!(
                        !value.references.flags.intersects(ReferenceFlags::ENV),
                        "Should've been handled earlier"
                    );
                    if kind == SubstitutionFunctionKind::Attr || registered {
                        // We might still need to compute the value if this is not an universal
                        // registration but we thought it had a dependency during the cascade and it
                        // turned out not to. Note that if this was already computed we would've
                        // bailed out in the as_universal() check.
                        let value = value.clone();
                        substitute_references_if_needed_and_apply(
                            name,
                            var.namespace(),
                            &value,
                            context.stylist,
                            context.computed_context,
                            attribute_tracker,
                        );
                    }
                    context.record_lookup_value(&var);
                    return VisitResult::Complete;
                }

                // Has this variable been visited?
                let index_map = if kind == SubstitutionFunctionKind::Var {
                    &mut context.index_map.var
                } else {
                    context
                        .index_map
                        .attr
                        .entry(var.namespace().unwrap().clone())
                        .or_default()
                };
                match index_map.entry_ref(name) {
                    EntryRef::Occupied(entry) => {
                        return VisitResult::SemanticOpen(*entry.get());
                    }
                    EntryRef::Vacant(entry) => {
                        entry.insert(context.count);
                    }
                }
                // Hold a strong reference to the value so that we don't
                // need to keep reference to context.map.
                Some(value.clone())
            }
            VarType::NonCustom(ref non_custom) => {
                let entry = &mut context.non_custom_index_map[*non_custom];
                if let Some(v) = entry {
                    return VisitResult::SemanticOpen(*v);
                }
                *entry = Some(context.count);
                None
            }
        };

        // Add new entry to the information table.
        let index = context.count;
        context.count += 1;
        debug_assert_eq!(index, context.var_info.len());
        context.publication_names.push(var.clone());
        context.var_info.push(VarInfo {
            var: Some(var.clone()),
            lowlink: index,
            publication: NodePublication::SemanticOpen,
        });
        context.stack.push(index);

        let mut self_ref = false;
        let mut lowlink = index;
        let mut prepared_custom = None;
        if let Some(v) = value.as_ref() {
            debug_assert!(
                matches!(var, VarType::Custom(_) | VarType::Attr(..)),
                "Non-custom property has references?"
            );

            let property_id = match &var {
                VarType::Custom(name) | VarType::Attr(name, _) => Some(PropertyIdRef::from(name)),
                VarType::NonCustom(_) => unreachable!(),
            };
            // Visit the references in this value...
            visit_value_references(
                &v.references,
                &v.url_data,
                property_id,
                index,
                references_from_non_custom_properties,
                context,
                &mut lowlink,
                &mut self_ref,
                attribute_tracker,
                &mut value_non_custom_refs,
            );

            if let VarType::Custom(ref name) = var
                && selected_dependency_eligible
            {
                let may_compute_color =
                    value_non_custom_refs.intersects(ReferenceFlags::COLOR_SCHEME);
                value_non_custom_refs.remove(ReferenceFlags::COLOR_SCHEME);
                if registered
                    && may_compute_color
                    && lowlink == index
                    && !self_ref
                    && context.stack.last() == Some(&index)
                {
                    let prepared = prepare_custom_value(
                        name,
                        v,
                        context.stylist,
                        context.computed_context,
                        attribute_tracker,
                    );
                    if prepared.depends_on_color_scheme() {
                        value_non_custom_refs |= ReferenceFlags::COLOR_SCHEME;
                    }
                    prepared_custom = Some(prepared);
                }
            }

            // ... Then the non-custom properties this value depends on (font-size, line-height,
            // color-scheme), as computed by `find_non_custom_references` above.
            let is_root = context.computed_context.is_root_element();
            if registered && !value_non_custom_refs.is_empty() {
                value_non_custom_refs.for_each_non_custom(is_root, |r| {
                    visit_link(
                        VarType::NonCustom(r),
                        index,
                        references_from_non_custom_properties,
                        context,
                        &mut lowlink,
                        &mut self_ref,
                        attribute_tracker,
                    );
                });
            }
        } else if let VarType::NonCustom(non_custom) = var {
            // line-height's resolution depends on font-size's, so its node has a graph edge to the
            // font-size node. This is needed for cycle detection (not just application order, which
            // `prioritary_property_dependencies(LineHeight)` handles): it puts the line-height node
            // in the same strongly-connected component as a font-size<->custom cycle, so the node
            // doesn't apply line-height (and, transitively, font-size) before that cycle is
            // removed.
            //
            // TODO(emilio): I think the right fix for this is
            // s/SingleNonCustomReference/PrioritaryPropertyId in VarType::NonCustom.
            if non_custom == SingleNonCustomReference::LhUnits {
                visit_link(
                    VarType::NonCustom(SingleNonCustomReference::FontUnits),
                    index,
                    references_from_non_custom_properties,
                    context,
                    &mut lowlink,
                    &mut self_ref,
                    attribute_tracker,
                );
            }
            let entry = &references_from_non_custom_properties[non_custom];
            if let Some(values) = entry.as_ref() {
                for (longhand_id, value) in values {
                    // Traverse the non-custom property's declaration value(s), creating edges to
                    // the custom properties they reference (directly or through a used fallback)
                    // that might cycle back to this node. Note we traverse unregistered/universal
                    // references too: while their own font-relative units are textual (resolved
                    // against the parent, see `find_non_custom_references`), they may chain to a
                    // registered property that does cycle back.
                    let property_id = value.substitution_property_id(*longhand_id);
                    let value = &value.variable_value;
                    visit_value_references(
                        &value.references,
                        &value.url_data,
                        Some(property_id),
                        index,
                        references_from_non_custom_properties,
                        context,
                        &mut lowlink,
                        &mut self_ref,
                        attribute_tracker,
                        &mut Default::default(),
                    );
                }
            }
        }

        if let VarType::Custom(ref name) = var {
            let cyclic = self_ref || lowlink < index || context.stack.last() != Some(&index);
            if registered
                && selected_dependency_eligible
                && cyclic
                && !value_non_custom_refs.intersects(ReferenceFlags::COLOR_SCHEME)
                && invalid_custom_value_depends_on_color_scheme(
                    name,
                    context.stylist,
                    context.computed_context,
                )
            {
                visit_link(
                    VarType::NonCustom(SingleNonCustomReference::ColorScheme),
                    index,
                    references_from_non_custom_properties,
                    context,
                    &mut lowlink,
                    &mut self_ref,
                    attribute_tracker,
                );
            }
        }

        context.var_info[index].lowlink = lowlink;
        if lowlink != index {
            // This variable is in a loop, but it is not the root of this strong connected
            // component. We simply return for now, and the root would remove it from the map.
            //
            // This cannot be removed from the map here, because otherwise the shortcut check at the
            // beginning of this function would return the wrong value.
            return VisitResult::SemanticOpen(index);
        }

        // This is the root of a strong-connected component.
        let mut in_loop = self_ref;
        let mut cycle_members = SmallVec::<[usize; 5]>::new();
        loop {
            let var_index = context
                .stack
                .pop()
                .expect("The current variable should still be in stack");
            let var_info = &mut context.var_info[var_index];
            // We should never visit the variable again, so it's safe to take the name away.
            let var_name = var_info
                .var
                .take()
                .expect("Variable should not be popped from stack twice");
            if var_index != index {
                // Anything here is in a loop which can traverse to the node we are handling, so
                // it's invalid at computed-value time.
                in_loop = true;
            }
            if in_loop {
                context.var_info[var_index].publication.begin_cycle();
                cycle_members.push(var_index);
                context.handle_loop(&var_name);
            }
            if var_index == index {
                debug_assert_eq!(var_name, var);
                break;
            }
        }

        if in_loop {
            for member in cycle_members {
                context.var_info[member].publication.settle_cycle();
                context.record_lookup_publication(member);
            }
            return VisitResult::CycleSettled;
        }

        let publication = match var {
            VarType::Custom(ref name) | VarType::Attr(ref name, _) => {
                if let Some(prepared) = prepared_custom {
                    ClosedValue::Prepared(name.clone(), prepared)
                } else {
                    ClosedValue::Substitute(
                        var,
                        value.expect("Custom and attr nodes retain their value"),
                    )
                }
            }
            VarType::NonCustom(non_custom) => {
                ClosedValue::Prioritary(non_custom.to_prioritary_id())
            }
        };
        context.var_info[index].publication.close(publication);
        assert_eq!(
            context.publish_closed(index, attribute_tracker),
            ComputationStatus::Ready
        );
        VisitResult::Complete
    }

    let lookup_bindings = InitializedCustomBindings::new(seen, computed_context);
    let mut context = Context {
        lookup_bindings,
        publication_names: Vec::new(),
        settled_attributes: FxHashMap::default(),
        environment_inputs: Vec::new(),
        metric_lookup: None,
        lookup_reply: None,
        count: 0,
        index_map: OrderIndexMap::default(),
        non_custom_index_map: NonCustomReferenceMap::default(),
        stack: SmallVec::new(),
        var_info: SmallVec::new(),
        frames: Vec::new(),
        frame_root: None,
        frame_reply: None,
        priority_completion,
        metric_drain: MetricDrain::new(decls),
        metric_action: None,
        metric_references: None,
        font_preparation: None,
        size_preparation: None,
        size_node: None,
        size_identity: Arc::new(()),
        deferred_size: None,
        finished_root: None,
        completed_font_inputs: LonghandIdSet::default(),
        font_completion_flags: None,
        stylist,
        computed_context: &mut *computed_context,
        cascade: &mut *cascade,
        decls,
        cache: &mut *shorthand_cache,
    };
    let mut first = true;
    let mut run_one = |var: VarType| {
        if !first {
            context.reset();
        }
        first = false;
        let use_retained_frames = true;
        let result = if use_retained_frames {
            loop {
                let result = context.poll_root(
                    var.clone(),
                    references_from_non_custom_properties,
                    attr_tracker,
                    &mut font_publication_demand,
                );
                if !matches!(result, VisitResult::ComputationPending(_)) {
                    break result;
                }
                let Some(action) = context.pending_metric_action() else {
                    break result;
                };
                match context.drive_metric_action(
                    &action,
                    references_from_non_custom_properties,
                    attr_tracker,
                    &mut font_publication_demand,
                ) {
                    MetricActionProgress::Published(_) | MetricActionProgress::AlreadyComplete => {}
                    progress => {
                        let label = match &progress {
                            MetricActionProgress::ComputedSizeReadset => "ComputedSizeReadset",
                            MetricActionProgress::GeneratedPrerequisite(id) => {
                                eprintln!(
                                    "CSS_MINIMUM_PENDING prerequisite={:?}",
                                    id.to_longhand()
                                );
                                "GeneratedPrerequisite"
                            }
                            MetricActionProgress::References(id, _) => {
                                eprintln!("CSS_MINIMUM_PENDING references={:?}", id);
                                "References"
                            }
                            MetricActionProgress::Lookup(id, _, request) => {
                                eprintln!(
                                    "CSS_MINIMUM_PENDING lookup={:?} kind={:?} name={:?}",
                                    id, request.kind, request.name
                                );
                                "Lookup"
                            }
                            MetricActionProgress::Invalidated => "Invalidated",
                            MetricActionProgress::Unsupported => "Unsupported",
                            MetricActionProgress::WrongAction => "WrongAction",
                            MetricActionProgress::Published(_)
                            | MetricActionProgress::AlreadyComplete => unreachable!(),
                        };
                        eprintln!(
                            "CSS_MINIMUM_PENDING progress={} action_root={:?} owner={:?} index={} target={:?}",
                            label, action.root, action.owner, action.index, action.prerequisite
                        );
                        break result;
                    }
                }
            }
        } else {
            traverse(
                var,
                references_from_non_custom_properties,
                &mut context,
                attr_tracker,
            )
        };
        if !matches!(result, VisitResult::Complete | VisitResult::CycleSettled) {
            eprintln!(
                "CSS_MINIMUM_PENDING result={:?} root={:?} frames={} stack={:?} action={} lookup={} references={} size_node={:?} facet={} deferred={} finished={:?}",
                result,
                context.frame_root,
                context.frames.len(),
                context.stack,
                context.metric_action.is_some(),
                context.metric_lookup.is_some(),
                context.metric_references.is_some(),
                context.size_node,
                context.priority_completion.computed_size.is_some(),
                context.deferred_size.is_some(),
                context.finished_root
            );
            if let Some(lookup) = context.metric_lookup.as_ref() {
                eprintln!(
                    "CSS_MINIMUM_PENDING retained_lookup={:?} kind={:?} name={:?} depth={} floor={}",
                    lookup.longhand,
                    lookup.request.kind,
                    lookup.request.name,
                    lookup.depth,
                    lookup.semantic_floor
                );
            }
            for frame in &context.frames {
                let phase = match frame.phase {
                    FramePhase::References => "References",
                    FramePhase::Prepare => "Prepare",
                    FramePhase::Units => "Units",
                    FramePhase::PrioritySize => "PrioritySize",
                    FramePhase::PriorityReferences => "PriorityReferences",
                    FramePhase::LateDefault => "LateDefault",
                    FramePhase::Close => "Close",
                    FramePhase::Publish => "Publish",
                };
                eprintln!(
                    "CSS_MINIMUM_PENDING frame={:?} index={} lowlink={} phase={} registered={} waiting={:?}",
                    frame.var,
                    frame.index,
                    frame.lowlink,
                    phase,
                    frame.registered,
                    frame.waiting.as_ref().map(|(var, _)| var)
                );
            }
            if let Some(states) = context.size_preparation.as_ref() {
                eprintln!(
                    "CSS_MINIMUM_PENDING size_preparation={} size_omitted={} size_complete={} size_waiting={} text_scale_complete={} text_scale_waiting={} family={}",
                    states.index,
                    states.operation().is_none(),
                    states.size.complete,
                    states.size.waiting.is_some(),
                    states.text_scale.complete,
                    states.text_scale.waiting.is_some(),
                    states.family.is_some()
                );
                for state in [&states.size, &states.text_scale]
                    .into_iter()
                    .chain(states.family.iter())
                {
                    eprintln!(
                        "CSS_MINIMUM_PENDING selection={:?} complete={} waiting={} cursor={:?} prepared={} flags_unchanged={}",
                        state.longhand,
                        state.complete,
                        state.waiting.is_some(),
                        state.cursor,
                        state.prepared.len(),
                        state.observed_flags == context.computed_context.included_cascade_flags
                    );
                }
            }
            for id in [
                PrioritaryPropertyId::FontSize,
                PrioritaryPropertyId::FontFamily,
                PrioritaryPropertyId::Appearance,
                PrioritaryPropertyId::XLang,
                PrioritaryPropertyId::XTextScale,
                PrioritaryPropertyId::MozMinFontSizeRatio,
                PrioritaryPropertyId::Zoom,
            ] {
                eprintln!(
                    "CSS_MINIMUM_PENDING priority={:?} complete={} active={} claimed={} ensured={} seen={}",
                    id.to_longhand(),
                    context.priority_completion.complete.contains(id),
                    context.priority_completion.active.contains(id),
                    context.priority_completion.claimed.contains(id),
                    context.cascade.ensured_prioritary.contains(id),
                    context.cascade.seen.longhands.contains(id.to_longhand())
                );
            }
        }
        assert!(matches!(
            result,
            VisitResult::Complete | VisitResult::CycleSettled
        ));
    };
    // Note that `seen` doesn't contain names inherited from our parent, but
    // those can't have variable references (since we inherit the computed
    // variables) so we don't want to spend cycles traversing them anyway.
    for (var, has_refs) in &seen.var {
        if !has_refs {
            continue;
        }
        run_one(VarType::Custom((*var).clone()));
    }
    // Traverse potentially untraversed chained references from `attr(type())` in non-custom
    // properties.
    for (namespace, attributes) in &seen.attr {
        for attr in attributes {
            run_one(VarType::Attr((*attr).clone(), (*namespace).clone()));
        }
    }
    assert!(context.stack.is_empty());
    assert!(
        context.priority_completion.active.is_empty()
            && context.priority_completion.claimed.is_empty()
    );
    assert!(
        context
            .var_info
            .iter()
            .all(|info| info.publication.can_retire())
    );
}
