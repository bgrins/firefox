from pathlib import Path
import argparse, hashlib, json, sys
assert sys.flags.isolated and sys.flags.no_site
ROOT=Path(__file__).resolve().parents[1]
def generate():
    parser=(ROOT/'source/parser.rs').read_text()
    tokenizer=(ROOT/'source/tokenizer.rs').read_text()
    requests=[
        ('parser.rs','ParserState',parser,'pub struct ParserState {','\n}'),
        ('parser.rs','packed constants',parser,'    const BLOCK_TYPE_BITS: u32 = 2;','\n\n'),
        ('parser.rs','BlockType',parser,'pub(crate) enum BlockType {','\n}'),
        ('tokenizer.rs','SourcePosition',tokenizer,'pub struct SourcePosition(pub(crate) usize);','\n'),
        ('tokenizer.rs','SourcePosition accessor',tokenizer,'impl SourcePosition {','\n}'),
    ]
    records=[]
    for file,name,text,start_marker,end_marker in requests:
        assert text.count(start_marker)==1
        start=text.index(start_marker)
        end=text.index(end_marker,start)+len(end_marker)
        body=text[start:end]
        records.append({'source':file,'name':name,'start':start,'end':end,
                        'sha256':hashlib.sha256(body.encode()).hexdigest(),'complete_declaration':body})
    return records
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    records=generate();a.output.write_text(json.dumps(records,indent=2)+'\n')
    print(len(records),'complete field/constant declarations')
