#![allow(dead_code)]
pub fn normalize(v: f32) -> f32 {
    if v.is_nan() { 0.0 } else { v }
}
struct Number(f32);
impl Number {pub fn get(&self) -> f32 {
        normalize(self.0).min(f32::MAX).max(f32::MIN)
    }}
#[derive(Clone,Copy,Debug)] enum Mode { All, NonNegative, AtLeastOne, ZeroToOne }
impl Mode {pub fn clamp(&self, val: f32) -> f32 {
            match *self {
                Self::All => val,
                Self::NonNegative => val.max(0.),
                Self::AtLeastOne => val.max(1.),
                Self::ZeroToOne => val.clamp(0., 1.),
            }
        }}
fn round_head90(value:f32)->i32 { (value + 0.5).floor() as i32 }
fn context_head90(raw:f32, mode:Mode)->i32 { let value=mode.clamp(Number(raw).get()); let clamped=normalize(value).min(f32::MAX).max(f32::MIN); (clamped + 0.5).floor() as i32 }
fn round_118(value:f32)->i32 { (f64::from(value) + 0.5).floor() as i32 }
fn context_118(raw:f32, mode:Mode)->i32 { let value=mode.clamp(Number(raw).get()); let clamped=normalize(value).min(f32::MAX).max(f32::MIN); (f64::from(clamped) + 0.5).floor() as i32 }
fn main(){ for bits in [0u32,1u32,8388607u32,8388608u32,1056629063u32,1056629064u32,1056629065u32,1056964607u32,1056964608u32,1056964609u32,1065353215u32,1065353216u32,1065353217u32,1069463633u32,1069463634u32,1069463635u32,1069547519u32,1069547520u32,1069547521u32,1075838975u32,1075838976u32,1075838977u32,1258291200u32,1258291201u32,1258291202u32,1325400063u32,1325400064u32,1325400065u32,2139095039u32,2139095040u32,2141192193u32,2143289344u32,2147483648u32,2147483649u32,2155872255u32,2155872256u32,3204448255u32,3204448256u32,3204448257u32,3212836863u32,3212836864u32,3212836865u32,3217031167u32,3217031168u32,3217031169u32,3223322623u32,3223322624u32,3223322625u32,3240099839u32,3240099840u32,3240099841u32,3405774848u32,3405774849u32,3405774850u32,3472883711u32,3472883712u32,3472883713u32,4286578687u32,4286578688u32,4290772992u32] { let raw=f32::from_bits(bits); for mode in [Mode::All,Mode::NonNegative,Mode::AtLeastOne,Mode::ZeroToOne] { let got=Number(raw).get(); let clamped=mode.clamp(got);println!("head90 {bits:08x} {mode:?} {} {} {}",round_head90(got),round_head90(clamped),context_head90(raw,mode));println!("118 {bits:08x} {mode:?} {} {} {}",round_118(got),round_118(clamped),context_118(raw,mode));}}}
