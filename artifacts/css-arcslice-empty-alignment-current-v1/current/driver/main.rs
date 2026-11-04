use style_traits::arc_slice::ArcSlice;
#[repr(align(64))]
struct High([u8;64]);
fn normal(iter:bool) {
 let value:ArcSlice<u64>=if iter {ArcSlice::from_iter(std::iter::empty())}else{ArcSlice::default()};
 println!("constructed normal");assert_eq!(value.len(),0);println!("read zero");drop(value);println!("dropped normal");
}
fn high(iter:bool,read:bool) {
 let value:ArcSlice<High>=if iter {ArcSlice::from_iter(std::iter::empty())}else{ArcSlice::default()};
 println!("constructed high");if read {assert_eq!(value.len(),0);println!("read zero");}drop(value);println!("dropped high");
}
fn main() {
 let args:Vec<_>=std::env::args().collect();assert_eq!(cfg!(debug_assertions),args[2]=="on");println!("debug_assertions={}",cfg!(debug_assertions));
 match args[1].as_str() {"normal-default"=>normal(false),"normal-empty"=>normal(true),"high-default-read"=>high(false,true),"high-empty-read"=>high(true,true),"high-default-drop"=>high(false,false),"high-empty-drop"=>high(true,false),_=>panic!()}
}
