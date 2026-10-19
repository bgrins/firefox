import functools
import re
from html.parser import HTMLParser


class Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)


class UnicodeOracle:
    def __init__(self, root):
        self.categories = ["Cn"] * 0x110000
        self.combining = {}
        self.decompositions = {}
        first = None
        for line in (root / "spec/UnicodeData-17.0.0.txt").read_text().splitlines():
            fields = line.split(";")
            cp = int(fields[0], 16)
            name, category = fields[1:3]
            if name.endswith(", First>"):
                assert first is None
                first = (cp, category, name[:-8])
            elif name.endswith(", Last>"):
                assert first and first[1] == category and first[2] == name[:-7]
                self.categories[first[0]:cp + 1] = [category] * (cp + 1 - first[0])
                first = None
            else:
                assert first is None
                self.categories[cp] = category
            if int(fields[3]):
                self.combining[cp] = int(fields[3])
            raw = fields[5].split()
            if raw and raw[0].startswith("<"):
                raw = raw[1:]
            if raw:
                self.decompositions[cp] = tuple(int(c, 16) for c in raw)
        assert first is None
        parser = Text()
        parser.feed((root / "spec/css-text-decor-3.html").read_text())
        text = " ".join(" ".join(parser.parts).split())
        start = text.index("Punctuation--specifically,")
        end = text.index("Characters belonging to the Unicode classes", start)
        self.base_exceptions = frozenset(int(c, 16) for c in re.findall(r"U\+([0-9A-F]{4,6})", text[start:end]))
        assert len(self.base_exceptions) == 15

    @functools.lru_cache(maxsize=None)
    def decompose(self, cp):
        if 0xAC00 <= cp < 0xD7A4:
            n = cp - 0xAC00
            result = (0x1100 + n // 588, 0x1161 + (n % 588) // 28)
            return result + ((0x11A7 + n % 28,) if n % 28 else ())
        if cp not in self.decompositions:
            return (cp,)
        return tuple(c for d in self.decompositions[cp] for c in self.decompose(d))

    def nfkd(self, sequence):
        result = []
        for cp in sequence:
            for item in self.decompose(cp):
                result.append(item)
                cc = self.combining.get(item, 0)
                i = len(result) - 1
                while cc and i and self.combining.get(result[i - 1], 0) > cc:
                    result[i - 1], result[i] = result[i], result[i - 1]
                    i -= 1
        return tuple(result)

    def eligible(self, cp):
        category = self.categories[cp]
        if category[0] == "Z" or category in {"Cc", "Cf", "Cn", "Cs"}:
            return False
        if category[0] == "P":
            normalized = self.nfkd((cp,))
            return len(normalized) == 1 and normalized[0] in self.base_exceptions
        return True

    def validate_normalization(self, root):
        count = 0
        for line in (root / "spec/NormalizationTest-17.0.0.txt").read_text().splitlines():
            line = line.split("#", 1)[0].strip()
            if not line or line.startswith("@"):
                continue
            fields = [tuple(int(c, 16) for c in column.split()) for column in line.split(";")[:5]]
            assert all(self.nfkd(field) == fields[4] for field in fields), fields
            count += 1
        return count

    def decode(self, units, latin1=False):
        assert all(0 <= c < (256 if latin1 else 65536) for c in units)
        i = 0
        result = []
        while i < len(units):
            cp, width = units[i], 1
            if not latin1 and 0xD800 <= cp <= 0xDBFF and i + 1 < len(units) and 0xDC00 <= units[i + 1] <= 0xDFFF:
                cp, width = 65536 + (cp - 0xD800) * 1024 + units[i + 1] - 0xDC00, 2
            result.append((i, width, cp, self.eligible(cp)))
            i += width
        return result
