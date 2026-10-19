import hashlib
import json
from pathlib import Path
BASE=Path(__file__).resolve().parent

def body(text, marker, after=None):
    offset=text.index(after) if after else 0
    start=text.index(marker,offset)
    opening=text.index("{",start)
    depth=1
    end=opening+1
    while depth:
        depth+=(text[end]=="{")-(text[end]=="}")
        end+=1
    return text[start:end]

def generate(out, variant="candidate"):
    out.mkdir(parents=True,exist_ok=True)
    records=[]
    def get(path, marker, after=None):
        root="candidate" if path.endswith("specified/length.rs") and variant=="candidate" else "source"
        src=BASE/root/path
        text=body(src.read_text(),marker,after)
        records.append({"path":str(src.relative_to(BASE)),"source_sha256":hashlib.sha256(src.read_bytes()).hexdigest(),"marker":marker,"after":after,"text_sha256":hashlib.sha256(text.encode()).hexdigest(),"text":text,"adaptations":[]})
        return text
    cpp=[]
    def c(path,marker): cpp.append(get(path,marker))
    c("xpcom/ds/nsMathUtils.h","inline int32_t NS_lroundf(")
    c("gfx/src/nsCoord.h","inline int32_t NSToIntRound(float")
    c("gfx/src/nsCoord.h","inline nscoord NSToCoordRound(float")
    h="layout/style/ServoStyleConstsInlines.h"
    for marker in ["bool StyleCSSPixelLength::IsZero()","void StyleCSSPixelLength::ScaleBy(","StyleCSSPixelLength StyleCSSPixelLength::ScaledBy("]:
        c(h,marker)
    cpp.append("namespace detail {\n"+get(h,"static inline nscoord DefaultLengthToAppUnits(")+"\n}")
    c(h,"nscoord StyleCSSPixelLength::ToAppUnits()")
    c(h,"inline float StyleZoom::Unzoom(float")
    for marker in ["static nscoord GetNormalLineHeight(","static inline nscoord ComputeLineHeight(","nscoord ReflowInput::CalcLineHeight(const StyleLineHeight&"]:
        c("layout/generic/ReflowInput.cpp",marker)
    c("layout/style/GeckoBindings.cpp","nscoord Gecko_CalcLineHeight(")
    c("layout/style/nsComputedDOMStyle.cpp","void nsComputedDOMStyle::SetValueToPixels(")
    (out/"provider.inc").write_text("\n\n".join(cpp)+"\n")
    rs=[]
    rs.append("mod values { use super::*;\n"+get("servo/components/style/values/mod.rs","pub fn normalize(")+"\n}")
    def impl(name,parts): rs.append("impl "+name+" {\n"+"\n".join(parts)+"\n}\n")
    impl("Zoom",[get("servo/components/style/values/computed/box.rs",m) for m in ["pub fn zoom(self, value: f32)","pub fn unzoom(self, value: f32)"]])
    lh="servo/components/style/values/computed/length.rs"
    impl("CSSPixelLength",[get(lh,m) for m in ["pub fn finite(self)","pub fn zoom(self, zoom: Zoom)","pub fn px(self)"]])
    rs.append("impl std::ops::Mul<f32> for CSSPixelLength { type Output=Self;\n"+get(lh,"fn mul(self, other: CSSFloat)")+"\n}")
    impl("CSSPixelLength",[get(lh,"fn to_resolved_value(self, context: &ResolvedContext)").replace("Self::ResolvedValue","Self")])
    records[-1]["adaptations"]=["Associated trait return alias Self::ResolvedValue replaced by identical concrete Self; body unchanged"]
    impl("Au",[get("third_party/rust/app_units/src/app_unit.rs",m) for m in ["pub fn to_f32_px(self)","pub fn from_f32_px(px:","pub fn from_f64_au(float:"]])
    impl("FontSize",[get("servo/components/style/values/computed/font.rs",m) for m in ["pub fn computed_size(&self)","pub fn used_size(&self)","pub fn zoom(&self, zoom: Zoom)"]])
    impl("FontBaseSize",[get("servo/components/style/values/specified/length.rs","pub fn resolve(&self, context: &Context)","impl FontBaseSize")])
    impl("Builder",[get("servo/components/style/properties/properties.mako.rs","pub fn calc_line_height(")])
    impl("Device",[get("servo/components/style/device/gecko.rs","pub fn calc_line_height(")]+[get("servo/components/style/device/mod.rs",m) for m in ["pub fn root_line_height(&self)","pub fn set_root_line_height(&self, size: f32)"]])
    impl("NoCalcLength",[get("servo/components/style/values/specified/length.rs",m) for m in ["fn font_relative_to_computed_value(","fn reference_font_size_and_length(","pub fn to_computed_value_with_base_size("]])
    rs.append(get("servo/components/style/values/specified/font.rs","fn resolve_line_height_length("))
    pub=get("servo/components/style/matching.rs","if line_height_likely_changed {","// Update root line height for rlh units")
    records[-1]["adaptations"]=["Complete guarded publication block wrapped in publish(adapter arguments); scheduling/enclosing finish_restyle retained as external provider"]
    rs.append("fn publish(device:&Device,new_primary_style:&Builder,line_height_likely_changed:bool) {\n"+pub+"\n}")
    raw_rs="\n".join(rs)
    (out/"style.raw.inc").write_text(raw_rs)
    instruments=[
      ("pub fn zoom(self, value: f32) -> f32 {", "capsule_trace(30,0,value,self.value());"),
      ("pub fn unzoom(self, value: f32) -> f32 {", "capsule_trace(32,0,value,self.value());"),
      ("fn mul(self, other: CSSFloat) -> Self {", "capsule_trace(31,0,self.px(),other);"),
      ("pub fn root_line_height(&self) -> Length {", "capsule_trace(40,self.owner,f32::from_bits(self.root_line_height.load(Ordering::Relaxed)),0.0);"),
      ("pub fn set_root_line_height(&self, size: f32) {", "capsule_trace(41,self.owner,size,0.0);"),
    ]
    for marker,code in instruments:
      assert raw_rs.count(marker)==1,marker
      raw_rs=raw_rs.replace(marker,marker+"\n"+code)
    (out/"instrumentation.json").write_text(json.dumps(instruments,indent=2)+"\n")
    (out/"style.inc").write_text(raw_rs)
    (out/"extraction.json").write_text(json.dumps(records,indent=2)+"\n")
    boundaries=[]
    for path,marker,after,contract in [
      ("servo/components/style/values/specified/font.rs","fn to_computed_value(&self, context: &Context)","impl ToComputedValue for FontSize", "The inherited/inherited base pair reaches FontSize::to_computed_value_against; full cascade, calc and text-zoom scheduling remain external. Fixture pairs execute the complete length selector."),
      ("servo/components/style/values/specified/font.rs","fn to_computed_value(&self, context: &Context)","impl ToComputedValue for LineHeight", "Percentage branch dispatches an Em coefficient to extracted resolve_line_height_length. Its complete small resolver runs; parser/calc dispatch remains external."),
      ("servo/components/style/values/specified/length.rs","fn to_computed_value(&self, context: &Context)","impl ToComputedValue for NoCalcLength", "Ordinary length caller supplies current/current bases. Complete called selector is extracted."),
      ("servo/components/style/matching.rs","fn finish_restyle(",None,"Enclosing scheduling and root admission external; complete guarded root publication block extracted."),
      ("servo/components/style/matching.rs","fn line_height_likely_changed(",None,"Scheduling predicate retained, not proven. Freshness premise requires actual publication before cached read."),
    ]:
        source=BASE/'source'/path
        text=body(source.read_text(),marker,after)
        boundaries.append(dict(path='source/'+path,marker=marker,after=after,source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),text=text,text_sha256=hashlib.sha256(text.encode()).hexdigest(),contract=contract,compiled=False))
    (out/'caller-boundaries.json').write_text(json.dumps(boundaries,indent=2)+'\n')
    return records

if __name__=="__main__":
    import sys
    generate(Path(sys.argv[1]),sys.argv[2] if len(sys.argv)>2 else "candidate")
