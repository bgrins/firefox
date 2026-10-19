#![allow(dead_code, private_interfaces)]
use std::{collections::BTreeSet, mem, sync::{Arc, atomic::{AtomicBool, AtomicU8, Ordering}}, ops::{Deref, DerefMut}, iter::Zip, slice::Iter};
type ThinVec<T> = Vec<T>;
type SubpropertiesVec<T> = Vec<T>;
type ArrayVecDrain<'a, T, const N: usize> = std::vec::Drain<'a,T>;
type PrecomputedHashSet<T> = BTreeSet<T>;
mod custom_properties { pub type Name = u16; }
mod smallbitvec { pub type Iter<'a> = std::iter::Copied<std::slice::Iter<'a,bool>>; }
#[derive(Default,Clone,Debug)]
struct SmallBitVec(Vec<bool>);
impl SmallBitVec {
 fn new()->Self{Self(Vec::new())}
 fn from_elem(n:usize,v:bool)->Self{Self(vec![v;n])}
 fn set(&mut self,n:usize,v:bool){self.0[n]=v;}
 fn iter(&self)->smallbitvec::Iter<'_>{self.0.iter().copied()}
}
impl Deref for SmallBitVec{type Target=Vec<bool>;fn deref(&self)->&Self::Target{&self.0}}
impl DerefMut for SmallBitVec{fn deref_mut(&mut self)->&mut Self::Target{&mut self.0}}
trait TryPush<T>{fn try_push(&mut self,t:T)->Result<(),()>;}
impl<T> TryPush<T> for Vec<T>{fn try_push(&mut self,t:T)->Result<(),()>{self.push(t);Ok(())}}
trait ZipEq: Iterator+Sized{fn zip_eq<J:IntoIterator>(self,other:J)->std::iter::Zip<Self,J::IntoIter> where Self:ExactSizeIterator,J::IntoIter:ExactSizeIterator{let o=other.into_iter();assert_eq!(self.len(),o.len());self.zip(o)}}
impl<I:Iterator> ZipEq for I{}
#[derive(Clone,Copy,Debug,PartialEq,Eq,PartialOrd,Ord)]
struct LonghandId(usize);
impl LonghandId{fn logical_group(self)->Option<usize>{META[self.0].group} fn is_logical(self)->bool{META[self.0].logical}}
#[derive(Default,Clone,Debug)]
struct LonghandIdSet(BTreeSet<LonghandId>);
impl LonghandIdSet{fn contains(&self,id:LonghandId)->bool{self.0.contains(&id)} fn insert(&mut self,id:LonghandId){self.0.insert(id);} fn remove(&mut self,id:LonghandId){self.0.remove(&id);} fn clear(&mut self){self.0.clear();} fn is_empty(&self)->bool{self.0.is_empty()}}
#[derive(Clone,Copy,Debug,PartialEq,Eq)]
enum PropertyDeclarationId<'a>{Longhand(LonghandId),Custom(&'a u16)}
impl PropertyDeclarationId<'_>{
 fn as_longhand(self)->Option<LonghandId>{match self{Self::Longhand(x)=>Some(x),_=>None}}
 fn key(self)->usize{match self{Self::Longhand(x)=>x.0,Self::Custom(x)=>META.len()+usize::from(*x)}}
 fn is_longhand_of(self,s:ShorthandId)->bool{self.as_longhand().is_some_and(|id|s.longhands().any(|x|x==id))}
 fn is_or_is_longhand_of(self,p:&PropertyId)->bool{match p.as_shorthand(){Ok(s)=>self.is_longhand_of(s),Err(id)=>self==id}}
}
#[derive(Clone,Debug,PartialEq,Eq)]
struct UnparsedValue(u16);
#[derive(Clone,Debug,PartialEq,Eq)]
struct VariableDeclaration{id:LonghandId,value:Arc<UnparsedValue>}
#[derive(Clone,Debug,PartialEq,Eq)]
pub enum PropertyDeclaration{CSSWideKeyword(LonghandId,CSSWideKeyword),WithVariables(VariableDeclaration),Ordinary(LonghandId,u16),Custom(u16,u16)}
impl PropertyDeclaration{
 fn id(&self)->PropertyDeclarationId<'_>{match self{Self::CSSWideKeyword(id,_)|Self::Ordinary(id,_)=>PropertyDeclarationId::Longhand(*id),Self::WithVariables(v)=>PropertyDeclarationId::Longhand(v.id),Self::Custom(id,_)=>PropertyDeclarationId::Custom(id)}}
 fn css_wide_keyword(id:LonghandId,v:CSSWideKeyword)->Self{Self::CSSWideKeyword(id,v)}
 fn payload(&self)->u32{match self{Self::CSSWideKeyword(_,v)=>*v as u32,Self::WithVariables(v)=>1000+u32::from(v.value.0),Self::Ordinary(_,v)|Self::Custom(_,v)=>2000+u32::from(*v)}}
}
#[derive(Clone,Copy,Debug)]
enum ShorthandId{All,Selected(usize)}
impl ShorthandId{fn longhands(self)->NonCustomPropertyIterator<LonghandId>{NonCustomPropertyIterator{filter:true,iter:match self{Self::All=>ALL_IDS.iter(),Self::Selected(i)=>SHORTHANDS[i].iter()}}}}
enum PropertyId{Longhand(LonghandId),Custom(u16),Shorthand(ShorthandId)}
impl PropertyId{fn as_shorthand(&self)->Result<ShorthandId,PropertyDeclarationId<'_>>{match self{Self::Longhand(id)=>Err(PropertyDeclarationId::Longhand(*id)),Self::Custom(id)=>Err(PropertyDeclarationId::Custom(id)),Self::Shorthand(id)=>Ok(*id)}}}
static PREF_PROFILE:AtomicU8=AtomicU8::new(0);
struct NonCustomPropertyId(LonghandId);
impl From<LonghandId> for NonCustomPropertyId{fn from(id:LonghandId)->Self{Self(id)}}
impl NonCustomPropertyId{fn enabled_for_all_content(&self)->bool{let m=&META[self.0.0];m.content && (!m.pref || match PREF_PROFILE.load(Ordering::Relaxed){0=>true,1=>false,_=>self.0.0%2==0})}}
struct Meta{name:&'static str,group:Option<usize>,logical:bool,content:bool,pref:bool}
