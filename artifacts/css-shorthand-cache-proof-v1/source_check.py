from pathlib import Path
import hashlib,json

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[1]
RECORD=BASE/'SOURCE-v1.json'
RECORD_SHA='6728c4c7e4152c6d80f795b0a26b4cc7327bf7c5d6d7d0e37cef24bf9782afa9'
SOURCE='servo/components/style/properties/mod.rs'
SNIPPETS={
 'owned-entry':'FxHashMap<(ShorthandId, LonghandId), (Arc<UnparsedValue>, PropertyDeclaration)>;',
 'owning-receiver':"impl VariableDeclaration {\n    fn substitute_variables<'cache>(",
 'source-binding':'let longhand_id = self.id;\n        let unparsed = &self.value;',
 'first-guard':'.is_some_and(|(source, _)| Arc::ptr_eq(source, unparsed))',
 'logical-tag':'(shorthand, longhand.to_physical(writing_mode)),\n                    (unparsed.clone(), declaration.clone()),',
 'ordinary-tag':'shorthand_cache.insert((shorthand, longhand), (unparsed.clone(), declaration));',
 'second-guard':'Some((source, decl)) if Arc::ptr_eq(source, unparsed) => Cow::Borrowed(decl),',
}

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def record():
 if sha(RECORD)!=RECORD_SHA:raise RuntimeError('Source record drift')
 return json.loads(RECORD.read_text())

def inputs():
 r=record();result=[RECORD]
 for path,entry in r['files'].items():
  result += [ROOT/path,BASE/entry['current_snapshot'],BASE/entry['old_snapshot']]
 return result

def shape(source):
 for name,snippet in SNIPPETS.items():
  if source.count(snippet)!=1:raise RuntimeError('Reviewed source shape drift: '+name)
 if source.index(SNIPPETS['first-guard'])>=source.index(SNIPPETS['ordinary-tag']):raise RuntimeError('First lookup order')
 if source.index(SNIPPETS['ordinary-tag'])>=source.index(SNIPPETS['second-guard']):raise RuntimeError('Second lookup order')

def run():
 r=record()
 for path,entry in r['files'].items():
  for p,h in [(ROOT/path,entry['current_sha256']),(BASE/entry['current_snapshot'],entry['current_sha256']),(BASE/entry['old_snapshot'],entry['old_sha256'])]:
   if sha(p)!=h:raise RuntimeError('Source drift: '+str(p))
 source=(ROOT/SOURCE).read_text();shape(source)
 rejected=[]
 for name,snippet in SNIPPETS.items():
  bad=source.replace(snippet,'',1)
  try:shape(bad)
  except RuntimeError:rejected.append(name)
  else:raise RuntimeError('Accepted source mutation '+name)
 return r,rejected
