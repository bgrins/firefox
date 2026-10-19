def controls(verify,text,provider):
 lines=text.splitlines();base=lines[0].split('\t');tests={}
 def altered(name,index,value):
  fields=base.copy();fields[index]=value;tests[name]='\n'.join(['\t'.join(fields)]+lines[1:])+'\n'
 altered('junk_bits',12,base[12]+'junk')
 altered('junk_set',13,base[13]+',junk')
 altered('nonbinary_gate',2,'2')
 altered('wrong_name',1,'not-a-case')
 altered('omitted_action',9,','.join(base[9].split(',')[:-1]))
 altered('wrong_seed',6,base[6].replace('2001','2999',1))
 altered('wrong_plan',10,base[10].replace('M1','M0',1))
 altered('wrong_reserve',3,'1')
 tests['extra_field']='\n'.join([lines[0]+'\textra']+lines[1:])+'\n'
 tests['missing_row']='\n'.join(lines[1:])+'\n'
 results=[]
 for name,raw in tests.items():
  try:verify(raw,provider,'candidate')
  except (AssertionError,ValueError,IndexError):results.append({'case':name,'rejected':True})
  else:raise AssertionError(('fail-open row checker',name))
 return results
