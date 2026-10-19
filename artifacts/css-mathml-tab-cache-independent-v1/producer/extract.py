import hashlib,json,re
from pathlib import Path
R=Path(__file__).resolve().parent
TARGETS=[
 ('ComputePartialLigatureWidth','gfxTextRun.cpp','gfxFloat gfxTextRun::ComputePartialLigatureWidth('),
 ('GetAdvanceWidth','gfxTextRun.cpp','gfxFloat gfxTextRun::GetAdvanceWidth('),
 ('ShrinkToLigatureBoundaries','gfxTextRun.cpp','bool gfxTextRun::ShrinkToLigatureBoundaries('),
 ('AccumulateMetricsForRun','gfxTextRun.cpp','void gfxTextRun::AccumulateMetricsForRun('),
 ('AccumulatePartialLigatureMetrics','gfxTextRun.cpp','void gfxTextRun::AccumulatePartialLigatureMetrics('),
 ('MeasureText','gfxTextRun.cpp','gfxTextRun::Metrics gfxTextRun::MeasureText('),
 ('GlyphRunIterator','gfxTextRun.h','class MOZ_STACK_CLASS GlyphRunIterator {'),
 ('SetupJustificationSpacing','nsTextFrame.cpp','void nsTextFrame::PropertyProvider::SetupJustificationSpacing('),
 ('ReflowText','nsTextFrame.cpp','void nsTextFrame::ReflowText('),
 ('AddInlineMinISizeForFlow','nsTextFrame.cpp','void nsTextFrame::AddInlineMinISizeForFlow('),
 ('AddInlinePrefISizeForFlow','nsTextFrame.cpp','void nsTextFrame::AddInlinePrefISizeForFlow('),
 ('ComputeTightBounds','nsTextFrame.cpp','nsRect nsTextFrame::ComputeTightBounds('),
 ('GetPrefWidthTightBounds','nsTextFrame.cpp','nsresult nsTextFrame::GetPrefWidthTightBounds('),
 ('GetCharacterOffsetAtFramePointInternal','nsTextFrame.cpp','nsIFrame::ContentOffsets nsTextFrame::GetCharacterOffsetAtFramePointInternal('),
 ('SpacingContract','gfxTextRun.h','class PropertyProvider {'),
 ('GetAdjustedSpacing','gfxTextRun.cpp','static bool GetAdjustedSpacing('),
 ('GetAdjustedSpacingArray','gfxTextRun.cpp','bool gfxTextRun::GetAdjustedSpacingArray('),
 ('ComputeLigatureData','gfxTextRun.cpp','gfxTextRun::LigatureData gfxTextRun::ComputeLigatureData('),
 ('BreakAndMeasureText','gfxTextRun.cpp','uint32_t gfxTextRun::BreakAndMeasureText('),
 ('TabWidthStore','nsTextFrame.cpp','struct nsTextFrame::TabWidthStore {'),
 ('ApplySpacing','nsTextFrame.cpp','void nsTextFrame::TabWidthStore::ApplySpacing('),
 ('EnsureTextRun','nsTextFrame.cpp','gfxSkipCharsIterator nsTextFrame::EnsureTextRun('),
 ('ReflowConstructor','nsTextFrame.cpp','nsTextFrame::PropertyProvider::PropertyProvider(\n    gfxTextRun*'),
 ('DisplayConstructor','nsTextFrame.cpp','nsTextFrame::PropertyProvider::PropertyProvider(\n    nsTextFrame*'),
 ('GetSpacing','nsTextFrame.cpp','bool nsTextFrame::PropertyProvider::GetSpacing('),
 ('GetSpacingInternal','nsTextFrame.cpp','bool nsTextFrame::PropertyProvider::GetSpacingInternal('),
 ('CalcTabWidths','nsTextFrame.cpp','void nsTextFrame::PropertyProvider::CalcTabWidths('),
 ('InitializeForDisplay','nsTextFrame.cpp','void nsTextFrame::PropertyProvider::InitializeForDisplay('),
 ('InitializeForMeasure','nsTextFrame.cpp','void nsTextFrame::PropertyProvider::InitializeForMeasure('),
 ('SetStartOfLine','nsTextFrame.h','void SetStartOfLine('),
]
def extract(source,marker):
 assert source.count(marker)==1,marker
 start=source.index(marker);brace=source.index('{',start)
 tokens=r'//[^\n]*|/\*.*?\*/|"(?:\\.|[^"\\])*"|\x27(?:\\.|[^\x27\\])*\x27|[{}]'
 depth=0
 for token in re.finditer(tokens,source[brace:],re.S):
  if token[0]=='{':depth+=1
  elif token[0]=='}':
   depth-=1
   if depth==0:return source[start:brace+token.end()]
 raise ValueError(marker)
def records():
 return [{'name':name,'file':file,'marker':marker,'body_sha256':hashlib.sha256(extract((R/'source'/file).read_text(),marker).encode()).hexdigest()}for name,file,marker in TARGETS]
if __name__=='__main__':print(json.dumps(records(),indent=2))
