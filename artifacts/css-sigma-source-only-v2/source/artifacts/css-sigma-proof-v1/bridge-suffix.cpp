
struct Scalar {
  uint32_t cp;
  bool firstMask = false;
  bool secondMask = false;
};
static std::vector<uint8_t> properties;
static uint64_t checks = 0;
static nsTransformedTextRun encode(const std::vector<Scalar>& source) {
  nsTransformedTextRun r;
  for (auto s : source) {
    assert(s.cp <= 0x10ffff);
    if (s.cp < 0x10000) {
      r.mString.units.push_back(s.cp);
      r.mStyles.values.push_back({s.firstMask});
    } else {
      uint32_t x = s.cp - 0x10000;
      r.mString.units.push_back(0xd800 + x / 1024);
      r.mString.units.push_back(0xdc00 + x % 1024);
      r.mStyles.values.push_back({s.firstMask});
      r.mStyles.values.push_back({s.secondMask});
    }
  }
  return r;
}
static bool reference(const std::vector<Scalar>& source, size_t at, bool masks) {
  auto projected = [&](const Scalar& s) -> uint8_t {
    if (masks && (s.firstMask || (s.cp >= 0x10000 && s.secondMask))) return 0;
    return properties.at(s.cp);
  };
  std::vector<uint8_t> before, after;
  for (size_t j = 0; j < source.size(); ++j) {
    auto p = projected(source[j]);
    if (p & 2) continue;
    if (j < at) before.push_back(p);
    if (j > at) after.push_back(p);
  }
  return !before.empty() && (before.back() & 1) &&
         (after.empty() || !(after.front() & 1));
}
static void check(const std::vector<Scalar>& source, size_t at, bool slices = false) {
  auto r = encode(source);
  uint32_t offset = 0;
  for (size_t j = 0; j < at; ++j) offset += source[j].cp >= 0x10000 ? 2 : 1;
  assert(source.at(at).cp == GREEK_CAPITAL_LETTER_SIGMA);
  bool expected = reference(source, at, true);
  auto verify = [&](bool actual, bool want) {
    if (actual != want) {
      std::fprintf(stderr, "Mismatch at scalar %zu, UTF16 %u: actual %d expected %d\n", at, offset, actual, want);
      std::exit(1);
    }
    ++checks;
  };
  verify(IsFinalSigma(r.mString, offset, &r), expected);
  verify(IsFinalSigma(r.mString, offset, nullptr), reference(source, at, false));
  if (slices) {
    for (uint32_t start = 0; start <= offset; ++start) {
      for (uint32_t end = offset + 1; end <= r.mString.Length(); ++end) {
        nsAString slice{r.mString.units.substr(start, end - start)};
        verify(bridgeCall(slice, offset - start, &r, offset) == GREEK_SMALL_LETTER_FINAL_SIGMA,
               expected);
      }
    }
    verify(bridgeCall(r.mString, offset, nullptr, 0) == GREEK_SMALL_LETTER_FINAL_SIGMA,
           reference(source, at, false));
  }
}
int main(int argc, char** argv) {
  assert(argc == 2);
  std::ifstream input(argv[1], std::ios::binary);
  properties.assign(std::istreambuf_iterator<char>(input), {});
  assert(properties.size() == 0x110000);
  for (uint32_t cp = 0; cp <= 0x10ffff; ++cp) {
    check({{cp}, {0x3a3}}, 1);
    check({{0x41}, {0x3a3}, {cp}}, 1);
    check({{cp, true, true}, {0x3a3}}, 1);
    check({{0x41}, {0x3a3}, {cp, true, true}}, 1);
    if (cp >= 0x10000) {
      check({{cp, true, false}, {0x3a3}}, 1);
      check({{cp, false, true}, {0x3a3}}, 1);
      check({{0x41}, {0x3a3}, {cp, true, false}}, 1);
      check({{0x41}, {0x3a3}, {cp, false, true}}, 1);
    }
  }
  const uint64_t exhaustive = checks;
  const std::vector<uint32_t> alphabet{0x41, 0x3a3, 0x0345, 0x27, 0x6f22, 0x10400, 0x1d167, 0x20000};
  std::vector<std::vector<Scalar>> contexts(1);
  for (auto a : alphabet) {
    contexts.push_back({{a}});
    for (auto b : alphabet) contexts.push_back({{a}, {b}});
  }
  for (auto before : contexts) for (auto after : contexts) {
    std::vector<Scalar> source = before;
    source.push_back({0x3a3});
    source.insert(source.end(), after.begin(), after.end());
    for (uint32_t mask = 0; mask < (1u << (before.size() + after.size())); ++mask) {
      uint32_t bit = 0;
      for (size_t j = 0; j < source.size(); ++j) {
        if (j == before.size()) continue;
        source[j].firstMask = source[j].secondMask = bool(mask & (1u << bit++));
      }
      check(source, before.size(), true);
    }
  }
  for (size_t n : {size_t(0), size_t(1), size_t(63), size_t(1024), size_t(10000)}) {
    std::vector<Scalar> source{{0x41}};
    source.insert(source.end(), n, {0x0345});
    size_t at = source.size(); source.push_back({0x3a3});
    source.insert(source.end(), n, {0x1d167});
    check(source, at);
    source.push_back({0x41}); check(source, at);
    source[0].firstMask = true; check(source, at);
  }
  for (auto cp : {0xd800u, 0xdbffu, 0xdc00u, 0xdfffu}) {
    check({{cp}, {0x3a3}}, 1, true);
    check({{0x41}, {0x3a3}, {cp}, {0x41}}, 1, true);
  }
  std::printf("{\"all_codepoint_and_pair_mask_checks\":%llu,\"total_checks\":%llu}\n",
              (unsigned long long)exhaustive, (unsigned long long)checks);
}
