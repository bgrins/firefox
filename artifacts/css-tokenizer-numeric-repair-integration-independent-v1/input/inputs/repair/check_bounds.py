from fractions import Fraction as Q
import json
u=Q(1,2**52)
lo,hi=1-u,1+u
minimum_normal=Q(1,2**1022)
maximum=Q(2**853)
b=Q(0)
f_lo=lo/10
f_hi=hi/10
sum_hi=Q(0)
rows=[]
for n in range(256):
 assert f_lo>minimum_normal
 assert b<maximum and sum_hi<2
 assert (b+sum_hi)*hi<maximum
 rows.append({'digits':n,'integral_bound_lt_2pow853':True,'fraction_factor_normal':True,'fraction_sum_lt_2':True,'combined_bound_lt_2pow853':True})
 b=(10*b+9)*hi**2
 sum_hi=(sum_hi+9*f_hi*hi)*hi
 f_lo=f_lo*lo**2/10
 f_hi=f_hi*hi**2/10
assert maximum*minimum_normal*hi+Q(1,2**1074)<Q(1,2**168)
assert Q(1,2**168)<Q(1,2**150)
assert Q(10**255+1,10**308)*hi+Q(1,2**1074)<Q(1,2**150)
print(json.dumps({'status':'PASS','arithmetic':'exact rational','max_short_prefix_digits':255,'unit_roundoff_envelope':'2^-52 (conservative)','rows':rows,'rounded_tiny_product_lt':'2^-168','half_minimum_f32_subnormal':'2^-150','percentage_division_cannot_increase_magnitude':True},indent=2))
