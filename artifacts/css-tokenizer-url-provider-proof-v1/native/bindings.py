from pathlib import Path
import argparse,re,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
def extract(source,name,indent=0):
 pattern=r'^'+(' '*indent)+r'(?:pub(?:\([^)]*\))? )?(?:unsafe )?fn '+re.escape(name)+r'[<(]'
 hits=list(re.finditer(pattern,source,re.M));assert len(hits)==1,(name,len(hits))
 start=hits[0].start();end=source.index('\n'+' '*indent+'}',start)+1+indent+1
 return start,end,source[start:end]
def generate():
 records=[]
 requests={
 'tokenizer.rs':[(n,0)for n in ['next_token_unchecked','is_ident_start','consume_ident_like','consume_name','consume_string','consume_quoted_string','consume_unquoted_url','consume_hex_digits','consume_escape_and_write','consume_escape','byte_to_hex_digit','from_utf8_release_unchecked']]+[(n,4)for n in ['see_function','look_for_arbitrary_substitution_functions','seen_arbitrary_substitution_functions','next_unchecked','position','current_source_location','slice_from','slice','next_byte','next_byte_unchecked','is_eof','has_at_least','has_newline_at','advance','advance_while','byte_at','consume_known_byte','consume_4byte_intro','consume_continuation_byte','next_char','consume_newline','consume_char','consume_unquoted_url_internal','consume_url_end','consume_bad_url']],
 'parser.rs':[(n,4)for n in ['position','source_location','line_number','advance_line_number','set_at_start_of','take_at_start_of','at_start_of']]}
 for source,items in requests.items():
  text=(ROOT/'source'/source).read_text()
  for name,indent in items:
   start,end,body=extract(text,name,indent)
   records.append({'source':source,'name':name,'indent':indent,'start':start,'end':end,'sha256':hashlib.sha256(body.encode()).hexdigest(),'full_body':body})
 return records
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();records=generate();a.output.write_text(json.dumps(records,indent=2)+'\n');print(len(records),'complete source definitions')
