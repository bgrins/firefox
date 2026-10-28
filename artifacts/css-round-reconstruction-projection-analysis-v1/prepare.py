from pathlib import Path
P=Path(__file__).resolve().parent
common='''(set-logic QF_FP)
(set-option :timeout 45000)
(set-option :parallel.enable false)
(set-option :smt.threads 1)
(define-sort F32 () (_ FloatingPoint 8 24))
(define-sort F64 () (_ FloatingPoint 11 53))
(define-fun wide ((x F32)) F64 ((_ to_fp 11 53) RNE x))
(define-fun finite ((x F32)) Bool (and (not (fp.isNaN x)) (not (fp.isInfinite x))))
(define-fun positive ((x F32)) Bool (and (finite x) (fp.gt x (_ +zero 8 24))))
(declare-fun b () F32)
(declare-fun r () F32)
(assert (and (positive b) (positive r) (fp.lt r b)))
(define-fun wb () F64 (wide b))
(define-fun wr () F64 (wide r))
(define-fun far () F64 (fp.sub RNE wb wr))
(define-fun twice () F64 (fp.mul RNE wr ((_ to_fp 11 53) RNE 2.0)))
'''
queries={
'distance-positive':common+'(assert (xor (fp.lt wr far) (fp.lt twice wb)))\n(check-sat)\n',
'distance-negative':common+'(assert (xor (fp.lt far wr) (fp.lt wb twice)))\n(check-sat)\n',
'bad-tie-adapter':common+'(assert (fp.eq twice wb))\n(assert (xor (fp.leq wr far) (fp.lt twice wb)))\n(check-sat)\n(get-value (b r))\n',
'small-step-projection':common+'''(declare-fun a () F32)
(assert (positive a))
(define-fun wa () F64 (wide a))
(define-fun threshold () F64 (fp.mul RNE wa ((_ to_fp 11 53) RNE (/ 1.0 268435456.0))))
(assert (fp.lt wb threshold))
(define-fun toward () F64 (fp.sub RNE wa wr))
(define-fun other () F64 (fp.add RNE toward wb))
(assert (or (not (= ((_ to_fp 8 24) RNE toward) a)) (not (= ((_ to_fp 8 24) RNE other) a))))
(check-sat)
'''}
for n,s in queries.items():(P/(n+'.smt2')).write_text(s)

s=(P/'small-step-projection.smt2').read_text()
prefix=s[:s.index('(define-fun toward')]
body="""(define-fun downLo () F64 (fp.sub RTN wa wr))
(define-fun upLo () F64 (fp.sub RTP wa wr))
(define-fun downHi () F64 (fp.add RTN downLo wb))
(define-fun upHi () F64 (fp.add RTP upLo wb))
(define-fun project ((x F64)) F32 ((_ to_fp 8 24) RNE x))
(assert (or (not (= (project downLo) a)) (not (= (project upLo) a))
            (not (= (project downHi) a)) (not (= (project upHi) a))
            (not (= (project (fp.neg downLo)) (fp.neg a)))
            (not (= (project (fp.neg upLo)) (fp.neg a)))
            (not (= (project (fp.neg downHi)) (fp.neg a)))
            (not (= (project (fp.neg upHi)) (fp.neg a)))))
(check-sat)
"""
(P/'small-step-exact-enclosure.smt2').write_text(prefix+body)
neg=s.replace('(assert (fp.lt wb threshold))',"""(assert (= a ((_ to_fp 8 24) RNE 1.0)))
(assert (= b ((_ to_fp 8 24) RNE 0.75)))
(assert (= r ((_ to_fp 8 24) RNE 0.25)))""")+'(get-value (a b r))\n'
(P/'bad-omitted-small-premise.smt2').write_text(neg)
nonv=prefix+"""(assert (= a ((_ to_fp 8 24) #x3f800000)))
(assert (= b ((_ to_fp 8 24) #x00000005)))
(assert (= r ((_ to_fp 8 24) #x00000002)))
(check-sat)
(get-value (a b r))
"""
(P/'small-step-nonvacuity.smt2').write_text(nonv)
