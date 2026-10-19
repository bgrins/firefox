int main(){std::string line;while(std::getline(std::cin,line)){
 std::istringstream in(line);std::string id;in>>id;std::vector<int>v(36);for(auto&x:v)in>>x;assert(in);
 ComputedStyle style[8];nsIFrame root[2],parent[2],extra[3];nsTextFrame frame[2];nsPresContext pc;CharacterDataBuffer buffers[2];
 for(int i=0;i<2;i++){root[i].style=&style[2+i];root[i].block=true;root[i].content=10+i;parent[i].style=&style[4+i];parent[i].content=20+i;parent[i].parent=&root[v[0]==2?i:0];frame[i].style=&style[i];frame[i].content=v[1]?30:30+i;frame[i].parent=v[0]?&parent[i]:&root[0];frame[i].context=&pc;frame[i].buffer=&buffers[i];buffers[i].text=i==0&&v[14]?u"a\n":u"aa";frame[i].end=2;frame[i].style->text.hyphenLimit=v[34+i];}
 if(v[0]==3){for(int i=0;i<3;i++){extra[i].style=&style[6];extra[i].content=40+i;extra[i].parent=i?&extra[i-1]:&root[0];}parent[0].parent=&extra[2];}
 frame[0].next=v[2]?&frame[1]:nullptr;
 frame[0].bidi.embeddingLevel=v[5];frame[1].bidi.embeddingLevel=v[6];frame[1].bidi.precedingControl=v[7];
 style[0].visibility.mWritingMode=StyleWritingModeProperty(v[8]);style[1].visibility.mWritingMode=StyleWritingModeProperty(v[9]);style[0].rtl=v[10];style[1].rtl=v[11];
 style[0].text.newline=v[12];frame[0].suppress=v[13];style[0].combined=v[15];
 style[1].text.mTextTransform=v[16];style[1].text.wordBreak=v[17];style[1].text.mLineBreak=v[18];style[1].font.mFont.identity=v[19];style[1].font.mLanguage=v[20];style[1].text.mLetterSpacing.value=v[21];style[1].text.mTextJustify=StyleTextJustify(v[22]);style[1].text.mMozControlCharacterVisibility=StyleMozControlCharacterVisibility(v[23]);style[1].text.mTextRendering=StyleTextRendering(v[24]);style[0].font.mFont.size.value=v[25];style[1].font.mFont.size.value=v[26];style[0].visibility.mTextOrientation=StyleTextOrientation(v[27]);style[1].visibility.mTextOrientation=StyleTextOrientation(v[28]);root[0].svg=v[29];
 if(v[3])frame[1].style=&style[0];
 nsIFrame*targets[]={&frame[0],&frame[1],&parent[0],&parent[1]};auto*s=targets[v[30]]->style;int side=v[31],kind=v[32];
 if(kind==1||kind==2){s->margin.values.values[side].value=kind==1;s->margin.values.values[side].converts=kind!=2;}
 if(kind==3||kind==4){s->padding.mPadding.values[side].value=kind==3;s->padding.mPadding.values[side].converts=kind!=4;}
 if(kind==5)s->border.values[side]=1;
 if(kind==6)s->display.mAlignmentBaseline=StyleAlignmentBaseline::Other;
 if(kind==7)s->display.mBaselineShift.keyword=true;
 if(kind==8)s->display.mBaselineShift.value=1;
 if(kind==9||kind==10)s->reset.mUnicodeBidi=kind==9?StyleUnicodeBidi::Isolate:StyleUnicodeBidi::IsolateOverride;
 frame[0].svg=frame[1].svg=v[33];
 BuildTextRunsScanner scanner;scanner.mBidiEnabled=v[4];bool answer=scanner.ContinueTextRunAcrossFrames(&frame[0],&frame[1]);
 std::cout<<id<<' '<<answer<<' '<<int(nsLayoutUtils::GetTextRunFlagsForStyle(frame[0].style,&pc,frame[0].StyleFont(),frame[0].StyleText(),ResolveLetterSpacing(&frame[0],*frame[0].StyleText())))<<' '<<int(nsLayoutUtils::GetTextRunFlagsForStyle(frame[1].style,&pc,frame[1].StyleFont(),frame[1].StyleText(),ResolveLetterSpacing(&frame[1],*frame[1].StyleText())))<<'\n';
}}
