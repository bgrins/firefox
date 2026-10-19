from pathlib import Path
import json,hashlib
p=Path(__file__).resolve().parent;j=json.loads((p/'inputs/SOURCE-BINDING.json').read_text());a=(p/j['source']).read_text();b=(p/j['candidate']).read_text();marker='impl LineBreakType for Utf16 {';x=a.index(marker);y=a.index('#[cfg(test)]',x);u=b.index(marker);v=b.index('#[cfg(test)]',u);assert a[:x]==b[:u]and a[y:]==b[v:]
t=a[x:y]
for old,new in j['replacements']:assert t.count(old)==1;t=t.replace(old,new)
assert t==b[u:v]
assert hashlib.sha256(a[x:y].encode()).hexdigest()==j['original_impl_sha256']
assert hashlib.sha256(b[u:v].encode()).hexdigest()==j['candidate_impl_sha256']
s=(p/j['source']).with_name('rule_segmenter.rs').read_text();n=s.index(marker.replace('LineBreakType','RuleBreakType'));body=s[n:]
assert 'fn char_len(ch: Self::CharType) -> usize {\n        if ch >= 0x10000 {\n            2\n        } else {\n            1\n        }\n    }'in body
print('full source delta and actual char_len bound')
