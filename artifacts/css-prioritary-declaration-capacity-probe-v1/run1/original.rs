
trait Array { type Item; }
impl<T, const N: usize> Array for [T; N] { type Item = T; }
type SmallVec<A> = Vec<<A as Array>::Item>;
mod property_counts { pub const PRIORITARY: usize = 1; }
#[derive(Clone, Copy)]
enum PropertyDeclaration { FontSize(u32), Color }
#[derive(Clone, Copy)]
enum LonghandId { FontSize, Color }
#[derive(Clone, Copy)]
enum PrioritaryPropertyId { FontSize }
impl PrioritaryPropertyId {
    fn from_longhand(id: LonghandId) -> Option<Self> {
        match id { LonghandId::FontSize => Some(Self::FontSize), LonghandId::Color => None }
    }
}
type CascadePriority = u8;
/// We track the index only for prioritary properties. For other properties we can just iterate.
type DeclarationIndex = u16;

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

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let count: usize = args[1].parse().unwrap();
    let first = args[2] == "first";
    let font = PropertyDeclaration::FontSize(37);
    let color = PropertyDeclaration::Color;
    let mut declarations = Declarations::default();
    if first { declarations.note_declaration(&font, 0, LonghandId::FontSize); }
    for _ in 0..count { declarations.note_declaration(&color, 0, LonghandId::Color); }
    if !first { declarations.note_declaration(&font, 0, LonghandId::FontSize); }
    let expected: Vec<u32> = declarations.longhand_declarations.iter().filter_map(|entry| {
        match entry.decl { PropertyDeclaration::FontSize(value) => Some(*value), _ => None }
    }).collect();
    let mut indexed = Vec::new();
    let mut index = declarations.prioritary_positions[0].most_important;
    if index != DeclarationIndex::MAX {
        loop {
            let entry = declarations.longhand_declarations[index as usize];
            if let PropertyDeclaration::FontSize(value) = entry.decl { indexed.push(*value); }
            if entry.next_index == 0 { break; }
            assert!(entry.next_index > index);
            index = entry.next_index;
        }
    }
    assert_eq!(expected, vec![37]);
    println!("unrelated={count} position={} indexed={indexed:?} expected={expected:?}", args[2]);
    assert_eq!(indexed, expected, "unrelated properties must not remove the sole font-size declaration");
}
