use icu_provider::{DataProvider,DataRequest};
use icu_segmenter::provider::{Baked,SegmenterBreakLineV1};
fn main(){
 let response=<Baked as DataProvider<SegmenterBreakLineV1>>::load(&Baked,DataRequest::default()).unwrap();
 let table=&response.payload.get().property_table;
 let mut count=0;let mut beyond=0;let mut first=None;let mut last=0;
 for value in 0..=0x10ffff {
  if let Some(ch)=char::from_u32(value){
   if table.get(ch)==46 {count+=1;if value>0xffff{beyond+=1;}if first.is_none(){first=Some(value);}last=value;}
   else if let Some(start)=first.take(){println!("RANGE {start:X} {last:X}");}
  }
 }
 if let Some(start)=first{println!("RANGE {start:X} {last:X}");}
 println!("SUMMARY {count} {beyond}");
 for value in [10,0xe01,0x116d0,0x116ff] {println!("POINT {value:X} {}",table.get(char::from_u32(value).unwrap()));}
}
