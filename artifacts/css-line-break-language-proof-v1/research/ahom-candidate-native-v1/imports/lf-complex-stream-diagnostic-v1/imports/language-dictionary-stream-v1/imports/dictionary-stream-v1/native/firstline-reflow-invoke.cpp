nsFirstLineFrame lines[3];nsLineLayout layout;layout.container=&container;
for(unsigned i=0;i<3;i++){lines[i].pc=&pc;lines[i].previous=i?&lines[i-1]:nullptr;lines[i].next=i<2?&lines[i+1]:nullptr;}
for(size_t i=0;i<moved.size();i++){unsigned line=i%3;auto&target=lines[line];bool overflow=line==0||(i%2)!=0;if(overflow){if(!target.overflowFrames)target.overflowFrames=std::make_unique<nsFrameList>();target.overflowFrames->InsertFrame(&target,target.overflowFrames->LastChild(),moved[i]);}else target.mFrames.InsertFrame(&target,target.mFrames.LastChild(),moved[i]);}
std::vector<nsIFrame*>expected;for(auto&line:lines){expected.insert(expected.end(),line.mFrames.frames.begin(),line.mFrames.frames.end());if(line.overflowFrames)expected.insert(expected.end(),line.overflowFrames->frames.begin(),line.overflowFrames->frames.end());}
ReflowInput input{&lines[0],&layout};ReflowOutput output;nsReflowStatus status;lines[0].Reflow(&pc,output,input,status);
assert(lines[0].marked&&lines[0].reflowEntered&&!layout.GetInFirstLine());assert(lines[0].entryFrames==expected);assert(lines[1].mFrames.IsEmpty()&&lines[2].mFrames.IsEmpty());
for(auto*f:moved){assert(f->GetParent()==&lines[0]);assert(std::find(restyle.reparents.begin(),restyle.reparents.end(),f)!=restyle.reparents.end());f->parent=&container;}
