def controls(verify,text,providers):
 lines=text.splitlines();first=lines[0].split('\t');tests={}
 for name,index,value in [('junk_bits',9,first[9]+'junk'),('junk_set',10,first[10]+'junk'),('gate_two',3,'2'),('claimed_two',2,'2'),('wrong_name',1,'wrong-case')]:
  changed=first.copy();changed[index]=value;tests[name]='\n'.join(['\t'.join(changed)]+lines[1:])+'\n'
 tests['extra_tab_field']=lines[0]+'\textra\n'+'\n'.join(lines[1:])+'\n'
 tests['missing_final_row']='\n'.join(lines[:-1])+'\n'
 # This first case starts empty, so removing one action and all corresponding
 # result fields is internally consistent but violates its named input.
 import re
 rowpat=r'Row \{ key: \d+, value: \d+, important: (?:true|false) \}'
 modified=first.copy()
 oldrows=re.findall(rowpat,first[8]);removed_key=int(re.search(r'key: (\d+)',oldrows[-1])[1])
 for i in [6,7,8]:modified[i]='['+', '.join(oldrows[:-1])+']'
 modified[9]='['+', '.join(re.findall(r'true|false',first[9])[:-1])+']'
 ids=[int(x) for x in re.findall(r'LonghandId\((\d+)\)',first[10]) if int(x)!=removed_key]
 modified[10]='{'+', '.join(f'LonghandId({x})' for x in ids)+'}'
 tests['self_consistent_omitted_all_action']='\n'.join(['\t'.join(modified)]+lines[1:])+'\n'
 results=[]
 for name,altered in tests.items():
  try:verify(altered,providers,'candidate',0)
  except AssertionError as e:results.append({'name':name,'rejected':True,'reason':str(e)[:300]})
  else:raise AssertionError(('row guard accepted',name))
 return results
