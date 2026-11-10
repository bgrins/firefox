static bool sFeedbackWriteFailed = false;

static bool WriteCSSFeedbackRecord(const char* aBuffer, size_t aLength) {
  ssize_t written;
  do {
    written = write(STDERR_FILENO, aBuffer, aLength);
  } while (written < 0 && errno == EINTR);
  return written == static_cast<ssize_t>(aLength);
}

static void CSSFeedbackFailure(unsigned long long aSequence,
                               const char* aReason) {
  sFeedbackWriteFailed = true;
  char buffer[128];
  const int length = std::snprintf(
      buffer, sizeof(buffer),
      "CSSFB pid=%ld seq=%llu event=trace-error reason=%s\n",
      static_cast<long>(getpid()), aSequence, aReason);
  if (length > 0 && static_cast<size_t>(length) < sizeof(buffer)) {
    (void)WriteCSSFeedbackRecord(buffer, static_cast<size_t>(length));
  }
}

void CSSFeedbackLog(const char* aEvent, const void* aObject,
                    const char* aFormat, ...) {
  if (!CSSFeedbackTracing() || sFeedbackWriteFailed || sFeedbackSequence > 20000) {
    return;
  }
  const auto sequence = ++sFeedbackSequence;
  char buffer[512];
  if (sequence == 20001) {
    const int length = std::snprintf(
        buffer, sizeof(buffer), "CSSFB pid=%ld seq=%llu event=cap limit=20000\n",
        static_cast<long>(getpid()), sequence);
    if (length < 0 || static_cast<size_t>(length) >= sizeof(buffer)) {
      CSSFeedbackFailure(sequence, "cap-format");
    } else if (!WriteCSSFeedbackRecord(buffer, static_cast<size_t>(length))) {
      CSSFeedbackFailure(sequence, "cap-write");
    }
    return;
  }
  const int prefix = std::snprintf(
      buffer, sizeof(buffer),
      "CSSFB pid=%ld seq=%llu style_call=%llu style_depth=%u event=%s object=%p ",
      static_cast<long>(getpid()), sequence, sFeedbackStyleCall,
      sFeedbackStyleDepth, aEvent, aObject);
  if (prefix < 0 || static_cast<size_t>(prefix) >= sizeof(buffer) - 1) {
    CSSFeedbackFailure(sequence, "prefix-format");
    return;
  }
  const size_t remaining = sizeof(buffer) - static_cast<size_t>(prefix) - 1;
  va_list args;
  va_start(args, aFormat);
  const int body = std::vsnprintf(buffer + prefix, remaining, aFormat, args);
  va_end(args);
  if (body < 0 || static_cast<size_t>(body) >= remaining) {
    CSSFeedbackFailure(sequence, "body-format");
    return;
  }
  const size_t length = static_cast<size_t>(prefix) + static_cast<size_t>(body);
  buffer[length] = '\n';
  if (!WriteCSSFeedbackRecord(buffer, length + 1)) {
    CSSFeedbackFailure(sequence, "record-write");
  }
}
