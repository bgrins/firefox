from fractions import Fraction as Q
import json
hi=1+Q(1,2**52);lo=1-Q(1,2**52)
a=10*hi**2;c=9*hi**2
b=lambda n:c*(a**n-1)/(a-1)
flo=lambda n:lo**(2*n+1)/10**(n+1)
fhi=lambda n:hi**(2*n+1)/10**(n+1)
s=lambda n:9*hi**(n+2)/10*(1-(hi/10)**n)/(1-hi/10)
minimum=Q(1,2**1022)
for n in range(256):
 assert b(n)>=0 and s(n)>=0
 assert b(n)<=b(255) and s(n)<=s(255)
 assert (b(n)+s(255))*hi<2**853
 assert (b(255)+s(n))*hi<2**853
 assert flo(n)>minimum
 assert 10*b(n)+9<2**1023
 assert 9*fhi(n)<2 and s(n)+9*fhi(n)*hi<4
 if n<255:
  assert b(n+1)==a*b(n)+c
  assert s(n+1)==hi*s(n)+9*fhi(n)*hi**2
  assert flo(n)*(lo/10)>minimum
  assert flo(n+1)==flo(n)*(lo/10)*lo
  assert b(n+1)>=b(n) and s(n+1)>=s(n)
assert (b(255)+s(255))*hi<2**853
native_upper=Q(2**853)*minimum*hi+Q(1,2**1074)
exact_upper=Q(10**255+1,10**308)*hi+Q(1,2**1074)
assert native_upper<Q(1,2**168)<Q(1,2**150)
assert exact_upper<Q(1,2**150)
print(json.dumps({'status':'PASS','method':'closed geometric series and exact rational bounds; not native IEEE verification','digits_checked':list(range(256)),'unequal_lengths':'each accumulator bounded independently by maximum at255','normality':'next exact factor product checked before rounding-envelope use','ordinary_nonzero_products_and_sums':'normal under positive integer digit and factor lower bounds','native_small_lt':'2^-168','robust_parse_small_lt':'half minimum f32 subnormal','premises':['IEEE nearest rounding envelope on admitted normal arithmetic','positive base10 pow classification','correct whole-prefix f64 parsing and f32 cast','signed zero preserved','native forward bounded ASCII prefix']},indent=2))
