#ifndef HiddenColumnIdentityTrace_h
#define HiddenColumnIdentityTrace_h

#include <stdio.h>
#include <unistd.h>
#include "mozilla/dom/Element.h"
#include "nsGkAtoms.h"
#include "nsIFrame.h"
#include "nsString.h"

namespace mozilla::HiddenColumnIdentityTrace {
inline uint64_t NextSerial() {
  static uint64_t serial = 0;
  return ++serial;
}

inline nsAutoCString NodeID(nsIFrame* frame) {
  nsAutoString value;
  if (frame && frame->GetContent() && frame->GetContent()->IsElement()) {
    frame->GetContent()->AsElement()->GetAttr(nsGkAtoms::id, value);
  }
  return NS_ConvertUTF16toUTF8(value);
}

inline bool Fixture(nsIFrame* frame, nsAutoCString& id, int& narrow,
                    int& hidden) {
  if (!frame || !frame->GetContent()) return false;
  auto* element = dom::Element::FromNodeOrNull(frame->GetContent());
  for (unsigned depth = 0; element && depth < 12;
       ++depth, element = element->GetParentElement()) {
    nsAutoString value;
    nsAutoString classes;
    element->GetAttr(nsGkAtoms::id, value);
    element->GetAttr(nsGkAtoms::_class, classes);
    if (classes.EqualsLiteral("outer") || classes.EqualsLiteral("outer narrow")) {
      narrow = classes.EqualsLiteral("outer narrow");
    }
    if (classes.EqualsLiteral("subject") || classes.EqualsLiteral("subject hidden")) {
      hidden = classes.EqualsLiteral("subject hidden");
    }
    if (value.EqualsLiteral("cvjoin-col-target-host") ||
        value.EqualsLiteral("cvjoin-col-reference-host") ||
        value.EqualsLiteral("cvjoin-colgroup-target-host") ||
        value.EqualsLiteral("cvjoin-colgroup-reference-host")) {
      id = NS_ConvertUTF16toUTF8(value);
      return true;
    }
  }
  return false;
}

inline const char* Kind(nsIFrame* frame) {
  if (!frame) return "null";
  if (frame->IsTableColFrame()) return "col";
  if (frame->IsTableColGroupFrame()) return "group";
  if (frame->IsTableFrame()) return "table";
  if (frame->IsTableWrapperFrame()) return "wrapper";
  if (frame->IsBlockFrame()) return "block";
  return "other";
}

inline nsIFrame* Provider(nsIFrame* frame) {
  if (!frame) return nullptr;
  if (frame->IsTableColFrame()) frame = frame->GetParent();
  if (frame && frame->IsTableColGroupFrame()) frame = frame->GetParent();
  return frame && frame->IsTableFrame() ? frame : nullptr;
}

inline void Record(const char* event, nsIFrame* frame,
                   nsIFrame* actor = nullptr, uint64_t batch = 0,
                   unsigned depth = 0) {
  nsAutoCString fixture;
  int narrow = -1;
  int hidden = -1;
  if (!Fixture(frame, fixture, narrow, hidden)) return;
  nsIFrame* parent = frame->GetParent();
  nsIFrame* provider = Provider(frame);
  const nsRect& rect = frame->GetRect();
  fprintf(stderr,
          "CVJOIN pid=%ld seq=%llu batch=%llu event=%s case=%s narrow=%d hidden=%d depth=%u "
          "doc=%p content=%p frame=%p node=%s kind=%s dirty=%d kids=%d "
          "parent=%p parent_node=%s parent_kind=%s provider=%p provider_node=%s pd=%d pk=%d "
          "actor=%p actor_node=%s prev=%p next=%p rect=%d,%d,%d,%d\n",
          long(getpid()), (unsigned long long)NextSerial(),
          (unsigned long long)batch, event, fixture.get(), narrow, hidden, depth,
          static_cast<void*>(frame->GetContent()->OwnerDoc()),
          static_cast<void*>(frame->GetContent()), static_cast<void*>(frame),
          NodeID(frame).get(), Kind(frame),
          int(frame->HasAnyStateBits(NS_FRAME_IS_DIRTY)),
          int(frame->HasAnyStateBits(NS_FRAME_HAS_DIRTY_CHILDREN)),
          static_cast<void*>(parent), NodeID(parent).get(), Kind(parent),
          static_cast<void*>(provider), NodeID(provider).get(),
          int(provider && provider->HasAnyStateBits(NS_FRAME_IS_DIRTY)),
          int(provider && provider->HasAnyStateBits(NS_FRAME_HAS_DIRTY_CHILDREN)),
          static_cast<void*>(actor), NodeID(actor).get(),
          static_cast<void*>(frame->GetPrevContinuation()),
          static_cast<void*>(frame->GetNextContinuation()),
          int(rect.x), int(rect.y), int(rect.width), int(rect.height));
}

inline void Walk(const char* event, nsIFrame* frame, nsIFrame* actor,
                 uint64_t batch, unsigned depth, unsigned& budget) {
  if (!frame) return;
  if (!budget || depth > 8) {
    Record("tree-cut", frame, actor, batch, depth);
    return;
  }
  --budget;
  Record(event, frame, actor, batch, depth);
  for (nsIFrame* child : frame->PrincipalChildList()) {
    Walk(event, child, actor, batch, depth + 1, budget);
    if (!budget) break;
  }
}

inline void Tree(const char* event, nsIFrame* frame, nsIFrame* actor) {
  nsAutoCString fixture;
  int narrow = -1;
  int hidden = -1;
  if (!Fixture(frame, fixture, narrow, hidden)) return;
  unsigned budget = 32;
  Walk(event, frame, actor, NextSerial(), 0, budget);
  if (!budget) Record("tree-budget-exhausted", frame, actor);
}
}  // namespace mozilla::HiddenColumnIdentityTrace

#endif
