from dataclasses import dataclass,field
import json
from pathlib import Path
import sys
assert sys.flags.isolated and sys.flags.no_site
@dataclass
class Node:
    own: dict=field(default_factory=dict)
    parent: object=None
    length: int=0
    ancestors: int=0

def lookup(node,key):
    if key in node.own:return node.own[key]
    return lookup(node.parent,key) if node.parent else None

def insert(node,key,value):
    new=key not in node.own
    node.own[key]=value
    if new and (node.parent is None or lookup(node.parent,key) is None):node.length+=1

def shared_insert(node,key,value):
    if lookup(node,key)==value:return node
    if len(node.own)<=8 or node.ancestors>=4:
        result=Node(dict(node.own),node.parent,node.length,node.ancestors)
    else:
        result=Node({},node,node.length,node.ancestors+1)
    insert(result,key,value)
    return result

def original_iter(node):
    descendants=[]
    while node:
        for name,value in node.own.items():
            for descendant in descendants:
                if name in descendant.own:
                    continue
            yield name,value
        descendants.append(node)
        node=node.parent

def reference(node):
    result={}
    while node:
        for key,value in node.own.items():
            if key not in result:result[key]=value
        node=node.parent
    return list(result.items())

def corrected_iter(node):
    descendants=[]
    while node:
        for name,value in node.own.items():
            if any(name in descendant.own for descendant in descendants):continue
            yield name,value
        descendants.append(node)
        node=node.parent

rows=[]
for count,changes in [(8,[(0,'child')]),(9,[(0,'child')]),(9,[(0,'first'),(1,'second')]),(9,[]),(9,[(0,'parent')]),(9,[(9,'new')])]:
    parent=Node()
    for i in range(count):insert(parent,str(i),'parent')
    child=parent
    for key,value in changes:child=shared_insert(child,str(key),value)
    actual=list(original_iter(child));expected=reference(child);fixed=list(corrected_iter(child))
    assert fixed==expected
    rows.append({'parent_size':count,'changes':changes,'ancestors':child.ancestors,'stored_len':child.length,'original_full_iterator':actual,'original_cssom_prefix':actual[:child.length],'independent_first_owner_reference':expected,'proposed_label_equivalent':fixed,'mismatch':actual[:child.length]!=expected})
assert [r['mismatch'] for r in rows]==[False,True,True,False,False,False]
print(json.dumps({'kind':'finite Python source-shaped model; not actual Rust execution or universal proof','rows':rows},indent=2))
