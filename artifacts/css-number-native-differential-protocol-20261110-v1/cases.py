import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PREFIX = '"é𐀀" '


def eligible(source):
    raw = source.encode()
    normalized = all(b < 128 and b not in (0, 13, 12) for b in raw)
    entry = raw[1:] if raw[:1] in (b'+', b'-') else raw
    starts = bool(entry) and (48 <= entry[0] <= 57 or
        (entry[0] == 46 and len(entry) > 1 and 48 <= entry[1] <= 57))
    return normalized and starts


def cases():
    old = json.loads((ROOT / 'inputs/legacy-cases.json').read_text())
    seeds = [(f'legacy-{i}', '', c['css'], i) for i, c in enumerate(old) if c['model']]
    assert len(seeds) == 81
    seeds += [('utf8-fraction', PREFIX, '.5px', None),
              ('utf8-escape', PREFIX, '1\\65 m', None),
              ('utf8-compensated', PREFIX, '5' + '0' * 308 + 'e-309em', None)]
    assert len(seeds) == 84
    result = []
    for name, prefix, tail, legacy in seeds:
        for history in [False, True]:
            value = tail + (' ;q' if history else '')
            result.append(dict(id=name + ('-history' if history else '-single'), group='inherited-84',
                legacy_case_index=legacy, prefix=prefix, tail=value,
                prefix_utf8_bytes=len(prefix.encode()), warmup_tokens=2 if prefix else 0,
                mode='history' if history else 'single', bridge_eligible=eligible(value)))
    new = ['1e+', '1e-', '+.5E+', '1e\\+x', '1E+2px', '1%1em']
    new += ['0' * (n - 1) + '1em' for n in [254, 255, 256, 257]]
    new += ['1' + '0' * (n - 6) + 'e-100em' for n in [254, 255, 256, 257]]
    for i, tail in enumerate(new):
        for prefix in ['', PREFIX]:
            result.append(dict(id=f'extension-{i}-' + ('utf8' if prefix else 'zero'), group='new-history',
                legacy_case_index=None, prefix=prefix, tail=tail + ' ;q',
                prefix_utf8_bytes=len(prefix.encode()), warmup_tokens=2 if prefix else 0,
                mode='history', bridge_eligible=True))
    assert len({c['id'] for c in result}) == len(result)
    return result


def emit(out):
    out.mkdir(parents=True, exist_ok=False)
    rows = cases()
    (out / 'CASES.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2) + '\n')
    (out / 'native-input.tsv').write_text(''.join(
        f"{c['id']}\t{c['warmup_tokens']}\t{c['prefix_utf8_bytes']}\t{c['mode']}\t{(c['prefix'] + c['tail']).encode().hex()}\n"
        for c in rows))
    admitted = [c for c in rows if c['bridge_eligible']]
    (out / 'model-input.json').write_text(json.dumps([[c['tail'], False] for c in admitted], ensure_ascii=False) + '\n')
    (out / 'model-ids.json').write_text(json.dumps([c['id'] for c in admitted], indent=2) + '\n')
    return rows


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--out', required=True, type=Path)
    emit(p.parse_args().out)
