from pathlib import Path
import hashlib
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
base=ROOT/'artifacts/css-registered-selected-color-dependency-proposal-v5/base/servo/components/style'
candidate=ROOT/'artifacts/css-registered-selected-color-dependency-proposal-v5/candidate/servo/components/style'
image=ROOT/'artifacts/css-registered-image-only-dependency-proposal-v1/candidate/servo/components/style/properties/cascade.rs'
excerpts={}
def section(label,path,start,end):
    source=path.read_text();a=source.index(start);b=source.index(end,a);body=source[a:b]
    excerpts[label]={'source':str(path.relative_to(ROOT)),'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'excerpt_sha256':hashlib.sha256(body.encode()).hexdigest(),'text':body}
section('base-admission',base/'properties/cascade.rs','fn find_non_custom_references(','/// Resolves the custom properties')
section('combined-admission',candidate/'properties/cascade.rs','fn find_non_custom_references(','/// Resolves the custom properties')
section('image-only-admission',image,'fn registration_needs_image_dependencies(','/// Resolves the custom properties')
section('nested-token-recursion',base/'custom_properties.rs','        macro_rules! nested {','        if let Some(index) = prev_reference_index.take()')
section('dimension-unit-flags',base/'custom_properties.rs','                if matches!(token, Token::Dimension { .. }) {','                let is_unquoted_url')
section('font-lh-unit-mapping',base/'custom_properties.rs','    fn from_unit(value: &CowRcStr) -> Self {','        if value.eq_ignore_ascii_case(NoCalcLength::RLH)')
section('flag-bit-and-node-mapping',base/'custom_properties.rs','pub struct ReferenceFlags(u8);','    fn from_unit(value: &CowRcStr)')
section('root-and-resolved-reference-flags',base/'properties/cascade.rs',"    fn visit_value_references<'a",'    fn visit_link')
section('combined-preparation-and-units',candidate/'properties/cascade.rs','        let mut prepared_custom = None;','        } else if let VarType::NonCustom(non_custom) = var')
section('noncustom-before-custom-application',candidate/'properties/cascade.rs','        // Not in a loop, apply the value.','    let mut context = Context {')
section('base-early-computation',base/'properties/cascade.rs','        let has_references = match value {','                let value = ComputedRegisteredValue::universal')
section('noncustom-priority-mapping',base/'custom_properties.rs','pub enum SingleNonCustomReference {','/// A map from NonCustomReferenceMap')
section('ensure-priority-before-computation',candidate/'properties/cascade.rs','    fn ensure_prioritary_property(','    /// Cascade a given custom property declaration.')
section('admitted-image-syntax-dependencies',ROOT/'artifacts/css-registered-image-data-type-source-v1/data_type.rs','    pub fn dependent_types(&self) -> DependentDataTypes {','impl ToCss for DataType')
section('historical-union-syntax-dependencies',ROOT/'artifacts/css-contextual-easing-servo-closure-v4/baseline/servo/components/style/properties_and_values/syntax/mod.rs','    pub fn dependent_types(&self) -> DependentDataTypes {','impl ToCss for Descriptor')
(HERE/'EXCERPTS.json').write_text(json.dumps(excerpts,indent=2)+'\n')
refs={}
for name in set(e['source'] for e in excerpts.values()) | {'artifacts/css-registered-image-data-type-source-v1/SOURCE.json','artifacts/css-registered-image-only-dependency-proposal-v1/FILES.json','artifacts/css-registered-selected-color-dependency-proposal-v5/FILES.json','artifacts/css-registered-image-unit-probe-v1/FILES.json','artifacts/css-registered-image-unit-probe-v1/tests/css/css-properties-values-api/registered-image-font-dependencies.tentative.html'}:
    body=(ROOT/name).read_bytes();refs[name]={'sha256':hashlib.sha256(body).hexdigest(),'bytes':len(body)}
(HERE/'REFERENCES.json').write_text(json.dumps(refs,indent=2,sort_keys=True)+'\n')
print(json.dumps({'excerpts':len(excerpts),'refs':len(refs)}))
