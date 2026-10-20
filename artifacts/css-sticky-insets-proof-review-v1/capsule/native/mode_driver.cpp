int main(){
 for(int raw=0;raw<256;raw++){
  WritingMode w(raw);
  std::cout<<"["<<raw<<","<<int(w.IsVertical());
  for(auto side:{LogicalSide::BStart,LogicalSide::BEnd,LogicalSide::IStart,LogicalSide::IEnd})std::cout<<","<<int(w.PhysicalSide(side));
  std::cout<<"]\n";
 }
}
