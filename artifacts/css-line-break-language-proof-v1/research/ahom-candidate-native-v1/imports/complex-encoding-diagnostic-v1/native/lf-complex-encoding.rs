use icu_segmenter::{LineSegmenter,options::{LineBreakOptions,LineBreakWordOption}};
fn main(){
 let fixtures=[("thai-ahom-thai",vec![0xe01,0x11700,0xe01]),("ahom-thai-ahom",vec![0x11700,0xe01,0x11700]),("two-ahom",vec![0xe01,0x11700,0x11701,0xe01]),("thai-pairs",vec![0xe01,0xe02,0x11700,0xe01,0xe02]),("bmp-unknown",vec![0xe01,0x1950,0xe01]),("ahom-only",vec![0x11700,0x11701,0x11702])];
 for (name,scalars) in fixtures {
  let chars=scalars.iter().map(|v|char::from_u32(*v).unwrap()).collect::<Vec<_>>();
  let text=chars.iter().collect::<String>();let utf16=text.encode_utf16().collect::<Vec<_>>();
  let mut utf8_starts=vec![0];let mut utf16_starts=vec![0];
  for ch in &chars {utf8_starts.push(utf8_starts.last().unwrap()+ch.len_utf8());utf16_starts.push(utf16_starts.last().unwrap()+ch.len_utf16());}
  for word in [LineBreakWordOption::Normal,LineBreakWordOption::BreakAll] {
   let mut options=LineBreakOptions::default();options.word_option=Some(word);
   let segmenter=LineSegmenter::new_lstm(options);
   let a=segmenter.segment_str(&text).collect::<Vec<_>>();let b=segmenter.segment_utf16(&utf16).collect::<Vec<_>>();
   let a_scalars=a.iter().map(|pos|utf8_starts.iter().position(|p|p==pos)).collect::<Vec<_>>();
   let b_scalars=b.iter().map(|pos|utf16_starts.iter().position(|p|p==pos)).collect::<Vec<_>>();
   println!("{name} {word:?} SCALARS {scalars:?} UTF8 {a:?} UTF16 {b:?} MAP8 {a_scalars:?} MAP16 {b_scalars:?} EQUAL {}",a_scalars==b_scalars);
  }
 }
}
