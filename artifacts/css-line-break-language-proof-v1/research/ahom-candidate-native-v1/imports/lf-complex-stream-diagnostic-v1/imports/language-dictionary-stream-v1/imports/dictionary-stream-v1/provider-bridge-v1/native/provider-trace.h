#include <sstream>
extern "C" void language_trace(const char*);
static void provider_event(const std::string& event) { language_trace(event.c_str()); }
template<class T> static void provider_input(T text, unsigned word, unsigned line, bool script) {
  std::ostringstream s;
  s << "provider input " << sizeof(text[0])*8 << ' ' << word << ' ' << line << ' ' << script;
  for(auto unit:text) s << ' ' << unsigned(unit);
  provider_event(s.str());
}
