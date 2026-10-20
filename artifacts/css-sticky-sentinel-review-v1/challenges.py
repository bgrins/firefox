import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError("Require python3 -I -S without optimization")
sys.dont_write_bytecode=True
import json
LOW=-536870911
HIGH=536870912
def step(n,low,high,cmin,cmax,near,far):
    if near:n=max(n,min(low,cmax))
    if far:n=min(n,max(high,cmin))
    return n
rows=[]
for label,n,low,high,cmin,cmax,near,far,expected in [
 ("all-auto",700000000,LOW,HIGH,0,900000000,False,False,700000000),
 ("near-only-must-not-use-auto-far",700000000,0,HIGH,0,900000000,True,False,700000000),
 ("far-only",700000000,LOW,90,0,900000000,False,True,90),
 ("explicit-far-equals-sentinel",700000000,LOW,HIGH,0,900000000,False,True,HIGH),
 ("explicit-near-equals-sentinel",-700000000,LOW,HIGH,-900000000,900000000,True,False,LOW),
 ("both-preserve-order",0,10,-10,-100,100,True,True,-10)]:
    actual=step(n,low,high,cmin,cmax,near,far);assert actual==expected
    original=step(n,low,high,cmin,cmax,True,True)
    numerical_guard=step(n,low,high,cmin,cmax,low!=LOW,high!=HIGH)
    rows.append({"case":label,"normal":n,"near_active":near,"far_active":far,"correct":actual,"old":original,"numeric_edge_guard":numerical_guard})
assert 100-(-536870822)-10==HIGH
assert -536870822!=-1073741823 and -536870822!=1073741823
print(json.dumps({"scope":"Independent exact-integer boundary calculations; not compiled native execution or browser reachability", "cases":rows,"explicit_far_edge_construction":{"scrollport":100,"box":10,"bottom_inset":-536870822,"computed_edge":HIGH},"missing_property_policy":"normal position for both axes"},indent=2))
