from pathlib import Path
import difflib, hashlib, json
P = Path(__file__).resolve().parent
BASE = P.parent / 'css-style-query-timeline-feedback-source-20261110-v1'
NAMES = ['dom/animation/Animation.h', 'dom/animation/Animation.cpp', 'dom/animation/ScrollTimeline.cpp', 'layout/style/ServoStyleSet.cpp']
def replace(s, a, b):
    assert s.count(a) == 1, (a, s.count(a))
    return s.replace(a, b)
sources = {n: (BASE/'source'/n).read_text() for n in NAMES}
out = dict(sources)
n = NAMES[0]
out[n] = replace(out[n], 'class AnimationEffect;', '''bool CSSFeedbackTracing();
void CSSFeedbackLog(const char* aEvent, const void* aObject,
                    const char* aFormat, ...);
class CSSFeedbackScope {
 public:
  CSSFeedbackScope(const char* aEvent, const void* aObject, bool aStyle = false);
  ~CSSFeedbackScope();
 private:
  const char* mEvent;
  const void* mObject;
  bool mStyle;
  unsigned long long mOldCall = 0;
};

class AnimationEffect;''')
out[n] = replace(out[n], '  explicit Animation(nsIGlobalObject* aGlobal);', '''  explicit Animation(nsIGlobalObject* aGlobal);
  void TraceCSSFeedback(const char* aEvent,
                        const AnimationTimeline* aNext = nullptr) const;''')
n = NAMES[1]
out[n] = replace(out[n], '#include "Animation.h"', '''#include "Animation.h"
#include <cstdarg>
#include <cstdio>
#include <cstdlib>
#include <unistd.h>
#include "mozilla/ScopeExit.h"''')
out[n] = replace(out[n], '// Static members', '''static unsigned long long sFeedbackSequence = 0;
static unsigned long long sFeedbackCallSequence = 0;
static unsigned long long sFeedbackStyleCall = 0;
static unsigned sFeedbackStyleDepth = 0;

bool CSSFeedbackTracing() {
  static const bool enabled = std::getenv("MOZ_CSS_FEEDBACK_TRACE") != nullptr;
  if (enabled) {
    MOZ_ASSERT(NS_IsMainThread());
  }
  return enabled;
}

void CSSFeedbackLog(const char* aEvent, const void* aObject,
                    const char* aFormat, ...) {
  if (!CSSFeedbackTracing() || sFeedbackSequence > 20000) {
    return;
  }
  const auto sequence = ++sFeedbackSequence;
  if (sequence == 20001) {
    std::fprintf(stderr, "CSSFB pid=%ld seq=%llu event=cap limit=20000\\n",
                 static_cast<long>(getpid()), sequence);
    return;
  }
  std::fprintf(stderr,
               "CSSFB pid=%ld seq=%llu style_call=%llu style_depth=%u event=%s object=%p ",
               static_cast<long>(getpid()), sequence, sFeedbackStyleCall,
               sFeedbackStyleDepth, aEvent, aObject);
  va_list args;
  va_start(args, aFormat);
  std::vfprintf(stderr, aFormat, args);
  va_end(args);
  std::fputc('\\n', stderr);
}

CSSFeedbackScope::CSSFeedbackScope(const char* aEvent, const void* aObject,
                                   bool aStyle)
    : mEvent(aEvent), mObject(aObject), mStyle(aStyle) {
  if (!CSSFeedbackTracing()) {
    return;
  }
  if (mStyle) {
    mOldCall = sFeedbackStyleCall;
    sFeedbackStyleCall = ++sFeedbackCallSequence;
    ++sFeedbackStyleDepth;
  }
  CSSFeedbackLog(mEvent, mObject, "edge=enter");
}

CSSFeedbackScope::~CSSFeedbackScope() {
  if (!CSSFeedbackTracing()) {
    return;
  }
  CSSFeedbackLog(mEvent, mObject, "edge=exit");
  if (mStyle) {
    --sFeedbackStyleDepth;
    sFeedbackStyleCall = mOldCall;
  }
}

void Animation::TraceCSSFeedback(const char* aEvent,
                                  const AnimationTimeline* aNext) const {
  if (!CSSFeedbackTracing() || !AsCSSAnimation()) {
    return;
  }
  const auto target = GetTargetForAnimation();
  if (!target || !target.mElement->GetID() ||
      !target.mElement->GetID()->Equals(u"outside", 7)) {
    return;
  }
  CSSFeedbackLog(aEvent, this,
      "animation_index=%llu target=%p document=%p timeline=%p next=%p start_null=%d hold_null=%d pending=%u auto_align=%d rate=%.17g",
      static_cast<unsigned long long>(mAnimationIndex),
      static_cast<const void*>(target.mElement),
      static_cast<const void*>(target.mElement->OwnerDoc()),
      static_cast<const void*>(mTimeline.get()), static_cast<const void*>(aNext),
      int(mStartTime.IsNull()), int(mHoldTime.IsNull()), unsigned(mPendingState),
      int(mAutoAlignStartTime), mPlaybackRate);
}

// Static members''')
for signature,event,nextarg in [
('bool Animation::SetTimelineNoUpdate(AnimationTimeline* aTimeline,\n                                    const ScopedTimelineName& aTimelineName,\n                                    FromJS aFromJS) {','rebind', ', aTimeline'),
('void Animation::Tick(AnimationTimeline::TickState& aTickState) {','tick',''),
('bool Animation::MakeReadyAndMaybeTrigger() {','ready',''),
('bool Animation::TryTriggerNow() {','trigger',''),
('void Animation::AutoAlignStartTime() {','align','')]:
    out[n] = replace(out[n], signature, signature + f'\n  TraceCSSFeedback("{event}.enter"{nextarg});\n  auto feedbackExit = MakeScopeExit([&] {{ TraceCSSFeedback("{event}.exit"{nextarg}); }});')
n = NAMES[2]
out[n] = replace(out[n], '#include "mozilla/dom/Animation.h"', '#include "mozilla/dom/Animation.h"\n#include "mozilla/ScopeExit.h"')
for sig,event in [('void ScrollTimeline::WillRefresh() {','refresh'), ('bool ScrollTimeline::UpdateIfStale() {','stale')]:
    out[n] = replace(out[n], sig, sig + f'\n  CSSFeedbackScope feedbackScope("{event}", this);')
out[n] = replace(out[n], 'bool ScrollTimeline::UpdateCachedCurrentTime() {', '''bool ScrollTimeline::UpdateCachedCurrentTime() {
  CSSFeedbackLog("cache.enter", this, "document=%p source=%p cached=%d",
                 static_cast<const void*>(mDocument.get()),
                 mCachedStateSnapshot ? static_cast<const void*>(mCachedStateSnapshot->SourceElement()) : nullptr,
                 int(bool(mCachedCurrentTime)));
  auto feedbackExit = MakeScopeExit([&] {
    CSSFeedbackLog("cache.exit", this, "document=%p source=%p cached=%d position=%lld range=%lld",
                   static_cast<const void*>(mDocument.get()),
                   mCachedStateSnapshot ? static_cast<const void*>(mCachedStateSnapshot->SourceElement()) : nullptr,
                   int(bool(mCachedCurrentTime)),
                   mCachedCurrentTime ? static_cast<long long>(mCachedCurrentTime->mPosition) : 0,
                   mCachedCurrentTime ? static_cast<long long>(mCachedCurrentTime->mMaxScrollOffset) : 0);
  });''')
n = NAMES[3]
out[n] = replace(out[n], '#include "mozilla/ServoStyleSet.h"', '#include "mozilla/ServoStyleSet.h"\n#include "mozilla/dom/Animation.h"')
out[n] = replace(out[n], 'bool ServoStyleSet::StyleDocument(ServoTraversalFlags aFlags) {', '''bool ServoStyleSet::StyleDocument(ServoTraversalFlags aFlags) {
  dom::CSSFeedbackScope feedbackScope("style", mDocument, true);''')
patch = ''
for n in NAMES:
    dest=P/'source'/n
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(out[n])
    patch += ''.join(difflib.unified_diff(sources[n].splitlines(True),out[n].splitlines(True),fromfile='a/'+n,tofile='b/'+n))
(P/'instrumentation.patch').write_text(patch)
records={n:{'base_sha256':hashlib.sha256(sources[n].encode()).hexdigest(),'instrumented_sha256':hashlib.sha256(out[n].encode()).hexdigest()} for n in NAMES}
(P/'SOURCES.json').write_text(json.dumps({'revision':'3a6a6bfe2b0d3d551b2392206179f251002cfc7e','files':records,'patch_sha256':hashlib.sha256(patch.encode()).hexdigest()},indent=2)+'\n')
print('Prepared',len(NAMES),'copied native files; patch',hashlib.sha256(patch.encode()).hexdigest())
