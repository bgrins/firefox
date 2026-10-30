namespace {
uint64_t sDurationQuery = 0;
uint64_t sDurationParentQuery = 0;
uint64_t sDurationNextQuery = 0;
unsigned sDurationSequence = 0;
size_t sDurationBytes = 0;
bool sDurationCapped = false;

bool DurationTraceEnabled() {
  if (!NS_IsMainThread()) {
    return false;
  }
  static const bool enabled = [] {
    const char* value = std::getenv("MOZ_DURATION_FIRST_READ_TRACE");
    return value && value[0] == '1' && value[1] == '\0';
  }();
  return enabled;
}

const char* DurationTracePage(dom::Document* aDocument) {
  if (!DurationTraceEnabled() || !aDocument) {
    return nullptr;
  }
  auto* parent = aDocument->GetInProcessParentDocument();
  auto* uri = aDocument->GetDocumentURI();
  if (!parent || !uri || !parent->GetDocumentURI()) {
    return nullptr;
  }
  nsAutoCString spec;
  if (NS_FAILED(uri->GetSpec(spec)) || !spec.EqualsLiteral("about:srcdoc")) {
    return nullptr;
  }
  nsAutoCString path;
  if (NS_FAILED(parent->GetDocumentURI()->GetPathQueryRef(path))) {
    return nullptr;
  }
  if (path.EqualsLiteral("/css/css-animations/animation-duration-acyclic-two-hop.tentative.html")) {
    return "rem";
  }
  if (path.EqualsLiteral("/css/css-animations/animation-duration-acyclic-line-height-chain.tentative.html")) {
    return "lh";
  }
  if (path.EqualsLiteral("/css/css-animations/animation-duration-property-only-wakeup.tentative.html")) {
    return "property";
  }
  return nullptr;
}

const char* DurationTraceRole(Element* aElement) {
  if (!aElement) {
    return "none";
  }
  nsAutoString classes;
  aElement->GetAttr(kNameSpaceID_None, nsGkAtoms::_class, classes);
  if (classes.EqualsLiteral("child")) {
    return "child";
  }
  if (classes.EqualsLiteral("middle")) {
    return "middle";
  }
  if (aElement == aElement->OwnerDoc()->GetRootElement()) {
    return "root";
  }
  if (classes.EqualsLiteral("parent literal") ||
      classes.EqualsLiteral("parent ordinary") ||
      classes.EqualsLiteral("parent animated") ||
      classes.EqualsLiteral("parent literal advanced") ||
      classes.EqualsLiteral("parent ordinary advanced")) {
    return "parent";
  }
  return "other";
}

const char* DurationTraceMode(Element* aElement) {
  unsigned depth = 0;
  for (auto* element = aElement; element && depth++ < 8;
       element = element->GetParentElement()) {
    nsAutoString classes;
    element->GetAttr(kNameSpaceID_None, nsGkAtoms::_class, classes);
    if (classes.EqualsLiteral("literal") ||
        classes.EqualsLiteral("literal advanced") ||
        classes.EqualsLiteral("parent literal") ||
        classes.EqualsLiteral("parent literal advanced")) {
      return "literal";
    }
    if (classes.EqualsLiteral("ordinary") ||
        classes.EqualsLiteral("ordinary advanced") ||
        classes.EqualsLiteral("parent ordinary") ||
        classes.EqualsLiteral("parent ordinary advanced")) {
      return "ordinary";
    }
    if (classes.EqualsLiteral("animated") ||
        classes.EqualsLiteral("parent animated")) {
      return "animated";
    }
  }
  return "unknown";
}

struct DurationTraceRecord {
  const char* stage;
  dom::Document* document;
  Element* target = nullptr;
  const PseudoStyleRequest* pseudo = nullptr;
  const void* compositor = nullptr;
  const void* shell = nullptr;
  const void* traversalRoot = nullptr;
  const void* styleSource = nullptr;
  int cascade = -1;
  int state = -2;
  int request = -1;
  int pre = -1;
  int property = -1;
  int flush = -1;
  int animations = -1;
  int need = -1;
  int style = -1;
  int throttled = -1;
  int layout = -1;
  unsigned flags = 0;
  unsigned count = 0;
  const nsACString* value = nullptr;
};

void DurationTraceEmit(const DurationTraceRecord& aRecord) {
  const char* page = DurationTracePage(aRecord.document);
  if (!page || sDurationCapped) {
    return;
  }
  auto cap = [](const char* aReason) {
    sDurationCapped = true;
    std::fprintf(stderr,
                 "DURATION_FIRST_READ_TRACE v=1 pid=%lu cap=%s seq=%u\n",
                 static_cast<unsigned long>(base::GetCurrentProcId()), aReason,
                 sDurationSequence);
  };
  if (sDurationSequence >= 16384 || sDurationBytes >= 4 * 1024 * 1024) {
    cap("limit");
    return;
  }
  auto* shell = aRecord.document->GetPresShell();
  auto* context = shell ? shell->GetPresContext() : nullptr;
  auto* restyleManager = context ? context->RestyleManager() : nullptr;
  int refresh = restyleManager ? int(restyleManager->IsInStyleRefresh()) : -1;
  char value[257] = "-";
  unsigned valueLength = 0;
  int valueTruncated = 0;
  if (aRecord.value) {
    valueLength = aRecord.value->Length();
    valueTruncated = valueLength > 128;
    unsigned copied = std::min(valueLength, 128u);
    static constexpr char hex[] = "0123456789abcdef";
    for (unsigned i = 0; i < copied; ++i) {
      auto c = static_cast<unsigned char>((*aRecord.value)[i]);
      value[i * 2] = hex[c >> 4];
      value[i * 2 + 1] = hex[c & 15];
    }
    value[copied * 2] = '\0';
    if (!copied) {
      value[0] = '-';
      value[1] = '\0';
    }
  }
  char line[1536];
  int length = std::snprintf(
      line, sizeof(line),
      "DURATION_FIRST_READ_TRACE v=1 pid=%lu seq=%u query=%llu parent=%llu "
      "window=%llu document=%p page=%s target=%p role=%s mode=%s pseudo=%d "
      "identifier=%p compositor=%p shell=%p stage=%s cascade=%d state=%d "
      "request=%d servo=%d pre=%d refresh=%d root=%p traversal=%p flags=%u "
      "property=%d flush=%d animations=%d need=%d style=%d throttle=%d "
      "layout=%d source=%p count=%u value=%s valueLength=%u valueTruncated=%d\n",
      static_cast<unsigned long>(base::GetCurrentProcId()), sDurationSequence + 1,
      static_cast<unsigned long long>(sDurationQuery),
      static_cast<unsigned long long>(sDurationParentQuery),
      static_cast<unsigned long long>(aRecord.document->InnerWindowID()),
      static_cast<void*>(aRecord.document), page,
      static_cast<void*>(aRecord.target), DurationTraceRole(aRecord.target),
      DurationTraceMode(aRecord.target),
      aRecord.pseudo ? int(aRecord.pseudo->mType) : -1,
      aRecord.pseudo ? static_cast<void*>(aRecord.pseudo->mIdentifier.get()) : nullptr,
      aRecord.compositor, aRecord.shell ? aRecord.shell : shell, aRecord.stage,
      aRecord.cascade, aRecord.state, aRecord.request,
      int(ServoStyleSet::IsInServoTraversal()), aRecord.pre, refresh,
      static_cast<void*>(aRecord.document->GetServoRestyleRoot()),
      aRecord.traversalRoot, aRecord.flags, aRecord.property, aRecord.flush,
      aRecord.animations, aRecord.need, aRecord.style, aRecord.throttled,
      aRecord.layout, aRecord.styleSource, aRecord.count, value, valueLength,
      valueTruncated);
  if (length < 0 || size_t(length) >= sizeof(line) ||
      sDurationBytes + size_t(length) > 4 * 1024 * 1024) {
    cap("bytes");
    return;
  }
  ++sDurationSequence;
  sDurationBytes += length;
  std::fwrite(line, 1, length, stderr);
}
}  // namespace

EffectCompositor::DurationTraceQuery EffectCompositor::BeginDurationQuery(
    Element* aElement, const PseudoStyleRequest& aPseudo, int aProperty) {
  if (!aElement || !DurationTracePage(aElement->OwnerDoc())) {
    return {};
  }
  DurationTraceQuery query{++sDurationNextQuery, sDurationQuery,
                           sDurationParentQuery};
  sDurationParentQuery = sDurationQuery;
  sDurationQuery = query.mId;
  DurationTraceRecord record{"query-enter", aElement->OwnerDoc(), aElement,
                             &aPseudo};
  record.property = aProperty;
  DurationTraceEmit(record);
  TraceDurationSources("query-entry-state", aElement, aPseudo);
  return query;
}

void EffectCompositor::EndDurationQuery(DurationTraceQuery aQuery,
                                        Element* aElement,
                                        const PseudoStyleRequest& aPseudo,
                                        int aProperty,
                                        const nsACString& aValue) {
  if (!aQuery.mId) {
    return;
  }
  if (aElement) {
    TraceDurationSources("query-return-state", aElement, aPseudo);
    DurationTraceRecord record{"query-exit", aElement->OwnerDoc(), aElement,
                               &aPseudo};
    record.property = aProperty;
    record.value = &aValue;
    DurationTraceEmit(record);
  }
  sDurationQuery = aQuery.mParent;
  sDurationParentQuery = aQuery.mGrandparent;
}

void EffectCompositor::TraceDurationSources(
    const char* aStage, Element* aElement, const PseudoStyleRequest& aPseudo,
    const void* aStyleSource, int aFlush) {
  if (!aElement || !DurationTracePage(aElement->OwnerDoc())) {
    return;
  }
  DurationTraceRecord record{aStage, aElement->OwnerDoc(), aElement, &aPseudo};
  record.styleSource = aStyleSource;
  record.flush = aFlush;
  DurationTraceEmit(record);
  if (auto* shell = aElement->OwnerDoc()->GetPresShell()) {
    shell->TraceDurationFlush(aStage, -1, -1, -1);
    if (auto* context = shell->GetPresContext()) {
      if (auto* compositor = context->EffectCompositor()) {
        compositor->TraceDurationSnapshot(aElement, aPseudo);
      }
    }
  }
}

void PresShell::TraceDurationFlush(const char* aStage, int aFlush,
                                  int aAnimations, int aNeed) {
  DurationTraceRecord record{aStage, mDocument};
  record.shell = this;
  record.flush = aFlush;
  record.animations = aAnimations;
  record.need = aNeed;
  record.style = mNeedStyleFlush;
  record.throttled = mNeedThrottledAnimationFlush;
  record.layout = mNeedLayoutFlush;
  DurationTraceEmit(record);
}

void EffectCompositor::TraceDurationRestyle(
    const char* aStage, Element* aElement, const PseudoStyleRequest& aPseudo,
    int aCascade, int aRequest, Element* aRoot, unsigned aFlags) {
  if (!aElement) {
    return;
  }
  auto* document = mPresContext ? mPresContext->Document() : aElement->OwnerDoc();
  if (!DurationTracePage(document)) {
    return;
  }
  DurationTraceRecord record{aStage, document, aElement, &aPseudo};
  record.compositor = this;
  record.pre = mIsInPreTraverse;
  record.cascade = aCascade;
  record.request = aRequest;
  record.traversalRoot = aRoot;
  record.flags = aFlags;
  if (aCascade >= 0) {
    auto entry = mElementsToRestyle[CascadeLevel(aCascade)].Lookup(
        {aElement, aPseudo});
    record.state = entry ? int(entry.Data()) : -1;
  }
  DurationTraceEmit(record);
}

void EffectCompositor::TraceDurationSnapshot(
    Element* aElement, const PseudoStyleRequest& aPseudo) {
  if (!aElement || !DurationTracePage(aElement->OwnerDoc())) {
    return;
  }
  unsigned inspected = 0;
  for (size_t i = 0; i < kCascadeLevelCount; ++i) {
    TraceDurationRestyle("snapshot-query-key", aElement, aPseudo, int(i));
    for (auto iter = mElementsToRestyle[CascadeLevel(i)].ConstIter();
         !iter.Done(); iter.Next()) {
      if (++inspected > 64) {
        DurationTraceRecord record{"snapshot-truncated", aElement->OwnerDoc(),
                                   aElement, &aPseudo};
        record.count = inspected;
        DurationTraceEmit(record);
        return;
      }
      const auto& target = iter.Key();
      if (target.mElement->OwnerDoc() == aElement->OwnerDoc()) {
        TraceDurationRestyle("snapshot-entry", target.mElement,
                             target.mPseudoRequest, int(i));
      }
    }
  }
  DurationTraceRecord record{"snapshot-end", aElement->OwnerDoc(), aElement,
                             &aPseudo};
  record.count = inspected;
  DurationTraceEmit(record);
}
