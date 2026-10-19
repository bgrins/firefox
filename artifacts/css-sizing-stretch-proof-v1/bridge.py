from pathlib import Path

BASE = Path(__file__).resolve().parent


def branch(text):
    start = text.index('  if (!isAutoOrMaxContentISize) {')
    end = text.index('\n\n  // Flex items ignore', start)
    return text[start:end]


def generate(text):
    natural_start = text.index('  const bool isAutoOrMaxContentISize =')
    natural_end = text.index(';', natural_start) + 1
    return (BASE / 'adapter.cpp').read_text().replace('@NATURAL@', text[natural_start:natural_end]).replace('@BRANCH@', branch(text))
