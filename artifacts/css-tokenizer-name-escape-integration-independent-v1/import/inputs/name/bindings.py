import argparse
import hashlib
import json
from pathlib import Path
import rust_reader

ROOT = Path(__file__).resolve().parent
NAMES = ['is_eof','has_at_least','advance','advance_while','next_byte_unchecked','byte_at',
         'consume_4byte_intro','consume_continuation_byte','consume_newline','has_newline_at',
         'consume_char','next_char','next_token_unchecked','is_ident_start','consume_ident_like',
         'consume_name','byte_to_hex_digit','consume_numeric','consume_hex_digits',
         'consume_escape_and_write','consume_escape']

def extract():
    path = ROOT / 'source/cssparser/src/tokenizer.rs'
    source = path.read_text()
    ts = rust_reader.tokens(source)
    result = []
    for name in NAMES:
        found = [i for i in range(len(ts)-1) if ts[i][0] == 'fn' and ts[i+1][0] == name]
        assert len(found) == 1, (name, found)
        i = found[0]
        j = i+2
        while ts[j][0] != '{':
            j += 1
        end = rust_reader.pair(ts,j)
        body = source[ts[i][1]:ts[end][2]]
        result.append(dict(name=name,source='source/cssparser/src/tokenizer.rs',
                           byte_start=len(source[:ts[i][1]].encode()),
                           byte_end=len(source[:ts[end][2]].encode()),
                           sha256=hashlib.sha256(body.encode()).hexdigest(),body=body))
    return result

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--output',type=Path,required=True)
    a = p.parse_args()
    a.output.write_text(json.dumps(extract(),indent=2)+'\n')
