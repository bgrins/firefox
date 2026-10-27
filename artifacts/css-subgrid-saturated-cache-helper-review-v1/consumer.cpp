#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <iostream>
#include <string>
struct Result { uint64_t remaining, remainder, grouped; };
Result width32(int32_t mClampMaxLine, uint32_t stored, uint32_t fillLen) {
    struct { uint32_t expanded_line_names_length; } aStyleLineNameList{stored};
    const uint32_t maxLine = std::max<int32_t>(0, mClampMaxLine);
      const uint32_t fixedLineCount = aStyleLineNameList.expanded_line_names_length;
      // Maximum possible number of repeat name lists.
      // Note: |expanded_line_names_length| doesn't include auto repeat.
      const uint32_t possibleRepeatLength =
          maxLine > fixedLineCount ? uint32_t(maxLine - fixedLineCount) : 0;
    const uint32_t repeatRemainder = possibleRepeatLength % fillLen;
    const uint32_t len = possibleRepeatLength - repeatRemainder;
    return {possibleRepeatLength, repeatRemainder, len};
}

Result width64(int32_t mClampMaxLine, uint64_t stored, uint64_t fillLen) {
    struct { uint64_t expanded_line_names_length; } aStyleLineNameList{stored};
    const uint64_t maxLine = std::max<int32_t>(0, mClampMaxLine);
      const uint64_t fixedLineCount = aStyleLineNameList.expanded_line_names_length;
      // Maximum possible number of repeat name lists.
      // Note: |expanded_line_names_length| doesn't include auto repeat.
      const uint32_t possibleRepeatLength =
          maxLine > fixedLineCount ? uint32_t(maxLine - fixedLineCount) : 0;
    const uint32_t repeatRemainder = possibleRepeatLength % fillLen;
    const uint64_t len = possibleRepeatLength - repeatRemainder;
    return {possibleRepeatLength, repeatRemainder, len};
}

Result host(int32_t mClampMaxLine, size_t stored, size_t fillLen) {
    struct { size_t expanded_line_names_length; } aStyleLineNameList{stored};
    const size_t maxLine = std::max<int32_t>(0, mClampMaxLine);
      const size_t fixedLineCount = aStyleLineNameList.expanded_line_names_length;
      // Maximum possible number of repeat name lists.
      // Note: |expanded_line_names_length| doesn't include auto repeat.
      const uint32_t possibleRepeatLength =
          maxLine > fixedLineCount ? uint32_t(maxLine - fixedLineCount) : 0;
    const uint32_t repeatRemainder = possibleRepeatLength % fillLen;
    const size_t len = possibleRepeatLength - repeatRemainder;
    return {possibleRepeatLength, repeatRemainder, len};
}
int main() {
    std::cout << "host_bits " << sizeof(size_t)*8 << '\n';
    std::string id, mode;
    int32_t cap;
    uint64_t stored, fill;
    while (std::cin >> id >> mode >> cap >> stored >> fill) {
        if (fill == 0) return 2;
        Result result;
        if (mode == "width32") {
            if (stored > UINT32_MAX || fill > UINT32_MAX) return 3;
            result = width32(cap, uint32_t(stored), uint32_t(fill));
        } else if (mode == "width64") {
            result = width64(cap, stored, fill);
        } else if (mode == "host") {
            if (stored > SIZE_MAX || fill > SIZE_MAX) return 4;
            result = host(cap, size_t(stored), size_t(fill));
        } else return 5;
        std::cout << id << ' ' << result.remaining << ' ' << result.remainder << ' ' << result.grouped << '\n';
    }
    return std::cin.eof() ? 0 : 6;
}
