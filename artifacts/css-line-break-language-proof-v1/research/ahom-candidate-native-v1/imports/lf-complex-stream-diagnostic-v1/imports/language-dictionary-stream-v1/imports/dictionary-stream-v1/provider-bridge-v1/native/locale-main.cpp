#define DEBUG 1
#include "locale-prefix.h"
#include "locale-glue.h"
#include "gecko-locale.h"
#include "locale.cpp"
#include "locale-generated.cpp"
#include <iostream>
int main() {
  using namespace mozilla::intl;
  std::string line;
  while (std::getline(std::cin,line)) {
    Locale locale;
    auto parsed=LocaleParser::TryParse(mozilla::Span<const char>(line.data(),line.size()),locale);
    if(parsed.isErr()) { std::cout << "parse-error\n"; continue; }
    auto added=locale.AddLikelySubtags();
    if(added.isErr()) { std::cout << "likely-error\n"; continue; }
    for(auto s:{locale.Language().Span(),locale.Script().Span(),locale.Region().Span()})
      std::cout << std::string(s.data(),s.size()) << ' ';
    std::cout << '\n';
  }
}
